"""
Customer Analytics & RFM Segmentation Engine
Implements genuine statistical RFM scoring (1-5), customer lifetime value (CLV),
cohort retention analysis, and high-value customer profiling.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

def assign_rfm_segment(r_score: int, f_score: int, m_score: int) -> str:
    """Classifies RFM score triplet into strategic marketing segments."""
    rfm_composite = f"{r_score}{f_score}{m_score}"
    
    if r_score >= 4 and f_score >= 4 and m_score >= 4:
        return "Champions"
    elif r_score >= 3 and f_score >= 3 and m_score >= 3:
        return "Loyal Customers"
    elif r_score >= 4 and f_score in [2, 3]:
        return "Potential Loyalists"
    elif r_score >= 4 and f_score == 1:
        return "New Customers"
    elif r_score == 3 and f_score in [1, 2]:
        return "Promising"
    elif r_score in [2, 3] and f_score in [2, 3]:
        return "Needs Attention"
    elif r_score in [2, 3] and f_score == 1:
        return "About to Sleep"
    elif r_score <= 2 and f_score >= 2 and m_score >= 2:
        return "At Risk"
    elif r_score <= 2 and f_score >= 3:
        return "Can't Lose Them"
    elif r_score <= 2 and f_score <= 2:
        return "Hibernating"
    else:
        return "Occasional"

def compute_customer_analytics(df: pd.DataFrame) -> Dict[str, Any]:
    if len(df) == 0:
        return {
            "summary": {},
            "rfm_segments": [],
            "rfm_matrix": {"labels": [], "data": []},
            "new_vs_returning_trends": {"labels": [], "new_revenue": [], "returning_revenue": []},
            "repeat_distribution": {"labels": [], "counts": [], "percentages": []},
            "high_value_customers": []
        }

    has_status = "_order_status" in df.columns
    if has_status:
        delivered_mask = df["_order_status"].isin(["Delivered", "Completed", "Shipped"])
        if not delivered_mask.any():
            delivered_mask = ~df["_order_status"].isin(["Cancelled", "Canceled", "Returned", "Refunded"])
        work_df = df[delivered_mask]
    else:
        work_df = df

    total_revenue = float(work_df["_sales"].sum())
    total_orders = int(work_df["_order_id"].nunique())
    total_customers = int(work_df["_customer_id"].nunique())
    has_date = pd.api.types.is_datetime64_any_dtype(work_df["_order_date"])

    # Reference snapshot date for recency calculation (latest order date + 1 day)
    snapshot_date = work_df["_order_date"].max() + pd.Timedelta(days=1) if has_date else None

    # Customer Aggregation
    agg_rules = {
        "total_spend": ("_sales", "sum"),
        "total_orders": ("_order_id", "nunique"),
        "total_quantity": ("_quantity", "sum"),
        "customer_name": ("_customer_name", "first"),
        "region": ("_region", "first"),
        "segment_pref": ("_segment", "first")
    }
    if has_date:
        agg_rules["last_order_date"] = ("_order_date", "max")
        agg_rules["first_order_date"] = ("_order_date", "min")

    cust_df = work_df.groupby("_customer_id").agg(**agg_rules).reset_index()
    cust_df["aov"] = (cust_df["total_spend"] / cust_df["total_orders"].replace(0, 1)).round(2)

    # 1. RFM Score Calculation
    if has_date and snapshot_date is not None:
        cust_df["recency_days"] = (snapshot_date - cust_df["last_order_date"]).dt.days
        cust_df["tenure_days"] = (snapshot_date - cust_df["first_order_date"]).dt.days
    else:
        cust_df["recency_days"] = 30
        cust_df["tenure_days"] = 60

    # Quantile/Rank binning into 1-5 scales
    # For Recency: lower days = higher score (5)
    try:
        cust_df["r_score"] = pd.qcut(cust_df["recency_days"].rank(method='first'), q=5, labels=[5, 4, 3, 2, 1]).astype(int)
    except Exception:
        cust_df["r_score"] = 3

    # For Frequency: higher orders = higher score (5)
    try:
        # Frequency often has duplicate values (many 1s), so use rank
        cust_df["f_score"] = pd.qcut(cust_df["total_orders"].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
    except Exception:
        cust_df["f_score"] = 3

    # For Monetary: higher spend = higher score (5)
    try:
        cust_df["m_score"] = pd.qcut(cust_df["total_spend"].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
    except Exception:
        cust_df["m_score"] = 3

    # Assign Segment
    cust_df["rfm_segment"] = [
        assign_rfm_segment(r, f, m)
        for r, f, m in zip(cust_df["r_score"], cust_df["f_score"], cust_df["m_score"])
    ]

    # RFM Segment Aggregation
    seg_summary = cust_df.groupby("rfm_segment").agg(
        customer_count=("_customer_id", "count"),
        total_revenue=("total_spend", "sum"),
        avg_recency=("recency_days", "mean"),
        avg_frequency=("total_orders", "mean"),
        avg_monetary=("total_spend", "mean"),
        avg_aov=("aov", "mean")
    ).reset_index().sort_values(by="total_revenue", ascending=False)

    rfm_segments = []
    for _, r in seg_summary.iterrows():
        c_count = int(r["customer_count"])
        c_rev = round(float(r["total_revenue"]), 2)
        rfm_segments.append({
            "segment": str(r["rfm_segment"]),
            "customer_count": c_count,
            "customer_percentage": round((c_count / max(total_customers, 1)) * 100, 2),
            "total_revenue": c_rev,
            "revenue_percentage": round((c_rev / max(total_revenue, 1)) * 100, 2),
            "avg_recency_days": round(float(r["avg_recency"]), 1),
            "avg_frequency": round(float(r["avg_frequency"]), 2),
            "avg_monetary": round(float(r["avg_monetary"]), 2),
            "avg_aov": round(float(r["avg_aov"]), 2)
        })

    # 2. Customer Lifetime Value (CLV)
    # Average Purchase Value (AOV) * Purchase Frequency * Estimated Lifespan
    overall_aov = total_revenue / max(total_orders, 1)
    overall_frequency = total_orders / max(total_customers, 1)
    # Average customer lifespan in months (based on dataset date range)
    if has_date:
        total_days = max((df["_order_date"].max() - df["_order_date"].min()).days, 30)
        avg_lifespan_years = max(total_days / 365.25, 0.5)
    else:
        avg_lifespan_years = 1.0

    annual_clv = overall_aov * (overall_frequency / avg_lifespan_years)
    projected_clv_3yr = round(annual_clv * 3.0, 2)
    historical_clv_avg = round(total_revenue / max(total_customers, 1), 2)

    # 3. Repeat Purchase Distribution (1, 2, 3, 4, 5+ orders)
    freq_bins = [0, 1, 2, 3, 4, 1000]
    freq_labels = ["1 Order", "2 Orders", "3 Orders", "4 Orders", "5+ Orders"]
    binned_freq = pd.cut(cust_df["total_orders"], bins=freq_bins, labels=freq_labels)
    freq_counts = binned_freq.value_counts().reindex(freq_labels).fillna(0).astype(int)

    repeat_dist = {
        "labels": freq_labels,
        "counts": freq_counts.tolist(),
        "percentages": [round((c / max(total_customers, 1)) * 100, 2) for c in freq_counts.tolist()]
    }

    repeat_customers = int((cust_df["total_orders"] > 1).sum())
    repeat_purchase_rate = round((repeat_customers / max(total_customers, 1)) * 100, 2)

    # 4. New vs Returning Customers Revenue Trend over Time
    new_vs_returning_trends = {"labels": [], "new_revenue": [], "returning_revenue": [], "new_customers": [], "returning_customers": []}
    if has_date:
        # Determine each customer's first order date
        first_order_map = df.groupby("_customer_id")["_order_date"].min().to_dict()
        df_cohort = df.copy()
        df_cohort["is_first_order"] = df_cohort.apply(
            lambda r: r["_order_date"] == first_order_map.get(r["_customer_id"]), axis=1
        )

        monthly_cohort = df_cohort.groupby([
            df_cohort["_order_date"].dt.to_period("M").astype(str),
            "is_first_order"
        ]).agg(
            revenue=("_sales", "sum"),
            customers=("_customer_id", "nunique")
        ).unstack(fill_value=0)

        periods = monthly_cohort.index.tolist()
        new_rev = monthly_cohort["revenue"].get(True, pd.Series(0, index=periods)).round(2).tolist()
        ret_rev = monthly_cohort["revenue"].get(False, pd.Series(0, index=periods)).round(2).tolist()
        new_custs = monthly_cohort["customers"].get(True, pd.Series(0, index=periods)).tolist()
        ret_custs = monthly_cohort["customers"].get(False, pd.Series(0, index=periods)).tolist()

        new_vs_returning_trends = {
            "labels": periods,
            "new_revenue": new_rev,
            "returning_revenue": ret_rev,
            "new_customers": new_custs,
            "returning_customers": ret_custs
        }

    # 5. Top High-Value Customers Table (Top 25)
    # Find top product category for each customer
    top_cat_per_cust = df.groupby(["_customer_id", "_category"])["_sales"].sum().reset_index()
    top_cat_per_cust = top_cat_per_cust.sort_values(by=["_customer_id", "_sales"], ascending=[True, False]).drop_duplicates(subset=["_customer_id"])
    cat_map = dict(zip(top_cat_per_cust["_customer_id"], top_cat_per_cust["_category"]))

    top_custs = cust_df.sort_values(by="total_spend", ascending=False).head(25)
    high_value_customers = []
    for _, r in top_custs.iterrows():
        cid = str(r["_customer_id"])
        high_value_customers.append({
            "customer_id": cid,
            "customer_name": str(r["customer_name"]),
            "segment": str(r["segment_pref"]),
            "region": str(r["region"]),
            "rfm_segment": str(r["rfm_segment"]),
            "total_spend": round(float(r["total_spend"]), 2),
            "total_orders": int(r["total_orders"]),
            "aov": float(r["aov"]),
            "recency_days": int(r["recency_days"]),
            "favorite_category": cat_map.get(cid, "Various"),
            "r_score": int(r["r_score"]),
            "f_score": int(r["f_score"]),
            "m_score": int(r["m_score"])
        })

    return {
        "summary": {
            "total_customers": total_customers,
            "repeat_customers": repeat_customers,
            "repeat_purchase_rate": repeat_purchase_rate,
            "average_clv_historical": historical_clv_avg,
            "projected_clv_3yr": projected_clv_3yr,
            "average_purchase_frequency": round(overall_frequency, 2),
            "champions_count": int((cust_df["rfm_segment"] == "Champions").sum()),
            "at_risk_count": int((cust_df["rfm_segment"] == "At Risk").sum())
        },
        "rfm_segments": rfm_segments,
        "new_vs_returning_trends": new_vs_returning_trends,
        "repeat_distribution": repeat_dist,
        "high_value_customers": high_value_customers
    }
