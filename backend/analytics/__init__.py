"""Analytics Package Initialization"""
from .filters import apply_filters, get_filter_options
from .executive import compute_executive_dashboard
from .sales import compute_sales_analytics
from .products import compute_product_analytics
from .customers import compute_customer_analytics
from .regional import compute_regional_analytics
from .insights import generate_business_insights

__all__ = [
    "apply_filters",
    "get_filter_options",
    "compute_executive_dashboard",
    "compute_sales_analytics",
    "compute_product_analytics",
    "compute_customer_analytics",
    "compute_regional_analytics",
    "generate_business_insights"
]
