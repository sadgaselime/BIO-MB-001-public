"""Provenance-preserving retrieval of GEO files.

Rules implemented here:
  * Raw files are written once. A completed file is made read-only (chmod 444).
  * An existing file is NEVER overwritten. It is re-used only after its size is
    verified against the server (and its checksum against the manifest, if any);
    otherwise a CONFLICT status is recorded and a human must decide.
  * Downloads stream into '<name>.part' and are resumed with HTTP Range requests
    when possible. Only a fully verified file is renamed to its final name.
  * Every attempt (success or failure) is appended to a JSON manifest holding the
    source URL, timestamps, sizes, SHA-256 and status.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import logging
import os
import stat
import tarfile
import tempfile
import time
import zlib
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .geo_client import GeoAccessError, GeoClient, GeoNotFoundError, OfflineModeError

log = logging.getLogger(__name__)

CHUNK = 1024 * 1024
STREAM_CHUNK = 256 * 1024

# Status vocabulary for retrieval records.
DOWNLOADED = "DOWNLOADED"
REUSED_VERIFIED = "REUSED_VERIFIED"                    # size matches server; checksum matches manifest if recorded
REUSED_VERIFIED_MANIFEST = "REUSED_VERIFIED_AGAINST_MANIFEST"  # offline: checksum matches earlier record
REUSED_UNVERIFIED = "REUSED_UNVERIFIED"                # exists, but could not be verified against server or manifest
SKIPPED_TOO_LARGE = "SKIPPED_TOO_LARGE"
SKIPPED_NOT_REQUESTED = "SKIPPED_NOT_REQUESTED"
SKIPPED_OFFLINE = "SKIPPED_OFFLINE"
FAILED = "FAILED"
FAILED_NOT_FOUND = "FAILED_NOT_FOUND"
FAILED_SIZE_MISMATCH = "FAILED_SIZE_MISMATCH"
FAILED_INTEGRITY = "FAILED_INTEGRITY"
CONFLICT = "CONFLICT_EXISTING_FILE_DIFFERS"

AVAILABLE_STATUSES = {DOWNLOADED, REUSED_VERIFIED, REUSED_VERIFIED_MANIFEST, REUSED_UNVERIFIED}


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(CHUNK), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check_integrity(path: Path) -> dict[str, Any]:
    """Structural integrity check by file type, without modifying or extracting anything."""
    path = Path(path)
    with open(path, "rb") as fh:
        magic = fh.read(2)
    try:
        if magic == b"\x1f\x8b":
            n = 0
            with gzip.open(path, "rb") as gz:
                for chunk in iter(lambda: gz.read(CHUNK), b""):
                    n += len(chunk)
            return {"method": "gzip_full_decompression", "ok": True, "detail": f"{n} uncompressed bytes"}
        if tarfile.is_tarfile(path):
            with tarfile.open(path, "r:") as tf:
                members = tf.getmembers()
            return {"method": "tar_member_listing", "ok": True, "detail": f"{len(members)} members"}
    except (OSError, EOFError, zlib.error, tarfile.TarError) as exc:
        return {"method": "gzip/tar", "ok": False, "detail": f"{type(exc).__name__}: {exc}"}
    return {"method": "none_applicable", "ok": True, "detail": "plain file; size and checksum only"}


def make_read_only(path: Path) -> None:
    mode = os.stat(path).st_mode
    os.chmod(path, mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        os.chmod(tmp, 0o644)  # mkstemp creates 0600; reports/manifests should be readable by collaborators
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


@dataclass
class RetrievalRecord:
    name: str
    url: str | None
    path: str
    status: str
    started_at: str = field(default_factory=utcnow)
    finished_at: str | None = None
    remote_size: int | None = None
    local_size: int | None = None
    sha256: str | None = None
    remote_last_modified: str | None = None
    resumed: bool = False
    integrity: dict[str, Any] | None = None
    network_used: bool = False
    error: str | None = None
    notes: list[str] = field(default_factory=list)

    @property
    def available(self) -> bool:
        return self.status in AVAILABLE_STATUSES

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["available_locally"] = self.available
        return d


class Manifest:
    """JSON manifest of retrieval attempts: {"files": {name: {"current": {...}, "history": [...]}}}."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self.data: dict[str, Any] = {"files": {}}
        if self.path.exists():
            self.data = json.loads(self.path.read_text(encoding="utf-8"))
            self.data.setdefault("files", {})

    def current(self, name: str) -> dict[str, Any] | None:
        return (self.data["files"].get(name) or {}).get("current")

    def last_verified_sha(self, name: str) -> str | None:
        """Most recent checksum recorded for a locally available copy of this file."""
        for entry in reversed((self.data["files"].get(name) or {}).get("history", [])):
            if entry.get("available_locally") and entry.get("sha256"):
                return entry["sha256"]
        return None

    def record(self, rec: RetrievalRecord) -> None:
        entry = self.data["files"].setdefault(rec.name, {"history": []})
        d = rec.to_dict()
        try:  # record new entries relative to the manifest directory; earlier entries are left untouched
            d["path"] = str(Path(rec.path).resolve().relative_to(self.path.parent.resolve()))
        except ValueError:
            pass
        entry["current"] = d
        entry["history"].append(d)
        self.save()

    def save(self) -> None:
        atomic_write_text(self.path, json.dumps(self.data, indent=2, sort_keys=True) + "\n")


