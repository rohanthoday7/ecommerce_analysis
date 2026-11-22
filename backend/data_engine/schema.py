"""
Adaptive Schema Detection and Mapping for E-Commerce Data
Maps heterogeneous incoming columns to canonical internal analytical features.
"""

from typing import Dict, List, Optional, Any
import re

CANONICAL_FIELDS = {
    "order_id": {
        "label": "Order ID",
        "required": True,
        "aliases": [
            "order id", "order_id", "orderid", "order number", "order_no", "invoice no",
            "invoiceno", "invoice_number", "transaction id", "transaction_id", "trans_id",
            "order_number", "order#", "invoice#", "receipt_no", "order"
        ]
    },
    "order_date": {
        "label": "Order Date",
        "required": True,
        "aliases": [
            "order date", "order_date", "orderdate", "invoice date", "invoicedate",
            "transaction date", "purchase date", "created at", "timestamp", "order_time", "date"
        ]
    },
    "sales": {
        "label": "Sales / Revenue",
        "required": True,
        "aliases": [
            "recognized_revenue", "recognized revenue", "recognized_sales", "recognized sales",
            "discounted_price", "discounted price", "discount_price", "discount price",
            "selling_price", "selling price", "final_price", "final price", "sale_price",
            "actual_price", "actual price", "retail_price", "price", "mrp", "sales", "revenue",
            "net_sales", "net sales", "gross_sales", "gross sales",
            "amount", "total", "total amount", "total_amount", "line total",
            "grand total", "price total", "order total", "item total", "subtotal",
            "order_amount", "transaction_amount", "balance", "paid", "charge"
        ]
    },
    "customer_id": {
        "label": "Customer ID",
        "required": False,
        "aliases": [
            "customer id", "customer_id", "customerid", "client id", "user id", "userid",
            "user_id", "reviewer id", "reviewer_id", "shopper id", "account id"
        ]
    },
    "customer_name": {
        "label": "Customer Name",
        "required": False,
        "aliases": [
            "customer name", "customer_name", "customer", "client name", "buyer name",
            "user name", "username", "user_name", "reviewer_name", "reviewer name", "full name"
        ]
    },
    "product_id": {
        "label": "Product ID",
        "required": False,
        "aliases": ["product id", "product_id", "productid", "item id", "item_id", "asin", "sku", "article no", "part number"]
    },
    "product_name": {
        "label": "Product Name",
        "required": False,
        "aliases": [
            "product name", "product_name", "product", "product_title", "title",
            "about_product", "item name", "item_name", "description", "item description"
        ]
    },
    "category": {
        "label": "Product Category",
        "required": False,
        "aliases": ["category", "product category", "product_category", "main_category", "item category", "department", "genre", "product group"]
    },
    "sub_category": {
        "label": "Sub-Category",
        "required": False,
        "aliases": ["sub-category", "sub category", "sub_category", "subcategory", "sub department", "class"]
    },
    "quantity": {
        "label": "Quantity",
        "required": False,
        "aliases": ["quantity", "qty", "units", "units sold", "volume", "count", "items count", "order_quantity", "order quantity"]
    },
    "unit_price": {
        "label": "Unit Price",
        "required": False,
        "aliases": ["actual_price", "actual price", "original_price", "list_price", "mrp", "unit price", "unit_price", "unitprice", "price", "rate", "price each"]
    },
    "discount": {
        "label": "Discount",
        "required": False,
        "aliases": ["discount_percentage", "discount percentage", "discount", "discount rate", "discount amount", "disc", "promo", "rebate", "markdown"]
    },
    "profit": {
        "label": "Profit",
        "required": False,
        "aliases": ["profit", "net profit", "gross profit", "margin", "earnings", "net income", "operating profit"]
    },
    "unit_cost": {
        "label": "Unit Cost",
        "required": False,
        "aliases": ["unit cost", "unit_cost", "cost", "cogs", "cost of goods", "cost price"]
    },
    "region": {
        "label": "Region",
        "required": False,
        "aliases": ["region", "territory", "zone", "sales region", "area", "market"]
    },
    "state": {
        "label": "State / Province",
        "required": False,
        "aliases": ["state", "province", "region state"]
    },
    "city": {
        "label": "City",
        "required": False,
        "aliases": ["city", "town", "municipality"]
    },
    "country": {
        "label": "Country",
        "required": False,
        "aliases": ["country", "nation"]
    },
    "payment_method": {
        "label": "Payment Method",
        "required": False,
        "aliases": ["payment method", "payment_method", "payment type", "payment", "tender type"]
    },
    "segment": {
        "label": "Customer Segment",
        "required": False,
        "aliases": ["segment", "customer segment", "customer_segment", "account type", "tier", "cohort"]
    },
    "order_status": {
        "label": "Order Status",
        "required": False,
        "aliases": [
            "order_status", "order status", "status", "delivery_status", "delivery status",
            "order_state", "order state", "shipping_status"
        ]
    }
}

