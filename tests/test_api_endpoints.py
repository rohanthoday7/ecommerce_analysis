"""
API Service & Endpoint Function Tests
Validates all analytical routes, dataset preview, profiling, and exports.
"""

import os
import sys
import unittest
import pandas as pd

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
import app

class TestApiDirectEndpoints(unittest.TestCase):
    def test_01_dataset_status(self):
        status = app.get_dataset_status()
        self.assertTrue(status["loaded"])
        self.assertGreaterEqual(status["total_rows"], 1800)
        self.assertTrue(status["has_profit_data"])
        self.assertIn("capabilities", status)
        self.assertIn("filter_options", status)

    def test_02_dataset_profile(self):
        profile = app.get_dataset_profile()
        self.assertGreaterEqual(profile["health_score"], 80)
        self.assertIn("columns", profile)
        self.assertIn("preview", profile)

    def test_03_dataset_preview(self):
        preview = app.preview_dataset(page=1, page_size=15, search=None)
        self.assertEqual(len(preview["rows"]), 15)
        self.assertGreaterEqual(preview["total"], 1800)
        self.assertGreater(preview["total_pages"], 1)

    def test_04_preview_search(self):
        # Search for a term that exists in the dataset (e.g. 'Delivered' or 'Electronics')
        preview = app.preview_dataset(page=1, page_size=15, search="Delivered")
        self.assertGreater(preview["total"], 0)
        for r in preview["rows"]:
            row_str = " ".join(str(v) for v in r.values())
            self.assertIn("delivered", row_str.lower())

    def test_05_executive_analytics(self):
        res = app.get_executive_analytics()
        kpis = res["kpis"]
        self.assertGreater(kpis["total_revenue"], 1000000)
        self.assertGreater(kpis["total_orders"], 1000)
        self.assertGreater(kpis["average_order_value"], 0)
        self.assertIn("revenue_trend", res)
        self.assertIn("category_breakdown", res)
        self.assertIn("region_breakdown", res)
        self.assertIn("top_products", res)

    def test_06_sales_analytics(self):
        res = app.get_sales_analytics()
        self.assertIn("time_series", res)
        self.assertIn("daily", res["time_series"])
        self.assertIn("monthly", res["time_series"])
        self.assertIn("seasonality", res)
        self.assertIn("order_distribution", res)

    def test_07_product_analytics(self):
        res = app.get_product_analytics()
        self.assertEqual(len(res["top_products_revenue"]), 10)
        self.assertEqual(len(res["bottom_products"]), 10)
        self.assertIn("pareto_analysis", res)
        self.assertIn("comparison", res)

    def test_08_customer_analytics(self):
        res = app.get_customer_analytics()
        self.assertIn("rfm_segments", res)
        self.assertIn("new_vs_returning_trends", res)
        self.assertGreater(len(res["high_value_customers"]), 0)

    def test_09_regional_analytics(self):
        res = app.get_regional_analytics()
        self.assertGreater(len(res["regions"]), 0)
        self.assertGreater(len(res["states"]), 0)
        self.assertGreater(len(res["cities"]), 0)
        self.assertGreater(len(res["map_points"]), 0)

    def test_10_insights(self):
        insights = app.get_insights()
        self.assertGreater(len(insights), 2)
        for ins in insights:
            self.assertIn("title", ins)
            self.assertIn("finding", ins)
            self.assertIn("supporting_data", ins)
            self.assertIn("business_implication", ins)
            self.assertIn("recommended_action", ins)

    def test_11_export_csv(self):
        resp = app.export_dataset(format="csv")
        self.assertEqual(resp.media_type, "text/csv")
        self.assertIn("attachment", resp.headers["content-disposition"])

    def test_12_remap_and_reload(self):
        # Test remap with current mapping
        curr_map = app.state.mapping
        remap_res = app.remap_dataset(curr_map)
        self.assertTrue(remap_res["success"])
        self.assertTrue(remap_res["status"]["loaded"])

if __name__ == "__main__":
    unittest.main()
