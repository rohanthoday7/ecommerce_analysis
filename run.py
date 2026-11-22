"""
Single-Command Launcher for Enterprise E-Commerce Analytics Platform
Starts the FastAPI application and serves the web analytics portal.
"""

import os
import sys
import uvicorn

def main():
    workspace_dir = os.path.dirname(os.path.abspath(__file__))
    sample_path = os.path.join(workspace_dir, "data", "sample_ecommerce.csv")

    if not os.path.exists(sample_path):
        print("Default dataset not found. Generating sample enterprise dataset...")
        sys.path.insert(0, os.path.join(workspace_dir, "backend"))
        from sample_generator import generate_ecommerce_dataset
        generate_ecommerce_dataset(sample_path)

    print("=" * 70)
    print("   NEXUS-BI — ENTERPRISE E-COMMERCE BUSINESS ANALYTICS PLATFORM")
    print("=" * 70)
    print(" • Backend API:      http://127.0.0.1:8000/docs")
    print(" • Web Dashboard:    http://127.0.0.1:8000/")
    print("=" * 70)

    # Change working directory to backend so relative imports work seamlessly
    sys.path.insert(0, os.path.join(workspace_dir, "backend"))
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)

if __name__ == "__main__":
    main()
