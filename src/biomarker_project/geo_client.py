"""Minimal, conservative client for public NCBI GEO resources.

Access methods used (all public, no credentials):
  * GEO accession display in SOFT text form ("brief" view):
      acc.cgi?acc=<GSE>&targ=self&form=text&view=brief   -> series record
      acc.cgi?acc=<GSE>&targ=gsm&form=text&view=brief    -> all sample (GSM) records
      acc.cgi?acc=<GPL>&targ=self&form=text&view=brief   -> platform record
  * GEO HTTPS file tree (mirror of the GEO FTP site):
      https://ftp.ncbi.nlm.nih.gov/geo/series/<GSEnnn>/<GSE>/{matrix,suppl}/<file>

Every network call goes through GeoClient._request(), which applies a timeout, a
bounded number of retries with back-off for transient failures, and a polite
delay between requests. In offline mode every network call raises
OfflineModeError, so offline checks can never touch the network by accident.
"""
from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass
from typing import Any, Callable

import requests

from .config import Settings

log = logging.getLogger(__name__)

RETRYABLE_STATUS = {408, 429, 500, 502, 503, 504}


class OfflineModeError(RuntimeError):
    """A network operation was requested while running in offline mode."""


class GeoAccessError(RuntimeError):
    """A GEO request failed after the permitted number of attempts."""

    def __init__(self, message: str, url: str, status: int | None = None, attempts: int = 0):
        super().__init__(message)
        self.url = url
        self.status = status
        self.attempts = attempts


class GeoNotFoundError(GeoAccessError):
    """GEO reported that the resource does not exist (HTTP 404)."""


@dataclass
class DirectoryEntry:
    name: str
    modified: str
    size_label: str  # human-readable size from the directory index (approximate)


def series_stub(accession: str) -> str:
    """GEO groups series in directories such as GSE63nnn (GSE63060) or GSEnnn (GSE123)."""
    m = re.fullmatch(r"(GSE|GPL|GSM)(\d+)", accession)
    if not m:
        raise ValueError(f"Not a GEO accession: {accession!r}")
    prefix, digits = m.groups()
    head = digits[:-3] if len(digits) > 3 else ""
    return f"{prefix}{head}nnn"


