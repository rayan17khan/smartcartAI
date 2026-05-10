# 🛒 SmartCart AI – Intelligent E-Commerce Recommendation System

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python"/>
  <img src="https://img.shields.io/badge/Flask-3.0-green?style=for-the-badge&logo=flask"/>
  <img src="https://img.shields.io/badge/ML-Scikit--Learn-orange?style=for-the-badge&logo=scikit-learn"/>
  <img src="https://img.shields.io/badge/UI-Flipkart%20Style-blueviolet?style=for-the-badge"/>
</p>

---

## 📌 Introduction

**SmartCart AI** is a production-grade, full-stack intelligent e-commerce platform that delivers personalised product recommendations using Machine Learning. Inspired by Flipkart and Amazon, it combines collaborative filtering, content-based filtering, and a hybrid recommendation engine to serve tailored product suggestions in real time.

---

## 🎯 Problem Statement

Modern e-commerce platforms face the challenge of helping users discover relevant products from catalogues of thousands of items. Without personalisation, users experience:
- **Information overload** from irrelevant products
- **Lower conversion rates** due to poor discoverability
- **Cold-start problems** for new users and products

SmartCart AI addresses all three using a multi-algorithm ML recommendation system.

---

## 🏆 Objectives

1. Build a scalable dataset of 10,000+ products and 5,000+ users
2. Implement Content-Based, Collaborative, and Hybrid Recommendation algorithms
3. Evaluate models using Precision, Recall, and F1-Score
4. Deliver a modern, Flipkart-style frontend with real-time AI recommendations
5. Provide an admin dashboard with analytics and ML performance monitoring
6. Handle cold-start, trending detection, and recommendation explanations

---

## 🗂️ Project Structure

```
SmartCart-AI/
├── app.py                        # Flask application entry point
├── run.py                        # Startup script with health checks
├── requirements.txt              # Python dependencies
├── README.md                     # This file
│
├── data/
│   ├── products.csv              # 10,530 products
│   ├── users.csv                 # 5,200 users
│   ├── interactions.csv          # 150,000+ interactions
│   └── products_preprocessed.csv # Cleaned & feature-engineered
│
├── backend/
│   ├── __init__.py
│   ├── models.py                 # SQLAlchemy DB models
│   └── recommender.py            # Core ML recommendation engine
│
├── static/
│   ├── index.html                # SPA entry point
│   ├── css/
│   │   ├── main.css              # Global styles + theme
│   │   └── components.css        # Component-specific styles
│   └── js/
│       ├── api.js                # All REST API calls
│       ├── store.js              # Global state management
│       ├── components.js         # Reusable UI components
│       ├── pages.js              # Page renderers (Home, Shop, Cart…)
│       ├── admin.js              # Admin dashboard + Chart.js charts
│       └── app.js                # SPA router & bootstrap
│
├── models/
│   ├── ui_matrix.pkl             # Sparse user–item matrix
│   ├── tfidf_vectorizer.pkl      # Trained TF-IDF model
│   ├── evaluation_results.json   # Precision/Recall/F1 metrics
│   ├── performance_dashboard.png # Model performance visualisation
│   ├── algorithm_comparison.png  # CBF vs CF vs Hybrid chart
│   └── dataset_overview.png      # Dataset statistics charts
│
├── notebooks/
│   └── train_and_evaluate.py     # Model training & evaluation script
│
└── utils/
    ├── generate_dataset.py       # Synthetic dataset generator
    └── preprocess.py             # Data preprocessing pipeline
```

---

## 🧠 Algorithms Used

### 1. Content-Based Filtering (CBF)
- **Vectorisation**: TF-IDF over product text (name, category, brand, description, tags)
- **Similarity**: Cosine similarity matrix across all 10,530 products
- **Features**: Normalised price, rating, discount appended as dense features
- **Output**: Top-N similar products for any given item

### 2. Collaborative Filtering (CF)
- **Matrix**: Sparse user–item interaction matrix (3,000 users × 5,000 items)
- **User-Based CF**: Finds top-30 similar users via cosine similarity, aggregates their preferences
- **Item-Based CF**: Cosine similarity between item vectors
- **Interaction weights**: view=1, click=2, wishlist=3, add_to_cart=4, purchase=5
- **Time decay**: Recent interactions (30 days) boosted by ×1.5

### 3. Hybrid Recommender
- **Blend**: 60% CF + 40% CBF weighted score merge
- **Cold-Start fallback**: New users → category preferences + trending products
- **Pipeline**: CF recs → CBF on user history → merge & re-rank → top-N

