"""Shared fixtures. Every test runs offline: network access goes through FakeSession."""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import requests

from biomarker_project.config import load_config

FIXTURES = Path(__file__).parent / "fixtures"
ACC = "GSE1000001"


class FakeResponse:
    def __init__(self, status: int, body: bytes = b"", headers: dict | None = None):
        self.status_code = status
        self._body = body
        self.headers = headers or {}
        self.encoding = "utf-8"

    @property
    def content(self) -> bytes:
        return self._body

    @property
    def text(self) -> str:
        return self._body.decode(self.encoding)

    def iter_content(self, chunk_size: int = 1024):
        for i in range(0, len(self._body), chunk_size):
            yield self._body[i:i + chunk_size]

    def close(self) -> None:
        pass


class FakeSession:
    """Serves byte bodies by URL; unknown URLs return 404. No real network is ever used."""

    def __init__(self, routes: dict[str, bytes] | None = None, raise_all: bool = False, support_range: bool = True,
                 truncate: dict[str, int] | None = None):
        self.routes = routes or {}
        self.raise_all = raise_all
        self.support_range = support_range
        self.truncate = truncate or {}
        self.calls: list[tuple[str, str, dict]] = []
        self.headers: dict[str, str] = {}

    def request(self, method, url, timeout=None, stream=False, headers=None, allow_redirects=True):
        self.calls.append((method, url, dict(headers or {})))
        if self.raise_all:
            raise requests.ConnectionError("simulated network failure")
        if url not in self.routes:
            return FakeResponse(404)
        body = self.routes[url]
        if method == "HEAD":
            return FakeResponse(200, b"", {"Content-Length": str(len(body))})
        rng = (headers or {}).get("Range")
        if rng and self.support_range:
            start = int(rng.split("=")[1].split("-")[0])
            return FakeResponse(206, body[start:])
        if url in self.truncate:
            return FakeResponse(200, body[: self.truncate[url]])
        return FakeResponse(200, body)


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES


@pytest.fixture
def config_path() -> Path:
    return FIXTURES / "valid_config.yaml"


@pytest.fixture
def cfg(config_path):
    return load_config(config_path)


@pytest.fixture
def mini_project(tmp_path: Path) -> Path:
    """A throw-away project tree with locally cached metadata and raw files for GSE1000001."""
    root = tmp_path / "proj"
    (root / "config").mkdir(parents=True)
    shutil.copy(FIXTURES / "valid_config.yaml", root / "config" / "datasets.yaml")
    meta = root / "data" / "metadata" / ACC
    raw = root / "data" / "raw" / ACC
    meta.mkdir(parents=True)
    raw.mkdir(parents=True)
    shutil.copy(FIXTURES / "series_brief.soft.txt", meta / f"{ACC}_series_brief.soft.txt")
    shutil.copy(FIXTURES / "samples_brief.soft.txt", meta / f"{ACC}_samples_brief.soft.txt")
    shutil.copy(FIXTURES / "platform_brief.soft.txt", meta / "GPL9999999_platform_brief.soft.txt")
    shutil.copy(FIXTURES / "series_matrix.txt.gz", raw / f"{ACC}_series_matrix.txt.gz")
    shutil.copy(FIXTURES / "normalized.txt.gz", raw / f"{ACC}_normalized.txt.gz")
    return root