class GeoClient:
    def __init__(
        self,
        settings: Settings,
        offline: bool = False,
        session: Any | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ):
        self.settings = settings
        self.offline = offline
        self._session = session
        self._sleep = sleep
        self._last_request = 0.0
        self.request_log: list[dict[str, Any]] = []

    # ------------------------------------------------------------------ URLs
    def query_url(self, accession: str, targ: str = "self") -> str:
        return f"{self.settings.geo_query_url}?acc={accession}&targ={targ}&form=text&view=brief"

    def dir_url(self, accession: str, location: str) -> str:
        return f"{self.settings.geo_files_base_url}/{series_stub(accession)}/{accession}/{location}/"

    def file_url(self, accession: str, location: str, name: str) -> str:
        return self.dir_url(accession, location) + name

    # --------------------------------------------------------------- network
    @property
    def session(self):
        if self._session is None:
            self._session = requests.Session()
            self._session.headers["User-Agent"] = self.settings.user_agent
            # Ask for bytes exactly as stored: with HTTP compression, HEAD Content-Length would describe the
            # compressed transfer while requests transparently decodes the body, breaking size verification.
            self._session.headers["Accept-Encoding"] = "identity"
        return self._session

    def _polite_wait(self) -> None:
        wait = self.settings.polite_delay_seconds - (time.monotonic() - self._last_request)
        if wait > 0:
            self._sleep(wait)
        self._last_request = time.monotonic()

    def _request(self, method: str, url: str, **kwargs):
        if self.offline:
            raise OfflineModeError(f"Offline mode: refusing network request {method} {url}")
        attempts = max(1, int(self.settings.max_retries) + 1)
        last_exc: Exception | None = None
        last_status: int | None = None
        for attempt in range(1, attempts + 1):
            self._polite_wait()
            try:
                resp = self.session.request(method, url, timeout=self.settings.http_timeout_seconds, **kwargs)
            except requests.RequestException as exc:  # connection errors, timeouts
                last_exc = exc
                log.warning("%s %s failed (attempt %d/%d): %s", method, url, attempt, attempts, exc)
            else:
                self.request_log.append({"method": method, "url": url, "status": resp.status_code, "attempt": attempt})
                if resp.status_code == 404:
                    resp.close()
                    raise GeoNotFoundError(f"HTTP 404 Not Found: {url}", url, 404, attempt)
                if resp.status_code in RETRYABLE_STATUS:
                    last_status = resp.status_code
                    resp.close()
                    log.warning("%s %s returned HTTP %d (attempt %d/%d)", method, url, resp.status_code, attempt, attempts)
                elif resp.status_code >= 400:
                    resp.close()
                    raise GeoAccessError(f"HTTP {resp.status_code} for {url}", url, resp.status_code, attempt)
                else:
                    return resp
            if attempt < attempts:
                self._sleep(self.settings.retry_backoff_seconds * attempt)
        detail = f"HTTP {last_status}" if last_status else f"{type(last_exc).__name__}: {last_exc}"
        raise GeoAccessError(f"Giving up on {url} after {attempts} attempt(s): {detail}", url, last_status, attempts)

    def get_bytes(self, url: str) -> bytes:
        """Response body exactly as sent by the server (no character decoding)."""
        resp = self._request("GET", url)
        try:
            return resp.content
        finally:
            resp.close()

    def get_text(self, url: str) -> str:
        # GEO text responses often omit a charset; GEO content is UTF-8, so decode explicitly.
        return self.get_bytes(url).decode("utf-8", errors="replace")

    def head(self, url: str) -> dict[str, Any]:
        resp = self._request("HEAD", url, allow_redirects=True)
        try:
            size = resp.headers.get("Content-Length")
            return {
                "status": resp.status_code,
                "size": int(size) if size is not None and str(size).isdigit() else None,
                "last_modified": resp.headers.get("Last-Modified"),
                "accept_ranges": resp.headers.get("Accept-Ranges"),
            }
        finally:
            resp.close()

    def stream(self, url: str, headers: dict[str, str] | None = None):
        """Return an open streaming response; the caller must close it."""
        return self._request("GET", url, stream=True, headers=headers or {})

    def list_directory(self, accession: str, location: str) -> list[DirectoryEntry]:
        html = self.get_text(self.dir_url(accession, location))
        return parse_directory_index(html)


_DIR_LINE = re.compile(r'<a href="([^"?/][^"]*)">[^<]*</a>\s+(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\s+(\S+)')


def parse_directory_index(html: str) -> list[DirectoryEntry]:
    entries = []
    for m in _DIR_LINE.finditer(html):
        name = m.group(1)
        if name.startswith("http") or name.endswith("/"):
            continue
        entries.append(DirectoryEntry(name=name, modified=m.group(2), size_label=m.group(3)))
    return entries


# ---------------------------------------------------------------- SOFT parsing
def parse_soft_brief(text: str) -> list[dict[str, Any]]:
    """Parse GEO SOFT 'brief' text into records.

    Returns a list of {"entity": "SAMPLE", "accession": "GSM...", "fields": {key: [values...]}}.
    Field keys are kept exactly as given (e.g. "Sample_characteristics_ch1"); repeated
    keys accumulate in order. Values are not altered other than removing the line ending.
    Raises ValueError if the text contains no SOFT entity records (e.g. an HTML error page).
    """
    records: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for line in text.splitlines():
        if line.startswith("^"):
            entity, _, acc = line[1:].partition(" = ")
            current = {"entity": entity.strip(), "accession": acc.strip(), "fields": {}}
            records.append(current)
        elif line.startswith("!") and current is not None:
            key, sep, value = line[1:].partition(" = ")
            if not sep:
                key, value = line[1:].rstrip("="), ""
            current["fields"].setdefault(key.strip(), []).append(value)
    if not records:
        snippet = text[:200].replace("\n", " ")
        raise ValueError(f"No GEO SOFT records found (response began: {snippet!r})")
    return records


def parse_characteristics(values: list[str]) -> list[tuple[str, str]]:
    """Split GEO 'key: value' characteristics. Values without ': ' get an empty key."""
    out = []
    for v in values:
        key, sep, val = v.partition(": ")
        out.append((key.strip(), val) if sep else ("", v))
    return out
