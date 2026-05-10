"""
SmartCart AI – Data Preprocessing Utility
==========================================
Standalone script to clean, validate and feature-engineer
the raw CSV datasets before model training.

Usage:
    python utils/preprocess.py
"""

import os, sys
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


def preprocess_products(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and feature-engineer the products dataframe."""
    print("  Preprocessing products …")

    # ── Missing values ─────────────────────────────────────────
    df["description"]      = df["description"].fillna("No description available")
    df["brand"]            = df["brand"].fillna("Generic")
    df["rating"]           = df["rating"].fillna(df["rating"].median())
    df["num_reviews"]      = df["num_reviews"].fillna(0).astype(int)
    df["discount_percent"] = df["discount_percent"].fillna(0)
    df["stock"]            = df["stock"].fillna(50).astype(int)
    df["tags"]             = df["tags"].fillna("")
    df["is_featured"]      = df["is_featured"].fillna(False)

    # ── Duplicates ─────────────────────────────────────────────
    before = len(df)
    df.drop_duplicates(subset="product_id", inplace=True)
    print(f"    Duplicate products removed: {before - len(df)}")

    # ── Clip outliers ─────────────────────────────────────────
    df["price"]  = df["price"].clip(lower=1, upper=500000)
    df["rating"] = df["rating"].clip(1.0, 5.0)
    df["discount_percent"] = df["discount_percent"].clip(0, 95)

    # ── Encode categoricals ───────────────────────────────────
    le_cat = LabelEncoder()
    le_sub = LabelEncoder()
    df["category_enc"]    = le_cat.fit_transform(df["category"].astype(str))
    df["subcategory_enc"] = le_sub.fit_transform(df.get("subcategory", df["category"]).astype(str))

    # ── Normalise numerics ────────────────────────────────────
    scaler = MinMaxScaler()
    num_cols = ["price", "rating", "discount_percent", "num_reviews"]
    norm_vals = scaler.fit_transform(df[num_cols].fillna(0))
    df[["price_norm","rating_norm","discount_norm","reviews_norm"]] = norm_vals

    # ── Feature engineering ───────────────────────────────────
    # Composite popularity score
    df["popularity_score"] = (
        0.40 * df["rating_norm"] +
        0.35 * df["reviews_norm"] +
        0.15 * df["discount_norm"] +
        0.10 * df["is_featured"].astype(float)
    )

    # Price bucket
    df["price_bucket"] = pd.cut(
        df["price"],
        bins=[0, 500, 2000, 10000, 50000, float("inf")],
        labels=["budget", "affordable", "mid-range", "premium", "luxury"]
    ).astype(str)

    # High-rated flag
    df["is_high_rated"] = (df["rating"] >= 4.0).astype(int)

    df.reset_index(drop=True, inplace=True)
    print(f"    Products after cleaning: {len(df):,}")
    return df


def preprocess_users(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the users dataframe."""
    print("  Preprocessing users …")

    df["preferred_categories"] = df["preferred_categories"].fillna("")
    df["city"]  = df["city"].fillna("Unknown")
    df["state"] = df["state"].fillna("Unknown")
    df["age"]   = df["age"].fillna(df["age"].median()).astype(int)
    df["gender"]= df["gender"].fillna("Other")

    before = len(df)
    df.drop_duplicates(subset="user_id", inplace=True)
    print(f"    Duplicate users removed: {before - len(df)}")
    print(f"    Users after cleaning: {len(df):,}")
    return df


def preprocess_interactions(df: pd.DataFrame, products_df: pd.DataFrame) -> pd.DataFrame:
    """Clean and weight the interactions dataframe."""
    print("  Preprocessing interactions …")

    # ── Drop NaN keys ─────────────────────────────────────────
    df.dropna(subset=["user_id", "product_id", "interaction"], inplace=True)

    # ── Remove interactions for unknown products ───────────────
    valid_pids = set(products_df["product_id"])
    before = len(df)
    df = df[df["product_id"].isin(valid_pids)].copy()
    print(f"    Interactions with unknown products removed: {before - len(df)}")

    # ── Duplicates ─────────────────────────────────────────────
    before = len(df)
    df.drop_duplicates(subset=["user_id", "product_id", "interaction"], inplace=True)
    print(f"    Duplicate interactions removed: {before - len(df)}")

    # ── Parse timestamps ──────────────────────────────────────
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df.dropna(subset=["timestamp"], inplace=True)

    # ── Interaction weights ────────────────────────────────────
    WEIGHT_MAP = {"view": 1, "click": 2, "wishlist": 3, "add_to_cart": 4, "purchase": 5}
    df["weight"] = df["interaction"].map(WEIGHT_MAP).fillna(1).astype(float)

    # ── Time-decay boost: last 30 days ×1.5 ──────────────────
    cutoff = datetime.now() - timedelta(days=30)
    df.loc[df["timestamp"] >= cutoff, "weight"] *= 1.5

    # ── Aggregate score per user–item pair ─────────────────────
    agg = (df.groupby(["user_id", "product_id"])["weight"]
             .sum()
             .reset_index()
             .rename(columns={"weight": "agg_score"}))
    agg["agg_score"] = agg["agg_score"].clip(upper=20)  # cap outliers

    print(f"    Interactions after cleaning: {len(df):,}")
    print(f"    Unique user–item pairs     : {len(agg):,}")

    # Merge agg score back
    df = df.merge(agg, on=["user_id", "product_id"], how="left")
    return df


def build_user_item_matrix(interactions_df: pd.DataFrame):
    """Build and return a sparse user–item interaction matrix."""
    from scipy.sparse import csr_matrix

    print("  Building user–item interaction matrix …")
    agg = (interactions_df
           .groupby(["user_id", "product_id"])["weight"]
           .sum()
           .reset_index())

    # Limit to top 3000 users and 5000 items for memory efficiency
    top_users = agg.groupby("user_id")["weight"].sum().nlargest(3000).index
    top_items = agg.groupby("product_id")["weight"].sum().nlargest(5000).index
    agg = agg[agg["user_id"].isin(top_users) & agg["product_id"].isin(top_items)]

    user_enc  = {u: i for i, u in enumerate(agg["user_id"].unique())}
    item_enc  = {p: i for i, p in enumerate(agg["product_id"].unique())}

    rows  = agg["user_id"].map(user_enc)
    cols  = agg["product_id"].map(item_enc)
    vals  = agg["weight"].astype(float)
    mat   = csr_matrix((vals, (rows, cols)), shape=(len(user_enc), len(item_enc)))

    density = mat.nnz / (mat.shape[0] * mat.shape[1])
    print(f"    Matrix shape  : {mat.shape}")
    print(f"    Non-zeros     : {mat.nnz:,}")
    print(f"    Density       : {density:.4%}")
    return mat, user_enc, item_enc


def run():
    print("\n" + "=" * 56)
    print("  SmartCart AI – Data Preprocessing Pipeline")
    print("=" * 56)

    # Load
    print("\n[1/4] Loading raw CSVs …")
    products     = pd.read_csv(os.path.join(DATA_DIR, "products.csv"))
    users        = pd.read_csv(os.path.join(DATA_DIR, "users.csv"))
    interactions = pd.read_csv(os.path.join(DATA_DIR, "interactions.csv"))
    print(f"  Loaded  products={len(products):,}  users={len(users):,}  interactions={len(interactions):,}")

    # Preprocess
    print("\n[2/4] Cleaning & engineering features …")
    products     = preprocess_products(products)
    users        = preprocess_users(users)
    interactions = preprocess_interactions(interactions, products)

    # Save preprocessed CSVs
    print("\n[3/4] Saving preprocessed CSVs …")
    products.to_csv(os.path.join(DATA_DIR, "products_preprocessed.csv"), index=False)
    users.to_csv(os.path.join(DATA_DIR, "users_preprocessed.csv"), index=False)
    interactions.to_csv(os.path.join(DATA_DIR, "interactions_preprocessed.csv"), index=False)
    print("  ✓ products_preprocessed.csv")
    print("  ✓ users_preprocessed.csv")
    print("  ✓ interactions_preprocessed.csv")

    # Build UI matrix
    print("\n[4/4] Building user–item matrix …")
    matrix, user_enc, item_enc = build_user_item_matrix(interactions)

    import pickle, os
    os.makedirs(os.path.join(BASE_DIR, "models"), exist_ok=True)
    with open(os.path.join(BASE_DIR, "models", "ui_matrix.pkl"), "wb") as f:
        pickle.dump({"matrix": matrix, "user_enc": user_enc, "item_enc": item_enc}, f)
    print("  ✓ models/ui_matrix.pkl")

    print("\n✅  Preprocessing complete!\n")


if __name__ == "__main__":
    run()
