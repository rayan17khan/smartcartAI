import pandas as pd
import random
from datetime import datetime, timedelta

# -----------------------------
# GENERATE USERS
# -----------------------------
users = []

categories = [
    "Electronics",
    "Fashion",
    "Books",
    "Sports",
    "Beauty",
    "Grocery"
]

cities = [
    "Bangalore",
    "Mumbai",
    "Delhi",
    "Pune",
    "Hyderabad"
]

for i in range(1, 101):
    users.append({
        "user_id": f"U{i:05d}",
        "username": f"user{i}",
        "email": f"user{i}@gmail.com",
        "preferred_categories": random.choice(categories),
        "city": random.choice(cities)
    })

users_df = pd.DataFrame(users)
users_df.to_csv("data/users.csv", index=False)

print("users.csv generated!")

# -----------------------------
# GENERATE INTERACTIONS
# -----------------------------
products = pd.read_csv("data/products.csv")

interaction_types = [
    "view",
    "click",
    "wishlist",
    "add_to_cart",
    "purchase"
]

interactions = []

for _ in range(5000):

    user = random.choice(users)
    product = products.sample(1).iloc[0]

    interactions.append({
        "user_id": user["user_id"],
        "product_id": product["product_id"],
        "interaction": random.choice(interaction_types),
        "timestamp": datetime.now() - timedelta(days=random.randint(0, 30))
    })

interactions_df = pd.DataFrame(interactions)
interactions_df.to_csv("data/interactions.csv", index=False)

print("interactions.csv generated!")