"""
SmartCart AI — ML Debug Script
Run: python debug_ml.py
"""
import sys
sys.path.insert(0, '.')
from backend.recommender import get_recommender

r = get_recommender()

# ── Test with a qualified user ────────────────────────────────────────────
uid = 'U00019'

# Get recommendations
recs = r.recommend(uid, n=10)
print(f"\nRecommendations for {uid}: {len(recs)} items")
for rec in recs[:3]:
    print(f"  keys: {list(rec.keys())}")
    print(f"  product_id field: {rec.get('product_id', 'NOT FOUND')}")
    break

# Check purchases in CSV
interactions = r.loader.interactions
purchases = interactions[
    (interactions['user_id'] == uid) &
    (interactions['interaction'].isin(['purchase', 'add_to_cart']))
]
print(f"\nPurchases in CSV for {uid}: {len(purchases)}")
print("Sample product_ids:", purchases['product_id'].tolist()[:5])

# ── Check if product_ids match between recs and purchases ─────────────────
if recs:
    rec_ids  = set(r.get('product_id', '') for r in recs)
    purch_ids = set(purchases['product_id'].tolist())
    hits = rec_ids & purch_ids
    print(f"\nRec product_ids sample:      {list(rec_ids)[:3]}")
    print(f"Purchase product_ids sample: {list(purch_ids)[:3]}")
    print(f"Matching hits: {len(hits)}")

    if not hits:
        print("\n❌ NO MATCHES — product_id format is different!")
        print("Rec format:      ", list(rec_ids)[:2])
        print("Purchase format: ", list(purch_ids)[:2])
    else:
        print("\n✅ IDs match! Evaluator should work.")

# ── Check qualified users count ───────────────────────────────────────────
all_purchases = interactions[
    interactions['interaction'].isin(['purchase', 'add_to_cart'])
]
counts     = all_purchases.groupby('user_id').size()
qualified  = counts[counts >= 10]
print(f"\nQualified users (10+ purchases): {len(qualified)}")
print("Sample:", qualified.head().to_string())