"""
E-Commerce Analytics Platform — Backend API Service
FastAPI application providing dataset management, automated schema mapping,
and high-performance statistical analytics endpoints.
"""

import os
import sys
import io

# Ensure backend and root directories are in sys.path for local, Vercel, and containerized runtimes
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
for p in [CURRENT_DIR, PROJECT_ROOT]:
    if p not in sys.path:
        sys.path.insert(0, p)
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
import pandas as pd
import numpy as np

from data_engine import DatasetLoader, SchemaMapper, DataPreprocessor
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

app = FastAPI(
    title="Dataverse — Enterprise E-Commerce Business Analytics Platform",
    description="Production-grade analytics and business intelligence engine",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------
# Global In-Memory Dataset State Manager
# -------------------------------------------------------------
class StateManager:
    def __init__(self):
        self.dataset_name = "sample_ecommerce.csv"
        self.raw_df: pd.DataFrame = pd.DataFrame()
        self.working_df: pd.DataFrame = pd.DataFrame()
        self.mapping: Dict[str, Optional[str]] = {}
        self.profile: Dict[str, Any] = {}
        self.clean_report: Dict[str, Any] = {}

    def load_from_df(self, df: pd.DataFrame, name: str, custom_mapping: Optional[Dict[str, Optional[str]]] = None):
        self.raw_df = df
        self.dataset_name = name
        
        # 1. Detect or apply mapping
        if custom_mapping:
            self.mapping = custom_mapping
        else:
            self.mapping = SchemaMapper.detect_mapping(df.columns.tolist())

        # 2. Quality profiling
        self.profile = DatasetLoader.profile_dataset(self.raw_df, self.mapping)

        # 3. Clean and canonicalize
        self.working_df, self.clean_report = DataPreprocessor.process(
            df=self.raw_df,
            mapping=self.mapping,
            drop_duplicates=True,
            impute_missing=True,
            remove_negative_sales=True
        )

state = StateManager()

# Initialize with synthetic dataset (single source of truth) on startup
SYNTHETIC_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "synthetic_ecommerce_orders_2025.csv")
LEGACY_SAMPLE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sample_ecommerce.csv")
DEFAULT_SAMPLE_PATH = SYNTHETIC_PATH if os.path.exists(SYNTHETIC_PATH) else LEGACY_SAMPLE_PATH
DEFAULT_DATASET_NAME = "synthetic_ecommerce_orders_2025.csv" if os.path.exists(SYNTHETIC_PATH) else "sample_ecommerce.csv"

if os.path.exists(DEFAULT_SAMPLE_PATH):
    try:
        init_df = pd.read_csv(DEFAULT_SAMPLE_PATH)
        state.load_from_df(init_df, DEFAULT_DATASET_NAME)
        print(f"Initialized application with source dataset '{DEFAULT_DATASET_NAME}': {len(init_df)} records.")
    except Exception as e:
        print(f"Warning: Failed to load default sample dataset: {e}")

# -------------------------------------------------------------
# Dataset Management Endpoints
# -------------------------------------------------------------
@app.get("/api/dataset/status")
def get_dataset_status():
    if len(state.raw_df) == 0:
        return {"loaded": False, "message": "No dataset currently loaded."}

    capabilities = SchemaMapper.get_capabilities(state.mapping)
    filter_opts = get_filter_options(state.working_df)

    return {
        "loaded": True,
        "name": state.dataset_name,
        "total_rows": state.profile.get("total_rows", 0),
        "total_columns": state.profile.get("total_columns", 0),
        "health_score": state.profile.get("health_score", 100),
        "duplicate_rows": state.profile.get("duplicate_rows", 0),
        "total_missing_cells": state.profile.get("total_missing_cells", 0),
        "has_profit_data": state.clean_report.get("has_profit_data", False),
        "currency_symbol": state.clean_report.get("currency_symbol", "$"),
        "capabilities": capabilities,
        "mapping": state.mapping,
        "filter_options": filter_opts,
        "cleaning_log": state.clean_report.get("cleaning_log", [])
    }

