"""
SmartCart AI – Recommendation Engine
=====================================
Implements:
  1. Content-Based Filtering  (TF-IDF + cosine similarity)
  2. Collaborative Filtering  (User-based & Item-based cosine similarity)
  3. Hybrid System            (weighted blend of CF + CBF)
  4. Trending Detection       (time-decayed interaction scoring)
  5. Cold-Start Handling      (category-preference fallback)
  6. Recommendation Explanation generator
"""

import os, time, warnings
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from scipy.sparse import csr_matrix
from datetime import datetime, timedelta
import logging

# ── In-process recommendation cache ──────────────────────────────────────────
# Keyed by "rec:<user_id>:<n>", value is (monotonic_timestamp, list_of_recs)
# Call invalidate_cache(user_id) after any cart / wishlist / purchase action.
_cache: dict = {}
CACHE_TTL = 300  # seconds (5 minutes)

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR    = os.path.join(BASE_DIR, "data")
MODELS_DIR  = os.path.join(BASE_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADING & PREPROCESSING
# ─────────────────────────────────────────────────────────────────────────────
class DataLoader:
    """Loads, cleans and caches all datasets."""

    def __init__(self):
        self.products     = None
        self.users        = None
        self.interactions = None
        self._load()

    def _load(self):
        log.info("Loading datasets …")

        # ── Products ──────────────────────────────────────────────────────────
        self.products = pd.read_csv(os.path.join(DATA_DIR, "products.csv"))
        self.products.drop_duplicates(subset="product_id", inplace=True)
        self.products.fillna({
            "description": "No description available",
            "brand": "Generic",
            "rating": self.products["rating"].median(),
            "num_reviews": 0,
            "discount_percent": 0,
            "stock": 0
        }, inplace=True)
        self.products["price"]  = self.products["price"].clip(lower=1)
        self.products["rating"] = self.products["rating"].clip(1, 5)
        self.products.reset_index(drop=True, inplace=True)

        # ── Users ─────────────────────────────────────────────────────────────
        self.users = pd.read_csv(os.path.join(DATA_DIR, "users.csv"))
        self.users.drop_duplicates(subset="user_id", inplace=True)
        self.users.fillna({"preferred_categories": "", "city": "Unknown"}, inplace=True)

        # ── Interactions ─────────────────────────────────────────────────────
        self.interactions = pd.read_csv(os.path.join(DATA_DIR, "interactions.csv"))
        self.interactions.drop_duplicates(
            subset=["user_id", "product_id", "interaction"], inplace=True)
        self.interactions["timestamp"] = pd.to_datetime(
            self.interactions["timestamp"], errors="coerce")
        self.interactions.dropna(subset=["timestamp"], inplace=True)

        log.info(
            f"Loaded → products={len(self.products):,}  "
            f"users={len(self.users):,}  "
            f"interactions={len(self.interactions):,}"
        )

    # ── Interaction weights ───────────────────────────────────────────────────
    WEIGHT_MAP = {"view": 1, "click": 2, "wishlist": 3, "add_to_cart": 4, "purchase": 5}

    def interaction_scores(self) -> pd.DataFrame:
        """Return user×product implicit feedback scores (weighted interactions)."""
        df = self.interactions.copy()
        df["score"] = df["interaction"].map(self.WEIGHT_MAP).fillna(1).astype(float)
        # Time decay: interactions in last 30 days get ×1.5 boost
        cutoff = datetime.now() - timedelta(days=30)
        mask = df["timestamp"] >= cutoff
        df["score"] = df["score"].where(~mask, df["score"] * 1.5)
        agg = df.groupby(["user_id", "product_id"])["score"].sum().reset_index()
        return agg


# ─────────────────────────────────────────────────────────────────────────────
# CONTENT-BASED FILTERING
# ─────────────────────────────────────────────────────────────────────────────
class ContentBasedFilter:
    """
    Builds a TF-IDF matrix over product text features and computes
    cosine similarity for item-to-item recommendations.
    """

    def __init__(self, products: pd.DataFrame):
        self.products  = products.reset_index(drop=True)
        self.pid_index = {pid: i for i, pid in enumerate(self.products["product_id"])}
        self.sim_matrix = None
        # FIX: search vectoriser fitted once here, reused in search() — not
        # re-fitted on every call (original re-fitted per-request, O(n×vocab))
        self._search_vectoriser = None
        self._search_matrix     = None
        self._build()

    def _build(self):
        log.info("Building content-based TF-IDF model …")
        # Combine rich text features
        self.products["_text"] = (
            self.products["product_name"].fillna("") + " " +
            self.products["category"].fillna("") + " " +
            self.products["subcategory"].fillna("") + " " +
            self.products["brand"].fillna("") + " " +
            self.products["description"].fillna("") + " " +
            self.products["tags"].fillna("")
        )
        # ── Similarity matrix (for similar_items) ─────────────────────────────
        tfidf = TfidfVectorizer(
            max_features=8000,
            ngram_range=(1, 2),
            stop_words="english",
            sublinear_tf=True
        )
        tfidf_matrix = tfidf.fit_transform(self.products["_text"])

        scaler  = MinMaxScaler()
        numeric = scaler.fit_transform(
            self.products[["price", "rating", "discount_percent"]].fillna(0))
        from scipy.sparse import hstack, csr_matrix
        combined = hstack([tfidf_matrix, csr_matrix(numeric)])
        self.sim_matrix = cosine_similarity(combined, dense_output=False)

        # ── Search index — fitted ONCE, reused for every query ────────────────
        self._search_vectoriser = TfidfVectorizer(
            stop_words="english", max_features=5000,
            ngram_range=(1, 2), sublinear_tf=True
        )
        self._search_matrix = self._search_vectoriser.fit_transform(
            self.products["_text"]
        )
        log.info("Content-based model ready.")

    def similar_items(self, product_id: str, n: int = 10) -> list[dict]:
        """Return top-N similar products."""
        if product_id not in self.pid_index:
            return []
        idx  = self.pid_index[product_id]
        row  = self.sim_matrix[idx].toarray().flatten()
        row[idx] = 0  # exclude self
        top  = np.argsort(row)[::-1][:n]
        return self._format(top, scores=row[top], reason=f"Similar to this product")

    def _format(self, indices, scores, reason=""):
        rows = []
        for i, s in zip(indices, scores):
            if i < len(self.products):
                p = self.products.iloc[i].to_dict()
                p["rec_score"]  = round(float(s), 4)
                p["rec_reason"] = reason
                rows.append(p)
        return rows


# ─────────────────────────────────────────────────────────────────────────────
# COLLABORATIVE FILTERING
# ─────────────────────────────────────────────────────────────────────────────
class CollaborativeFilter:
    """
    User-based and Item-based collaborative filtering
    using cosine similarity on a sparse user-item matrix.
    """

    def __init__(self, scores_df: pd.DataFrame, products: pd.DataFrame, max_users=3000):
        self.products   = products.set_index("product_id")
        self.max_users  = max_users
        self._build(scores_df)

    def _build(self, scores_df: pd.DataFrame):
        log.info("Building collaborative filter …")
        # Keep top-N active users for memory efficiency
        active = (scores_df.groupby("user_id")["score"]
                  .count().nlargest(self.max_users).index)
        df = scores_df[scores_df["user_id"].isin(active)].copy()

        self.user_enc = {u: i for i, u in enumerate(df["user_id"].unique())}
        self.item_enc = {p: i for i, p in enumerate(df["product_id"].unique())}
        self.item_dec = {i: p for p, i in self.item_enc.items()}

        rows = df["user_id"].map(self.user_enc)
        cols = df["product_id"].map(self.item_enc)
        vals = df["score"].astype(float)
        self.matrix = csr_matrix(
            (vals, (rows, cols)),
            shape=(len(self.user_enc), len(self.item_enc))
        )
        # Item similarity (item-based CF)
        self.item_sim = cosine_similarity(self.matrix.T, dense_output=False)
        log.info("Collaborative filter ready.")

    # ── User-based recommendations ────────────────────────────────────────────
    def user_based(self, user_id: str, n: int = 12) -> list[dict]:
        if user_id not in self.user_enc:
            return []
        u_idx = self.user_enc[user_id]
        u_vec = self.matrix[u_idx]

        # Cosine similarity between this user and all others
        sims  = cosine_similarity(u_vec, self.matrix).flatten()
        sims[u_idx] = 0
        top_users = np.argsort(sims)[::-1][:30]

        # Items liked by similar users that this user hasn't interacted with
        scores_agg = {}
        seen  = set(self.matrix[u_idx].nonzero()[1])
        for peer_idx in top_users:
            peer_sim  = sims[peer_idx]
            peer_items = self.matrix[peer_idx].nonzero()[1]
            for item_idx in peer_items:
                if item_idx not in seen:
                    scores_agg[item_idx] = scores_agg.get(item_idx, 0) + peer_sim

        if not scores_agg:
            return []
        top_n = sorted(scores_agg, key=scores_agg.get, reverse=True)[:n]
        return self._format(top_n, scores_agg, reason="Recommended for you")

    # ── Item-based recommendations ────────────────────────────────────────────
    def item_based(self, product_id: str, n: int = 10) -> list[dict]:
        if product_id not in self.item_enc:
            return []
        i_idx = self.item_enc[product_id]
        row   = self.item_sim[i_idx].toarray().flatten()
        row[i_idx] = 0
        top_n = np.argsort(row)[::-1][:n]
        return self._format(top_n, dict(enumerate(row)), reason="Customers also bought")

    def _format(self, item_indices, score_map, reason=""):
        rows = []
        for idx in item_indices:
            pid = self.item_dec.get(idx)
            if pid and pid in self.products.index:
                p = self.products.loc[pid].to_dict()
                p["product_id"]  = pid
                p["rec_score"]   = round(float(score_map.get(idx, 0)), 4)
                p["rec_reason"]  = reason
                rows.append(p)
        return rows

    def get_user_history(self, user_id: str) -> list[str]:
        if user_id not in self.user_enc:
            return []
        u_idx = self.user_enc[user_id]
        cols  = self.matrix[u_idx].nonzero()[1]
        return [self.item_dec[c] for c in cols if c in self.item_dec]


# ─────────────────────────────────────────────────────────────────────────────
# HYBRID RECOMMENDER
# ─────────────────────────────────────────────────────────────────────────────
class HybridRecommender:
    """
    Blends Content-Based + Collaborative Filtering scores.
    Falls back to trending + category preferences for cold-start.
    """

    CF_WEIGHT  = 0.60
    CBF_WEIGHT = 0.40

    def __init__(self):
        self.loader  = DataLoader()
        self.cbf     = ContentBasedFilter(self.loader.products)
        scores_df    = self.loader.interaction_scores()
        self.cf      = CollaborativeFilter(scores_df, self.loader.products)
        self._precompute_trending()
        log.info("HybridRecommender ready ✓")
    

    # ── Trending ──────────────────────────────────────────────────────────────
    def _precompute_trending(self):
        df = self.loader.interactions.copy()
        cutoff = datetime.now() - timedelta(days=30)
        recent = df[df["timestamp"] >= cutoff]
        WEIGHTS = {"view":1,"click":2,"wishlist":3,"add_to_cart":4,"purchase":5}
        recent = recent.copy()
        recent["score"] = recent["interaction"].map(WEIGHTS).fillna(1)
        trend = recent.groupby("product_id")["score"].sum().reset_index()
        trend.columns = ["product_id","trend_score"]
        trend = trend.merge(
            self.loader.products[["product_id","product_name","category",
                                  "price","rating","image_url","discount_percent",
                                  "brand","num_reviews","mrp","stock","is_featured"]],
            on="product_id", how="inner"
        ).sort_values("trend_score", ascending=False)
        self.trending = trend.head(100).to_dict("records")

    # ── Main recommend entry-point ────────────────────────────────────────────
    def recommend(self, user_id: str, n: int = 20) -> list[dict]:
        """
        Full personalised recommendation pipeline:
          1. CF user-based recs
          2. CBF on user's history items
          3. Hybrid score blend
          4. Cold-start fallback if needed (APPENDS, does not replace)
        """
        # ── Cache check ───────────────────────────────────────────────────────
        cache_key = f"rec:{user_id}:{n}"
        entry = _cache.get(cache_key)
        if entry and (time.monotonic() - entry[0]) < CACHE_TTL:
            return entry[1]

        # ── CF recommendations ────────────────────────────────────────────────
        cf_recs = self.cf.user_based(user_id, n=n*2)

        # ── CBF on recently interacted items ──────────────────────────────────
        history  = self.cf.get_user_history(user_id)[:5]
        cbf_recs = []
        for pid in history:
            cbf_recs.extend(self.cbf.similar_items(pid, n=8))

        # ── Merge scores ──────────────────────────────────────────────────────
        score_map: dict[str, dict] = {}
        for r in cf_recs:
            pid = r["product_id"]
            score_map[pid] = r.copy()
            score_map[pid]["_hybrid"] = r.get("rec_score", 0) * self.CF_WEIGHT

        for r in cbf_recs:
            pid = r["product_id"]
            if pid in score_map:
                score_map[pid]["_hybrid"] += r.get("rec_score", 0) * self.CBF_WEIGHT
            else:
                score_map[pid] = r.copy()
                score_map[pid]["_hybrid"] = r.get("rec_score", 0) * self.CBF_WEIGHT

        results = sorted(score_map.values(), key=lambda x: x["_hybrid"], reverse=True)
        results = [r for r in results if r.get("stock", 1) >= 0]

        # ── Cold-start fallback — APPENDS remaining slots, does not replace ───
        # FIX: original did `results = self._cold_start(...)` which discarded
        # any partial personalised results computed above.
        if len(results) < n:
            existing  = [r["product_id"] for r in results]
            fallback  = self._cold_start(user_id, n - len(results), existing)
            results.extend(fallback)

        results = results[:n]
        _cache[cache_key] = (time.monotonic(), results)
        return results

    def _cold_start(self, user_id: str, n: int, existing: list[str]) -> list[dict]:
        """
        Multi-stage cold-start fallback — fills remaining slots only.

        Stage 1: Trending items in the user's preferred categories.
        Stage 2: Global trending (any category).
        Stage 3: Top-rated safety net.

        FIX: category names are .title()-normalised before matching so
        "electronics" == "Electronics".  Original silent-failed when casing
        differed, falling through to all-products.

        FIX: trending is now used (stages 1 & 2) so new users see what's
        popular, not a static top-rated list that never changes.
        """
        recs: list[dict] = []
        seen: set[str]   = set(existing)

        def _left() -> int:
            return max(0, n - len(recs))

        # Resolve preferred categories (normalise case)
        user_row  = self.loader.users[self.loader.users["user_id"] == user_id]
        pref_cats: list[str] = []
        if not user_row.empty:
            cats_str  = user_row.iloc[0].get("preferred_categories", "")
            pref_cats = [c.strip().title() for c in str(cats_str).split(",") if c.strip()]

        # Stage 1: trending in preferred categories
        if pref_cats and _left() > 0:
            max_score = self.trending[0].get("trend_score", 1) if self.trending else 1
            for item in self.trending:
                if _left() == 0:
                    break
                pid = item.get("product_id")
                if pid in seen:
                    continue
                if str(item.get("category", "")).title() in pref_cats:
                    d = item.copy()
                    d["rec_score"]  = round(float(item.get("trend_score", 0)) / max_score, 4)
                    d["rec_reason"] = "Trending in your favourite category"
                    recs.append(d)
                    seen.add(pid)

        # Stage 2: global trending
        if _left() > 0:
            max_score = self.trending[0].get("trend_score", 1) if self.trending else 1
            for item in self.trending:
                if _left() == 0:
                    break
                pid = item.get("product_id")
                if pid not in seen:
                    d = item.copy()
                    d["rec_score"]  = round(float(item.get("trend_score", 0)) / max_score, 4)
                    d["rec_reason"] = "Trending right now"
                    recs.append(d)
                    seen.add(pid)

        # Stage 3: top-rated safety net
        if _left() > 0:
            prod = self.loader.products.copy()
            prod["_cat_norm"] = prod["category"].str.title()
            pool = prod[prod["_cat_norm"].isin(pref_cats)] if pref_cats else prod
            if pool.empty:
                pool = prod
            pool = (pool[~pool["product_id"].isin(seen)]
                    .sort_values(["rating", "num_reviews"], ascending=False)
                    .head(_left()))
            for _, row in pool.iterrows():
                d = row.drop("_cat_norm", errors="ignore").to_dict()
                d["rec_score"]  = round(float(row["rating"]) / 5.0, 4)
                d["rec_reason"] = "Top rated in your preferred category" if pref_cats else "Top rated"
                recs.append(d)
                seen.add(row["product_id"])

        return recs[:n]

    # ── Trending ──────────────────────────────────────────────────────────────
    def get_trending(self, n: int = 20, category: str = None) -> list[dict]:
        items = self.trending
        if category:
            items = [i for i in items if i.get("category") == category]
        return items[:n]

    # ── Similar items ─────────────────────────────────────────────────────────
    def similar_items(self, product_id: str, n: int = 10) -> list[dict]:
        cbf = self.cbf.similar_items(product_id, n=n)
        cf  = self.cf.item_based(product_id, n=n)
        # Merge
        seen, merged = set(), []
        for r in cbf + cf:
            pid = r["product_id"]
            if pid not in seen:
                seen.add(pid)
                merged.append(r)
        return merged[:n]

    # ── Explanation generator ─────────────────────────────────────────────────
    def explain(self, user_id: str, product_id: str) -> str:
        history = self.cf.get_user_history(user_id)
        if not history:
            return "Recommended based on trending popularity."
        # Find the most similar item in user's history
        prod_idx = self.cbf.pid_index.get(product_id)
        best_pid, best_score = None, -1
        for pid in history[:10]:
            h_idx = self.cbf.pid_index.get(pid)
            if prod_idx is None or h_idx is None:
                continue
            score = float(self.cbf.sim_matrix[prod_idx, h_idx])
            if score > best_score:
                best_score, best_pid = score, pid
        if best_pid:
            p = self.loader.products[self.loader.products["product_id"] == best_pid]
            if not p.empty:
                name = p.iloc[0]["product_name"]
                return f"Because you interacted with: {name}"
        return "Recommended based on your activity."

    # ── Search ranking ────────────────────────────────────────────────────────
    def search(self, query: str, user_id: str = None, n: int = 30) -> list[dict]:
        """AI-ranked search: TF-IDF relevance + personalisation boost.

        FIX: uses self.cbf._search_vectoriser fitted once at startup.
        Original re-fitted a brand-new TfidfVectorizer on every single call
        (O(n × vocab) per keystroke).  Now it's a cheap transform + dot product.
        """
        products = self.loader.products.copy()

        # Use the pre-fitted vectoriser from ContentBasedFilter
        q_vec = self.cbf._search_vectoriser.transform([query])
        sims  = cosine_similarity(q_vec, self.cbf._search_matrix).flatten()
        products["search_score"] = sims

        # Personalisation boost for user's preferred categories
        if user_id:
            user_row = self.loader.users[self.loader.users["user_id"] == user_id]
            if not user_row.empty:
                cats = str(user_row.iloc[0].get("preferred_categories", "")).split(",")
                cats = [c.strip() for c in cats]
                products.loc[products["category"].isin(cats), "search_score"] *= 1.25

        products["_rank"] = (
            products["search_score"] * 0.70 +
            (products["rating"] / 5.0) * 0.20 +
            (products["num_reviews"] / products["num_reviews"].clip(lower=1).max()) * 0.10
        )
        top = products[products["search_score"] > 0.01].nlargest(n, "_rank")
        results = []
        for _, row in top.iterrows():
            d = row.drop(["_text", "search_score", "_rank"], errors="ignore").to_dict()
            d["rec_score"]  = round(row["_rank"], 4)
            d["rec_reason"] = f'Search result for "{query}"'
            results.append(d)
        return results

    # ── Products API helpers ──────────────────────────────────────────────────
    def get_products(self, category=None, min_price=None, max_price=None,
                     min_rating=None, sort="popularity", page=1, per_page=24):
        df = self.loader.products.copy()
        if category:
            df = df[df["category"] == category]
        if min_price is not None:
            df = df[df["price"] >= float(min_price)]
        if max_price is not None:
            df = df[df["price"] <= float(max_price)]
        if min_rating is not None:
            df = df[df["rating"] >= float(min_rating)]
        if sort == "price_asc":
            df = df.sort_values("price")
        elif sort == "price_desc":
            df = df.sort_values("price", ascending=False)
        elif sort == "rating":
            df = df.sort_values("rating", ascending=False)
        elif sort == "discount":
            df = df.sort_values("discount_percent", ascending=False)
        else:
            df = df.sort_values(["is_featured","rating","num_reviews"],
                                ascending=[False,False,False])
        total   = len(df)
        start   = (page - 1) * per_page
        page_df = df.iloc[start:start + per_page]
        return page_df.to_dict("records"), total

    def get_product(self, product_id: str) -> dict | None:
        row = self.loader.products[self.loader.products["product_id"] == product_id]
        if row.empty:
            return None
        return row.iloc[0].to_dict()

    # ── Analytics ─────────────────────────────────────────────────────────────
    def analytics_summary(self):
        import sqlite3, os
        from datetime import datetime, timedelta
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'smartcart.db')
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        # Total products
        total_products = len(self.products)

        # Total users
        c.execute("SELECT COUNT(*) FROM users")
        total_users = c.fetchone()[0]

        # Total interactions
        c.execute("SELECT COUNT(*) FROM user_activity")
        total_interactions = c.fetchone()[0]

        # Total purchases
        c.execute("SELECT COUNT(*) FROM orders")
        total_purchases = c.fetchone()[0]

        # Interaction breakdown by action
        c.execute("SELECT action, COUNT(*) FROM user_activity GROUP BY action")
        interaction_breakdown = {row[0]: row[1] for row in c.fetchall()}

        # Category distribution
        cat_counts = self.products.groupby('category').size().reset_index(name='count')
        category_dist = {row['category']: row['count'] for _, row in cat_counts.iterrows()}

        # Daily sales last 30 days
        c.execute("""
            SELECT date(created_at) as day, COUNT(*) as orders, COALESCE(SUM(total),0) as revenue
            FROM orders
            GROUP BY day
            ORDER BY day DESC
            LIMIT 30
        """)
        daily_sales = [
            {"date": row[0], "orders": row[1], "revenue": row[2]}
            for row in c.fetchall()
        ]

        # Top products by review count
        top_products = (
            self.products
            .sort_values('num_reviews', ascending=False)
            .head(10)
            [['product_id','product_name','category','price','rating','num_reviews']]
            .rename(columns={'product_name': 'name'})
            .to_dict('records')
        )

        # Users list
        c.execute("SELECT user_id, username, email, city, preferred_categories, is_admin, signup_date FROM users LIMIT 100")
        users = [
            {
                "user_id": row[0], "username": row[1], "email": row[2],
                "city": row[3], "preferred_categories": row[4],
                "is_admin": bool(row[5]), "signup_date": row[6]
            }
            for row in c.fetchall()
        ]

        conn.close()

        return {
            # ── Fields admin.js reads directly ──────────────────────────
            "total_products":        total_products,
            "total_users":           total_users,
            "total_interactions":    total_interactions,
            "total_purchases":       total_purchases,
            "interaction_breakdown": interaction_breakdown,
            "category_dist":         category_dist,
            "daily_sales":           daily_sales,
            "top_products":          top_products,
            "users":                 users,

            # ── Fields admin.html panel reads ────────────────────────────
            "summary": {
                "total_orders":    total_purchases,
                "total_revenue":   sum(d["revenue"] for d in daily_sales),
                "total_users":     total_users,
                "conversion_rate": round(
                    interaction_breakdown.get("purchase", 0) /
                    max(interaction_breakdown.get("view", 1), 1) * 100, 2),
                "last_updated":    datetime.now().strftime("%H:%M:%S"),
                "today_date":      datetime.now().strftime("%A, %d %B %Y"),
            },
            "funnel":    interaction_breakdown,
            "categories": [
                {"category": k, "count": v}
                for k, v in category_dist.items()
            ],
            "daily_trend": daily_sales,
        }

