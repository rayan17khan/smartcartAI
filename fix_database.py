"""
SmartCart AI — Database Check & Fix Script
Run this to check your database and import all CSV users.
Usage: python fix_database.py
"""

import os
import sys
import sqlite3
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, 'smartcart.db')

def check_database():
    print("=" * 50)
    print("  SmartCart AI — Database Check")
    print("=" * 50)

    # ── Check if DB file exists ───────────────────────
    if not os.path.exists(DB_PATH):
        print("\n❌ smartcart.db NOT FOUND — creating now...")
        create_database()
    else:
        print(f"\n✅ smartcart.db found!")

    # ── Show all tables ───────────────────────────────
    conn = sqlite3.connect(DB_PATH)
    c    = conn.cursor()

    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = c.fetchall()

    if not tables:
        print("❌ No tables found — creating now...")
        conn.close()
        create_database()
        conn = sqlite3.connect(DB_PATH)
        c    = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = c.fetchall()

    print(f"\n📋 Tables in database:")
    for t in tables:
        c.execute(f"SELECT COUNT(*) FROM {t[0]}")
        count = c.fetchone()[0]
        print(f"   {t[0]:<20} → {count} rows")

    conn.close()
    return tables


def create_database():
    print("\n🔧 Creating database...")
    from app import create_app
    app = create_app()
    print("✅ Database created with all tables!")


def import_csv_users():
    print("\n" + "=" * 50)
    print("  Importing users from CSV...")
    print("=" * 50)

    # ── Check CSV exists ──────────────────────────────
    csv_path = os.path.join(BASE_DIR, 'data', 'users_preprocessed.csv')
    if not os.path.exists(csv_path):
        csv_path = os.path.join(BASE_DIR, 'data', 'users.csv')
        if not os.path.exists(csv_path):
            print("❌ No users CSV found in data/ folder!")
            return

    print(f"✅ Found: {csv_path}")

    # ── Load CSV ──────────────────────────────────────
    df = pd.read_csv(csv_path)
    print(f"📊 CSV has {len(df)} users")
    print(f"📋 Columns: {df.columns.tolist()}")

    # ── Import into database ──────────────────────────
    from app import create_app
    from backend.models import db, User
    from datetime import datetime

    app = create_app()

    with app.app_context():
        added   = 0
        skipped = 0

        for _, row in df.iterrows():
            try:
                # Skip if user already exists
                uid      = str(row.get('user_id', '')).strip()
                username = str(row.get('username', '')).strip()

                if User.query.filter_by(user_id=uid).first():
                    skipped += 1
                    continue
                if User.query.filter_by(username=username).first():
                    skipped += 1
                    continue

                # Get preferred_categories
                prefs = str(row.get('preferred_categories', '')).strip()
                prefs = prefs.replace('"', '').replace("'", '')

                # Create user
                u = User(
                    user_id=uid,
                    username=username,
                    email=str(row.get('email', f"{username}@smartcart.ai")),
                    full_name=str(row.get('full_name', username)),
                    age=int(row['age']) if pd.notna(row.get('age')) else None,
                    gender=str(row.get('gender', '')),
                    city=str(row.get('city', '')),
                    preferred_categories=prefs,
                    is_admin=bool(row.get('is_admin', False)),
                    signup_date=datetime.utcnow()
                )

                # Set password — use existing hash if available
                pwd_hash = str(row.get('password_hash', ''))
                if pwd_hash.startswith('pbkdf2:'):
                    u.password_hash = pwd_hash
                else:
                    u.set_password('Test@1234')

                db.session.add(u)
                added += 1

                if added % 50 == 0:
                    db.session.commit()
                    print(f"   ... {added} users imported so far")

            except Exception as e:
                skipped += 1
                continue

        db.session.commit()

        total = User.query.count()
        print(f"\n✅ Import complete!")
        print(f"   Added   : {added} users")
        print(f"   Skipped : {skipped} users (already existed)")
        print(f"   Total   : {total} users in database")


def import_interactions():
    print("\n" + "=" * 50)
    print("  Importing interactions from CSV...")
    print("=" * 50)

    csv_path = os.path.join(BASE_DIR, 'data', 'interactions.csv')
    if not os.path.exists(csv_path):
        print("⚠️  interactions.csv not found — skipping")
        return

    df = pd.read_csv(csv_path)
    print(f"✅ Found {len(df)} interactions in CSV")

    from app import create_app
    from backend.models import db, UserActivity

    app = create_app()

    with app.app_context():
        existing = UserActivity.query.count()
        if existing > 1000:
            print(f"⚠️  Already have {existing} interactions — skipping import")
            return

        added = 0
        for _, row in df.iterrows():
            try:
                ua = UserActivity(
                    user_id=str(row.get('user_id', '')),
                    product_id=str(row.get('product_id', '')),
                    action=str(row.get('action', 'view'))
                )
                db.session.add(ua)
                added += 1
                if added % 200 == 0:
                    db.session.commit()
            except Exception:
                continue

        db.session.commit()
        print(f"✅ {added} interactions imported!")


def final_summary():
    print("\n" + "=" * 50)
    print("  Final Database Summary")
    print("=" * 50)

    conn = sqlite3.connect(DB_PATH)
    c    = conn.cursor()

    tables = ['user', 'user_activity', 'cart_item',
              'wishlist_item', 'order', 'review']

    for t in tables:
        try:
            c.execute(f"SELECT COUNT(*) FROM {t}")
            count = c.fetchone()[0]
            print(f"   {t:<20} → {count} rows")
        except Exception:
            print(f"   {t:<20} → table not found")

    conn.close()

    print(f"""
╔══════════════════════════════════════╗
║     ✅ Database Ready!               ║
╠══════════════════════════════════════╣
║  Now restart Flask:                  ║
║  > python app.py                     ║
║                                      ║
║  AI recommendations will now use     ║
║  all your CSV users & interactions!  ║
╚══════════════════════════════════════╝
    """)


if __name__ == "__main__":
    check_database()
    import_csv_users()
    import_interactions()
    final_summary()