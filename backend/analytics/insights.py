"""
Automated Business Intelligence & Diagnostic Insights Engine
Scans dataset for real mathematical patterns, anomalies, customer dynamics,
and margin trends. Generates actionable C-suite insights backed by empirical data.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np

def generate_business_insights(df: pd.DataFrame) -> List[Dict[str, Any]]:
    if len(df) == 0:
        return []

    insights = []
    total_rev = float(df["_sales"].sum())
    total_orders = int(df["_order_id"].nunique())
    total_custs = int(df["_customer_id"].nunique())
    aov = total_rev / max(total_orders, 1)
    has_date = pd.api.types.is_datetime64_any_dtype(df["_order_date"])
    has_profit = "_profit" in df.columns and df["_profit"].notna().any()

    # -------------------------------------------------------------
    # Insight 1: Pareto Product Catalog Concentration Risk
    # -------------------------------------------------------------
    prod_rev = df.groupby("_product_name")["_sales"].sum().sort_values(ascending=False)
    cum_rev = prod_rev.cumsum()
    eighty_cut = cum_rev[cum_rev <= (total_rev * 0.80)]
    num_prods_for_80 = max(len(eighty_cut), 1)
    total_catalog = len(prod_rev)
    pct_prods_for_80 = round((num_prods_for_80 / max(total_catalog, 1)) * 100, 1)

    top_3_rev = float(prod_rev.head(3).sum())
    top_3_pct = round((top_3_rev / max(total_rev, 1)) * 100, 1)
    top_3_names = ", ".join(list(prod_rev.head(3).index))

    if pct_prods_for_80 < 30:
        insights.append({
            "id": "INS-PARETO-01",
            "category": "Catalog & Inventory",
            "type": "warning" if pct_prods_for_80 < 20 else "info",
            "badge": "High Concentration",
            "title": f"High Catalog Concentration: {pct_prods_for_80}% of Products Drive 80% of Sales",
            "finding": f"Revenue is heavily concentrated in a small subset of the catalog. The top 3 products alone generate ₹{top_3_rev:,.2f} ({top_3_pct}% of total revenue).",
            "supporting_data": f"• Total Catalog Size: {total_catalog} items\n• 80% Revenue Threshold: Achieved by only {num_prods_for_80} items ({pct_prods_for_80}% of catalog)\n• Top 3 Products: {top_3_names} (₹{top_3_rev:,.2f})",
            "business_implication": "Any supply-chain disruption, stock-out, or supplier price hike on these hero SKUs poses an outsized risk to overall top-line revenue.",
            "recommended_action": "Implement priority safety-stock buffers on top SKUs. Develop bundling strategies to cross-sell mid-tier items alongside high-performing hero products."
        })

    # -------------------------------------------------------------
    # Insight 2: Customer Retention & Repeat Purchase Multiplier
    # -------------------------------------------------------------
    cust_orders = df.groupby("_customer_id").agg(
        orders=("_order_id", "nunique"),
        spend=("_sales", "sum")
    )
    repeat_mask = cust_orders["orders"] > 1
    repeat_count = int(repeat_mask.sum())
    repeat_rate = round((repeat_count / max(total_custs, 1)) * 100, 1)
    repeat_rev = float(cust_orders.loc[repeat_mask, "spend"].sum())
    repeat_rev_pct = round((repeat_rev / max(total_rev, 1)) * 100, 1)
    
    repeat_aov = repeat_rev / max(int(df.loc[df["_customer_id"].isin(cust_orders[repeat_mask].index), "_order_id"].nunique()), 1)
    new_mask = ~repeat_mask
    new_rev = float(cust_orders.loc[new_mask, "spend"].sum())
    new_aov = new_rev / max(int(df.loc[df["_customer_id"].isin(cust_orders[new_mask].index), "_order_id"].nunique()), 1)
    aov_premium_pct = round(((repeat_aov - new_aov) / max(new_aov, 1)) * 100, 1)

    insights.append({
        "id": "INS-RETENTION-02",
        "category": "Customer Equity",
        "type": "positive",
        "badge": "Retention Driver",
        "title": f"Repeat Customers Generate {repeat_rev_pct}% of Revenue with {aov_premium_pct}% Higher AOV",
        "finding": f"Although repeat buyers comprise {repeat_rate}% of the total customer base, they generate ₹{repeat_rev:,.2f} ({repeat_rev_pct}% of total sales).",
        "supporting_data": f"• Repeat Customer Base: {repeat_count:,} customers ({repeat_rate}% of total)\n• Repeat Customer Revenue: ₹{repeat_rev:,.2f} ({repeat_rev_pct}% of total sales)\n• Repeat AOV: ₹{repeat_aov:.2f} vs. Single-Purchase AOV: ₹{new_aov:.2f} (+{aov_premium_pct}%)",
        "business_implication": "Customer loyalty represents your highest margin revenue stream. Acquiring new customers without retaining them leaves substantial equity on the table.",
        "recommended_action": "Establish an automated 45-day post-purchase replenishment workflow and a tiered VIP rewards program to shorten the re-order interval."
    })

    # -------------------------------------------------------------
    # Insight 3: Discount Elasticity & Margin Dilution
    # -------------------------------------------------------------
    if has_profit and "_discount" in df.columns:
        disc_zero = df[df["_discount"] == 0]
        disc_promo = df[df["_discount"] > 0]
        
        if len(disc_promo) > 0 and len(disc_zero) > 0:
            margin_zero = (disc_zero["_profit"].sum() / max(disc_zero["_sales"].sum(), 1)) * 100
            margin_promo = (disc_promo["_profit"].sum() / max(disc_promo["_sales"].sum(), 1)) * 100
            margin_gap = round(margin_zero - margin_promo, 1)
            promo_order_pct = round((disc_promo["_order_id"].nunique() / max(total_orders, 1)) * 100, 1)

            if margin_gap > 3.0:
                insights.append({
                    "id": "INS-MARGIN-03",
                    "category": "Pricing & Margins",
                    "type": "warning",
                    "badge": "Margin Dilution",
                    "title": f"Discounted Orders Exhibit {margin_gap}% Lower Profit Margin",
                    "finding": f"Promotions and discounts are applied across {promo_order_pct}% of orders, reducing average profit margin from {margin_zero:.1f}% to {margin_promo:.1f}%.",
                    "supporting_data": f"• Full-Price Profit Margin: {margin_zero:.1f}%\n• Discounted Orders Profit Margin: {margin_promo:.1f}% (compression: -{margin_gap}%)\n• Share of Orders Discounted: {promo_order_pct}%\n• Total Profit Lost to Discounts: ₹{float(df['_sales'].sum() / (1 - df['_discount'].mean()) - total_rev):,.2f}",
                    "business_implication": "Heavy discounting is training customers to delay purchasing until sales events occur, eroding gross operating profits without proportional volume elasticity.",
                    "recommended_action": "Cap blanket promotional discounts at 15%. Transition promotional offers from percentage price cuts to non-price incentives (e.g. free expedited shipping, gift with purchase over ₹1,500)."
                })

    # -------------------------------------------------------------
    # Insight 4: Category Margin vs Revenue Mismatch
    # -------------------------------------------------------------
    if has_profit:
        cat_stats = df.groupby("_category").agg(
            rev=("_sales", "sum"),
            profit=("_profit", "sum")
        )
        cat_stats["margin"] = (cat_stats["profit"] / cat_stats["rev"].replace(0, 1)) * 100
        cat_stats = cat_stats.sort_values(by="rev", ascending=False)
        
        highest_rev_cat = cat_stats.index[0]
        highest_margin_cat = cat_stats["margin"].idxmax()
        
        if highest_rev_cat != highest_margin_cat:
            rev_cat_margin = cat_stats.loc[highest_rev_cat, "margin"]
            best_cat_margin = cat_stats.loc[highest_margin_cat, "margin"]
            insights.append({
                "id": "INS-CAT-04",
                "category": "Product Strategy",
                "type": "info",
                "badge": "Portfolio Optimization",
                "title": f"{highest_margin_cat} Yields Highest Margin ({best_cat_margin:.1f}%) Despite Lower Volume",
                "finding": f"While '{highest_rev_cat}' drives the largest top-line revenue, '{highest_margin_cat}' generates the highest profit margin per dollar sold ({best_cat_margin:.1f}% vs {rev_cat_margin:.1f}%).",
                "supporting_data": f"• '{highest_rev_cat}': ₹{cat_stats.loc[highest_rev_cat, 'rev']:,.2f} revenue, {rev_cat_margin:.1f}% margin\n• '{highest_margin_cat}': ₹{cat_stats.loc[highest_margin_cat, 'rev']:,.2f} revenue, {best_cat_margin:.1f}% margin\n• Margin Advantage: +{best_cat_margin - rev_cat_margin:.1f}% on '{highest_margin_cat}'",
                "business_implication": "Marketing spend and ad budget weighted heavily toward lower-margin categories limits total enterprise EBITDA.",
                "recommended_action": f"Reallocate 15-20% of digital acquisition ad spend toward high-margin '{highest_margin_cat}' campaigns to boost total bottom-line profit."
            })

    # -------------------------------------------------------------
    # Insight 5: Regional Skew & Market Penetration
    # -------------------------------------------------------------
    reg_rev = df.groupby("_region")["_sales"].sum().sort_values(ascending=False)
    top_reg = reg_rev.index[0]
    top_reg_rev = float(reg_rev.iloc[0])
    top_reg_share = round((top_reg_rev / max(total_rev, 1)) * 100, 1)
    bottom_reg = reg_rev.index[-1]
    bottom_reg_rev = float(reg_rev.iloc[-1])
    bottom_reg_share = round((bottom_reg_rev / max(total_rev, 1)) * 100, 1)

    insights.append({
        "id": "INS-GEO-05",
        "category": "Geographic Expansion",
        "type": "info",
        "badge": "Geographic Distribution",
        "title": f"The {top_reg} Region Represents {top_reg_share}% of Total Demand",
        "finding": f"The {top_reg} territory leads regional performance with ₹{top_reg_rev:,.2f} in sales, generating {top_reg_share / max(bottom_reg_share, 0.1):.1f}x the volume of {bottom_reg} (₹{bottom_reg_rev:,.2f}).",
        "supporting_data": f"• {top_reg} Territory: ₹{top_reg_rev:,.2f} ({top_reg_share}% of total sales)\n• {bottom_reg} Territory: ₹{bottom_reg_rev:,.2f} ({bottom_reg_share}% of total sales)\n• Regional Spread Ratio: {top_reg_share / max(bottom_reg_share, 0.1):.1f}x gap between top and bottom territories",
        "business_implication": "Significant untapped commercial headroom exists in under-penetrated markets where brand awareness is lagging.",
        "recommended_action": f"Audit regional digital marketing bids and localized landing pages in the {bottom_reg} region. Evaluate fulfillment logistics in {top_reg} for 2-day delivery guarantees."
    })

    # -------------------------------------------------------------
    # Insight 6: Day of Week Seasonal Spike
    # -------------------------------------------------------------
    if has_date:
        dow_sales = df.groupby("_day_name")["_sales"].sum()
        best_day = dow_sales.idxmax()
        worst_day = dow_sales.idxmin()
        best_day_rev = float(dow_sales[best_day])
        worst_day_rev = float(dow_sales[worst_day])
        day_gap = round(((best_day_rev - worst_day_rev) / max(worst_day_rev, 1)) * 100, 1)

        insights.append({
            "id": "INS-DOW-06",
            "category": "Operational Efficiency",
            "type": "info",
            "badge": "Weekly Seasonality",
            "title": f"{best_day} Generates Peak Weekly Sales (+{day_gap}% vs {worst_day})",
            "finding": f"Customer purchasing patterns exhibit consistent weekly cyclicality, surging to ₹{best_day_rev:,.2f} on {best_day}s before hitting a low of ₹{worst_day_rev:,.2f} on {worst_day}s.",
            "supporting_data": f"• Peak Order Day: {best_day} (₹{best_day_rev:,.2f})\n• Trough Order Day: {worst_day} (₹{worst_day_rev:,.2f})\n• Day-of-Week Variance: +{day_gap}% higher sales velocity on peak day",
            "business_implication": "Staffing customer support and scheduling email marketing campaigns evenly across all 7 days misallocates resources away from peak conversion windows.",
            "recommended_action": f"Schedule core email broadcasts, promo launches, and social retargeting campaigns for {best_day} morning to capture maximum conversion intent."
        })

    return insights
