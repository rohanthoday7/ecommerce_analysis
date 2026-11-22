# Dataverse — Enterprise E-Commerce Business Analytics Platform

An enterprise-grade, full-stack **Business Intelligence & Data Science Platform** built to transform raw e-commerce transactional data into actionable commercial insights.

Built with **Python (FastAPI, Pandas, NumPy, SciPy)** on the backend and a responsive, high-performance **Enterprise Dark Theme (Tailwind/Inter aesthetic, Chart.js, Leaflet, Lucide)** on the frontend.

---

## 🌟 Key Features & Analytical Modules

### 1. Executive Performance Dashboard
- **Dynamic C-Suite KPIs**: Total Revenue, Completed Orders, Average Order Value (AOV), Active Customers, Repeat Purchase Rate, Gross Profit, and Operating Margin %.
- **Period-over-Period Growth Benchmarking**: Real-time delta indicators comparing the active date range to the equivalent preceding period.
- **Dual-Axis Trend Velocity**: Synchronized revenue trajectory, order counts, and AOV evolution over time.
- **Categorical & Regional Distributions**: High-level departmental shares and top geographic territory volume.
- **Hero SKUs Leaderboard**: Top revenue-generating products with order frequencies and unit depths.

### 2. Advanced Sales Analytics
- **Multi-Grain Time Series**: Instantly toggle chronological granularity between **Daily**, **Weekly**, **Monthly**, and **Yearly** views.
- **Month-over-Month (MoM) Growth Dynamics**: Color-coded sequential growth and contraction rates.
- **Cyclical Seasonality Decomposition**:
  - *Calendar Month Seasonality*: Historical aggregate demand curves across all 12 months.
  - *Day-of-Week Purchasing Cycle*: Conversion velocity from Monday through Sunday.
- **Order Basket Size Distribution**: Transaction frequency grouped by check-out dollar tiers ($0-$50, $50-$100, $100-$250, $250-$500, $500-$1,000, $1,000-$2,500, $2,500+).
- **Departmental Economics Table**: Unit volumes, departmental revenue shares, and category-level AOVs.

### 3. Product Catalog Intelligence
- **Pareto 80/20 Concentration Engine**: Calculates the exact percentage of SKUs driving 80% of top-line revenue with interactive cumulative distribution curves.
- **Hero vs. Slow-Mover Rankings**: Top 10 revenue/volume leaders contrasted against the bottom 10 slowest-moving SKUs.
- **Side-by-Side Product Comparison Tool**: Select any 2 or 3 products from the catalog to benchmark unit velocity, average selling price, margin profiles, and historical monthly demand trends.
- **Product Hierarchy Matrix**: Multi-level breakdown across Categories and Sub-Categories.

### 4. Customer Intelligence & RFM Segmentation
- **Statistical RFM Scoring (1–5)**:
  - *Recency (R)*: Days elapsed since last order.
  - *Frequency (F)*: Total transaction count.
  - *Monetary (M)*: Total historical gross spend.
- **Behavioral Segments**: Algorithmic classification into *Champions*, *Loyal Customers*, *Potential Loyalists*, *New Customers*, *Needs Attention*, *At Risk*, *Can't Lose Them*, and *Hibernating*.
- **Customer Lifetime Value (CLV)**: Empirical historical average CLV alongside 3-year projected predictive CLV based on purchase cadence and lifespan.
- **New vs. Returning Cohort Trends**: Monthly breakdown of new acquisition revenue versus repeat customer equity.
- **VIP Customer Directory**: Searchable profiles of the top 25 high-value spenders with RFM badges, favorite categories, and recency tracking.

### 5. Regional & Geospatial Analytics
- **Interactive Leaflet Map**: Dark-matter geospatial map with circle bubble markers proportional to sales volume, complete with interactive state metrics popups.
- **Territory Volume & Growth**: Cross-regional comparisons and quarterly performance trajectories.
- **State & Municipality Benchmarks**: State-level rankings and top 15 municipal market hubs.

### 6. Automated Business Insights & Diagnostic Engine
Algorithmic pattern recognition scanning for real mathematical findings backed by supporting data:
1. **Catalog Concentration Risk**: Quantifies revenue vulnerability to hero SKU stockouts.
2. **Customer Retention Multiplier**: Measures repeat customer revenue dominance and AOV premiums.
3. **Discount Elasticity & Margin Dilution**: Diagnoses margin erosion caused by promotional discounting.
4. **Portfolio Optimization**: Identifies high-margin categories that merit higher ad spend allocation.
5. **Geographic Headroom**: Identifies under-penetrated regional markets.
6. **Day-of-Week Spikes**: Pinpoints peak conversion days to optimize campaign scheduling.

