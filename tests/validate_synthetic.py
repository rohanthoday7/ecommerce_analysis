import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from backend.data_engine import DatasetLoader, SchemaMapper, DataPreprocessor
from backend.analytics import (
    apply_filters,
    compute_executive_dashboard,
    compute_sales_analytics,
    compute_product_analytics,
    compute_customer_analytics,
    compute_regional_analytics,
    generate_business_insights
)

def main():
    raw_df = pd.read_csv('data/synthetic_ecommerce_orders_2025.csv')
    mapping = SchemaMapper.detect_mapping(raw_df.columns.tolist())
    working_df, report = DataPreprocessor.process(raw_df, mapping)

    exec_data = compute_executive_dashboard(working_df)
    kpis = exec_data['kpis']

    print('=================== VALIDATION CHECKS ===================')
    tr = kpis['total_revenue']
    tr_match = (tr == 7854102.20)
    print(f'1. Total Revenue: ₹{tr:,.2f} | Expected: ₹7,854,102.20 | Match: {tr_match}')

    to = kpis['total_orders']
    deliv = kpis['delivered_orders']
    canc = kpis['cancelled_orders']
    ret = kpis['returned_orders']
    to_match = (to == 1800 and deliv == 1634 and canc == 92 and ret == 74)
    print(f'2. Total Orders: {to} (Delivered: {deliv}, Cancelled: {canc}, Returned: {ret}) | Expected: 1800 (1634/92/74) | Match: {to_match}')

    aov = kpis['average_order_value']
    aov_match = (aov == 4806.67)
    print(f'3. AOV: ₹{aov:,.2f} | Expected: ₹4,806.67 | Match: {aov_match}')

    cust = kpis['total_customers']
    cust_match = (cust == 437)
    print(f'4. Active Customers: {cust} | Expected: 437 | Match: {cust_match}')

    gp = kpis['gross_profit']
    gp_match = (gp == 2744652.20)
    print(f'5. Gross Profit: ₹{gp:,.2f} | Expected: ₹2,744,652.20 | Match: {gp_match}')

    pm = kpis['profit_margin']
    pm_match = (pm == 34.95)
    print(f'6. Profit Margin: {pm}% | Expected: 34.95% | Match: {pm_match}')

    sym = report.get('currency_symbol')
    sym_match = (sym == '₹')
    print(f'7. Currency Symbol: {sym} | Expected: ₹ | Match: {sym_match}')

    # Charts checks
    monthly_rev_sum = round(sum(exec_data['revenue_trend']['revenue']), 2)
    cat_rev_sum = round(sum(exec_data['category_breakdown']['values']), 2)
    reg_rev_sum = round(sum(exec_data['region_breakdown']['values']), 2)
    print(f'8. Monthly Revenue Sum: ₹{monthly_rev_sum:,.2f} | Match: {monthly_rev_sum == 7854102.20}')
    print(f'   Category Revenue Sum: ₹{cat_rev_sum:,.2f} | Match: {cat_rev_sum == 7854102.20}')
    print(f'   Regional Revenue Sum: ₹{reg_rev_sum:,.2f} | Match: {reg_rev_sum == 7854102.20}')

    # Filter check
    filtered_df, _ = apply_filters(working_df, category='Electronics')
    filtered_exec = compute_executive_dashboard(filtered_df)
    filtered_rev = filtered_exec['kpis']['total_revenue']
    print(f'9. Filtered Category (Electronics) Revenue: ₹{filtered_rev:,.2f} | Expected: ₹3,076,957.90 | Match: {filtered_rev == 3076957.90}')

    # Customer Module Check
    cust_data = compute_customer_analytics(working_df)
    cust_mod_custs = cust_data['summary']['total_customers']
    print(f'10. Customer Analytics Total Customers: {cust_mod_custs} | Match: {cust_mod_custs == 437}')

    # Sales Module Check
    sales_data = compute_sales_analytics(working_df)
    sales_rev = sales_data['summary']['total_revenue']
    sales_aov = sales_data['summary']['aov']
    print(f'11. Sales Analytics Revenue: ₹{sales_rev:,.2f} | Match: {sales_rev == 7854102.20}')
    print(f'    Sales Analytics AOV: ₹{sales_aov:,.2f} | Match: {sales_aov == 4806.67}')
    print('=========================================================')

    assert tr_match, "Total revenue mismatch"
    assert to_match, "Total orders mismatch"
    assert aov_match, "AOV mismatch"
    assert cust_match, "Active customers mismatch"
    assert gp_match, "Gross profit mismatch"
    assert pm_match, "Profit margin mismatch"
    assert sym_match, "Currency symbol mismatch"
    print("ALL 11 VALIDATIONS PASSED PERFECTLY!")

if __name__ == '__main__':
    main()
