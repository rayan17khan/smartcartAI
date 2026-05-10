import pandas as pd
import csv

df = pd.read_csv('data/products.csv')

# Realistic price ranges per subcategory (min, max) in INR
price_ranges = {
    "Smartphone":      (5000,   80000),
    "Laptop":          (25000,  150000),
    "Headphones":      (500,    30000),
    "Camera":          (8000,   120000),
    "Tablet":          (8000,   80000),
    "Smartwatch":      (1500,   40000),
    "TV":              (8000,   150000),
    "Speaker":         (500,    20000),
    "Monitor":         (8000,   60000),
    "Keyboard":        (300,    8000),
    "Mouse":           (200,    5000),
    "T-Shirt":         (199,    2999),
    "Jeans":           (499,    4999),
    "Shoes":           (499,    8000),
    "Dress":           (399,    5999),
    "Jacket":          (599,    6999),
    "Bag":             (299,    5000),
    "Watch":           (500,    15000),
    "Saree":           (299,    8000),
    "Kurta":           (299,    3999),
    "Sunglasses":      (199,    3000),
    "Skincare":        (99,     2999),
    "Makeup":          (99,     2499),
    "Perfume":         (199,    4999),
    "Haircare":        (99,     1499),
    "Lipstick":        (99,     1499),
    "Fiction":         (99,     599),
    "Non-Fiction":     (99,     699),
    "Textbook":        (199,    1499),
    "Children":        (79,     499),
    "Cricket":         (199,    8000),
    "Football":        (199,    3000),
    "Fitness":         (299,    10000),
    "Yoga":            (199,    3000),
    "Cycling":         (3000,   30000),
    "Action Figures":  (199,    2999),
    "Board Games":     (299,    2999),
    "Lego":            (499,    5999),
    "Soft Toys":       (199,    1999),
    "Snacks":          (20,     499),
    "Beverages":       (20,     299),
    "Dairy":           (20,     299),
    "Spices":          (30,     499),
    "Furniture":       (2000,   50000),
    "Kitchen":         (299,    8000),
    "Bedding":         (499,    5000),
    "Lighting":        (199,    3000),
    "Decor":           (199,    4000),
    "Supplements":     (299,    3999),
    "Medical Devices": (299,    8000),
    "Car Accessories": (99,     5000),
    "Bike Accessories":(99,     3000),
}

import random
random.seed(42)

def fix_price(row):
    subcat = str(row.get('subcategory', '')).strip()
    lo, hi = price_ranges.get(subcat, (199, 9999))
    price  = round(random.uniform(lo, hi), 2)
    mrp    = round(price * random.uniform(1.05, 1.5), 2)
    disc   = round((mrp - price) / mrp * 100, 1)
    return price, mrp, disc

prices = df.apply(fix_price, axis=1)
df['price']            = [p[0] for p in prices]
df['mrp']              = [p[1] for p in prices]
df['discount_percent'] = [p[2] for p in prices]

df.to_csv('data/products.csv', index=False, quoting=csv.QUOTE_ALL)
print(f"✅ Fixed prices for {len(df)} products!")
print(df[['product_name','subcategory','price','mrp']].head(10))