class SchemaMapper:
    @staticmethod
    def normalize_str(s: str) -> str:
        s = str(s).strip().lower()
        s = re.sub(r'[\s_\-\.\/]+', ' ', s)
        return s.strip()

    @classmethod
    def detect_mapping(cls, raw_columns: List[str]) -> Dict[str, Optional[str]]:
        """
        Given a list of column names in the uploaded dataset,
        heuristically match them to the canonical e-commerce schema fields.
        Respects alias prioritization so more specific fields match first.
        """
        mapping: Dict[str, Optional[str]] = {k: None for k in CANONICAL_FIELDS.keys()}
        normalized_cols = {col: cls.normalize_str(col) for col in raw_columns}
        
        assigned_cols = set()

        # Step 1: Exact alias matching in prioritized alias order
        for canonical, info in CANONICAL_FIELDS.items():
            for alias in info["aliases"]:
                for raw_col, norm in normalized_cols.items():
                    if raw_col in assigned_cols:
                        continue
                    # Negative filter for date: prevent accounting to-date columns
                    if canonical == "order_date" and any(neg in norm for neg in ["to date", "quarter", "history", "balance", "unitized"]):
                        continue
                    if norm == alias:
                        mapping[canonical] = raw_col
                        assigned_cols.add(raw_col)
                        break
                if mapping[canonical] is not None:
                    break

        # Step 2: Substring matching for unassigned fields in prioritized alias order
        for canonical, info in CANONICAL_FIELDS.items():
            if mapping[canonical] is not None:
                continue
            for alias in info["aliases"]:
                for raw_col, norm in normalized_cols.items():
                    if raw_col in assigned_cols:
                        continue
                    if canonical == "order_date" and any(neg in norm for neg in ["to date", "quarter", "history", "balance", "unitized"]):
                        continue
                    # Exact word match or boundary
                    if re.search(r'\b' + re.escape(alias) + r'\b', norm):
                        mapping[canonical] = raw_col
                        assigned_cols.add(raw_col)
                        break
                if mapping[canonical] is not None:
                    break

        return mapping

    @classmethod
    def get_capabilities(cls, mapping: Dict[str, Optional[str]]) -> Dict[str, Any]:
        """
        Inspect which analytical modules and metrics can be calculated
        based on the detected column mapping.
        """
        has = lambda key: bool(mapping.get(key))

        return {
            "has_order_id": has("order_id"),
            "has_date": has("order_date"),
            "has_sales": has("sales"),
            "has_customer": has("customer_id") or has("customer_name"),
            "has_product": has("product_id") or has("product_name"),
            "has_category": has("category"),
            "has_quantity": has("quantity"),
            "has_profit": has("profit") or (has("sales") and has("unit_cost") and has("quantity")),
            "has_cost": has("unit_cost") or (has("sales") and has("profit")),
            "has_discount": has("discount"),
            "has_region": has("region") or has("state") or has("country"),
            "has_payment": has("payment_method"),
            
            # Module support flags
            "modules_supported": {
                "executive": has("order_date") and has("sales"),
                "sales_analytics": has("order_date") and has("sales"),
                "product_analytics": has("sales") and (has("product_name") or has("product_id") or has("category")),
                "customer_analytics": has("sales") and has("order_date") and (has("customer_id") or has("customer_name")),
                "regional_analytics": has("sales") and (has("region") or has("state")),
                "rfm_segmentation": has("sales") and has("order_date") and (has("customer_id") or has("customer_name")),
                "profitability_analysis": has("profit") or (has("sales") and has("unit_cost") and has("quantity"))
            },
            "missing_critical": [k for k, v in CANONICAL_FIELDS.items() if v["required"] and not has(k)]
        }