*Each insight strictly includes:*
1. **Finding**
2. **Supporting Data**
3. **Business Implication**
4. **Recommended Action**

### 7. Data Management & Preprocessing Studio
- **Multi-Format Ingestion**: Drag-and-drop support for `.csv`, `.xlsx`, `.xls`, and `.tsv` files.
- **Dataset Health Audit**: Real-time integrity score (0–100) evaluating missing cells, duplicate records, and schema completeness.
- **Column Schema Mapper**: Automatically detects e-commerce columns (`order_id`, `sales`, `date`, `customer_id`, etc.) and provides a manual dropdown remapping interface.
- **Data Hygiene Pipeline**: Toggles for deduplication, statistical median imputation, and negative anomaly filtering.
- **Live Paginated Data Preview**: Fast client-side search and page navigation over the active dataset.
- **Exporting**: Download processed and cleaned data as CSV or Excel.

---

## 🛠️ Architecture

```
ecommerce_analysis/
├── backend/
│   ├── app.py                     # FastAPI application & REST endpoints
│   ├── analytics/
│   │   ├── __init__.py
│   │   ├── filters.py             # Multi-dimensional filtering & comparison periods
│   │   ├── executive.py           # Executive dashboard KPIs & high-level trends
│   │   ├── sales.py               # Time-series, MoM growth, seasonality, basket size
│   │   ├── products.py            # Pareto 80/20, rankings, product comparison
│   │   ├── customers.py           # RFM segmentation (1-5), CLV, cohort curves
│   │   ├── regional.py            # Geographic analysis, state stats, map points
│   │   └── insights.py            # Automated diagnostic & recommendation engine
│   ├── data_engine/
│   │   ├── __init__.py
│   │   ├── loader.py              # File parsing & quality profiling
│   │   ├── preprocessor.py        # Cleaning, missing-value imputation, deduplication
│   │   └── schema.py              # Adaptive column detection & canonical mapping
│   └── sample_generator.py        # Generates realistic multi-year enterprise dataset
├── frontend/
│   ├── index.html                 # Single-page application shell
│   ├── css/
│   │   └── styles.css             # Enterprise dark theme design system
│   └── js/
│       ├── api.js                 # API client with automatic filter serialization
│       ├── state.js               # Reactive state store & event dispatcher
│       ├── charts.js              # Chart.js initialization & dark theme palettes
│       ├── modules/
│       │   ├── executive.js       # Executive view renderer
│       │   ├── sales.js           # Sales analytics view renderer
│       │   ├── products.js        # Products & comparison renderer
│       │   ├── customers.js       # Customers & RFM renderer
│       │   ├── regional.js        # Regional & Leaflet map renderer
│       │   ├── insights.js        # Automated business insights renderer
│       │   └── data_mgmt.js       # Dataset upload, preview & cleaning renderer
│       └── app.js                 # Application router, toast alerts & lifecycle
├── data/
│   └── sample_ecommerce.csv       # Default enterprise dataset (9,696 records)
├── tests/
│   ├── test_analytics.py          # Unit tests for analytics engines
│   └── test_api_endpoints.py      # Unit tests for backend endpoints
├── requirements.txt               # Python dependencies
├── run.py                         # Single-command application launcher
└── README.md
```

---

## 🚀 Quick Start Guide

### 1. Requirements
- Python 3.9+
- Standard libraries: `fastapi`, `uvicorn`, `pandas`, `numpy`, `scipy`, `openpyxl`, `python-multipart`

Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Launch Platform
Run the single-command runner:
```bash
python run.py
```

Open your browser to:
- **Web Analytics Platform:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Interactive OpenAPI Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 3. Run Test Suite
Execute the comprehensive test suite across all analytical engines and API routes:
```bash
python -m unittest discover -s tests -p "test_*.py"
```
*(All 21 unit and endpoint tests pass in ~1.0s)*

---

## 🔒 Enterprise Standards Adhered To
- **No Hardcoding**: Every metric, chart coordinate, ranking, and insight is computed dynamically from the active dataset.
- **Adaptive Schema Support**: Works out of the box with any dataset; automatically detects standard columns and degrades gracefully if columns are missing.
- **Zero Mock UI**: Every filter, date picker, preset button, table sort, and comparison selector triggers real analytical recalculation.
