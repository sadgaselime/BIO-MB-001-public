"""Download/provenance tests using a fake HTTP session (no network)."""
import gzip
import hashlib
import os

import pytest

from biomarker_project.config import load_config
from biomarker_project.download import (
    CONFLICT, DOWNLOADED, FAILED, FAILED_INTEGRITY, FAILED_NOT_FOUND, FAILED_SIZE_MISMATCH, REUSED_VERIFIED,
    SKIPPED_OFFLINE, SKIPPED_TOO_LARGE, Manifest, download_file, retrieve_text,
)
from biomarker_project.geo_client import GeoAccessError, GeoClient, OfflineModeError, parse_directory_index, series_stub

from conftest import FakeSession

URL = "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE1nnn/GSE1000/suppl/GSE1000_data.txt.gz"
BODY = gzip.compress(("ID_REF\tS1\n" + "".join(f"P{i}\t{(i * 7919) % 10007 / 13:.6f}\n" for i in range(2000))).encode())
assert len(BODY) > 1000


def _client(cfg, session, offline=False):
    return GeoClient(cfg.settings, offline=offline, session=session, sleep=lambda s: None)


def test_series_stub():
    assert series_stub("GSE63060") == "GSE63nnn"
    assert series_stub("GSE140829") == "GSE140nnn"
    assert series_stub("GSE123") == "GSEnnn"


def test_download_records_provenance_and_is_read_only(cfg, tmp_path):
    m = Manifest(tmp_path / "manifest.json")
    rec = download_file(_client(cfg, FakeSession({URL: BODY})), URL, tmp_path / "f.txt.gz", 10**6, m)
    assert rec.status == DOWNLOADED and rec.local_size == rec.remote_size == len(BODY)
    assert rec.sha256 == hashlib.sha256(BODY).hexdigest()
    assert rec.url == URL and rec.started_at and rec.finished_at
    assert rec.integrity["ok"] and rec.integrity["method"] == "gzip_full_decompression"
    assert not os.access(tmp_path / "f.txt.gz", os.W_OK)
    assert Manifest(tmp_path / "manifest.json").current("f.txt.gz")["sha256"] == rec.sha256


def test_existing_complete_file_is_reused_not_redownloaded(cfg, tmp_path):
    session = FakeSession({URL: BODY})
    m = Manifest(tmp_path / "m.json")
    download_file(_client(cfg, session), URL, tmp_path / "f.gz", 10**6, m)
    session.calls.clear()
    rec = download_file(_client(cfg, session), URL, tmp_path / "f.gz", 10**6, m)
    assert rec.status == REUSED_VERIFIED
    assert [c[0] for c in session.calls] == ["HEAD"], "no second GET for a verified file"


def test_existing_file_with_different_size_is_never_overwritten(cfg, tmp_path):
    dest = tmp_path / "f.gz"
    dest.write_bytes(b"something else")
    rec = download_file(_client(cfg, FakeSession({URL: BODY})), URL, dest, 10**6)
    assert rec.status == CONFLICT and dest.read_bytes() == b"something else"


def test_too_large_is_skipped_with_instructions(cfg, tmp_path):
    rec = download_file(_client(cfg, FakeSession({URL: BODY})), URL, tmp_path / "f.gz", 10)
    assert rec.status == SKIPPED_TOO_LARGE and not (tmp_path / "f.gz").exists()
    assert "--max-download-mb" in rec.notes[0] and "curl -C -" in rec.notes[0]


def test_resume_partial_download(cfg, tmp_path):
    dest = tmp_path / "f.gz"
    (tmp_path / "f.gz.part").write_bytes(BODY[:100])
    session = FakeSession({URL: BODY})
    rec = download_file(_client(cfg, session), URL, dest, 10**6)
    assert rec.status == DOWNLOADED and rec.resumed and dest.read_bytes() == BODY
    assert session.calls[-1][2] == {"Range": "bytes=100-"}


def test_truncated_transfer_is_failed_and_kept_for_resume(cfg, tmp_path):
    rec = download_file(_client(cfg, FakeSession({URL: BODY}, truncate={URL: 50})), URL, tmp_path / "f.gz", 10**6)
    assert rec.status == FAILED_SIZE_MISMATCH
    assert not (tmp_path / "f.gz").exists() and (tmp_path / "f.gz.part").stat().st_size == 50


