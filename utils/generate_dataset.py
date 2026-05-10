"""
SmartCart AI - Dataset Generator
Generates synthetic e-commerce data: 10,000+ products, 5,000+ users, interactions
"""

import pandas as pd
import numpy as np
from faker import Faker
import random
import os
from datetime import datetime, timedelta

fake = Faker()
np.random.seed(42)
random.seed(42)

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
NUM_PRODUCTS = 10500
NUM_USERS = 5200
NUM_INTERACTIONS = 150000

CATEGORIES = {
    "Electronics": ["Smartphone", "Laptop", "Tablet", "Smartwatch", "Earbuds", "Camera",
                    "TV", "Speaker", "Router", "Power Bank", "SSD", "GPU"],
    "Fashion": ["T-Shirt", "Jeans", "Dress", "Jacket", "Sneakers", "Handbag",
                "Watch", "Sunglasses", "Belt", "Scarf"],
    "Home & Kitchen": ["Blender", "Air Fryer", "Coffee Maker", "Pressure Cooker",
                       "Vacuum Cleaner", "Iron", "Mixer", "Toaster", "Microwave"],
    "Books": ["Fiction Novel", "Self Help Book", "Textbook", "Biography",
              "Children's Book", "Science Book", "History Book"],
    "Sports": ["Yoga Mat", "Dumbbells", "Running Shoes", "Cycling Helmet",
               "Cricket Bat", "Football", "Tennis Racket", "Gym Gloves"],
    "Beauty": ["Face Cream", "Shampoo", "Perfume", "Lipstick",
               "Sunscreen", "Serum", "Foundation", "Mascara"],
    "Toys": ["LEGO Set", "Action Figure", "Board Game", "Puzzle",
             "Remote Control Car", "Doll", "Building Blocks"],
    "Grocery": ["Protein Bar", "Green Tea", "Olive Oil", "Honey",
                "Nuts Mix", "Quinoa", "Chia Seeds"],
    "Automotive": ["Car Cover", "Dash Cam", "Car Vacuum", "Seat Cover",
                   "Jump Starter", "Tyre Inflator"],
    "Health": ["Pulse Oximeter", "Blood Pressure Monitor", "Thermometer",
               "Multivitamin", "Resistance Band", "Foam Roller"]
}

BRANDS = {
    "Electronics": ["Samsung", "Apple", "Sony", "LG", "OnePlus", "Xiaomi", "Dell", "HP", "Asus", "Bose"],
    "Fashion": ["Nike", "Adidas", "Zara", "H&M", "Levi's", "Puma", "Reebok", "Tommy Hilfiger"],
    "Home & Kitchen": ["Philips", "Bajaj", "Prestige", "Pigeon", "Bosch", "Inalsa", "Kent"],
    "Books": ["Penguin", "HarperCollins", "Random House", "Oxford", "Scholastic"],
    "Sports": ["Nike", "Adidas", "Puma", "Decathlon", "MRF", "Vector X"],
    "Beauty": ["Lakme", "L'Oreal", "Dove", "Garnier", "Maybelline", "Biotique"],
    "Toys": ["LEGO", "Hasbro", "Mattel", "Fisher-Price", "Funskool"],
    "Grocery": ["Organic India", "Nestle", "Patanjali", "Tata", "Britannia"],
    "Automotive": ["3M", "Michelin", "Bosch", "Philips", "Stanley"],
    "Health": ["Dr. Trust", "Omron", "HealthSense", "Healthkart", "Optimum Nutrition"]
}

PRICE_RANGES = {
    "Electronics": (999, 199999),
    "Fashion": (299, 29999),
    "Home & Kitchen": (499, 49999),
    "Books": (99, 2999),
    "Sports": (299, 19999),
    "Beauty": (99, 4999),
    "Toys": (199, 9999),
    "Grocery": (99, 1999),
    "Automotive": (299, 14999),
    "Health": (299, 9999)
}

INTERACTION_TYPES = ["view", "click", "add_to_cart", "wishlist", "purchase"]
INTERACTION_WEIGHTS = [0.40, 0.25, 0.18, 0.10, 0.07]

IMAGE_BASE = "https://picsum.photos/seed/{}/400/400"