@app.post("/api/dataset/upload")
async def upload_dataset(file: UploadFile = File(...)):
    filename = file.filename or "uploaded_dataset.csv"
    contents = await file.read()
    
    try:
        buffer = io.BytesIO(contents)
        df = DatasetLoader.read_file(buffer, filename)
        if len(df) == 0:
            raise HTTPException(status_code=400, detail="The uploaded file contains no data rows.")
        
        state.load_from_df(df, filename)
        return {
            "success": True,
            "message": f"Successfully loaded dataset '{filename}' with {len(df):,} records.",
            "status": get_dataset_status()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process file: {str(e)}")

@app.post("/api/dataset/load-sample")
def load_sample_dataset():
    if not os.path.exists(DEFAULT_SAMPLE_PATH):
        raise HTTPException(status_code=404, detail="Default sample dataset file not found.")
    
    df = pd.read_csv(DEFAULT_SAMPLE_PATH)
    state.load_from_df(df, DEFAULT_DATASET_NAME)
    return {
        "success": True,
        "message": f"Reset to single source of truth dataset '{DEFAULT_DATASET_NAME}'.",
        "status": get_dataset_status()
    }

@app.post("/api/dataset/remap")
def remap_dataset(custom_mapping: Dict[str, Optional[str]]):
    if len(state.raw_df) == 0:
        raise HTTPException(status_code=400, detail="No dataset loaded to remap.")

    state.load_from_df(state.raw_df, state.dataset_name, custom_mapping=custom_mapping)
    return {
        "success": True,
        "message": "Column mappings updated and analytics recalibrated.",
        "status": get_dataset_status()
    }

@app.post("/api/dataset/preprocess")
def preprocess_dataset(
    drop_duplicates: bool = Form(True),
    impute_missing: bool = Form(True),
    remove_negative_sales: bool = Form(True)
):
    if len(state.raw_df) == 0:
        raise HTTPException(status_code=400, detail="No dataset loaded.")

    state.working_df, state.clean_report = DataPreprocessor.process(
        df=state.raw_df,
        mapping=state.mapping,
        drop_duplicates=drop_duplicates,
        impute_missing=impute_missing,
        remove_negative_sales=remove_negative_sales
    )
    return {
        "success": True,
        "clean_report": state.clean_report,
        "status": get_dataset_status()
    }

@app.get("/api/dataset/profile")
def get_dataset_profile():
    if len(state.raw_df) == 0:
        raise HTTPException(status_code=400, detail="No dataset loaded.")
    return state.profile

@app.get("/api/dataset/preview")
def preview_dataset(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=5, le=100),
    search: Optional[str] = Query(None)
):
    if len(state.working_df) == 0:
        return {"rows": [], "total": 0, "page": page, "page_size": page_size}

    df = state.working_df
    # Select user-friendly display columns (strip leading underscore)
    display_cols = [c for c in df.columns if not c.startswith('_')]
    if not display_cols:
        display_cols = df.columns.tolist()

    sub_df = df[display_cols].copy()

    # Apply search filter if provided
    if search:
        search_lower = search.lower()
        mask = pd.Series(False, index=sub_df.index)
        for col in sub_df.columns:
            mask = mask | sub_df[col].astype(str).str.lower().str.contains(search_lower, na=False)
        sub_df = sub_df[mask]

    total_records = len(sub_df)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    page_df = sub_df.iloc[start_idx:end_idx]

    # Convert to JSON serializable records
    records = []
    for _, row in page_df.iterrows():
        rec = {}
        for col in display_cols:
            v = row[col]
            if pd.isna(v):
                rec[col] = None
            elif isinstance(v, (np.integer, int)):
                rec[col] = int(v)
            elif isinstance(v, (np.floating, float)):
                rec[col] = round(float(v), 2)
            else:
                rec[col] = str(v)
        records.append(rec)

    return {
        "columns": display_cols,
        "rows": records,
        "total": total_records,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, int(np.ceil(total_records / page_size)))
    }

@app.get("/api/dataset/export")
def export_dataset(format: str = Query("csv", pattern="^(csv|excel)$")):
    if len(state.working_df) == 0:
        raise HTTPException(status_code=400, detail="No dataset loaded.")

    df = state.working_df.copy()
    # Remove internal underscore columns for clean presentation
    clean_cols = [c for c in df.columns if not c.startswith('_')]
    export_df = df[clean_cols] if clean_cols else df

    if format == "csv":
        stream = io.StringIO()
        export_df.to_csv(stream, index=False)
        response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
        response.headers["Content-Disposition"] = f"attachment; filename=cleaned_{state.dataset_name.replace('.xlsx', '.csv')}"
        return response
    else:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            export_df.to_excel(writer, index=False, sheet_name="Cleaned Data")
        output.seek(0)
        response = StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response.headers["Content-Disposition"] = f"attachment; filename=cleaned_{os.path.splitext(state.dataset_name)[0]}.xlsx"
        return response

