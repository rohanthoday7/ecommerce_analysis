"""
Comprehensive Test Suite for Analytics Platform Backend
Validates schema detection, data preprocessing, statistical models,
and all analytical calculations.
"""

import os
import sys
import unittest
import pandas as pd
import numpy as np

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from data_engine import SchemaMapper, DatasetLoader, DataPreprocessor
from analytics import (
    apply_filters,
    get_filter_options,
    compute_executive_dashboard,
    compute_sales_analytics,
    compute_product_analytics,
    compute_customer_analytics,
    compute_regional_analytics,
    generate_business_insights
)

class TestAnalyticsPlatform(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sample_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "sample_ecommerce.csv"))
        cls.raw_df = pd.read_csv(sample_path)
        cls.mapping = SchemaMapper.detect_mapping(cls.raw_df.columns.tolist())
        cls.working_df, cls.clean_report = DataPreprocessor.process(
            df=cls.raw_df,
            mapping=cls.mapping,
            drop_duplicates=True,
            impute_missing=True,
            remove_negative_sales=True
        )

    def test_schema_mapping(self):
        self.assertIsNotNone(self.mapping.get("order_id"))
        self.assertIsNotNone(self.mapping.get("order_date"))
        self.assertIsNotNone(self.mapping.get("sales"))
        self.assertIsNotNone(self.mapping.get("customer_id"))
        self.assertIsNotNone(self.mapping.get("product_id"))
        self.assertIsNotNone(self.mapping.get("category"))
        self.assertIsNotNone(self.mapping.get("profit"))
        
        caps = SchemaMapper.get_capabilities(self.mapping)
        self.assertTrue(caps["modules_supported"]["executive"])
        self.assertTrue(caps["modules_supported"]["sales_analytics"])
        self.assertTrue(caps["modules_supported"]["product_analytics"])
        self.assertTrue(caps["modules_supported"]["customer_analytics"])
        self.assertTrue(caps["modules_supported"]["regional_analytics"])
        self.assertTrue(caps["modules_supported"]["rfm_segmentation"])

    def test_dataset_profiling(self):
        profile = DatasetLoader.profile_dataset(self.raw_df, self.mapping)
        self.assertGreater(profile["total_rows"], 5000)
        self.assertGreaterEqual(profile["health_score"], 80)
        self.assertIn("columns", profile)
        self.assertIn("preview", profile)

    def test_executive_dashboard(self):
        res = compute_executive_dashboard(self.working_df)
        kpis = res["kpis"]
        self.assertGreater(kpis["total_revenue"], 1000000)
        self.assertGreater(kpis["total_orders"], 1000)
        self.assertGreater(kpis["total_customers"], 500)
        self.assertGreater(kpis["average_order_value"], 0)
        self.assertGreater(kpis["repeat_purchase_rate"], 10)
        self.assertIsNotNone(kpis["gross_profit"])
        self.assertGreater(kpis["profit_margin"], 0)
        self.assertGreater(len(res["revenue_trend"]["labels"]), 0)
        self.assertGreater(len(res["category_breakdown"]["labels"]), 0)
        self.assertGreater(len(res["top_products"]), 0)

    def test_sales_analytics(self):
        res = compute_sales_analytics(self.working_df)
        self.assertIn("time_series", res)
        self.assertIn("monthly", res["time_series"])
        self.assertIn("daily", res["time_series"])
        self.assertIn("seasonality", res)
        self.assertEqual(len(res["seasonality"]["monthly"]["labels"]), 12)
        self.assertEqual(len(res["seasonality"]["day_of_week"]["labels"]), 7)
        self.assertIn("order_distribution", res)
        self.assertGreater(len(res["order_distribution"]["bins"]), 0)

    def test_product_analytics(self):
        res = compute_product_analytics(self.working_df)
        self.assertEqual(len(res["top_products_revenue"]), 10)
        self.assertEqual(len(res["top_products_quantity"]), 10)
        self.assertEqual(len(res["bottom_products"]), 10)
        self.assertIn("pareto_analysis", res)
        self.assertGreater(res["pareto_analysis"]["top_pct_for_80_revenue"], 0)
        self.assertGreater(len(res["comparison"]), 0)

    def test_customer_analytics_rfm(self):
        res = compute_customer_analytics(self.working_df)
        self.assertIn("rfm_segments", res)
        self.assertGreater(len(res["rfm_segments"]), 3)
        self.assertGreater(res["summary"]["average_clv_historical"], 0)
        self.assertIn("repeat_distribution", res)
        self.assertEqual(len(res["repeat_distribution"]["labels"]), 5)
        self.assertEqual(len(res["high_value_customers"]), 25)

    def test_regional_analytics(self):
        res = compute_regional_analytics(self.working_df)
        self.assertGreater(len(res["regions"]), 0)
        self.assertGreater(len(res["states"]), 0)
        self.assertGreater(len(res["cities"]), 0)
        self.assertGreater(len(res["map_points"]), 0)

    def test_insights_engine(self):
        insights = generate_business_insights(self.working_df)
        self.assertGreater(len(insights), 3)
        for ins in insights:
            self.assertIn("finding", ins)
            self.assertIn("supporting_data", ins)
            self.assertIn("business_implication", ins)
            self.assertIn("recommended_action", ins)

    def test_filters(self):
        opts = get_filter_options(self.working_df)
        self.assertGreater(len(opts["categories"]), 0)
        self.assertGreater(len(opts["regions"]), 0)
        
        # Test category filter
        test_cat = opts["categories"][0]
        filtered_df, _ = apply_filters(self.working_df, category=test_cat)
        self.assertGreater(len(filtered_df), 0)
        self.assertTrue((filtered_df["_category"] == test_cat).all())

if __name__ == "__main__":
    unittest.main()
