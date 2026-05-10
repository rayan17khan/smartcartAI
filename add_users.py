"""
SmartCart AI — Add More Users Script
=====================================
Run this ONCE to add 50 diverse users with different preferences.
Usage: python add_users.py

These users will make AI recommendations much better!
"""

import os
import sys
import random
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from backend.models import db, User, UserActivity
from backend.recommender import get_recommender

# ── 50 Diverse Users ─────────────────────────────────────────────────────────
USERS = [
    # Electronics lovers
    {"username": "rahul_tech",   "email": "rahul@test.com",   "full_name": "Rahul Sharma",    "city": "Bangalore",  "age": 25, "gender": "Male",   "preferred_categories": "Electronics,Books"},
    {"username": "priya_gadget", "email": "priya@test.com",   "full_name": "Priya Nair",      "city": "Chennai",    "age": 28, "gender": "Female", "preferred_categories": "Electronics,Beauty"},
    {"username": "arjun_dev",    "email": "arjun@test.com",   "full_name": "Arjun Patel",     "city": "Pune",       "age": 22, "gender": "Male",   "preferred_categories": "Electronics,Sports"},
    {"username": "sneha_code",   "email": "sneha@test.com",   "full_name": "Sneha Reddy",     "city": "Hyderabad",  "age": 26, "gender": "Female", "preferred_categories": "Electronics,Books"},
    {"username": "vikram_it",    "email": "vikram@test.com",  "full_name": "Vikram Singh",    "city": "Delhi",      "age": 30, "gender": "Male",   "preferred_categories": "Electronics,Automotive"},

    # Fashion lovers
    {"username": "ananya_style", "email": "ananya@test.com",  "full_name": "Ananya Gupta",    "city": "Mumbai",     "age": 23, "gender": "Female", "preferred_categories": "Fashion,Beauty"},
    {"username": "riya_fashion", "email": "riya@test.com",    "full_name": "Riya Joshi",      "city": "Jaipur",     "age": 21, "gender": "Female", "preferred_categories": "Fashion,Toys"},
    {"username": "kavya_glam",   "email": "kavya@test.com",   "full_name": "Kavya Menon",     "city": "Kochi",      "age": 27, "gender": "Female", "preferred_categories": "Fashion,Beauty"},
    {"username": "ishaan_swag",  "email": "ishaan@test.com",  "full_name": "Ishaan Kapoor",   "city": "Mumbai",     "age": 24, "gender": "Male",   "preferred_categories": "Fashion,Sports"},
    {"username": "meera_trends", "email": "meera@test.com",   "full_name": "Meera Pillai",    "city": "Trivandrum", "age": 29, "gender": "Female", "preferred_categories": "Fashion,Home & Kitchen"},

    # Sports & Fitness
    {"username": "rohan_fit",    "email": "rohan@test.com",   "full_name": "Rohan Verma",     "city": "Delhi",      "age": 26, "gender": "Male",   "preferred_categories": "Sports,Health"},
    {"username": "aditya_run",   "email": "aditya@test.com",  "full_name": "Aditya Kumar",    "city": "Lucknow",    "age": 23, "gender": "Male",   "preferred_categories": "Sports,Grocery"},
    {"username": "neha_yoga",    "email": "neha@test.com",    "full_name": "Neha Sharma",     "city": "Rishikesh",  "age": 31, "gender": "Female", "preferred_categories": "Sports,Health"},
    {"username": "kartik_gym",   "email": "kartik@test.com",  "full_name": "Kartik Rao",      "city": "Bangalore",  "age": 28, "gender": "Male",   "preferred_categories": "Sports,Electronics"},
    {"username": "divya_active", "email": "divya@test.com",   "full_name": "Divya Nair",      "city": "Chennai",    "age": 25, "gender": "Female", "preferred_categories": "Sports,Beauty"},

    # Home & Kitchen
    {"username": "sunita_home",  "email": "sunita@test.com",  "full_name": "Sunita Agarwal",  "city": "Agra",       "age": 35, "gender": "Female", "preferred_categories": "Home & Kitchen,Grocery"},
    {"username": "rakesh_diy",   "email": "rakesh@test.com",  "full_name": "Rakesh Mehta",    "city": "Ahmedabad",  "age": 38, "gender": "Male",   "preferred_categories": "Home & Kitchen,Automotive"},
    {"username": "pooja_cook",   "email": "pooja@test.com",   "full_name": "Pooja Iyer",      "city": "Coimbatore", "age": 32, "gender": "Female", "preferred_categories": "Home & Kitchen,Grocery"},
    {"username": "amit_decor",   "email": "amit@test.com",    "full_name": "Amit Jain",       "city": "Surat",      "age": 36, "gender": "Male",   "preferred_categories": "Home & Kitchen,Books"},
    {"username": "lalita_nest",  "email": "lalita@test.com",  "full_name": "Lalita Desai",    "city": "Baroda",     "age": 40, "gender": "Female", "preferred_categories": "Home & Kitchen,Fashion"},

    # Books & Education
    {"username": "varun_reads",  "email": "varun@test.com",   "full_name": "Varun Bose",      "city": "Kolkata",    "age": 27, "gender": "Male",   "preferred_categories": "Books,Electronics"},
    {"username": "shreya_lit",   "email": "shreya@test.com",  "full_name": "Shreya Das",      "city": "Kolkata",    "age": 24, "gender": "Female", "preferred_categories": "Books,Fashion"},
    {"username": "harsh_study",  "email": "harsh@test.com",   "full_name": "Harsh Mishra",    "city": "Varanasi",   "age": 20, "gender": "Male",   "preferred_categories": "Books,Sports"},
    {"username": "ankita_learn", "email": "ankita@test.com",  "full_name": "Ankita Singh",    "city": "Patna",      "age": 22, "gender": "Female", "preferred_categories": "Books,Health"},
    {"username": "siddharth_phd","email": "sid@test.com",     "full_name": "Siddharth Nair",  "city": "Pune",       "age": 29, "gender": "Male",   "preferred_categories": "Books,Electronics"},

    # Beauty & Health
    {"username": "tanvi_glow",   "email": "tanvi@test.com",   "full_name": "Tanvi Kulkarni",  "city": "Nashik",     "age": 26, "gender": "Female", "preferred_categories": "Beauty,Fashion"},
    {"username": "simran_care",  "email": "simran@test.com",  "full_name": "Simran Kaur",     "city": "Amritsar",   "age": 23, "gender": "Female", "preferred_categories": "Beauty,Health"},
    {"username": "ayesha_glam",  "email": "ayesha@test.com",  "full_name": "Ayesha Khan",     "city": "Lucknow",    "age": 25, "gender": "Female", "preferred_categories": "Beauty,Grocery"},
    {"username": "zara_skin",    "email": "zara@test.com",    "full_name": "Zara Sheikh",     "city": "Hyderabad",  "age": 28, "gender": "Female", "preferred_categories": "Beauty,Home & Kitchen"},
    {"username": "nisha_health", "email": "nisha@test.com",   "full_name": "Nisha Gupta",     "city": "Noida",      "age": 34, "gender": "Female", "preferred_categories": "Health,Grocery"},

    # Grocery & Family
    {"username": "mohan_family", "email": "mohan@test.com",   "full_name": "Mohan Trivedi",   "city": "Indore",     "age": 42, "gender": "Male",   "preferred_categories": "Grocery,Home & Kitchen"},
    {"username": "geeta_mom",    "email": "geeta@test.com",   "full_name": "Geeta Sharma",    "city": "Bhopal",     "age": 39, "gender": "Female", "preferred_categories": "Grocery,Toys"},
    {"username": "suresh_daily", "email": "suresh@test.com",  "full_name": "Suresh Pillai",   "city": "Madurai",    "age": 45, "gender": "Male",   "preferred_categories": "Grocery,Health"},
    {"username": "kamala_house", "email": "kamala@test.com",  "full_name": "Kamala Devi",     "city": "Mysore",     "age": 37, "gender": "Female", "preferred_categories": "Grocery,Home & Kitchen"},
    {"username": "rajesh_mart",  "email": "rajesh@test.com",  "full_name": "Rajesh Kothari",  "city": "Rajkot",     "age": 44, "gender": "Male",   "preferred_categories": "Grocery,Automotive"},

    # Toys & Kids
    {"username": "papa_kiddo",   "email": "papa@test.com",    "full_name": "Sunil Mathur",    "city": "Jaipur",     "age": 33, "gender": "Male",   "preferred_categories": "Toys,Books"},
    {"username": "mama_fun",     "email": "mama@test.com",    "full_name": "Rekha Agarwal",   "city": "Kanpur",     "age": 31, "gender": "Female", "preferred_categories": "Toys,Grocery"},
    {"username": "deepak_kids",  "email": "deepak@test.com",  "full_name": "Deepak Chandra",  "city": "Nagpur",     "age": 36, "gender": "Male",   "preferred_categories": "Toys,Electronics"},
    {"username": "priti_junior", "email": "priti@test.com",   "full_name": "Priti Soni",      "city": "Raipur",     "age": 29, "gender": "Female", "preferred_categories": "Toys,Fashion"},
    {"username": "ankit_play",   "email": "ankit@test.com",   "full_name": "Ankit Dubey",     "city": "Gwalior",    "age": 27, "gender": "Male",   "preferred_categories": "Toys,Sports"},

    # Automotive
    {"username": "sanjay_auto",  "email": "sanjay@test.com",  "full_name": "Sanjay Pandey",   "city": "Pune",       "age": 34, "gender": "Male",   "preferred_categories": "Automotive,Electronics"},
    {"username": "vijay_motor",  "email": "vijay@test.com",   "full_name": "Vijay Tiwari",    "city": "Nagpur",     "age": 40, "gender": "Male",   "preferred_categories": "Automotive,Sports"},
    {"username": "manoj_speed",  "email": "manoj@test.com",   "full_name": "Manoj Yadav",     "city": "Agra",       "age": 32, "gender": "Male",   "preferred_categories": "Automotive,Home & Kitchen"},

    # Mixed / General shoppers
    {"username": "ritu_shop",    "email": "ritu@test.com",    "full_name": "Ritu Malhotra",   "city": "Delhi",      "age": 28, "gender": "Female", "preferred_categories": "Fashion,Electronics,Beauty"},
    {"username": "nikhil_all",   "email": "nikhil@test.com",  "full_name": "Nikhil Bajaj",    "city": "Mumbai",     "age": 26, "gender": "Male",   "preferred_categories": "Electronics,Sports,Books"},
    {"username": "payal_mix",    "email": "payal@test.com",   "full_name": "Payal Chopra",    "city": "Chandigarh", "age": 24, "gender": "Female", "preferred_categories": "Beauty,Fashion,Health"},
    {"username": "rohit_budget", "email": "rohit@test.com",   "full_name": "Rohit Saxena",    "city": "Lucknow",    "age": 21, "gender": "Male",   "preferred_categories": "Grocery,Books,Electronics"},
    {"username": "shweta_smart", "email": "shweta@test.com",  "full_name": "Shweta Bansal",   "city": "Noida",      "age": 30, "gender": "Female", "preferred_categories": "Home & Kitchen,Fashion,Grocery"},
    {"username": "gaurav_pro",   "email": "gaurav@test.com",  "full_name": "Gaurav Tripathi", "city": "Allahabad",  "age": 33, "gender": "Male",   "preferred_categories": "Sports,Health,Electronics"},
    {"username": "mamta_value",  "email": "mamta@test.com",   "full_name": "Mamta Srivastava","city": "Kanpur",     "age": 38, "gender": "Female", "preferred_categories": "Grocery,Toys,Home & Kitchen"},
    {"username": "lokesh_deal",  "email": "lokesh@test.com",  "full_name": "Lokesh Reddy",    "city": "Hyderabad",  "age": 29, "gender": "Male",   "preferred_categories": "Electronics,Automotive,Sports"},
]

