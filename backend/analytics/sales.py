"""
Sales Analytics Engine
Deep time-series decomposition, growth dynamics, seasonality, and basket distribution.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

def compute_sales_analytics(df: pd.DataFrame) -> Dict[str, Any]:
    if len(df) == 0:
        return {
            "summary": {},
            "time_series": {"daily": {}, "weekly": {}, "monthly": {}, "yearly": {}},
            "mom_growth": {},
            "seasonality": {"monthly": {}, "day_of_week": {}},
            "order_distribution": {"bins": [], "counts": [], "revenue": []},
            "category_performance": [],
            "payment_performance": []
        }

    has_status = "_order_status" in df.columns
    if has_status:
        delivered_mask = df["_order_status"].isin(["Delivered", "Completed", "Shipped"])
        if not delivered_mask.any():
            delivered_mask = ~df["_order_status"].isin(["Cancelled", "Canceled", "Returned", "Refunded"])
    else:
        delivered_mask = pd.Series(True, index=df.index)

    delivered_df = df[delivered_mask]
    total_revenue = float(delivered_df["_sales"].sum())
    total_orders = int(df["_order_id"].nunique())
    delivered_orders = int(delivered_df["_order_id"].nunique())
    cancelled_orders = int(df[df["_order_status"].isin(["Cancelled", "Canceled"])]["_order_id"].nunique()) if has_status else 0
    returned_orders = int(df[df["_order_status"].isin(["Returned", "Refunded"])]["_order_id"].nunique()) if has_status else 0
    aov = round(total_revenue / delivered_orders, 2) if delivered_orders > 0 else 0.0

    # 1. Multi-grain Time Series (Daily, Weekly, Monthly, Yearly)
    time_series = {"daily": {}, "weekly": {}, "monthly": {}, "yearly": {}}
    
    if pd.api.types.is_datetime64_any_dtype(df["_order_date"]):
        # Daily
        daily_df = df.groupby(df["_order_date"].dt.strftime("%Y-%m-%d")).agg(
            revenue=("_sales", "sum"),
            orders=("_order_id", "nunique"),
            quantity=("_quantity", "sum")
        ).reset_index().rename(columns={"_order_date": "period"}).tail(90) # Last 90 days for daily
        daily_df["aov"] = (daily_df["revenue"] / daily_df["orders"].replace(0, 1)).round(2)

        time_series["daily"] = {
            "labels": daily_df["period"].tolist(),
            "revenue": daily_df["revenue"].round(2).tolist(),
            "orders": daily_df["orders"].tolist(),
            "aov": daily_df["aov"].tolist()
        }

        # Weekly
        weekly_df = df.groupby(df["_order_date"].dt.to_period("W").astype(str)).agg(
            revenue=("_sales", "sum"),
            orders=("_order_id", "nunique"),
            quantity=("_quantity", "sum")
        ).reset_index().rename(columns={"_order_date": "period"}).tail(52)
        weekly_df["aov"] = (weekly_df["revenue"] / weekly_df["orders"].replace(0, 1)).round(2)

        time_series["weekly"] = {
            "labels": weekly_df["period"].tolist(),
            "revenue": weekly_df["revenue"].round(2).tolist(),
            "orders": weekly_df["orders"].tolist(),
            "aov": weekly_df["aov"].tolist()
        }

        # Monthly
        monthly_df = df.groupby(df["_order_date"].dt.to_period("M").astype(str)).agg(
            revenue=("_sales", "sum"),
            orders=("_order_id", "nunique"),
            quantity=("_quantity", "sum")
        ).reset_index().rename(columns={"_order_date": "period"})
        monthly_df["aov"] = (monthly_df["revenue"] / monthly_df["orders"].replace(0, 1)).round(2)

        time_series["monthly"] = {
            "labels": monthly_df["period"].tolist(),
            "revenue": monthly_df["revenue"].round(2).tolist(),
            "orders": monthly_df["orders"].tolist(),
            "aov": monthly_df["aov"].tolist()
        }

        # Yearly
        yearly_df = df.groupby(df["_order_date"].dt.year.astype(str)).agg(
            revenue=("_sales", "sum"),
            orders=("_order_id", "nunique"),
            quantity=("_quantity", "sum")
        ).reset_index().rename(columns={"_order_date": "period"})
        yearly_df["aov"] = (yearly_df["revenue"] / yearly_df["orders"].replace(0, 1)).round(2)

        time_series["yearly"] = {
            "labels": yearly_df["period"].tolist(),
            "revenue": yearly_df["revenue"].round(2).tolist(),
            "orders": yearly_df["orders"].tolist(),
            "aov": yearly_df["aov"].tolist()
        }

        # 2. Month-over-Month (MoM) Growth Analysis
        monthly_growth = []
        for i in range(len(monthly_df)):
            curr_rev = monthly_df.iloc[i]["revenue"]
            if i == 0:
                growth_rate = 0.0
            else:
                prev_rev = monthly_df.iloc[i - 1]["revenue"]
                growth_rate = round(((curr_rev - prev_rev) / max(prev_rev, 1)) * 100, 2)
            monthly_growth.append(growth_rate)

        mom_growth = {
            "labels": monthly_df["period"].tolist(),
            "growth_rates": monthly_growth,
            "revenue": monthly_df["revenue"].round(2).tolist()
        }

        # 3. Seasonality Patterns
        # Month of Year (Jan - Dec)
        month_order = ["January", "February", "March", "April", "May", "June", 
                       "July", "August", "September", "October", "November", "December"]
        month_stats = df.groupby("_month_name").agg(
            revenue=("_sales", "sum"),
            orders=("_order_id", "nunique")
        ).reindex(month_order).fillna(0).reset_index()

        # Day of Week (Mon - Sun)
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        dow_stats = df.groupby("_day_name").agg(
            revenue=("_sales", "sum"),
            orders=("_order_id", "nunique")
        ).reindex(day_order).fillna(0).reset_index()

        seasonality = {
            "monthly": {
                "labels": month_stats["_month_name"].tolist(),
                "revenue": month_stats["revenue"].round(2).tolist(),
                "orders": month_stats["orders"].tolist()
            },
            "day_of_week": {
                "labels": dow_stats["_day_name"].tolist(),
                "revenue": dow_stats["revenue"].round(2).tolist(),
                "orders": dow_stats["orders"].tolist()
            }
        }
    else:
        mom_growth = {}
        seasonality = {"monthly": {}, "day_of_week": {}}

    # 4. Order Basket Value Distribution (Histogram bins)
    order_totals = df.groupby("_order_id")["_sales"].sum()
    bins = [0, 50, 100, 250, 500, 1000, 2500, 100000]
    bin_labels = ["$0 - $50", "$50 - $100", "$100 - $250", "$250 - $500", "$500 - $1,000", "$1,000 - $2,500", "$2,500+"]
    
    binned = pd.cut(order_totals, bins=bins, labels=bin_labels, include_lowest=True)
    bin_counts = binned.value_counts().reindex(bin_labels).fillna(0).astype(int)
    
    # Calculate revenue per bin
    bin_rev = []
    for label in bin_labels:
        matching_orders = order_totals[binned == label]
        bin_rev.append(round(float(matching_orders.sum()), 2))

    order_distribution = {
        "bins": bin_labels,
        "counts": bin_counts.tolist(),
        "percentages": [round((c / max(total_orders, 1)) * 100, 2) for c in bin_counts.tolist()],
        "revenue": bin_rev
    }

    # 5. Category Performance table
    cat_summary = df.groupby("_category").agg(
        revenue=("_sales", "sum"),
        orders=("_order_id", "nunique"),
        quantity=("_quantity", "sum")
    ).reset_index().sort_values(by="revenue", ascending=False)
    
    cat_summary["share"] = (cat_summary["revenue"] / max(total_revenue, 1) * 100).round(2)
    cat_summary["aov"] = (cat_summary["revenue"] / cat_summary["orders"].replace(0, 1)).round(2)

    category_performance = []
    for _, r in cat_summary.iterrows():
        category_performance.append({
            "category": str(r["_category"]),
            "revenue": round(float(r["revenue"]), 2),
            "orders": int(r["orders"]),
            "quantity": int(r["quantity"]),
            "share": float(r["share"]),
            "aov": float(r["aov"])
        })

    # 6. Payment Method Performance
    pay_summary = df.groupby("_payment_method").agg(
        revenue=("_sales", "sum"),
        orders=("_order_id", "nunique")
    ).reset_index().sort_values(by="revenue", ascending=False)

    payment_performance = []
    for _, r in pay_summary.iterrows():
        payment_performance.append({
            "method": str(r["_payment_method"]),
            "revenue": round(float(r["revenue"]), 2),
            "orders": int(r["orders"]),
            "share": round(float(r["revenue"]) / max(total_revenue, 1) * 100, 2)
        })

    return {
        "summary": {
            "total_revenue": round(total_revenue, 2),
            "total_orders": total_orders,
            "delivered_orders": delivered_orders,
            "cancelled_orders": cancelled_orders,
            "returned_orders": returned_orders,
            "aov": aov,
            "avg_units_per_order": round(float(delivered_df["_quantity"].sum()) / max(delivered_orders, 1), 2)
        },
        "time_series": time_series,
        "mom_growth": mom_growth,
        "seasonality": seasonality,
        "order_distribution": order_distribution,
        "category_performance": category_performance,
        "payment_performance": payment_performance
    }
