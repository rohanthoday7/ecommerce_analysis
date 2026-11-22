"""
Dataset Loader and Quality Assessment Engine
Loads CSV / Excel files and performs statistical quality profiling.
"""

from typing import Dict, Any, List, Optional
import io
import os
import pandas as pd
import numpy as np
from .schema import SchemaMapper, CANONICAL_FIELDS

class DatasetLoader:
    @staticmethod
    def read_file(file_path_or_bytes, filename: str) -> pd.DataFrame:
        """
        Reads tabular data from file path or file-like bytes buffer.
        Supports .csv, .tsv, .xlsx, .xls.
        """
        lower_name = filename.lower()
        if lower_name.endswith('.csv') or lower_name.endswith('.txt'):
            try:
                # Try UTF-8 first, fallback to latin1
                df = pd.read_csv(file_path_or_bytes, encoding='utf-8')
            except UnicodeDecodeError:
                if hasattr(file_path_or_bytes, 'seek'):
                    file_path_or_bytes.seek(0)
                df = pd.read_csv(file_path_or_bytes, encoding='latin1')
        elif lower_name.endswith('.tsv'):
            df = pd.read_csv(file_path_or_bytes, sep='\t')
        elif lower_name.endswith('.xlsx') or lower_name.endswith('.xls'):
            df = pd.read_excel(file_path_or_bytes)
        else:
            raise ValueError(f"Unsupported file format: {filename}. Supported formats are .csv, .tsv, .xlsx, .xls.")

        return df

    @classmethod
    def profile_dataset(cls, df: pd.DataFrame, mapping: Optional[Dict[str, Optional[str]]] = None) -> Dict[str, Any]:
        """
        Generates deep data quality diagnostics, column profiles, and schema mappings.
        """
        if mapping is None:
            mapping = SchemaMapper.detect_mapping(df.columns.tolist())

        capabilities = SchemaMapper.get_capabilities(mapping)
        total_rows = int(len(df))
        total_cols = int(len(df.columns))
        duplicate_rows = int(df.duplicated().sum())

        # Column-by-column diagnostic audit
        columns_profile = []
        for col in df.columns:
            series = df[col]
            missing_count = int(series.isna().sum())
            missing_pct = round((missing_count / total_rows * 100), 2) if total_rows > 0 else 0
            unique_count = int(series.nunique(dropna=True))

            # Inferred dtype classification
            if pd.api.types.is_numeric_dtype(series):
                col_type = "Numeric"
                col_min = float(series.min()) if not np.isnan(series.min()) else None
                col_max = float(series.max()) if not np.isnan(series.max()) else None
                col_mean = round(float(series.mean()), 2) if not np.isnan(series.mean()) else None
                stats = {"min": col_min, "max": col_max, "mean": col_mean}
            elif pd.api.types.is_datetime64_any_dtype(series):
                col_type = "Datetime"
                stats = {"min": str(series.min()), "max": str(series.max())}
            else:
                col_type = "Categorical / Text"
                top_val = str(series.mode()[0]) if len(series.mode()) > 0 else None
                stats = {"top_value": top_val}

            sample_vals = [str(v) if pd.notna(v) else None for v in series.dropna().head(3).tolist()]

            # Check if this column maps to any canonical field
            mapped_to = None
            for canon_key, mapped_col in mapping.items():
                if mapped_col == col:
                    mapped_to = canon_key
                    break

            columns_profile.append({
                "name": str(col),
                "mapped_to": mapped_to,
                "mapped_label": CANONICAL_FIELDS[mapped_to]["label"] if mapped_to else None,
                "type": col_type,
                "missing_count": missing_count,
                "missing_percentage": missing_pct,
                "unique_values": unique_count,
                "sample_values": sample_vals,
                "stats": stats
            })

        # Generate sample records (first 15 rows)
        preview_records = []
        for _, row in df.head(15).iterrows():
            record = {}
            for col in df.columns:
                val = row[col]
                if pd.isna(val):
                    record[col] = None
                elif isinstance(val, (np.integer, int)):
                    record[col] = int(val)
                elif isinstance(val, (np.floating, float)):
                    record[col] = round(float(val), 4)
                else:
                    record[col] = str(val)
            preview_records.append(record)

        # Health score calculation (0 to 100)
        total_cells = max(total_rows * total_cols, 1)
        total_null_cells = int(df.isna().sum().sum())
        null_rate = total_null_cells / total_cells
        dup_rate = duplicate_rows / max(total_rows, 1)
        
        health_score = max(0, min(100, round(100 - (null_rate * 50) - (dup_rate * 30) - (len(capabilities["missing_critical"]) * 15))))

        return {
            "total_rows": total_rows,
            "total_columns": total_cols,
            "duplicate_rows": duplicate_rows,
            "duplicate_percentage": round(duplicate_rows / max(total_rows, 1) * 100, 2),
            "total_missing_cells": total_null_cells,
            "missing_cells_percentage": round(null_rate * 100, 2),
            "health_score": health_score,
            "mapping": mapping,
            "capabilities": capabilities,
            "columns": columns_profile,
            "preview": preview_records
        }