### 4. Trending Detection
- Time-windowed interaction scoring (last 30 days)
- Weighted by interaction type (purchase > add_to_cart > wishlist > click > view)
- Updates every session

### 5. AI-Ranked Search
- Per-query TF-IDF + cosine relevance
- Personalisation boost for preferred categories (×1.25)
- Final rank = 70% relevance + 20% rating + 10% review count

---

## 📊 Evaluation Metrics

| Model                | Precision@10 | Recall@10 | F1@10 |
|----------------------|:------------:|:---------:|:-----:|
| Content-Based (CBF)  |    ~11.6%    |   ~7.3%   | ~8.9% |
| Collaborative (CF)   |    ~14.2%    |   ~8.9%   |~10.9% |
| **Hybrid (Ours)**    |  **~15.9%**  | **~9.9%** |**~12.2%**|

> Evaluated on 50–120 users with held-out purchase data (20% split).

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- pip

### Installation & Run (3 steps)

```bash
# 1. Clone / extract the project
cd SmartCart-AI

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the application
python run.py
```

The startup script automatically:
- Checks Python version and dependencies
- Verifies datasets exist (generates them if not)
- Runs data preprocessing
- Starts Flask on http://localhost:5000

### Alternatively, run step by step:

```bash
# Generate dataset (if needed)
python utils/generate_dataset.py

# Preprocess data
python utils/preprocess.py

# Train models and generate charts
python notebooks/train_and_evaluate.py

# Start server
python app.py
```

---

## 🔑 Test Accounts

| Username  | Password    | Role  | Description              |
|-----------|-------------|-------|--------------------------|
| admin     | Admin@123   | Admin | Full dashboard access    |
| alice     | Alice@123   | User  | Fashion & Beauty profile |
| bob       | Bob@123     | User  | Sports & Health profile  |
| charlie   | Charlie@123 | User  | Electronics & Toys       |
| demo      | Demo@123    | User  | General demo account     |

---

## 📡 REST API Reference

| Method | Endpoint                   | Description                         | Auth |
|--------|----------------------------|-------------------------------------|------|
| POST   | `/api/auth/login`          | Login with username/password        | ✗    |
| POST   | `/api/auth/register`       | Register new user                   | ✗    |
| POST   | `/api/auth/logout`         | Logout current session              | ✓    |
| GET    | `/api/auth/me`             | Get current user info               | ✗    |
| GET    | `/api/products`            | List products (filters + pagination)| ✗    |
| GET    | `/api/products/<id>`       | Get single product + reviews        | ✗    |
| GET    | `/api/categories`          | Get all categories                  | ✗    |
| GET    | `/api/recommend`           | Personalised AI recommendations     | ✗    |
| GET    | `/api/trending`            | Trending products                   | ✗    |
| GET    | `/api/similar/<id>`        | Similar items (You may also like)   | ✗    |
| GET    | `/api/search?q=<query>`    | AI-ranked search results            | ✗    |
| GET    | `/api/explain`             | Recommendation explanation          | ✗    |
| GET    | `/api/cart`                | View cart                           | ✓    |
| POST   | `/api/cart`                | Add item to cart                    | ✓    |
| PUT    | `/api/cart/<id>`           | Update cart item quantity           | ✓    |
| DELETE | `/api/cart/<id>`           | Remove cart item                    | ✓    |
| POST   | `/api/cart/checkout`       | Place order & clear cart            | ✓    |
| GET    | `/api/wishlist`            | View wishlist                       | ✓    |
| POST   | `/api/wishlist`            | Add to wishlist                     | ✓    |
| DELETE | `/api/wishlist/<id>`       | Remove from wishlist                | ✓    |
| POST   | `/api/reviews`             | Submit product review               | ✓    |
| POST   | `/api/track`               | Track user behaviour event          | ✗    |
| GET    | `/api/admin/analytics`     | Full analytics summary              | ✗    |
| GET    | `/api/admin/users`         | User management list                | ✗    |
| GET    | `/api/admin/orders`        | All orders                          | ✗    |
| GET    | `/api/admin/evaluate`      | Run live ML evaluation              | ✗    |

---

## 🌟 Advanced Features

