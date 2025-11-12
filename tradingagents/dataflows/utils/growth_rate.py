"""Utilities for extracting growth rate signals across data sources.

This module centralises the logic for discovering a usable growth rate value
from the heterogeneous payloads returned by MongoDB caches, AKShare responses
and Tushare APIs.  The previous implementation duplicated the candidate key
lists and normalisation rules in several places which quickly drifted as the
project evolved.  Keeping the extraction logic in one place ensures new data
fields introduced by the providers are immediately available everywhere that
computes PEG ratios.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, Optional

# Growth rate signals appear under many different field names depending on the
# upstream provider.  The list below consolidates the known aliases gathered
# from MongoDB snapshots, AKShare/Tushare responses and recent provider
# updates.  Please keep the list sorted roughly by priority (most accurate
# signals first) so that higher-quality metrics are selected before broader
# fallbacks.
GROWTH_RATE_CANDIDATE_KEYS: Iterable[str] = (
    "growth_rate",
    "growth",
    "growth_pct",
    "netprofit_yoy",
    "net_profit_yoy",
    "netprofit_growth",
    "net_profit_growth",
    "netprofit_growth_rate",
    "net_profit_growth_rate",
    "netprofit_yoy_ttm",
    "net_profit_yoy_ttm",
    "n_income_attr_p_yoy",
    "n_income_yoy",
    "np_yoy",
    "profit_yoy",
    "epsg",
    "eps_growth",
    "eps_yoy",
    "eps_basic_yoy",
    "basic_eps_yoy",
    "eps_basic_growth",
    "profit_to_gr_yoy",
    "净利润同比增长率",
    "净利润增长率",
    "净利润同比增长",
    "归母净利润同比增长率",
    "基本每股收益同比增长率",
    "基本每股收益增长率",
    "每股收益同比增长率",
)


def _clean_growth_value(value: Any) -> Optional[float]:
    """Convert a raw growth value into a positive floating point number.

    The upstream data sources return growth rates either as percentages such as
    ``"15.3%"`` or as decimal ratios like ``0.153``.  This helper normalises
    both representations into the canonical percentage form used by the PEG
    calculation.  ``None`` is returned when the value cannot be interpreted as
    a positive number.
    """

    if value is None:
        return None

    try:
        if isinstance(value, str):
            cleaned = value.strip()
            if not cleaned or cleaned.lower() in {"nan", "--", "null"}:
                return None
            cleaned = (
                cleaned.replace("%", "")
                .replace("％", "")
                .replace(",", "")
            )
            numeric = float(cleaned)
        else:
            numeric = float(value)
    except (TypeError, ValueError):
        return None

    if numeric <= 0:
        return None

    # If the number is expressed as a unit ratio (e.g. 0.153 for 15.3%)
    # normalise it back to percentage form so that PEG = PE / growth_rate
    # remains consistent with financial conventions.
    if 0 < numeric < 1:
        numeric *= 100

    return numeric


def extract_growth_rate(*data_sources: Optional[Dict[str, Any]]) -> Optional[float]:
    """Return the first positive growth rate discovered in the provided data.

    Args:
        data_sources: A series of dictionaries originating from various
            providers.  The function will scan each source in order and return
            the first positive value found under the known growth aliases.

    Returns:
        A positive floating-point percentage if one is available, otherwise
        ``None``.
    """

    for source in data_sources:
        if not source:
            continue

        for key in GROWTH_RATE_CANDIDATE_KEYS:
            if key in source:
                growth = _clean_growth_value(source.get(key))
                if growth is not None:
                    return growth

    return None


__all__ = [
    "GROWTH_RATE_CANDIDATE_KEYS",
    "extract_growth_rate",
]