def _finish(rec: RetrievalRecord, manifest: Manifest | None) -> RetrievalRecord:
    rec.finished_at = utcnow()
    if manifest is not None:
        manifest.record(rec)
    level = logging.INFO if rec.available or rec.status.startswith("SKIPPED") else logging.WARNING
    log.log(level, "%s -> %s%s", rec.name, rec.status, f" ({rec.error})" if rec.error else "")
    return rec


def _verify_existing(rec: RetrievalRecord, dest: Path, manifest: Manifest | None) -> RetrievalRecord:
    """Decide whether an existing local file can be re-used. Never modifies it."""
    rec.local_size = dest.stat().st_size
    rec.sha256 = sha256_file(dest)
    prior_sha = manifest.last_verified_sha(dest.name) if manifest else None
    if prior_sha and prior_sha != rec.sha256:
        rec.status = CONFLICT
        rec.error = (f"local file checksum {rec.sha256[:12]}... differs from previously recorded "
                     f"{prior_sha[:12]}...; file left untouched - human review required")
        return rec
    if rec.remote_size is not None and rec.local_size != rec.remote_size:
        rec.status = CONFLICT
        rec.error = (f"local size {rec.local_size} != server size {rec.remote_size}; existing file left "
                     f"untouched. Move it aside manually if a fresh download is wanted.")
        return rec
    rec.integrity = check_integrity(dest)
    if not rec.integrity["ok"]:
        rec.status = FAILED_INTEGRITY
        rec.error = f"existing file failed integrity check: {rec.integrity['detail']}"
        return rec
    if rec.remote_size is not None:
        rec.status = REUSED_VERIFIED
        rec.notes.append("existing file re-used: size matches server" + ("; checksum matches manifest" if prior_sha else ""))
    elif prior_sha:
        rec.status = REUSED_VERIFIED_MANIFEST
        rec.notes.append("existing file re-used: checksum matches earlier manifest record (server not consulted)")
    else:
        rec.status = REUSED_UNVERIFIED
        rec.notes.append("existing file re-used but could not be verified against server or manifest")
    return rec