PASSWORD = "Test@1234"  # Same password for all test users


def add_users_and_interactions():
    app = create_app()

    with app.app_context():
        print("\n🚀 Starting user seeding...\n")

        # ── Add Users ─────────────────────────────────────────────────────────
        added = 0
        skipped = 0

        for i, ud in enumerate(USERS):
            if User.query.filter_by(username=ud["username"]).first():
                skipped += 1
                continue

            count   = User.query.count()
            user_id = f"U{count + 10000:05d}"

            u = User(
                user_id=user_id,
                username=ud["username"],
                email=ud["email"],
                full_name=ud["full_name"],
                city=ud.get("city", ""),
                age=ud.get("age"),
                gender=ud.get("gender", ""),
                preferred_categories=ud.get("preferred_categories", ""),
                is_admin=False,
                signup_date=datetime.utcnow() - timedelta(days=random.randint(1, 90))
            )
            u.set_password(PASSWORD)
            db.session.add(u)
            db.session.commit()
            added += 1
            print(f"  ✅ Added: {ud['full_name']} ({ud['city']}) — {ud['preferred_categories']}")

        print(f"\n✅ Users added: {added}")
        print(f"⏭️  Users skipped (already exist): {skipped}")

        # ── Seed Interactions ─────────────────────────────────────────────────
        print("\n🤖 Seeding user interactions for AI training...\n")

        try:
            r = get_recommender()
            interaction_count = 0

            all_users = User.query.filter(User.username != 'admin').all()

            for user in all_users:
                prefs = user.preferred_categories or ""
                cats  = [c.strip() for c in prefs.split(",") if c.strip()]

                for cat in cats:
                    try:
                        items = r.get_trending(n=10, category=cat)
                        actions = ["view", "view", "view", "add_to_cart", "wishlist", "purchase"]

                        for item in items:
                            pid = str(item.get("product_id") or item.get("id") or "")
                            if not pid:
                                continue
                            # Pick a random action (weighted toward view)
                            action = random.choice(actions)
                            existing = UserActivity.query.filter_by(
                                user_id=str(user.user_id),
                                product_id=pid,
                                action=action
                            ).first()
                            if not existing:
                                db.session.add(UserActivity(
                                    user_id=str(user.user_id),
                                    product_id=pid,
                                    action=action
                                ))
                                interaction_count += 1
                    except Exception as e:
                        pass

            db.session.commit()
            print(f"  ✅ {interaction_count} interactions seeded across {len(all_users)} users")

        except Exception as e:
            db.session.rollback()
            print(f"  ⚠️ Interaction seeding failed: {e}")

        # ── Summary ───────────────────────────────────────────────────────────
        total_users = User.query.count()
        total_interactions = UserActivity.query.count()

        print(f"""
╔══════════════════════════════════════╗
║        ✅ ALL DONE!                  ║
╠══════════════════════════════════════╣
║  Total Users       : {total_users:<15} ║
║  Total Interactions: {total_interactions:<15} ║
║  Password for all  : Test@1234       ║
╚══════════════════════════════════════╝

Now restart Flask:  python app.py
AI recommendations will be much better! 🎯
        """)


if __name__ == "__main__":
    add_users_and_interactions()