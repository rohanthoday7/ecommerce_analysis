"""
Global Filter Engine for E-Commerce Analytics
Applies multi-dimensional filters and extracts comparison periods for growth KPI benchmarking.
"""

from typing import Optional, List, Tuple, Dict, Any
import pandas as pd
from datetime import timedelta

def apply_filters(
    df: pd.DataFrame,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
    region: Optional[str] = None,
    segment: Optional[str] = None,
    payment_method: Optional[str] = None,
) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
    """
    Filters working dataframe and computes a matching previous-period dataframe
    to accurately calculate period-over-period percentage changes.
    """
    filtered = df.copy()

    # Apply categorical filters safely
    if isinstance(category, str) and category.strip() and category.lower() != "all":
        if category in filtered["_category"].values:
            filtered = filtered[filtered["_category"] == category]
    
    if isinstance(region, str) and region.strip() and region.lower() != "all":
        if region in filtered["_region"].values:
            filtered = filtered[filtered["_region"] == region]

    if isinstance(segment, str) and segment.strip() and segment.lower() != "all":
        if segment in filtered["_segment"].values:
            filtered = filtered[filtered["_segment"] == segment]

    if isinstance(payment_method, str) and payment_method.strip() and payment_method.lower() != "all":
        if payment_method in filtered["_payment_method"].values:
            filtered = filtered[filtered["_payment_method"] == payment_method]

    # Date range filtering
    prev_period_df = None
    if pd.api.types.is_datetime64_any_dtype(filtered["_order_date"]):
        valid_dates = filtered["_order_date"].dropna()
        if len(valid_dates) > 0:
            min_date = valid_dates.min()
            max_date = valid_dates.max()

            s_date = pd.to_datetime(start_date) if isinstance(start_date, str) and start_date.strip() else min_date
            e_date = pd.to_datetime(end_date) if isinstance(end_date, str) and end_date.strip() else max_date

            if pd.notna(s_date) and pd.notna(e_date):
                # Stale filter guard: If date filter is completely outside the dataset's date range,
                # snap to dataset's min/max so we never return empty data due to stale queries!
                if s_date > max_date or e_date < min_date:
                    s_date = min_date
                    e_date = max_date

                mask = (filtered["_order_date"] >= s_date) & (filtered["_order_date"] <= e_date + timedelta(days=1, microseconds=-1))
                current_df = filtered[mask].reset_index(drop=True)
                if len(current_df) == 0:
                    current_df = filtered

                # Calculate equivalent previous period
                duration = e_date - s_date
                prev_e_date = s_date - timedelta(days=1)
                prev_s_date = prev_e_date - duration

                prev_mask = (filtered["_order_date"] >= prev_s_date) & (filtered["_order_date"] <= prev_e_date + timedelta(days=1, microseconds=-1))
                prev_period_df = filtered[prev_mask].reset_index(drop=True)

                return current_df, prev_period_df

    return filtered, None

def get_filter_options(df: pd.DataFrame) -> Dict[str, Any]:
    """Returns available distinct filter values for the UI controls."""
    min_date = None
    max_date = None
    if pd.api.types.is_datetime64_any_dtype(df["_order_date"]):
        valid_dates = df["_order_date"].dropna()
        if len(valid_dates) > 0:
            min_date = valid_dates.min().strftime("%Y-%m-%d")
            max_date = valid_dates.max().strftime("%Y-%m-%d")

    categories = sorted([str(c) for c in df["_category"].dropna().unique().tolist() if str(c)])
    regions = sorted([str(r) for r in df["_region"].dropna().unique().tolist() if str(r)])
    segments = sorted([str(s) for s in df["_segment"].dropna().unique().tolist() if str(s)])
    payment_methods = sorted([str(p) for p in df["_payment_method"].dropna().unique().tolist() if str(p)])

    return {
        "min_date": min_date,
        "max_date": max_date,
        "categories": categories,
        "regions": regions,
        "segments": segments,
        "payment_methods": payment_methods,
        "total_records": len(df)
    }