def download_file(
    client: GeoClient,
    url: str,
    dest: Path,
    max_bytes: int,
    manifest: Manifest | None = None,
) -> RetrievalRecord:
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    rec = RetrievalRecord(name=dest.name, url=url, path=str(dest), status=FAILED)

    if client.offline:
        if dest.exists():
            return _finish(_verify_existing(rec, dest, manifest), manifest)
        rec.status = SKIPPED_OFFLINE
        rec.notes.append("offline mode: file not present locally and no download attempted")
        return _finish(rec, manifest)

    rec.network_used = True
    try:
        info = client.head(url)
        rec.remote_size = info.get("size")
        rec.remote_last_modified = info.get("last_modified")
    except GeoNotFoundError as exc:
        rec.status, rec.error = FAILED_NOT_FOUND, str(exc)
        return _finish(rec, manifest)
    except (GeoAccessError, OfflineModeError) as exc:
        rec.status, rec.error = FAILED, f"HEAD request failed: {exc}"
        return _finish(rec, manifest)

    if dest.exists():
        return _finish(_verify_existing(rec, dest, manifest), manifest)

    if rec.remote_size is not None and rec.remote_size > max_bytes:
        rec.status = SKIPPED_TOO_LARGE
        rec.notes.append(
            f"server size {rec.remote_size / 1e6:.1f} MB exceeds limit {max_bytes / 1e6:.0f} MB. To retrieve later: "
            f"re-run with --max-download-mb {int(rec.remote_size / 1e6) + 10}, or manually: "
            f"curl -C - -o '{dest}.part' '{url}' && mv '{dest}.part' '{dest}' (then re-run the audit to verify)."
        )
        return _finish(rec, manifest)

    part = dest.with_name(dest.name + ".part")
    resume_from = part.stat().st_size if part.exists() else 0
    if rec.remote_size is not None and resume_from > rec.remote_size:
        log.warning("Discarding partial download larger than server file: %s", part)
        part.unlink()
        resume_from = 0
    headers = {"Range": f"bytes={resume_from}-"} if resume_from else {}
    try:
        if resume_from and rec.remote_size is not None and resume_from == rec.remote_size:
            rec.resumed = True
            rec.notes.append("partial file already had full size; verifying instead of re-downloading")
        else:
            resp = client.stream(url, headers=headers)
            try:
                mode = "ab"
                if resume_from and resp.status_code == 206:
                    rec.resumed = True
                    rec.notes.append(f"resumed from byte {resume_from}")
                elif resume_from:
                    mode = "wb"
                    rec.notes.append("server ignored Range request; restarted download from byte 0")
                written = resume_from if mode == "ab" else 0
                started, this_session = time.monotonic(), 0
                window = client.settings.stall_window_seconds
                min_rate = client.settings.min_download_kb_per_s * 1000
                with open(part, mode) as fh:
                    for chunk in resp.iter_content(chunk_size=STREAM_CHUNK):
                        if not chunk:
                            continue
                        fh.write(chunk)
                        written += len(chunk)
                        this_session += len(chunk)
                        if written > max_bytes:
                            raise GeoAccessError(f"download exceeded size limit {max_bytes} bytes", url)
                        elapsed = time.monotonic() - started
                        if min_rate and elapsed > window and this_session / elapsed < min_rate:
                            raise GeoAccessError(
                                f"transfer stalled: {this_session / elapsed / 1000:.1f} KB/s average over {elapsed:.0f}s "
                                f"(minimum {min_rate / 1000:.0f} KB/s); partial data kept for resumption", url)
            finally:
                resp.close()
    except (GeoAccessError, OfflineModeError, OSError) as exc:
        rec.status, rec.error = FAILED, f"download failed: {exc}"
        rec.notes.append(f"partial data (if any) kept at {part} for resumption")
        return _finish(rec, manifest)
    except Exception as exc:  # e.g. requests ChunkedEncodingError mid-stream
        rec.status, rec.error = FAILED, f"download interrupted: {type(exc).__name__}: {exc}"
        rec.notes.append(f"partial data (if any) kept at {part} for resumption")
        return _finish(rec, manifest)

    rec.local_size = part.stat().st_size
    if rec.remote_size is not None and rec.local_size != rec.remote_size:
        rec.status = FAILED_SIZE_MISMATCH
        rec.error = f"downloaded {rec.local_size} bytes but server reported {rec.remote_size}"
        rec.notes.append(f"partial data kept at {part}; re-run to resume")
        return _finish(rec, manifest)
    rec.integrity = check_integrity(part)
    if not rec.integrity["ok"]:
        bad = dest.with_name(f"{dest.name}.corrupt-{datetime.now(timezone.utc):%Y%m%dT%H%M%S}")
        os.replace(part, bad)
        rec.status, rec.error = FAILED_INTEGRITY, f"integrity check failed ({rec.integrity['detail']}); moved to {bad.name}"
        return _finish(rec, manifest)
    rec.sha256 = sha256_file(part)
    os.replace(part, dest)
    make_read_only(dest)
    rec.status = DOWNLOADED
    if rec.remote_size is None:
        rec.notes.append("server did not report a size; completeness verified by integrity check only")
    return _finish(rec, manifest)