def test_corrupt_gzip_rejected(cfg, tmp_path):
    bad = b"\x1f\x8b\x08\x00" + b"\x00" * 60
    rec = download_file(_client(cfg, FakeSession({URL: bad})), URL, tmp_path / "f.gz", 10**6)
    assert rec.status == FAILED_INTEGRITY and not (tmp_path / "f.gz").exists()


def test_not_found_and_network_failure(cfg, tmp_path):
    assert download_file(_client(cfg, FakeSession({})), URL, tmp_path / "a.gz", 10**6).status == FAILED_NOT_FOUND
    rec = download_file(_client(cfg, FakeSession(raise_all=True)), URL, tmp_path / "b.gz", 10**6)
    assert rec.status == FAILED and "simulated network failure" in rec.error


def test_offline_mode(cfg, tmp_path):
    session = FakeSession({URL: BODY})
    client = _client(cfg, session, offline=True)
    assert download_file(client, URL, tmp_path / "f.gz", 10**6).status == SKIPPED_OFFLINE
    with pytest.raises(OfflineModeError):
        client.get_text(URL)
    assert session.calls == []


def test_retries_are_bounded(cfg, tmp_path):
    session = FakeSession(raise_all=True)
    client = GeoClient(cfg.settings.__class__(**{**cfg.settings.__dict__, "max_retries": 2}), session=session,
                       sleep=lambda s: None)
    with pytest.raises(GeoAccessError, match="after 3 attempt"):
        client.get_text(URL)
    assert len(session.calls) == 3


def test_retrieve_text_snapshots_are_immutable(cfg, tmp_path):
    url = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE1&targ=self&form=text&view=brief"
    m = Manifest(tmp_path / "m.json")
    session = FakeSession({url: b"^SERIES = GSE1\n!Series_title = v1\n"})
    first = retrieve_text(_client(cfg, session), url, tmp_path / "s.txt", m)
    assert first.status == DOWNLOADED
    session.routes[url] = b"^SERIES = GSE1\n!Series_title = v2\n"
    again = retrieve_text(_client(cfg, session), url, tmp_path / "s.txt", m)
    assert again.path.endswith("s.txt") and "v1" in (tmp_path / "s.txt").read_text(), "no silent re-query or overwrite"
    refreshed = retrieve_text(_client(cfg, session), url, tmp_path / "s.txt", m, refresh=True)
    assert refreshed.status == DOWNLOADED and refreshed.path != str(tmp_path / "s.txt")
    assert "v1" in (tmp_path / "s.txt").read_text() and "v2" in open(refreshed.path).read()


def test_parse_directory_index():
    html = ('<a href="/geo/series/">Parent</a>\n<a href="GSE1_RAW.tar">GSE1_RAW.tar</a>  2015-08-06 06:43  6.2M  \n'
            '<a href="filelist.txt">filelist.txt</a>  2015-08-06 06:43  173   \n')
    entries = parse_directory_index(html)
    assert [(e.name, e.size_label) for e in entries] == [("GSE1_RAW.tar", "6.2M"), ("filelist.txt", "173")]


def test_metadata_bytes_saved_verbatim(cfg, tmp_path):
    url = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE2&targ=self&form=text&view=brief"
    body = "^SERIES = GSE2\n!Series_title = Parkinson\u2019s disease\n".encode("utf-8")
    rec = retrieve_text(_client(cfg, FakeSession({url: body})), url, tmp_path / "s.txt")
    assert (tmp_path / "s.txt").read_bytes() == body and rec.sha256 == hashlib.sha256(body).hexdigest()


def test_identity_encoding_requested_for_exact_sizes(cfg):
    client = GeoClient(cfg.settings)  # real requests.Session is created lazily; no request is sent here
    assert client.session.headers["Accept-Encoding"] == "identity"


def test_stalled_transfer_aborts_resumably(cfg, tmp_path, monkeypatch):
    import biomarker_project.download as dl
    clock = iter(range(0, 10_000, 200))  # every chunk appears to take 200 s
    monkeypatch.setattr(dl.time, "monotonic", lambda: next(clock))
    settings = cfg.settings.__class__(**{**cfg.settings.__dict__, "stall_window_seconds": 100, "min_download_kb_per_s": 50})
    big = BODY * 30
    rec = download_file(GeoClient(settings, session=FakeSession({URL: big}), sleep=lambda s: None),
                        URL, tmp_path / "f.gz", 10**8)
    assert rec.status == FAILED and "stalled" in rec.error
    assert (tmp_path / "f.gz.part").exists() and not (tmp_path / "f.gz").exists()