| # | Feature                          | Description                                        |
|---|----------------------------------|----------------------------------------------------|
| 1 | Personalised Recommendations     | Hybrid CF+CBF recommendations per user             |
| 2 | Trending Detection               | Time-decayed scoring of recent interactions        |
| 3 | Recently Viewed Tracking         | Persisted in localStorage, shown on homepage       |
| 4 | "You May Also Like"              | Item-based CF + CBF blended similarity             |
| 5 | AI-Ranked Search                 | TF-IDF relevance + personalisation boost           |
| 6 | Recommendation Explanation       | "Because you interacted with: Product X"           |
| 7 | Real-Time Rec Updates            | Auto-refresh every 5 minutes on homepage           |
| 8 | User Behaviour Tracking          | Views, clicks, cart, wishlist, purchases logged    |
| 9 | Cold-Start Handling              | Category preferences + trending fallback           |
|10 | Wishlist Feature                 | Add/remove with persistence                        |
|11 | Shopping Cart + Checkout         | Full cart management with order placement          |
|12 | Login & Registration             | Session-based auth with Flask-Login                |
|13 | Review & Rating System           | Submit reviews on product detail page              |
|14 | Admin Analytics Dashboard        | Charts: sales, interactions, categories, ML perf   |
|15 | Sales Trend Visualisation        | Daily purchases chart (30-day window)              |
|16 | Product Filtering                | Price range, rating, category, sort                |
|17 | Flash Sale Timer                 | Countdown timer on homepage                        |
|18 | AI Insight Panel                 | Per-product recommendation explanation card        |
|19 | Search Autocomplete              | Live dropdown with product images                  |
|20 | Responsive UI                    | Works on mobile, tablet, desktop                   |

---

## 🖥️ Pages

| Page                 | Route Hash    | Description                              |
|----------------------|---------------|------------------------------------------|
| Home                 | `#home`       | Hero, AI recs, trending, categories      |
| Shop / Listing       | `#shop`       | Filters sidebar + paginated product grid |
| Product Detail       | `#product/ID` | Images, specs, reviews, similar items    |
| Cart                 | `#cart`       | Items, quantities, order summary         |
| Wishlist             | `#wishlist`   | Saved products grid                      |
| Login / Register     | `#login`      | Auth forms with test accounts            |
| Search Results       | `#search/q`   | AI-ranked results                        |
| Admin Dashboard      | `#admin`      | Analytics, charts, ML evaluation         |
| Profile              | `#profile`    | Edit profile, logout                     |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Browser (SPA)                         │
│   HTML + CSS + Vanilla JS (api.js / store.js / pages.js)    │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP / REST API
┌────────────────────────▼────────────────────────────────────┐
│                    Flask Backend (app.py)                     │
│   Auth · Products · Cart · Wishlist · Reviews · Track        │
├─────────────────────────────────────────────────────────────┤
│              Recommendation Engine (recommender.py)           │
│   ContentBasedFilter → CollaborativeFilter → HybridRecommender│
├──────────────┬──────────────────────────────────────────────┤
│  SQLite DB   │              CSV Data Store                   │
│  (users,     │  products.csv · users.csv · interactions.csv  │
│   cart,      │  products_preprocessed.csv                    │
│   orders…)   │                                               │
└──────────────┴──────────────────────────────────────────────┘
```

---

## 📈 Results

- **Dataset**: 10,530 products × 5,200 users × 154,949 interactions
- **Hybrid F1@10**: ~12.2% (vs 8.9% baseline CBF alone)
- **Search Relevance**: TF-IDF + personalisation achieves strong top-10 accuracy
- **Cold-Start**: Category + trending fallback ensures 0 empty recommendation pages
- **Response Time**: Recommendations served in <200ms after model load

---

## 🔮 Future Scope

1. **Deep Learning**: Implement Neural Collaborative Filtering (NCF) or BERT4Rec
2. **Real-Time Streaming**: Apache Kafka for live interaction ingestion
3. **A/B Testing**: Test recommendation algorithms per user cohort
4. **Image-Based Recommendations**: CNN visual similarity
5. **Reinforcement Learning**: Bandit algorithms for exploration vs exploitation
6. **Multi-Language Support**: Hindi, Tamil, Bengali interfaces
7. **Mobile App**: React Native wrapper around the REST API
8. **Graph Neural Networks**: Model user–item–category as a knowledge graph

---

## 🤝 Team & Acknowledgements

- Built as a Final Year Engineering Project
- Algorithms: Scikit-Learn, SciPy sparse matrices
- Visualisations: Matplotlib, Chart.js
- UI Design: Custom CSS inspired by Flipkart/Amazon
- Dataset: Synthetically generated with Faker

---

## 📄 License

MIT License – free to use for educational and commercial purposes.