def retrieve_text(
    client: GeoClient,
    url: str,
    dest: Path,
    manifest: Manifest | None = None,
    refresh: bool = False,
) -> RetrievalRecord:
    """Retrieve a small text resource (GEO SOFT metadata) into an immutable snapshot file.

    If dest exists it is re-used (offline-safe). With refresh=True the resource is
    re-fetched; an identical response is discarded, while a changed response is saved
    as a new timestamped snapshot and the manifest's current entry points to it. The
    original snapshot is never modified.
    """
    dest = Path(dest)
    rec = RetrievalRecord(name=dest.name, url=url, path=str(dest), status=FAILED)
    current = manifest.current(dest.name) if manifest else None
    # Resolve by file name within dest's directory so the project can be moved.
    current_path = dest
    if current and current.get("path") and (dest.parent / Path(current["path"]).name).exists():
        current_path = dest.parent / Path(current["path"]).name

    if current_path.exists() and (not refresh or client.offline):
        rec.path = str(current_path)
        rec.local_size = current_path.stat().st_size
        rec.sha256 = sha256_file(current_path)
        prior = manifest.last_verified_sha(dest.name) if manifest else None
        if prior and prior != rec.sha256:
            rec.status, rec.error = CONFLICT, "metadata snapshot changed since it was recorded"
        else:
            rec.status = REUSED_VERIFIED_MANIFEST if prior else REUSED_UNVERIFIED
            rec.notes.append("existing metadata snapshot re-used (use --refresh-metadata to re-query GEO)")
        return _finish(rec, manifest)
    if client.offline:
        rec.status = SKIPPED_OFFLINE
        rec.notes.append("offline mode: metadata snapshot not present locally")
        return _finish(rec, manifest)

    rec.network_used = True
    try:
        data = client.get_bytes(url)  # saved verbatim: no decoding/re-encoding of the server's bytes
    except GeoNotFoundError as exc:
        rec.status, rec.error = FAILED_NOT_FOUND, str(exc)
        return _finish(rec, manifest)
    except (GeoAccessError, OfflineModeError) as exc:
        rec.status, rec.error = FAILED, str(exc)
        return _finish(rec, manifest)
    if not data.strip():
        rec.status, rec.error = FAILED, "GEO returned an empty response"
        return _finish(rec, manifest)
    digest = sha256_bytes(data)
    target = dest
    if current_path.exists():
        if sha256_file(current_path) == digest:
            rec.path, rec.sha256, rec.local_size = str(current_path), digest, len(data)
            rec.status = REUSED_VERIFIED
            rec.notes.append("re-queried GEO: response identical to existing snapshot")
            return _finish(rec, manifest)
        target = dest.with_name(f"{dest.stem}.{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}{dest.suffix}")
        rec.notes.append(f"GEO response changed since {current_path.name}; new snapshot saved as {target.name}")
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "xb") as fh:  # 'x' guarantees we never overwrite
        fh.write(data)
    make_read_only(target)
    rec.path, rec.sha256, rec.local_size, rec.remote_size = str(target), digest, len(data), len(data)
    rec.status = DOWNLOADED
    return _finish(rec, manifest)