# ─────────────────────────────────────────────────────────────────────────────
# MODEL EVALUATION
# ─────────────────────────────────────────────────────────────────────────────
class ModelEvaluator:
    """Evaluate recommendation quality with precision, recall, F1."""

    def __init__(self, recommender: HybridRecommender):
        self.rec = recommender

    def evaluate(self, n_users: int = 100, top_n: int = 10) -> dict:
        log.info(f"Evaluating model on {n_users} users …")
        interactions = self.rec.loader.interactions
        purchases    = interactions[interactions["interaction"].isin(["purchase","add_to_cart"])]

        # Users with at least 10 interactions
        qualified = (purchases.groupby("user_id")
                     .size()[lambda x: x >= 10].index.tolist())
        if not qualified:
            return {}
        sample_users = qualified[:n_users]

        precisions, recalls, f1s = [], [], []
        for uid in sample_users:
            # Ground truth: items this user purchased
            user_items = set(purchases[purchases["user_id"] == uid]["product_id"])
            # Train/test split: hold out 20%
            test_size  = max(1, int(len(user_items) * 0.2))
            test_items = set(list(user_items)[-test_size:])
            # Get recommendations
            recs = self.rec.recommend(uid, n=top_n)
            rec_ids = {r["product_id"] for r in recs}
            # Metrics
            hits = len(rec_ids & test_items)
            p    = hits / len(rec_ids) if rec_ids else 0
            r    = hits / len(test_items) if test_items else 0
            f1   = 2 * p * r / (p + r) if (p + r) > 0 else 0
            precisions.append(p)
            recalls.append(r)
            f1s.append(f1)

        return {
            "precision" : round(np.mean(precisions), 4),
            "recall"    : round(np.mean(recalls), 4),
            "f1_score"  : round(np.mean(f1s), 4),
            "n_users"   : len(sample_users)
        }


# ─────────────────────────────────────────────────────────────────────────────
# SINGLETON – loaded once at startup
# ─────────────────────────────────────────────────────────────────────────────
_recommender: HybridRecommender | None = None

def get_recommender() -> HybridRecommender:
    global _recommender
    if _recommender is None:
        _recommender = HybridRecommender()
    return _recommender


def invalidate_cache(user_id: str = None) -> None:
    """
    Flush recommendation cache entries.

    Call this after logging any user interaction (cart, wishlist, purchase)
    so the next recommend() call re-scores instead of returning stale results.

    user_id=None  → flush the entire cache (e.g. after a model rebuild).
    user_id="U01" → flush only that user's entries.
    """
    global _cache
    if user_id is None:
        _cache = {}
    else:
        stale = [k for k in _cache if k.startswith(f"rec:{user_id}:")]
        for k in stale:
            del _cache[k]