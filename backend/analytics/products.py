"""
Product Analytics Engine
Product performance ranking, Pareto 80/20 distribution, category matrix,
profitability analysis, and dynamic multi-product comparison.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

def compute_product_analytics(df: pd.DataFrame, comparison_product_ids: Optional[List[str]] = None) -> Dict[str, Any]:
    if len(df) == 0:
        return {
            "summary": {},
            "top_products_revenue": [],
            "top_products_quantity": [],
            "bottom_products": [],
            "pareto_analysis": {"labels": [], "revenue_pct": [], "cumulative_pct": []},
            "category_matrix": [],
            "profitability": {"has_profit": False, "products": []},
            "comparison": []
        }

    total_revenue = float(df["_sales"].sum())
    total_quantity = float(df["_quantity"].sum())
    total_products = int(df["_product_id"].nunique())
    has_profit = bool("_profit" in df.columns and df["_profit"].notna().any())

    # Product Aggregation
    agg_dict = {
        "revenue": ("_sales", "sum"),
        "quantity": ("_quantity", "sum"),
        "orders": ("_order_id", "nunique"),
        "avg_discount": ("_discount", "mean")
    }
    if has_profit:
        agg_dict["profit"] = ("_profit", "sum")

    prod_df = df.groupby(["_product_id", "_product_name", "_category", "_sub_category"]).agg(**agg_dict).reset_index()
    prod_df["revenue"] = pd.to_numeric(prod_df["revenue"], errors='coerce').fillna(0.0).astype(float)
    prod_df["quantity"] = pd.to_numeric(prod_df["quantity"], errors='coerce').fillna(1.0).astype(float)
    prod_df["avg_price"] = (prod_df["revenue"] / prod_df["quantity"].replace(0, 1)).astype(float).round(2)
    prod_df["rev_share"] = (prod_df["revenue"] / max(total_revenue, 1) * 100).astype(float).round(2)

    if has_profit:
        prod_df["profit"] = pd.to_numeric(prod_df["profit"], errors='coerce').fillna(0.0).astype(float)
        prod_df["profit_margin"] = (prod_df["profit"] / prod_df["revenue"].replace(0, 1) * 100).astype(float).round(2)

    # 1. Best Sellers by Revenue (Top 10)
    top_rev = prod_df.sort_values(by="revenue", ascending=False).head(10)
    top_products_revenue = []
    for _, r in top_rev.iterrows():
        top_products_revenue.append({
            "product_id": str(r["_product_id"]),
            "product_name": str(r["_product_name"]),
            "category": str(r["_category"]),
            "sub_category": str(r["_sub_category"]),
            "revenue": round(float(r["revenue"]), 2),
            "quantity": int(r["quantity"]),
            "orders": int(r["orders"]),
            "rev_share": float(r["rev_share"]),
            "profit": round(float(r["profit"]), 2) if has_profit else None,
            "margin": float(r["profit_margin"]) if has_profit else None
        })

    # 2. Best Sellers by Quantity / Volume (Top 10)
    top_qty = prod_df.sort_values(by="quantity", ascending=False).head(10)
    top_products_quantity = []
    for _, r in top_qty.iterrows():
        top_products_quantity.append({
            "product_id": str(r["_product_id"]),
            "product_name": str(r["_product_name"]),
            "category": str(r["_category"]),
            "quantity": int(r["quantity"]),
            "revenue": round(float(r["revenue"]), 2),
            "orders": int(r["orders"])
        })

    # 3. Bottom Performing Products (Least Revenue)
    bottom_prods = prod_df.sort_values(by="revenue", ascending=True).head(10)
    bottom_products = []
    for _, r in bottom_prods.iterrows():
        bottom_products.append({
            "product_id": str(r["_product_id"]),
            "product_name": str(r["_product_name"]),
            "category": str(r["_category"]),
            "revenue": round(float(r["revenue"]), 2),
            "quantity": int(r["quantity"]),
            "orders": int(r["orders"])
        })

    # 4. Pareto 80/20 Analysis (Cumulative Revenue Distribution)
    sorted_pareto = prod_df.sort_values(by="revenue", ascending=False).reset_index(drop=True)
    sorted_pareto["cum_revenue"] = sorted_pareto["revenue"].cumsum()
    sorted_pareto["cum_pct"] = (sorted_pareto["cum_revenue"] / max(total_revenue, 1) * 100).round(2)
    sorted_pareto["product_rank_pct"] = ((sorted_pareto.index + 1) / len(sorted_pareto) * 100).round(2)

    # Calculate exact 80/20 metric: What % of products generate 80% of revenue?
    eighty_cutoff = sorted_pareto[sorted_pareto["cum_pct"] <= 80.0]
    num_prods_for_80 = max(len(eighty_cutoff), 1)
    pct_prods_for_80 = round((num_prods_for_80 / len(sorted_pareto)) * 100, 1)

    # Subsample 20 points for chart visualization
    sample_step = max(1, len(sorted_pareto) // 25)
    sampled_pareto = sorted_pareto.iloc[::sample_step]
    if len(sorted_pareto) > 0 and sorted_pareto.iloc[-1]["product_rank_pct"] != sampled_pareto.iloc[-1]["product_rank_pct"]:
        sampled_pareto = pd.concat([sampled_pareto, sorted_pareto.tail(1)])

    pareto_analysis = {
        "top_pct_for_80_revenue": pct_prods_for_80,
        "num_prods_for_80_revenue": num_prods_for_80,
        "total_catalog_size": len(sorted_pareto),
        "product_rank_pct": sampled_pareto["product_rank_pct"].tolist(),
        "cumulative_revenue_pct": sampled_pareto["cum_pct"].tolist(),
        "product_names": sampled_pareto["_product_name"].tolist()
    }

    # 5. Category & Sub-Category Matrix
    cat_matrix_df = prod_df.groupby(["_category", "_sub_category"]).agg(
        revenue=("revenue", "sum"),
        quantity=("quantity", "sum"),
        products=("_product_id", "nunique")
    ).reset_index().sort_values(by="revenue", ascending=False)

    category_matrix = []
    for _, r in cat_matrix_df.iterrows():
        category_matrix.append({
            "category": str(r["_category"]),
            "sub_category": str(r["_sub_category"]),
            "revenue": round(float(r["revenue"]), 2),
            "quantity": int(r["quantity"]),
            "products_count": int(r["products"]),
            "share": round(float(r["revenue"]) / max(total_revenue, 1) * 100, 2)
        })

    # 6. Profitability breakdown (if cost/profit data exists)
    profitability = {"has_profit": has_profit, "products": []}
    if has_profit:
        profit_prods = prod_df.sort_values(by="profit", ascending=False)
        for _, r in profit_prods.iterrows():
            profitability["products"].append({
                "product_id": str(r["_product_id"]),
                "product_name": str(r["_product_name"]),
                "category": str(r["_category"]),
                "revenue": round(float(r["revenue"]), 2),
                "profit": round(float(r["profit"]), 2),
                "margin": float(r["profit_margin"]),
                "avg_discount": round(float(r["avg_discount"]) * 100, 1)
            })

    # 7. Multi-Product Comparison Engine
    # If no specific products requested, compare top 3 products by revenue
    compare_ids = comparison_product_ids if comparison_product_ids else top_rev["_product_id"].head(3).tolist()
    comparison = []
    
    for pid in compare_ids:
        match = prod_df[prod_df["_product_id"] == pid]
        if len(match) == 0:
            continue
        prow = match.iloc[0]
        
        # Monthly demand trend for this product
        p_sub = df[df["_product_id"] == pid]
        demand_labels = []
        demand_rev = []
        demand_qty = []
        if pd.api.types.is_datetime64_any_dtype(p_sub["_order_date"]):
            m_trend = p_sub.groupby(p_sub["_order_date"].dt.to_period("M").astype(str)).agg(
                rev=("_sales", "sum"),
                qty=("_quantity", "sum")
            ).reset_index()
            demand_labels = m_trend["_order_date"].tolist()
            demand_rev = m_trend["rev"].round(2).tolist()
            demand_qty = m_trend["qty"].tolist()

        comparison.append({
            "product_id": str(prow["_product_id"]),
            "product_name": str(prow["_product_name"]),
            "category": str(prow["_category"]),
            "sub_category": str(prow["_sub_category"]),
            "revenue": round(float(prow["revenue"]), 2),
            "quantity": int(prow["quantity"]),
            "orders": int(prow["orders"]),
            "avg_price": float(prow["avg_price"]),
            "profit": round(float(prow["profit"]), 2) if has_profit else None,
            "margin": float(prow["profit_margin"]) if has_profit else None,
            "demand_trend": {
                "labels": demand_labels,
                "revenue": demand_rev,
                "quantity": demand_qty
            }
        })

    # All products list for the selector dropdown
    catalog_list = [
        {"id": str(r["_product_id"]), "name": f"{r['_product_name']} ({r['_category']})"}
        for _, r in prod_df.sort_values(by="revenue", ascending=False).iterrows()
    ]

    return {
        "summary": {
            "total_products": total_products,
            "total_revenue": round(total_revenue, 2),
            "total_quantity": int(total_quantity),
            "pareto_summary": f"Top {pct_prods_for_80}% of products generate 80% of revenue."
        },
        "top_products_revenue": top_products_revenue,
        "top_products_quantity": top_products_quantity,
        "bottom_products": bottom_products,
        "pareto_analysis": pareto_analysis,
        "category_matrix": category_matrix,
        "profitability": profitability,
        "comparison": comparison,
        "catalog_list": catalog_list
    }
