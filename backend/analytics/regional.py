"""
Regional & Geospatial Analytics Engine
Geographic performance metrics across regions, states, cities, and growth trends.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

# Extensive Coordinates Database: US States (names + codes), Global Regions, and Major Countries
GEO_COORDINATES = {
    # US States
    "alabama": {"lat": 32.806671, "lng": -86.791130, "code": "AL", "name": "Alabama"},
    "alaska": {"lat": 61.370716, "lng": -152.404419, "code": "AK", "name": "Alaska"},
    "arizona": {"lat": 34.0489, "lng": -111.0937, "code": "AZ", "name": "Arizona"},
    "arkansas": {"lat": 34.969704, "lng": -92.373123, "code": "AR", "name": "Arkansas"},
    "california": {"lat": 36.7783, "lng": -119.4179, "code": "CA", "name": "California"},
    "colorado": {"lat": 39.5501, "lng": -105.7821, "code": "CO", "name": "Colorado"},
    "connecticut": {"lat": 41.603221, "lng": -73.087749, "code": "CT", "name": "Connecticut"},
    "delaware": {"lat": 38.910832, "lng": -75.527670, "code": "DE", "name": "Delaware"},
    "district of columbia": {"lat": 38.9072, "lng": -77.0369, "code": "DC", "name": "District of Columbia"},
    "florida": {"lat": 27.6648, "lng": -81.5158, "code": "FL", "name": "Florida"},
    "georgia": {"lat": 32.1656, "lng": -82.9001, "code": "GA", "name": "Georgia"},
    "hawaii": {"lat": 21.094318, "lng": -157.498337, "code": "HI", "name": "Hawaii"},
    "idaho": {"lat": 44.240459, "lng": -114.478828, "code": "ID", "name": "Idaho"},
    "illinois": {"lat": 40.6331, "lng": -89.3985, "code": "IL", "name": "Illinois"},
    "indiana": {"lat": 40.267194, "lng": -86.134902, "code": "IN", "name": "Indiana"},
    "iowa": {"lat": 41.878003, "lng": -93.097702, "code": "IA", "name": "Iowa"},
    "kansas": {"lat": 39.011902, "lng": -98.484246, "code": "KS", "name": "Kansas"},
    "kentucky": {"lat": 37.839333, "lng": -84.270018, "code": "KY", "name": "Kentucky"},
    "louisiana": {"lat": 30.984298, "lng": -91.962333, "code": "LA", "name": "Louisiana"},
    "maine": {"lat": 45.253783, "lng": -69.445469, "code": "ME", "name": "Maine"},
    "maryland": {"lat": 39.045755, "lng": -76.641271, "code": "MD", "name": "Maryland"},
    "massachusetts": {"lat": 42.4072, "lng": -71.3824, "code": "MA", "name": "Massachusetts"},
    "michigan": {"lat": 44.3148, "lng": -85.6024, "code": "MI", "name": "Michigan"},
    "minnesota": {"lat": 46.7296, "lng": -94.6859, "code": "MN", "name": "Minnesota"},
    "mississippi": {"lat": 32.354668, "lng": -89.398528, "code": "MS", "name": "Mississippi"},
    "missouri": {"lat": 37.9643, "lng": -91.8318, "code": "MO", "name": "Missouri"},
    "montana": {"lat": 46.879682, "lng": -110.362566, "code": "MT", "name": "Montana"},
    "nebraska": {"lat": 41.492537, "lng": -99.901813, "code": "NE", "name": "Nebraska"},
    "nevada": {"lat": 38.8026, "lng": -116.4194, "code": "NV", "name": "Nevada"},
    "new hampshire": {"lat": 43.193852, "lng": -71.572395, "code": "NH", "name": "New Hampshire"},
    "new jersey": {"lat": 40.0583, "lng": -74.4057, "code": "NJ", "name": "New Jersey"},
    "new mexico": {"lat": 34.972730, "lng": -105.032363, "code": "NM", "name": "New Mexico"},
    "new york": {"lat": 40.7128, "lng": -74.0060, "code": "NY", "name": "New York"},
    "north carolina": {"lat": 35.7596, "lng": -79.0193, "code": "NC", "name": "North Carolina"},
    "north dakota": {"lat": 47.551493, "lng": -101.002012, "code": "ND", "name": "North Dakota"},
    "ohio": {"lat": 40.4173, "lng": -82.9071, "code": "OH", "name": "Ohio"},
    "oklahoma": {"lat": 35.007752, "lng": -97.092877, "code": "OK", "name": "Oklahoma"},
    "oregon": {"lat": 43.8041, "lng": -120.5542, "code": "OR", "name": "Oregon"},
    "pennsylvania": {"lat": 41.2033, "lng": -77.1945, "code": "PA", "name": "Pennsylvania"},
    "rhode island": {"lat": 41.580095, "lng": -71.477429, "code": "RI", "name": "Rhode Island"},
    "south carolina": {"lat": 33.836081, "lng": -81.163725, "code": "SC", "name": "South Carolina"},
    "south dakota": {"lat": 43.969515, "lng": -99.901813, "code": "SD", "name": "South Dakota"},
    "tennessee": {"lat": 35.5175, "lng": -86.5804, "code": "TN", "name": "Tennessee"},
    "texas": {"lat": 31.9686, "lng": -99.9018, "code": "TX", "name": "Texas"},
    "utah": {"lat": 39.320980, "lng": -111.093731, "code": "UT", "name": "Utah"},
    "vermont": {"lat": 44.558803, "lng": -72.577841, "code": "VT", "name": "Vermont"},
    "virginia": {"lat": 37.4316, "lng": -78.6569, "code": "VA", "name": "Virginia"},
    "washington": {"lat": 47.7511, "lng": -120.7401, "code": "WA", "name": "Washington"},
    "west virginia": {"lat": 38.597626, "lng": -80.454903, "code": "WV", "name": "West Virginia"},
    "wisconsin": {"lat": 43.784440, "lng": -88.787868, "code": "WI", "name": "Wisconsin"},
    "wyoming": {"lat": 43.075968, "lng": -107.290284, "code": "WY", "name": "Wyoming"},

    # Regional Fallbacks (directional centroids)
    "west": {"lat": 37.7749, "lng": -122.4194, "code": "WEST", "name": "West Region"},
    "east": {"lat": 40.7128, "lng": -74.0060, "code": "EAST", "name": "East Region"},
    "central": {"lat": 41.8781, "lng": -87.6298, "code": "CENT", "name": "Central Region"},
    "south": {"lat": 33.7490, "lng": -84.3880, "code": "STH", "name": "South Region"},
    "north": {"lat": 44.9778, "lng": -93.2650, "code": "NTH", "name": "North Region"},
    "midwest": {"lat": 41.8781, "lng": -87.6298, "code": "MW", "name": "Midwest Region"},
    "northeast": {"lat": 42.3601, "lng": -71.0589, "code": "NE", "name": "Northeast"},
    "southeast": {"lat": 28.5383, "lng": -81.3792, "code": "SE", "name": "Southeast"},
    "northwest": {"lat": 47.6062, "lng": -122.3321, "code": "NW", "name": "Northwest"},
    "southwest": {"lat": 33.4484, "lng": -112.0740, "code": "SW", "name": "Southwest"},

    # Global Hubs & Indian Metropolitan Centers
    "bhopal": {"lat": 23.2599, "lng": 77.4126, "code": "MP", "name": "Bhopal"},
    "delhi": {"lat": 28.6139, "lng": 77.2090, "code": "DL", "name": "Delhi"},
    "kochi": {"lat": 9.9312, "lng": 76.2673, "code": "KL", "name": "Kochi"},
    "hyderabad": {"lat": 17.3850, "lng": 78.4867, "code": "TG", "name": "Hyderabad"},
    "raipur": {"lat": 21.2514, "lng": 81.6296, "code": "CG", "name": "Raipur"},
    "lucknow": {"lat": 26.8467, "lng": 80.9462, "code": "UP", "name": "Lucknow"},
    "jaipur": {"lat": 26.9124, "lng": 75.7873, "code": "RJ", "name": "Jaipur"},
    "chandigarh": {"lat": 30.7333, "lng": 76.7794, "code": "CH", "name": "Chandigarh"},
    "bengaluru": {"lat": 12.9716, "lng": 77.5946, "code": "KA", "name": "Bengaluru"},
    "guwahati": {"lat": 26.1445, "lng": 91.7362, "code": "AS", "name": "Guwahati"},
    "indore": {"lat": 22.7196, "lng": 75.8577, "code": "MP", "name": "Indore"},
    "surat": {"lat": 21.1702, "lng": 72.8311, "code": "GJ", "name": "Surat"},
    "bhubaneswar": {"lat": 20.2961, "lng": 85.8245, "code": "OD", "name": "Bhubaneswar"},
    "patna": {"lat": 25.5941, "lng": 85.1376, "code": "BR", "name": "Patna"},
    "mumbai": {"lat": 19.0760, "lng": 72.8777, "code": "MH", "name": "Mumbai"},
    "pune": {"lat": 18.5204, "lng": 73.8567, "code": "MH", "name": "Pune"},
    "chennai": {"lat": 13.0827, "lng": 80.2707, "code": "TN", "name": "Chennai"},
    "nagpur": {"lat": 21.1458, "lng": 79.0882, "code": "MH", "name": "Nagpur"},
    "kolkata": {"lat": 22.5726, "lng": 88.3639, "code": "WB", "name": "Kolkata"},
    "ahmedabad": {"lat": 23.0225, "lng": 72.5714, "code": "GJ", "name": "Ahmedabad"},
    "united states": {"lat": 39.8283, "lng": -98.5795, "code": "US", "name": "United States"},
    "usa": {"lat": 39.8283, "lng": -98.5795, "code": "USA", "name": "United States"},
    "canada": {"lat": 56.1304, "lng": -106.3468, "code": "CA", "name": "Canada"},
    "united kingdom": {"lat": 55.3781, "lng": -3.4360, "code": "UK", "name": "United Kingdom"},
    "uk": {"lat": 55.3781, "lng": -3.4360, "code": "UK", "name": "United Kingdom"},
    "germany": {"lat": 51.1657, "lng": 10.4515, "code": "DE", "name": "Germany"},
    "france": {"lat": 46.2276, "lng": 2.2137, "code": "FR", "name": "France"},
    "australia": {"lat": -25.2744, "lng": 133.7751, "code": "AU", "name": "Australia"},
    "india": {"lat": 20.5937, "lng": 78.9629, "code": "IN", "name": "India"},
    "japan": {"lat": 36.2048, "lng": 138.2529, "code": "JP", "name": "Japan"},
    "global": {"lat": 39.8283, "lng": -98.5795, "code": "GLB", "name": "Global Market"}
}

# Add 2-letter uppercase postal code lookups
STATE_CODES = {v["code"].lower(): v for v in list(GEO_COORDINATES.values()) if "code" in v and len(v["code"]) == 2}
GEO_COORDINATES.update(STATE_CODES)

def lookup_coordinates(name: str) -> Optional[Dict[str, Any]]:
    if not name:
        return None
    cleaned = str(name).strip().lower()
    return GEO_COORDINATES.get(cleaned)

def compute_regional_analytics(df: pd.DataFrame) -> Dict[str, Any]:
    if len(df) == 0:
        return {
            "summary": {},
            "regions": [],
            "states": [],
            "cities": [],
            "regional_growth": {"labels": [], "datasets": []},
            "map_points": []
        }

    total_revenue = float(df["_sales"].sum())
    total_orders = int(df["_order_id"].nunique())
    total_customers = int(df["_customer_id"].nunique())
    has_profit = bool("_profit" in df.columns and df["_profit"].notna().any())

    # 1. Regional Level Aggregation
    reg_agg = {
        "revenue": ("_sales", "sum"),
        "orders": ("_order_id", "nunique"),
        "customers": ("_customer_id", "nunique"),
        "quantity": ("_quantity", "sum")
    }
    if has_profit:
        reg_agg["profit"] = ("_profit", "sum")

    reg_df = df.groupby("_region").agg(**reg_agg).reset_index().sort_values(by="revenue", ascending=False)
    reg_df["rev_share"] = (reg_df["revenue"] / max(total_revenue, 1) * 100).round(2)
    reg_df["aov"] = (reg_df["revenue"] / reg_df["orders"].replace(0, 1)).round(2)

    regions_list = []
    for _, r in reg_df.iterrows():
        regions_list.append({
            "region": str(r["_region"]),
            "revenue": round(float(r["revenue"]), 2),
            "orders": int(r["orders"]),
            "customers": int(r["customers"]),
            "quantity": int(r["quantity"]),
            "rev_share": float(r["rev_share"]),
            "aov": float(r["aov"]),
            "profit": round(float(r["profit"]), 2) if has_profit else None,
            "margin": round(float(r["profit"]) / float(r["revenue"]) * 100, 2) if has_profit and float(r["revenue"]) > 0 else None
        })

    # 2. State Level Aggregation
    state_agg = {
        "revenue": ("_sales", "sum"),
        "orders": ("_order_id", "nunique"),
        "customers": ("_customer_id", "nunique"),
        "region": ("_region", "first")
    }
    if has_profit:
        state_agg["profit"] = ("_profit", "sum")

    state_df = df.groupby("_state").agg(**state_agg).reset_index().sort_values(by="revenue", ascending=False)
    state_df["rev_share"] = (state_df["revenue"] / max(total_revenue, 1) * 100).round(2)
    state_df["aov"] = (state_df["revenue"] / state_df["orders"].replace(0, 1)).round(2)

    states_list = []
    map_points = []
    for _, r in state_df.iterrows():
        st_name = str(r["_state"])
        rev = round(float(r["revenue"]), 2)
        ords = int(r["orders"])
        custs = int(r["customers"])
        aov = float(r["aov"])
        reg_name = str(r["region"])

        states_list.append({
            "state": st_name,
            "region": reg_name,
            "revenue": rev,
            "orders": ords,
            "customers": custs,
            "aov": aov,
            "rev_share": float(r["rev_share"]),
            "profit": round(float(r["profit"]), 2) if has_profit else None
        })

        # Resolve geographic coordinates via multi-level fallback (state -> region -> country)
        geo = lookup_coordinates(st_name) or lookup_coordinates(reg_name)
        if geo:
            map_points.append({
                "name": st_name,
                "code": geo["code"],
                "lat": geo["lat"],
                "lng": geo["lng"],
                "region": reg_name,
                "revenue": rev,
                "orders": ords,
                "customers": custs,
                "aov": aov
            })

    # If state mapping yielded 0 points, map at regional territory level
    if len(map_points) == 0 and len(regions_list) > 0:
        for r in regions_list:
            geo = lookup_coordinates(r["region"])
            if geo:
                map_points.append({
                    "name": r["region"],
                    "code": geo["code"],
                    "lat": geo["lat"],
                    "lng": geo["lng"],
                    "region": r["region"],
                    "revenue": r["revenue"],
                    "orders": r["orders"],
                    "customers": r["customers"],
                    "aov": r["aov"]
                })

    # 3. Top Cities (Top 15)
    city_df = df.groupby(["_city", "_state", "_region"]).agg(
        revenue=("_sales", "sum"),
        orders=("_order_id", "nunique")
    ).reset_index().sort_values(by="revenue", ascending=False).head(15)

    cities_list = []
    for _, r in city_df.iterrows():
        cities_list.append({
            "city": str(r["_city"]),
            "state": str(r["_state"]),
            "region": str(r["_region"]),
            "revenue": round(float(r["revenue"]), 2),
            "orders": int(r["orders"]),
            "aov": round(float(r["revenue"]) / max(int(r["orders"]), 1), 2)
        })

    # 4. Regional Growth Comparison (Quarterly / Monthly trends by Region)
    regional_growth = {"labels": [], "datasets": []}
    if pd.api.types.is_datetime64_any_dtype(df["_order_date"]):
        reg_time_df = df.groupby([
            df["_order_date"].dt.to_period("Q").astype(str),
            "_region"
        ])["_sales"].sum().unstack(fill_value=0)

        regional_growth["labels"] = reg_time_df.index.tolist()
        for region_name in reg_time_df.columns:
            regional_growth["datasets"].append({
                "region": str(region_name),
                "revenue": reg_time_df[region_name].round(2).tolist()
            })

    top_region = regions_list[0] if regions_list else None

    return {
        "summary": {
            "total_regions": len(regions_list),
            "total_states": len(states_list),
            "total_cities": len(city_df),
            "top_region_name": top_region["region"] if top_region else "N/A",
            "top_region_revenue": top_region["revenue"] if top_region else 0,
            "top_region_share": top_region["rev_share"] if top_region else 0
        },
        "regions": regions_list,
        "states": states_list,
        "cities": cities_list,
        "regional_growth": regional_growth,
        "map_points": map_points
    }
