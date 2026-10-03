"""OBIS / GBIF occurrence search — DECLARED, not built (M-1b-i ruling)."""
from atlantis_core.fetch.base import DeclaredFetcher


class OBISOccurrence(DeclaredFetcher):
    protocol = "obis_occurrence"
    endpoint = "https://api.obis.org/v3/occurrence"
    needed_by = "an instance with a point_count / survey_log stream from OBIS"


class GBIFOccurrence(DeclaredFetcher):
    protocol = "gbif_occurrence"
    endpoint = "https://api.gbif.org/v1/occurrence/search"
    needed_by = "an instance with a point_count / survey_log stream from GBIF"
