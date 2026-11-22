"""
Executive Dashboard Analytics Engine
Computes core C-suite executive KPIs, trendlines, and high-level distribution metrics.
"""

from typing import Dict, Any, Optional
import pandas as pd
import numpy as np

def compute_executive_dashboard(
    current_df: pd.DataFrame,
    prev_df: Optional[pd.DataFrame] = None,
    full_df: Optional[pd.DataFrame] = None
) -> Dict[str, Any]:
    """
    Computes all executive KPIs, trendlines, and categorical breakdowns.
    """
    if len(current_df) == 0:
        return {
            "kpis": {},
            "revenue_trend": {"labels": [], "revenue": [], "orders": []},
            "category_breakdown": {"labels": [], "values": [], "percentages": []},
            "region_breakdown": {"labels": [], "values": []},
            "top_products": [],
            "customer_trends": {"new_customers": 0, "returning_customers": 0}
        }

    # Core Calculations with strict delivery and recognized revenue filtering
    has_status = "_order_status" in current_df.columns
    if has_status:
        delivered_mask = current_df["_order_status"].isin(["Delivered", "Completed", "Shipped"])
        if not delivered_mask.any():
            delivered_mask = ~current_df["_order_status"].isin(["Cancelled", "Canceled", "Returned", "Refunded"])
    else:
        delivered_mask = pd.Series(True, index=current_df.index)

    delivered_df = current_df[delivered_mask]

    # Total Revenue (Recognized revenue from valid orders, excluding cancelled and returned)
    total_revenue = float(delivered_df["_sales"].sum())

    # Total Orders (All placed orders) and status breakdown
    total_orders = int(current_df["_order_id"].nunique())
    delivered_orders = int(delivered_df["_order_id"].nunique())
    cancelled_orders = int(current_df[current_df["_order_status"].isin(["Cancelled", "Canceled"])]["_order_id"].nunique()) if has_status else 0
    returned_orders = int(current_df[current_df["_order_status"].isin(["Returned", "Refunded"])]["_order_id"].nunique()) if has_status else 0

    # AOV: Delivered Revenue / Delivered Orders
    aov = round(total_revenue / delivered_orders, 2) if delivered_orders > 0 else 0.0

    # Active Customers: unique customers from valid delivered orders
    total_customers = int(delivered_df["_customer_id"].nunique()) if len(delivered_df) > 0 else int(current_df["_customer_id"].nunique())

    # Customer Repeat Purchase Rate from valid delivered orders
    cust_order_counts = delivered_df.groupby("_customer_id")["_order_id"].nunique() if len(delivered_df) > 0 else current_df.groupby("_customer_id")["_order_id"].nunique()
    repeat_customers = int((cust_order_counts > 1).sum())
    repeat_rate = round((repeat_customers / max(total_customers, 1)) * 100, 2)

    # Customer Acquisition: Count new customers from valid orders
    reference_df = full_df if full_df is not None else current_df
    ref_delivered = reference_df[reference_df["_order_status"].isin(["Delivered", "Completed", "Shipped"])] if ("_order_status" in reference_df.columns and reference_df["_order_status"].isin(["Delivered", "Completed", "Shipped"]).any()) else reference_df

    if pd.api.types.is_datetime64_any_dtype(ref_delivered["_order_date"]):
        first_orders = ref_delivered.groupby("_customer_id")["_order_date"].min().reset_index()
        curr_min_date = delivered_df["_order_date"].min() if len(delivered_df) > 0 else current_df["_order_date"].min()
        curr_max_date = delivered_df["_order_date"].max() if len(delivered_df) > 0 else current_df["_order_date"].max()
        new_cust_ids = first_orders[
            (first_orders["_order_date"] >= curr_min_date) & 
            (first_orders["_order_date"] <= curr_max_date)
        ]["_customer_id"].unique()
        new_customers_count = int(len(new_cust_ids))
    else:
        new_customers_count = total_customers - repeat_customers

    returning_customers_count = max(0, total_customers - new_customers_count)

    # Gross Profit & Margin: Profit excluding cancelled and returned orders
    has_profit = bool("_profit" in current_df.columns and current_df["_profit"].notna().any())
    if has_profit:
        gross_profit = float(delivered_df["_profit"].dropna().sum())
        profit_margin = round((gross_profit / max(total_revenue, 1)) * 100, 2)
    else:
        gross_profit = None
        profit_margin = None

    # Calculate Period-over-Period Changes if prev_df is available
    growth_metrics = {}
    if prev_df is not None and len(prev_df) > 0:
        prev_has_status = "_order_status" in prev_df.columns
        prev_delivered = prev_df[prev_df["_order_status"].isin(["Delivered", "Completed", "Shipped"])] if (prev_has_status and prev_df["_order_status"].isin(["Delivered", "Completed", "Shipped"]).any()) else prev_df

        prev_rev = float(prev_delivered["_sales"].sum())
        prev_orders = int(prev_df["_order_id"].nunique())
        prev_del_orders = int(prev_delivered["_order_id"].nunique())
        prev_aov = round(prev_rev / max(prev_del_orders, 1), 2)
        prev_cust = int(prev_delivered["_customer_id"].nunique())

        rev_growth = round(((total_revenue - prev_rev) / max(prev_rev, 1)) * 100, 2)
        orders_growth = round(((total_orders - prev_orders) / max(prev_orders, 1)) * 100, 2)
        aov_growth = round(((aov - prev_aov) / max(prev_aov, 1)) * 100, 2)
        cust_growth = round(((total_customers - prev_cust) / max(prev_cust, 1)) * 100, 2)

        growth_metrics = {
            "revenue_growth": rev_growth,
            "orders_growth": orders_growth,
            "aov_growth": aov_growth,
            "customers_growth": cust_growth
        }
    else:
        growth_metrics = {
            "revenue_growth": 0.0,
            "orders_growth": 0.0,
            "aov_growth": 0.0,
            "customers_growth": 0.0
        }

    # Revenue & Order Trends over time (dynamically choose daily vs monthly)
    revenue_trend = {"labels": [], "revenue": [], "orders": [], "aov": []}
    if pd.api.types.is_datetime64_any_dtype(current_df["_order_date"]):
        date_span_days = (current_df["_order_date"].max() - current_df["_order_date"].min()).days
        if date_span_days <= 60:
            # Group daily
            trend_df = current_df.groupby(current_df["_order_date"].dt.strftime("%Y-%m-%d")).agg(
                revenue=("_sales", "sum"),
                orders=("_order_id", "nunique")
            ).reset_index().rename(columns={"_order_date": "period"})
        else:
            # Group monthly
            trend_df = current_df.groupby(current_df["_order_date"].dt.to_period("M").astype(str)).agg(
                revenue=("_sales", "sum"),
                orders=("_order_id", "nunique")
            ).reset_index().rename(columns={"_order_date": "period"})

        trend_df["aov"] = (trend_df["revenue"] / trend_df["orders"].replace(0, 1)).round(2)
        trend_df["revenue"] = trend_df["revenue"].round(2)

        revenue_trend = {
            "labels": trend_df["period"].tolist(),
            "revenue": trend_df["revenue"].tolist(),
            "orders": trend_df["orders"].tolist(),
            "aov": trend_df["aov"].tolist()
        }

    # Revenue by Category
    cat_df = current_df.groupby("_category").agg(
        revenue=("_sales", "sum"),
        orders=("_order_id", "nunique"),
        quantity=("_quantity", "sum")
    ).reset_index().sort_values(by="revenue", ascending=False)
    
    cat_labels = cat_df["_category"].tolist()
    cat_values = [round(float(v), 2) for v in cat_df["revenue"].tolist()]
    cat_pcts = [round(float(v) / max(total_revenue, 1) * 100, 2) for v in cat_values]

    category_breakdown = {
        "labels": cat_labels,
        "values": cat_values,
        "percentages": cat_pcts,
        "orders": cat_df["orders"].tolist(),
        "quantity": cat_df["quantity"].round(0).tolist()
    }

    # Sales by Region
    reg_df = current_df.groupby("_region").agg(
        revenue=("_sales", "sum"),
        orders=("_order_id", "nunique"),
        customers=("_customer_id", "nunique")
    ).reset_index().sort_values(by="revenue", ascending=False)

    region_breakdown = {
        "labels": reg_df["_region"].tolist(),
        "values": [round(float(v), 2) for v in reg_df["revenue"].tolist()],
        "orders": reg_df["orders"].tolist(),
        "customers": reg_df["customers"].tolist()
    }

    # Top-performing products (Top 8)
    top_prods_df = current_df.groupby(["_product_id", "_product_name", "_category"]).agg(
        revenue=("_sales", "sum"),
        orders=("_order_id", "nunique"),
        quantity=("_quantity", "sum")
    ).reset_index().sort_values(by="revenue", ascending=False).head(8)

    top_products = []
    for _, row in top_prods_df.iterrows():
        top_products.append({
            "product_id": str(row["_product_id"]),
            "product_name": str(row["_product_name"]),
            "category": str(row["_category"]),
            "revenue": round(float(row["revenue"]), 2),
            "orders": int(row["orders"]),
            "quantity": int(row["quantity"])
        })

    # Segment Breakdown
    seg_df = current_df.groupby("_segment").agg(
        revenue=("_sales", "sum"),
        customers=("_customer_id", "nunique")
    ).reset_index()

    segment_breakdown = {
        "labels": seg_df["_segment"].tolist(),
        "revenue": [round(float(v), 2) for v in seg_df["revenue"].tolist()],
        "customers": seg_df["customers"].tolist()
    }

    return {
        "kpis": {
            "total_revenue": round(total_revenue, 2),
            "total_orders": total_orders,
            "delivered_orders": delivered_orders,
            "cancelled_orders": cancelled_orders,
            "returned_orders": returned_orders,
            "average_order_value": aov,
            "total_customers": total_customers,
            "repeat_purchase_rate": repeat_rate,
            "new_customers": new_customers_count,
            "returning_customers": returning_customers_count,
            "gross_profit": round(gross_profit, 2) if gross_profit is not None else None,
            "profit_margin": profit_margin,
            "has_profit_data": has_profit,
            "growth": growth_metrics
        },
        "revenue_trend": revenue_trend,
        "category_breakdown": category_breakdown,
        "region_breakdown": region_breakdown,
        "segment_breakdown": segment_breakdown,
        "top_products": top_products
    }
