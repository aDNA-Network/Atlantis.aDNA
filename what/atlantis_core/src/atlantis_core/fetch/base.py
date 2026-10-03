"""The fetcher interface. One class per source protocol; one instance per stream.

Discipline kept from the exemplar: cache first, `offline=True` never touches the network, retries with backoff,
atomic writes (`.tmp` → rename), and a Rule-5 provenance summary after every real download. A fetcher writes into the
*instance's* cache directory — Atlantis itself never fetches (SO-3, ADR-002 §4); its tests run offline.
"""
from __future__ import annotations

import sys, time
from pathlib import Path

from atlantis_core import __version__
from atlantis_core.fetch import provenance


class OfflineError(RuntimeError):
    pass


class Fetcher:
    """Subclasses set `protocol` and `endpoint`, and implement `_download(spec) -> pandas.DataFrame`."""
    protocol: str = "abstract"
    endpoint: str = ""
    date_col: str = "date"
    spec_required: tuple = ()   # keys an `atlantis.yaml → streams[…].fetch` spec must carry (documented per subclass)

    def __init__(self, cache_dir, artifact: str, summary: str, offline: bool = False, retries: int = 5,
                 backoff: float = 2.0, timeout: int = 300, session=None):
        self.cache_dir = Path(cache_dir)
        self.artifact = self.cache_dir / artifact
        self.summary = self.cache_dir / summary
        self.offline, self.retries, self.backoff, self.timeout = offline, retries, backoff, timeout
        self._session = session

    @property
    def pipeline_version(self) -> str:
        return f"atlantis_core {__version__} · {type(self).__name__}"

    # -- network ---------------------------------------------------------------------------------------------------
    def _http(self):
        if self._session is None:
            import requests
            self._session = requests.Session()
        return self._session

    def get(self, url, params=None, empty_ok=None):
        """GET with retry/backoff; returns the Response. `empty_ok(resp) -> bool` short-circuits a server's
        'no data' reply (e.g. ERDDAP's 404 for an empty subset)."""
        if self.offline:
            raise OfflineError(f"offline: would fetch {url}")
        for i in range(self.retries):
            try:
                r = self._http().get(url, params=params, timeout=self.timeout)
                if empty_ok is not None and empty_ok(r):
                    return r
                r.raise_for_status()
                return r
            except Exception as e:  # noqa: BLE001 — network flakiness is the expected case
                wait = self.backoff * 2 ** i
                print(f"  retry {i+1}/{self.retries} after {wait:.0f}s: {e}", file=sys.stderr)
                time.sleep(wait)
        raise RuntimeError(f"gave up: {url}")

    # -- cache ------------------------------------------------------------------------------------------------------
    @staticmethod
    def write_atomic(df, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        df.to_parquet(tmp, index=False); tmp.rename(path)

    def extras(self, df) -> dict:
        return {}

    def fetch(self, spec: dict | None = None):
        """Cached artifact if present (summary written if missing); else download, write atomically, summarise."""
        import pandas as pd
        if self.artifact.exists():
            if not self.summary.exists():
                provenance.summarise(self.artifact, self.summary, self.date_col, self.extras,
                                     pipeline_version=self.pipeline_version)
            return pd.read_parquet(self.artifact)
        df = self._download(spec or {})
        self.write_atomic(df, self.artifact)
        provenance.summarise(self.artifact, self.summary, self.date_col, self.extras,
                             fetched_at=provenance.now_utc(), pipeline_version=self.pipeline_version)
        return df

    def _download(self, spec: dict):
        raise NotImplementedError

    def verify(self) -> bool:
        ok, _, _ = provenance.verify(self.artifact, self.summary)
        return ok


class DeclaredFetcher(Fetcher):
    """A protocol Atlantis names but has not built (operator ruling, M-1b-i: 3 real + 3 declared). It is built when an
    instance needs it — in Atlantis, as a template change (P2 rule), never patched inside the instance."""
    needed_by: str = "the first instance that declares a stream on this protocol"

    def _download(self, spec):
        raise NotImplementedError(f"{type(self).__name__} ({self.protocol}, {self.endpoint}) is declared, not built — "
                                  f"build it in atlantis_core when {self.needed_by} needs it")
