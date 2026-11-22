"""
Data Preprocessing Engine
Cleans, standardizes, imputes missing values, handles duplicates,
and prepares raw e-commerce data for robust analytical calculation.
"""

from typing import Dict, Any, Tuple, Optional
import re
import pandas as pd
import numpy as np

class DataPreprocessor:
    @staticmethod
    def clean_numeric_series(series: pd.Series) -> pd.Series:
        """
        Cleans string formatted currency/numeric values ($1,299.99, ₹1,299, Rs. 4,500, (50.00), 20%) into float.
        Handles international currencies, symbols, commas, and percentage markers.
        """
        if pd.api.types.is_numeric_dtype(series):
            return pd.to_numeric(series, errors='coerce')
        
        cleaned = series.astype(str).str.strip()
        # Handle accounting negative parenthesized values like (120.50)
        cleaned = cleaned.str.replace(r'^\((.*)\)$', r'-\1', regex=True)
        # Remove currency words
        cleaned = cleaned.str.replace(r'(?i)\b(rs|inr|usd|eur|gbp|cad|aud)\b\.?', '', regex=True)
        # Remove currency symbols (Rupee ₹, Dollar $, Euro €, Pound £, Yen ¥, commas, %)
        cleaned = cleaned.str.replace(r'[\$,€,£,¥,₹,%,`]', '', regex=True)
        cleaned = cleaned.str.replace(',', '', regex=False)
        # Extract clean numeric float string
        extracted = cleaned.str.extract(r'([-+]?\d+(?:\.\d+)?)')[0]
        return pd.to_numeric(extracted, errors='coerce')

    @classmethod
    def process(
        cls,
        df: pd.DataFrame,
        mapping: Dict[str, Optional[str]],
        drop_duplicates: bool = True,
        impute_missing: bool = True,
        remove_negative_sales: bool = True
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Standardizes raw DataFrame into analytical working format with internal canonical columns:
        _order_id, _order_date, _sales, _profit, _quantity, _discount, _customer_id, etc.
        """
        working_df = df.copy()
        log = []
        original_rows = len(working_df)

        # 1. Deduplication
        if drop_duplicates:
            dups = int(working_df.duplicated().sum())
            if dups > 0:
                working_df = working_df.drop_duplicates().reset_index(drop=True)
                log.append(f"Removed {dups} duplicate records.")

        # 2. Map Canonical Columns to standard internal names prefixed with '_'
        # Order Date
        date_col = mapping.get("order_date")
        if date_col and date_col in working_df.columns:
            working_df["_order_date"] = pd.to_datetime(working_df[date_col], errors='coerce')
            # If majority failed, try format='mixed'
            if working_df["_order_date"].isna().sum() > (len(working_df) * 0.5):
                working_df["_order_date"] = pd.to_datetime(working_df[date_col], format='mixed', errors='coerce')
            
            invalid_dates = working_df["_order_date"].isna().sum()
            if invalid_dates > 0:
                if invalid_dates == len(working_df):
                    # Fallback to current date sequence instead of dropping all rows
                    today = pd.Timestamp.now()
                    working_df["_order_date"] = [today - pd.Timedelta(days=i % 365) for i in range(len(working_df))]
                    log.append(f"Unparseable date column '{date_col}'; generated chronological indices.")
                else:
                    # Forward-fill / back-fill valid dates
                    working_df["_order_date"] = working_df["_order_date"].ffill().bfill().fillna(pd.Timestamp.now())
                    log.append(f"Imputed {invalid_dates} unparseable dates from surrounding records.")
        else:
            today = pd.Timestamp.now()
            working_df["_order_date"] = [today - pd.Timedelta(days=i % 365) for i in range(len(working_df))]
            log.append("No date column detected; initialized chronological sequence.")

        # Order ID
        oid_col = mapping.get("order_id")
        if oid_col and oid_col in working_df.columns:
            working_df["_order_id"] = working_df[oid_col].astype(str).str.strip()
            working_df.loc[working_df["_order_id"].isin(["nan", "None", ""]), "_order_id"] = [
                f"GEN-ORD-{i}" for i in range(len(working_df[working_df["_order_id"].isin(["nan", "None", ""])]))
            ]
        else:
            working_df["_order_id"] = [f"ORD-{i+1}" for i in range(len(working_df))]

        # Quantity
        qty_col = mapping.get("quantity")
        if qty_col and qty_col in working_df.columns:
            working_df["_quantity"] = cls.clean_numeric_series(working_df[qty_col])
            working_df["_quantity"] = working_df["_quantity"].fillna(1.0)
            working_df.loc[working_df["_quantity"] <= 0, "_quantity"] = 1.0
        else:
            working_df["_quantity"] = 1.0

        # Unit Price
        price_col = mapping.get("unit_price")
        if price_col and price_col in working_df.columns:
            working_df["_unit_price"] = cls.clean_numeric_series(working_df[price_col]).fillna(0.0)
        else:
            working_df["_unit_price"] = None

        # Sales / Revenue
        sales_col = mapping.get("sales")
        if sales_col and sales_col in working_df.columns:
            working_df["_sales"] = cls.clean_numeric_series(working_df[sales_col]).fillna(0.0)
            if remove_negative_sales:
                neg_sales = (working_df["_sales"] < 0).sum()
                if neg_sales > 0:
                    working_df = working_df[working_df["_sales"] >= 0].reset_index(drop=True)
                    log.append(f"Removed {neg_sales} transactions with negative sales values.")
        else:
            working_df["_sales"] = 0.0

        # CRITICAL AUTO-DETECTION FALLBACK:
        # If _sales sum is 0, scan all columns for candidate revenue columns (discounted_price, actual_price, price, amount, total, balance, etc.)
        if working_df["_sales"].sum() == 0:
            candidate_names = [
                "discounted_price", "discounted price", "selling_price", "selling price",
                "actual_price", "actual price", "final_price", "price", "amount", "total",
                "sales", "revenue", "balance", "paid", "mrp", "unit_price", "unit price"
            ]
            for cand in candidate_names:
                matched_col = next((c for c in working_df.columns if cand in c.lower()), None)
                if matched_col and not matched_col.startswith('_'):
                    cleaned = cls.clean_numeric_series(working_df[matched_col]).fillna(0.0)
                    if cleaned.sum() > 0:
                        working_df["_sales"] = cleaned
                        log.append(f"Auto-detected revenue column '{matched_col}'.")
                        break

            # If still 0, check ANY non-underscore column with a positive sum
            if working_df["_sales"].sum() == 0:
                for c in working_df.columns:
                    if not c.startswith('_'):
                        cleaned = cls.clean_numeric_series(working_df[c]).fillna(0.0)
                        if cleaned.sum() > 0:
                            working_df["_sales"] = cleaned
                            log.append(f"Assigned positive numeric column '{c}' as revenue metric.")
                            break

        if working_df["_unit_price"] is None:
            working_df["_unit_price"] = working_df["_sales"] / working_df["_quantity"].replace(0, 1)

        # Ensure order dates are distributed across time if all identical or missing
        if working_df["_order_date"].isna().all() or working_df["_order_date"].nunique() <= 1:
            now = pd.Timestamp.now()
            n_rows = len(working_df)
            days_spread = np.linspace(365, 1, n_rows)
            working_df["_order_date"] = [now - pd.Timedelta(days=int(d)) for d in days_spread]
            log.append("Distributed chronological order dates across preceding 12 months.")

        # Discount
        disc_col = mapping.get("discount")
        if disc_col and disc_col in working_df.columns:
            working_df["_discount"] = cls.clean_numeric_series(working_df[disc_col]).fillna(0.0)
            if (working_df["_discount"] > 1.0).sum() > 0:
                working_df["_discount"] = working_df["_discount"] / 100.0
        else:
            working_df["_discount"] = 0.0

        # Profit & Cost
        profit_col = mapping.get("profit")
        cost_col = mapping.get("unit_cost")
        
        if profit_col and profit_col in working_df.columns:
            working_df["_profit"] = cls.clean_numeric_series(working_df[profit_col]).fillna(0.0)
            has_profit_data = True
        elif cost_col and cost_col in working_df.columns:
            working_df["_unit_cost"] = cls.clean_numeric_series(working_df[cost_col]).fillna(0.0)
            working_df["_profit"] = working_df["_sales"] - (working_df["_quantity"] * working_df["_unit_cost"])
            has_profit_data = True
        else:
            working_df["_profit"] = None
            has_profit_data = False

        # Customer ID and Name (support Amazon user_id, reviewer_id)
        cid_col = mapping.get("customer_id")
        cname_col = mapping.get("customer_name")
        
        if not cid_col:
            for cand in ["user_id", "userid", "reviewer_id", "buyer_id"]:
                m = next((c for c in working_df.columns if cand in c.lower()), None)
                if m:
                    cid_col = m
                    break

        if cid_col and cid_col in working_df.columns:
            working_df["_customer_id"] = working_df[cid_col].astype(str).str.strip()
        elif cname_col and cname_col in working_df.columns:
            working_df["_customer_id"] = working_df[cname_col].astype(str).str.strip()
        else:
            working_df["_customer_id"] = working_df["_order_id"].apply(lambda x: f"CUST-{x}")

        if cname_col and cname_col in working_df.columns:
            working_df["_customer_name"] = working_df[cname_col].astype(str).str.strip()
        else:
            working_df["_customer_name"] = working_df["_customer_id"]

        # Product ID and Name
        pid_col = mapping.get("product_id")
        pname_col = mapping.get("product_name")

        if not pname_col:
            for cand in ["product_name", "product_title", "title", "about_product", "item_name"]:
                m = next((c for c in working_df.columns if cand in c.lower()), None)
                if m:
                    pname_col = m
                    break

        if pname_col and pname_col in working_df.columns:
            working_df["_product_name"] = working_df[pname_col].astype(str).str.strip()
        elif pid_col and pid_col in working_df.columns:
            working_df["_product_name"] = working_df[pid_col].astype(str).str.strip()
        else:
            working_df["_product_name"] = "General Product"

        if pid_col and pid_col in working_df.columns:
            working_df["_product_id"] = working_df[pid_col].astype(str).str.strip()
        else:
            working_df["_product_id"] = working_df["_product_name"]

        # Category and Sub-category (clean Amazon pipe hierarchies like "Home&Kitchen|Kitchen&HomeAppliances|...")
        cat_col = mapping.get("category")
        if cat_col and cat_col in working_df.columns:
            raw_cat = working_df[cat_col].astype(str).str.strip().replace(["nan", "None", ""], "Other")
            primary_cat = raw_cat.apply(lambda x: x.split('|')[0].strip() if isinstance(x, str) and '|' in x else x)
            primary_cat = primary_cat.str.replace('&', ' & ', regex=False).str.replace(r'\s+', ' ', regex=True).str.strip()
            working_df["_category"] = primary_cat

            sub_from_pipe = raw_cat.apply(lambda x: x.split('|')[1].strip() if isinstance(x, str) and len(x.split('|')) > 1 else None)
            working_df["_sub_category"] = sub_from_pipe.fillna(working_df["_category"])
        else:
            working_df["_category"] = "Standard Category"
            working_df["_sub_category"] = "Standard Category"

        # Geography: Region, State, City, Country
        reg_col = mapping.get("region")
        state_col = mapping.get("state")
        city_col = mapping.get("city")
        country_col = mapping.get("country")

        working_df["_region"] = working_df[reg_col].astype(str).str.strip() if (reg_col and reg_col in working_df.columns) else (
            working_df[state_col].astype(str).str.strip() if (state_col and state_col in working_df.columns) else "Global"
        )
        working_df["_state"] = working_df[state_col].astype(str).str.strip() if (state_col and state_col in working_df.columns) else working_df["_region"]
        working_df["_city"] = working_df[city_col].astype(str).str.strip() if (city_col and city_col in working_df.columns) else "Unknown"
        working_df["_country"] = working_df[country_col].astype(str).str.strip() if (country_col and country_col in working_df.columns) else "United States"

        # Customer Segment & Payment Method
        seg_col = mapping.get("segment")
        working_df["_segment"] = working_df[seg_col].astype(str).str.strip() if (seg_col and seg_col in working_df.columns) else "Consumer"

        pay_col = mapping.get("payment_method")
        working_df["_payment_method"] = working_df[pay_col].astype(str).str.strip() if (pay_col and pay_col in working_df.columns) else "Standard Payment"

        # Order Status (Delivered, Cancelled, Returned, etc.)
        status_col = mapping.get("order_status")
        if not status_col:
            for cand in ["order_status", "order status", "status", "delivery_status", "delivery status", "order_state"]:
                m = next((c for c in working_df.columns if cand in c.lower()), None)
                if m and not m.startswith('_'):
                    status_col = m
                    break
        if status_col and status_col in working_df.columns:
            working_df["_order_status"] = working_df[status_col].astype(str).str.strip().str.title()
        else:
            working_df["_order_status"] = "Delivered"

        # Derived calendar columns for fast grouping
        if pd.api.types.is_datetime64_any_dtype(working_df["_order_date"]):
            working_df["_year"] = working_df["_order_date"].dt.year
            working_df["_year_month"] = working_df["_order_date"].dt.to_period("M").astype(str)
            working_df["_month_name"] = working_df["_order_date"].dt.month_name()
            working_df["_month"] = working_df["_order_date"].dt.month
            working_df["_day_name"] = working_df["_order_date"].dt.day_name()
            working_df["_day_of_week"] = working_df["_order_date"].dt.dayofweek
            working_df["_quarter"] = "Q" + working_df["_order_date"].dt.quarter.astype(str)

        # Ensure all core numeric metrics are strictly float64
        working_df["_sales"] = pd.to_numeric(working_df["_sales"], errors='coerce').fillna(0.0).astype(float)
        working_df["_quantity"] = pd.to_numeric(working_df["_quantity"], errors='coerce').fillna(1.0).astype(float)
        working_df["_unit_price"] = pd.to_numeric(working_df["_unit_price"], errors='coerce').fillna(0.0).astype(float)
        working_df["_discount"] = pd.to_numeric(working_df["_discount"], errors='coerce').fillna(0.0).astype(float)
        if "_profit" in working_df.columns and working_df["_profit"] is not None and working_df["_profit"].notna().any():
            working_df["_profit"] = pd.to_numeric(working_df["_profit"], errors='coerce').fillna(0.0).astype(float)

        # Ensure cancelled and returned orders do not recognize revenue or profit
        is_cancelled_or_returned = working_df["_order_status"].isin(["Cancelled", "Canceled", "Returned", "Refunded"])
        if is_cancelled_or_returned.any():
            working_df.loc[is_cancelled_or_returned, "_sales"] = 0.0
            if "_profit" in working_df.columns and working_df["_profit"] is not None:
                working_df.loc[is_cancelled_or_returned, "_profit"] = 0.0

        # Currency symbol: Platform standard is INR (₹)
        detected_currency = "₹"
        price_cols = [c for c in df.columns if any(p in c.lower() for p in ["price", "amount", "sales", "revenue", "cost", "total"])]
        sample_snippets = []
        for c in price_cols[:4]:
            sample_snippets.extend(df[c].dropna().astype(str).head(20).tolist())
        sample_text = " ".join(sample_snippets)
        if "€" in sample_text or re.search(r'\b(eur)\b', sample_text, re.I):
            detected_currency = "€"
        elif "£" in sample_text or re.search(r'\b(gbp)\b', sample_text, re.I):
            detected_currency = "£"
        elif "¥" in sample_text or re.search(r'\b(jpy)\b', sample_text, re.I):
            detected_currency = "¥"
        else:
            detected_currency = "₹"

        final_rows = len(working_df)
        report = {
            "original_rows": original_rows,
            "final_rows": final_rows,
            "rows_retained_pct": round((final_rows / max(original_rows, 1)) * 100, 2),
            "has_profit_data": has_profit_data,
            "currency_symbol": detected_currency,
            "cleaning_log": log
        }

        return working_df, report
