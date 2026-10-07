"""Pluggable fetchers. `FETCHERS[name]` is what a stream registry's `fetcher` slot names.

Real (ported from the exemplar, M-1b-i): ArcGIS MapServer · ERDDAP griddap · NWIS daily values. Built at M-2a-i: Coral Reef
Watch (polygon-zone means over CRW's own ERDDAP; P2 FKNMS).
Declared (endpoint named, NotImplementedError): NDBC · OBIS · GBIF.
"""
from atlantis_core.fetch.base import Fetcher, DeclaredFetcher, OfflineError
from atlantis_core.fetch.arcgis import ArcGISMapServer
from atlantis_core.fetch.erddap import ERDDAPGriddap
from atlantis_core.fetch.nwis import NWISDailyValues
from atlantis_core.fetch.ndbc import NDBCStdmet
from atlantis_core.fetch.obis_gbif import OBISOccurrence, GBIFOccurrence
from atlantis_core.fetch.crw import CoralReefWatch

FETCHERS = {c.__name__: c for c in (ArcGISMapServer, ERDDAPGriddap, NWISDailyValues,
                                    NDBCStdmet, OBISOccurrence, GBIFOccurrence, CoralReefWatch)}
BUILT = ("ArcGISMapServer", "ERDDAPGriddap", "NWISDailyValues", "CoralReefWatch")

__all__ = ["Fetcher", "DeclaredFetcher", "OfflineError", "FETCHERS", "BUILT", *FETCHERS]
