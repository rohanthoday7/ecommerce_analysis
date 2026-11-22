"""
Enterprise E-commerce Dataset Generator
Generates realistic multi-year transactional data with genuine statistical patterns:
- Multi-tier customer purchasing frequency (1x buyers, loyalists, VIP champions)
- Seasonal variations (Q4 holiday surge, July summer sale)
- Realistic price, discount, cost, and profit margins
- Geographic distribution across US regions and states
- Multi-category product hierarchy
"""

import os
import random
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

def generate_ecommerce_dataset(output_path: str = "data/sample_ecommerce.csv", n_orders: int = 6500, seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)

    # Categories and product catalog
    catalog = [
        # Technology
        {"id": "TEC-PH-101", "name": "Nexus Pro 5G Smartphone", "category": "Technology", "sub_category": "Phones", "unit_price": 899.99, "margin": 0.32},
        {"id": "TEC-PH-102", "name": "Aero Lite Smartphone 128GB", "category": "Technology", "sub_category": "Phones", "unit_price": 549.99, "margin": 0.28},
        {"id": "TEC-LT-201", "name": "PrecisionBlade 15 Ultra Laptop", "category": "Technology", "sub_category": "Laptops", "unit_price": 1499.00, "margin": 0.25},
        {"id": "TEC-LT-202", "name": "CloudBook Air 13-inch", "category": "Technology", "sub_category": "Laptops", "unit_price": 999.00, "margin": 0.27},
        {"id": "TEC-MN-301", "name": "UltraView 34-inch Curved 4K Monitor", "category": "Technology", "sub_category": "Monitors", "unit_price": 649.50, "margin": 0.35},
        {"id": "TEC-MN-302", "name": "ColorMatch 27-inch Pro Monitor", "category": "Technology", "sub_category": "Monitors", "unit_price": 429.00, "margin": 0.30},
        {"id": "TEC-AU-401", "name": "SonicPulse ANC Wireless Headphones", "category": "Technology", "sub_category": "Audio", "unit_price": 279.99, "margin": 0.45},
        {"id": "TEC-AU-402", "name": "TrueAir Pro Studio Earbuds", "category": "Technology", "sub_category": "Audio", "unit_price": 159.00, "margin": 0.48},
        {"id": "TEC-AC-501", "name": "ErgoMaster Wireless Mechanical Keyboard", "category": "Technology", "sub_category": "Accessories", "unit_price": 129.99, "margin": 0.52},
        {"id": "TEC-AC-502", "name": "PrecisionFlow Ergonomic Laser Mouse", "category": "Technology", "sub_category": "Accessories", "unit_price": 79.99, "margin": 0.55},
        {"id": "TEC-AC-503", "name": "HyperDock Thunderbolt 4 Docking Hub", "category": "Technology", "sub_category": "Accessories", "unit_price": 219.00, "margin": 0.40},

        # Furniture
        {"id": "FUR-CH-101", "name": "AeroMesh Ergonomic Executive Chair", "category": "Furniture", "sub_category": "Chairs", "unit_price": 389.00, "margin": 0.38},
        {"id": "FUR-CH-102", "name": "Vanguard High-Back Leather Chair", "category": "Furniture", "sub_category": "Chairs", "unit_price": 520.00, "margin": 0.35},
        {"id": "FUR-DK-201", "name": "ApexLift Dual-Motor Standing Desk (60x30)", "category": "Furniture", "sub_category": "Desks", "unit_price": 680.00, "margin": 0.30},
        {"id": "FUR-DK-202", "name": "Nordic Solid Oak Minimalist Desk", "category": "Furniture", "sub_category": "Desks", "unit_price": 450.00, "margin": 0.34},
        {"id": "FUR-ST-301", "name": "ModuStack 5-Tier Industrial Bookcase", "category": "Furniture", "sub_category": "Storage", "unit_price": 249.99, "margin": 0.42},
        {"id": "FUR-ST-302", "name": "SteelCraft 3-Drawer Locking File Cabinet", "category": "Furniture", "sub_category": "Storage", "unit_price": 185.00, "margin": 0.40},
        {"id": "FUR-LT-401", "name": "Lumina Balance LED Architect Desk Lamp", "category": "Furniture", "sub_category": "Lighting", "unit_price": 89.99, "margin": 0.58},

        # Office Supplies
        {"id": "OFF-PR-101", "name": "Ecolux Premium Multipurpose Paper 24lb (5 Reams)", "category": "Office Supplies", "sub_category": "Paper", "unit_price": 42.50, "margin": 0.22},
        {"id": "OFF-PR-102", "name": "Archival Heavyweight Cardstock Pack", "category": "Office Supplies", "sub_category": "Paper", "unit_price": 24.99, "margin": 0.35},
        {"id": "OFF-IN-201", "name": "LaserJet Pro High-Yield Black Toner Cartridge", "category": "Office Supplies", "sub_category": "Ink & Toner", "unit_price": 115.00, "margin": 0.46},
        {"id": "OFF-IN-202", "name": "ColorMax 4-Pack CMYK Pigment Ink Set", "category": "Office Supplies", "sub_category": "Ink & Toner", "unit_price": 88.00, "margin": 0.44},
        {"id": "OFF-OR-301", "name": "Mesh Metal Desk Organizer Set (6-Piece)", "category": "Office Supplies", "sub_category": "Desk Organizers", "unit_price": 36.99, "margin": 0.60},
        {"id": "OFF-OR-302", "name": "Modular Cable Management Spine & Tray", "category": "Office Supplies", "sub_category": "Desk Organizers", "unit_price": 49.50, "margin": 0.55},
        {"id": "OFF-WR-401", "name": "Signet Gel Precision Roller Pens (12-Pack)", "category": "Office Supplies", "sub_category": "Writing", "unit_price": 18.99, "margin": 0.65},

        # Apparel
        {"id": "APP-HD-101", "name": "CoreLoop Organic French Terry Hoodie", "category": "Apparel", "sub_category": "Tops", "unit_price": 85.00, "margin": 0.62},
        {"id": "APP-TS-102", "name": "Pima Cotton Performance Crew Tee (3-Pack)", "category": "Apparel", "sub_category": "Tops", "unit_price": 54.00, "margin": 0.65},
        {"id": "APP-JK-201", "name": "StormShield All-Weather Commuter Jacket", "category": "Apparel", "sub_category": "Outerwear", "unit_price": 195.00, "margin": 0.55},
        {"id": "APP-PT-301", "name": "Apex Kinetic Flex Chino Pants", "category": "Apparel", "sub_category": "Bottoms", "unit_price": 98.00, "margin": 0.58},
        {"id": "APP-AC-401", "name": "Merino Wool Thermal Ribbed Beanie", "category": "Apparel", "sub_category": "Accessories", "unit_price": 34.00, "margin": 0.70},
        {"id": "APP-BG-501", "name": "Transit Weatherproof Tech Backpack 26L", "category": "Apparel", "sub_category": "Bags", "unit_price": 145.00, "margin": 0.52},

        # Home & Kitchen
        {"id": "HOM-CF-101", "name": "BaristaPro Precision Espresso Machine", "category": "Home & Kitchen", "sub_category": "Coffee", "unit_price": 699.99, "margin": 0.36},
        {"id": "HOM-CF-102", "name": "AeroGrind Conical Burr Coffee Grinder", "category": "Home & Kitchen", "sub_category": "Coffee", "unit_price": 149.00, "margin": 0.42},
        {"id": "HOM-CK-201", "name": "ProClad 5-Ply Stainless Steel Cookware Set (10-Pc)", "category": "Home & Kitchen", "sub_category": "Cookware", "unit_price": 499.00, "margin": 0.45},
        {"id": "HOM-CK-202", "name": "IronCraft Enameled Cast Iron Dutch Oven 6-Qt", "category": "Home & Kitchen", "sub_category": "Cookware", "unit_price": 129.50, "margin": 0.50},
        {"id": "HOM-AP-301", "name": "PureBreeze HEPA Smart Air Purifier Pro", "category": "Home & Kitchen", "sub_category": "Appliances", "unit_price": 249.00, "margin": 0.40},
        {"id": "HOM-AP-302", "name": "HydroSmart Temperature Controlled Glass Kettle", "category": "Home & Kitchen", "sub_category": "Appliances", "unit_price": 89.99, "margin": 0.52},
    ]

    # Geographies
    regions = {
        "West": [
            ("California", "San Francisco", 94105),
            ("California", "Los Angeles", 90012),
            ("California", "San Diego", 92101),
            ("Washington", "Seattle", 98101),
            ("Washington", "Bellevue", 98004),
            ("Oregon", "Portland", 97201),
            ("Colorado", "Denver", 80202),
            ("Arizona", "Phoenix", 85001),
            ("Nevada", "Las Vegas", 89101),
        ],
        "East": [
            ("New York", "New York", "10001"),
            ("New York", "Brooklyn", "11201"),
            ("Massachusetts", "Boston", "02108"),
            ("Pennsylvania", "Philadelphia", "19102"),
            ("Pennsylvania", "Pittsburgh", "15222"),
            ("New Jersey", "Jersey City", "07302"),
            ("District of Columbia", "Washington", "20001"),
        ],
        "Central": [
            ("Illinois", "Chicago", 60601),
            ("Texas", "Austin", 78701),
            ("Texas", "Houston", 77002),
            ("Texas", "Dallas", 75201),
            ("Ohio", "Columbus", 43215),
            ("Michigan", "Detroit", 48226),
            ("Minnesota", "Minneapolis", 55401),
            ("Missouri", "St. Louis", 63101),
        ],
        "South": [
            ("Florida", "Miami", 33101),
            ("Florida", "Orlando", 32801),
            ("Georgia", "Atlanta", 30303),
            ("North Carolina", "Charlotte", 28202),
            ("North Carolina", "Raleigh", 27601),
            ("Tennessee", "Nashville", 37201),
            ("Virginia", "Richmond", 23219),
        ],
    }

    first_names = [
        "Emma", "Liam", "Olivia", "Noah", "Ava", "Oliver", "Sophia", "Elijah", "Isabella", "James",
        "Mia", "William", "Harper", "Benjamin", "Evelyn", "Lucas", "Charlotte", "Henry", "Amelia", "Alexander",
        "Abigail", "Mason", "Emily", "Michael", "Elizabeth", "Ethan", "Mila", "Daniel", "Ella", "Jacob",
        "Avery", "Logan", "Sofia", "Jackson", "Camila", "Levi", "Aria", "Sebastian", "Scarlett", "Mateo",
        "David", "Joseph", "Samuel", "John", "David", "Carter", "Wyatt", "Jayden", "Dylan", "Luke"
    ]
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
        "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
        "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
        "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores"
    ]

    segments = ["Consumer", "Corporate", "Home Office"]
    segment_weights = [0.52, 0.31, 0.17]

    payment_methods = ["Credit Card", "PayPal", "Apple Pay", "Bank Transfer", "Buy Now Pay Later"]
    payment_weights = [0.46, 0.24, 0.18, 0.05, 0.07]

    shipping_modes = ["Standard Class", "Second Class", "First Class", "Same Day"]
    shipping_weights = [0.60, 0.20, 0.15, 0.05]

    # Pre-generate a pool of 1,200 unique customers with assigned traits
    num_customers = 1250
    customer_pool = []
    
    # 15% VIP High Frequency/Value, 35% Moderate Repeaters, 50% One-time or rare buyers
    customer_tiers = (
        ["VIP"] * int(num_customers * 0.15) +
        ["Regular"] * int(num_customers * 0.35) +
        ["Occasional"] * (num_customers - int(num_customers * 0.15) - int(num_customers * 0.35))
    )
    random.shuffle(customer_tiers)

    for i in range(num_customers):
        c_id = f"CUST-{10001 + i}"
        c_name = f"{random.choice(first_names)} {random.choice(last_names)}"
        c_seg = random.choices(segments, weights=segment_weights)[0]
        c_reg = random.choices(list(regions.keys()), weights=[0.33, 0.29, 0.22, 0.16])[0]
        loc = random.choice(regions[c_reg])
        tier = customer_tiers[i]
        
        # Acquisition date (when did they first join?)
        join_days_ago = random.randint(15, 1090)
        customer_pool.append({
            "id": c_id,
            "name": c_name,
            "segment": c_seg,
            "region": c_reg,
            "state": loc[0],
            "city": loc[1],
            "postal_code": loc[2],
            "tier": tier,
            "join_days_ago": join_days_ago
        })

    # Timeline bounds: 2022-01-01 to 2024-12-31 (1095 days)
    start_date = datetime(2022, 1, 1)
    
    # Weight customers by their tier
    customer_selection_weights = []
    for c in customer_pool:
        if c["tier"] == "VIP":
            customer_selection_weights.append(8.0)
        elif c["tier"] == "Regular":
            customer_selection_weights.append(3.0)
        else:
            customer_selection_weights.append(1.0)
    
    # Normalize weights
    weight_sum = sum(customer_selection_weights)
    customer_selection_weights = [w / weight_sum for w in customer_selection_weights]

    records = []
    order_counter = 10001

    for _ in range(n_orders):
        cust = random.choices(customer_pool, weights=customer_selection_weights)[0]
        
        # Order date must be on or after join date
        days_offset = random.randint(1095 - cust["join_days_ago"], 1095)
        current_date = start_date + timedelta(days=days_offset)
        
        # Incorporate Seasonality:
        # Boost Q4 (November & December holiday season), slight boost in July (Summer Sale)
        month = current_date.month
        day_of_week = current_date.weekday() # 0 = Monday, 6 = Sunday
        
        # Random rejection sampling for seasonal distribution
        keep_prob = 1.0
        if month in [11, 12]:
            keep_prob = 1.6  # 60% boost in Q4
        elif month in [7, 8]:
            keep_prob = 1.25 # 25% boost mid-year
        elif month in [1, 2]:
            keep_prob = 0.85 # Post-holiday dip
            
        # Day of week weighting: higher Mon-Thu
        if day_of_week in [0, 1, 2]: # Mon, Tue, Wed
            keep_prob *= 1.15
        elif day_of_week in [5, 6]: # Sat, Sun
            keep_prob *= 0.90

        if random.random() > (keep_prob / 1.8):
            # Slightly adjust date forward to higher activity period
            if month in [1, 2] and random.random() < 0.3:
                current_date += timedelta(days=random.randint(60, 120))

        # Products per order: 1 to 4 line items
        num_items = random.choices([1, 2, 3, 4], weights=[0.65, 0.23, 0.09, 0.03])[0]
        order_id = f"ORD-{current_date.year}-{order_counter}"
        order_counter += 1
        
        pay_method = random.choices(payment_methods, weights=payment_weights)[0]
        ship_mode = random.choices(shipping_modes, weights=shipping_weights)[0]

        selected_prods = random.sample(catalog, num_items)
        for item in selected_prods:
            # Quantity
            if item["category"] == "Office Supplies":
                qty = random.choices([1, 2, 3, 5, 10], weights=[0.40, 0.30, 0.15, 0.10, 0.05])[0]
            elif item["category"] == "Technology" and item["unit_price"] > 500:
                qty = random.choices([1, 2], weights=[0.92, 0.08])[0]
            elif item["category"] == "Apparel":
                qty = random.choices([1, 2, 3, 4], weights=[0.55, 0.30, 0.10, 0.05])[0]
            else:
                qty = random.choices([1, 2, 3], weights=[0.70, 0.22, 0.08])[0]

            # Realistic Discount structure (occasional promo)
            has_discount = random.random() < 0.28
            if has_discount:
                discount = round(random.choice([0.05, 0.10, 0.15, 0.20, 0.25, 0.30]), 2)
            else:
                discount = 0.0

            unit_price = item["unit_price"]
            gross_amount = round(qty * unit_price, 2)
            sales = round(gross_amount * (1.0 - discount), 2)
            
            # Cost calculation based on item's base margin + random supplier variation
            cost_ratio = 1.0 - item["margin"] + random.uniform(-0.04, 0.04)
            unit_cost = round(unit_price * max(cost_ratio, 0.20), 2)
            total_cost = round(qty * unit_cost, 2)
            
            # Profit = Sales - Total Cost
            profit = round(sales - total_cost, 2)

            # Shipping Days based on Shipping Mode
            ship_days = 5 if ship_mode == "Standard Class" else (3 if ship_mode == "Second Class" else (1 if ship_mode == "First Class" else 0))
            ship_date = current_date + timedelta(days=ship_days)

            records.append({
                "Order ID": order_id,
                "Order Date": current_date.strftime("%Y-%m-%d"),
                "Ship Date": ship_date.strftime("%Y-%m-%d"),
                "Ship Mode": ship_mode,
                "Customer ID": cust["id"],
                "Customer Name": cust["name"],
                "Segment": cust["segment"],
                "Region": cust["region"],
                "State": cust["state"],
                "City": cust["city"],
                "Postal Code": cust["postal_code"],
                "Product ID": item["id"],
                "Product Name": item["name"],
                "Category": item["category"],
                "Sub-Category": item["sub_category"],
                "Unit Price": unit_price,
                "Quantity": qty,
                "Discount": discount,
                "Sales": sales,
                "Unit Cost": unit_cost,
                "Profit": profit,
                "Payment Method": pay_method,
            })

    df = pd.DataFrame(records)
    # Sort chronologically by Order Date
    df = df.sort_values(by=["Order Date", "Order ID"]).reset_index(drop=True)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Generated enterprise dataset: {output_path} with {len(df)} records across {df['Order ID'].nunique()} orders.")
    print(f"Total Revenue: ${df['Sales'].sum():,.2f} | Total Profit: ${df['Profit'].sum():,.2f} | Unique Customers: {df['Customer ID'].nunique()}")
    return df

if __name__ == "__main__":
    generate_ecommerce_dataset()