def generate_products():
    """Generate 10,500 products across all categories."""
    print("Generating products...")
    products = []
    pid = 1

    for category, items in CATEGORIES.items():
        brands = BRANDS[category]
        pmin, pmax = PRICE_RANGES[category]
        per_item = NUM_PRODUCTS // sum(len(v) for v in CATEGORIES.values())

        for item in items:
            count = per_item + random.randint(0, 5)
            for _ in range(count):
                brand = random.choice(brands)
                variant = fake.word().capitalize()
                name = f"{brand} {item} {variant}"
                price = round(random.uniform(pmin, pmax), 2)
                mrp = round(price * random.uniform(1.1, 1.5), 2)
                discount = round((mrp - price) / mrp * 100, 1)
                rating = round(random.gauss(4.0, 0.7), 1)
                rating = max(1.0, min(5.0, rating))
                reviews = random.randint(5, 15000)

                products.append({
                    "product_id": f"P{pid:06d}",
                    "product_name": name,
                    "category": category,
                    "subcategory": item,
                    "brand": brand,
                    "price": price,
                    "mrp": mrp,
                    "discount_percent": discount,
                    "description": (f"Premium quality {item} by {brand}. "
                                    f"Features advanced technology and durable build. "
                                    f"Perfect for everyday use. "
                                    f"{fake.sentence(nb_words=8)}"),
                    "rating": rating,
                    "num_reviews": reviews,
                    "image_url": IMAGE_BASE.format(pid),
                    "stock": random.randint(0, 500),
                    "is_featured": random.random() < 0.05,
                    "tags": ", ".join(random.sample(
                        [item.lower(), brand.lower(), category.lower(),
                         "bestseller", "trending", "new arrival", "sale"],
                        k=random.randint(2, 4)
                    ))
                })
                pid += 1
                if pid > NUM_PRODUCTS:
                    break
            if pid > NUM_PRODUCTS:
                break
        if pid > NUM_PRODUCTS:
            break

    df = pd.DataFrame(products)
    print(f"  ✓ {len(df)} products generated")
    return df


def generate_users():
    """Generate 5,200 users with profiles."""
    print("Generating users...")
    users = []
    for i in range(1, NUM_USERS + 1):
        age = random.randint(18, 65)
        users.append({
            "user_id": f"U{i:05d}",
            "username": fake.user_name() + str(random.randint(10, 99)),
            "email": fake.email(),
            "password_hash": "pbkdf2:sha256:" + fake.sha256(),
            "full_name": fake.name(),
            "age": age,
            "gender": random.choice(["Male", "Female", "Other"]),
            "city": fake.city(),
            "state": fake.state(),
            "preferred_categories": ", ".join(
                random.sample(list(CATEGORIES.keys()), k=random.randint(1, 4))
            ),
            "signup_date": fake.date_between(start_date="-3y", end_date="today").isoformat(),
            "is_admin": i <= 3,  # first 3 users are admins
            "is_active": random.random() > 0.05
        })

    df = pd.DataFrame(users)
    print(f"  ✓ {len(df)} users generated")
    return df


def generate_interactions(products_df, users_df):
    """Generate 150,000 realistic user-product interactions."""
    print("Generating interactions...")

    product_ids = products_df["product_id"].tolist()
    user_ids = users_df["user_id"].tolist()

    # Give some products more popularity (power law)
    product_weights = np.random.power(0.3, len(product_ids))
    product_weights /= product_weights.sum()

    interactions = []
    start_date = datetime.now() - timedelta(days=365)

    for i in range(NUM_INTERACTIONS):
        uid = random.choice(user_ids)
        pid = np.random.choice(product_ids, p=product_weights)
        interaction = np.random.choice(INTERACTION_TYPES, p=INTERACTION_WEIGHTS)
        ts = start_date + timedelta(
            days=random.randint(0, 365),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        interactions.append({
            "interaction_id": f"I{i+1:07d}",
            "user_id": uid,
            "product_id": pid,
            "interaction": interaction,
            "timestamp": ts.isoformat(),
            "session_id": fake.uuid4()[:8],
            "device": random.choice(["mobile", "desktop", "tablet"]),
            "rating_given": round(random.uniform(1, 5), 1) if interaction == "purchase" else None
        })

    df = pd.DataFrame(interactions)
    df = df.drop_duplicates(subset=["user_id", "product_id", "interaction"])
    print(f"  ✓ {len(df)} interactions generated")
    return df


def save_datasets(products_df, users_df, interactions_df):
    """Save all datasets to /data folder."""
    os.makedirs("data", exist_ok=True)
    products_df.to_csv("data/products.csv", index=False)
    users_df.to_csv("data/users.csv", index=False)
    interactions_df.to_csv("data/interactions.csv", index=False)
    print("  ✓ All datasets saved to /data")


if __name__ == "__main__":
    print("=" * 50)
    print("SmartCart AI – Dataset Generator")
    print("=" * 50)
    products = generate_products()
    users = generate_users()
    interactions = generate_interactions(products, users)
    save_datasets(products, users, interactions)
    print("\nDataset generation complete!")
    print(f"  Products : {len(products):,}")
    print(f"  Users    : {len(users):,}")
    print(f"  Interactions: {len(interactions):,}")