# -------------------------------------------------------------
# Analytics Endpoints
# -------------------------------------------------------------
@app.get("/api/analytics/filters")
def get_filters():
    if len(state.working_df) == 0:
        return {}
    return get_filter_options(state.working_df)

@app.get("/api/analytics/executive")
def get_executive_analytics(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    segment: Optional[str] = Query(None),
    payment_method: Optional[str] = Query(None)
):
    if len(state.working_df) == 0:
        raise HTTPException(status_code=400, detail="No dataset loaded.")

    curr_df, prev_df = apply_filters(
        df=state.working_df,
        start_date=start_date,
        end_date=end_date,
        category=category,
        region=region,
        segment=segment,
        payment_method=payment_method
    )

    return compute_executive_dashboard(curr_df, prev_df, full_df=state.working_df)

@app.get("/api/analytics/sales")
def get_sales_analytics(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    segment: Optional[str] = Query(None),
    payment_method: Optional[str] = Query(None)
):
    if len(state.working_df) == 0:
        raise HTTPException(status_code=400, detail="No dataset loaded.")

    curr_df, _ = apply_filters(
        df=state.working_df,
        start_date=start_date,
        end_date=end_date,
        category=category,
        region=region,
        segment=segment,
        payment_method=payment_method
    )

    return compute_sales_analytics(curr_df)

@app.get("/api/analytics/products")
def get_product_analytics(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    segment: Optional[str] = Query(None),
    payment_method: Optional[str] = Query(None),
    compare: Optional[str] = Query(None) # Comma-separated product IDs
):
    if len(state.working_df) == 0:
        raise HTTPException(status_code=400, detail="No dataset loaded.")

    curr_df, _ = apply_filters(
        df=state.working_df,
        start_date=start_date,
        end_date=end_date,
        category=category,
        region=region,
        segment=segment,
        payment_method=payment_method
    )

    comparison_ids = [p.strip() for p in compare.split(",")] if isinstance(compare, str) and compare.strip() else None
    return compute_product_analytics(curr_df, comparison_product_ids=comparison_ids)

@app.get("/api/analytics/customers")
def get_customer_analytics(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    segment: Optional[str] = Query(None),
    payment_method: Optional[str] = Query(None)
):
    if len(state.working_df) == 0:
        raise HTTPException(status_code=400, detail="No dataset loaded.")

    curr_df, _ = apply_filters(
        df=state.working_df,
        start_date=start_date,
        end_date=end_date,
        category=category,
        region=region,
        segment=segment,
        payment_method=payment_method
    )

    return compute_customer_analytics(curr_df)

@app.get("/api/analytics/regional")
def get_regional_analytics(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    segment: Optional[str] = Query(None),
    payment_method: Optional[str] = Query(None)
):
    if len(state.working_df) == 0:
        raise HTTPException(status_code=400, detail="No dataset loaded.")

    curr_df, _ = apply_filters(
        df=state.working_df,
        start_date=start_date,
        end_date=end_date,
        category=category,
        region=region,
        segment=segment,
        payment_method=payment_method
    )

    return compute_regional_analytics(curr_df)

@app.get("/api/analytics/insights")
def get_insights(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    segment: Optional[str] = Query(None),
    payment_method: Optional[str] = Query(None)
):
    if len(state.working_df) == 0:
        raise HTTPException(status_code=400, detail="No dataset loaded.")

    curr_df, _ = apply_filters(
        df=state.working_df,
        start_date=start_date,
        end_date=end_date,
        category=category,
        region=region,
        segment=segment,
        payment_method=payment_method
    )

    return generate_business_insights(curr_df)

# -------------------------------------------------------------
# Static Frontend Serving
# -------------------------------------------------------------
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
def serve_index():
    index_file = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Enterprise Analytics Platform API running. Frontend pending build."}
