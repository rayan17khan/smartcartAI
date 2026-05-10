"""
SmartCart AI – SQLAlchemy Database Models
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id                    = db.Column(db.Integer, primary_key=True)
    user_id               = db.Column(db.String(10), unique=True, nullable=False)
    username              = db.Column(db.String(80), unique=True, nullable=False)
    email                 = db.Column(db.String(120), unique=True, nullable=False)
    password_hash         = db.Column(db.String(256), nullable=False)
    full_name             = db.Column(db.String(120))
    age                   = db.Column(db.Integer)
    gender                = db.Column(db.String(20))
    city                  = db.Column(db.String(60))
    state                 = db.Column(db.String(60))
    preferred_categories  = db.Column(db.Text, default="")
    signup_date           = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin              = db.Column(db.Boolean, default=False)
    is_active             = db.Column(db.Boolean, default=True)
    profile_pic           = db.Column(db.String(256), default="")

    cart_items   = db.relationship("CartItem",    back_populates="user", cascade="all,delete")
    wishlist     = db.relationship("WishlistItem",back_populates="user", cascade="all,delete")
    reviews      = db.relationship("Review",      back_populates="user", cascade="all,delete")

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)

    def to_dict(self):
        return {
            "user_id"   : self.user_id,
            "username"  : self.username,
            "email"     : self.email,
            "full_name" : self.full_name,
            "city"      : self.city,
            "is_admin"  : self.is_admin,
            "preferred_categories": self.preferred_categories
        }


class CartItem(db.Model):
    __tablename__ = "cart_items"
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_id = db.Column(db.String(10), nullable=False)
    quantity   = db.Column(db.Integer, default=1)
    added_at   = db.Column(db.DateTime, default=datetime.utcnow)
    user       = db.relationship("User", back_populates="cart_items")


class WishlistItem(db.Model):
    __tablename__ = "wishlist_items"
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_id = db.Column(db.String(10), nullable=False)
    added_at   = db.Column(db.DateTime, default=datetime.utcnow)
    user       = db.relationship("User", back_populates="wishlist")


class Review(db.Model):
    __tablename__ = "reviews"
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_id = db.Column(db.String(10), nullable=False)
    rating     = db.Column(db.Float, nullable=False)
    comment    = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user       = db.relationship("User", back_populates="reviews")


class UserActivity(db.Model):
    __tablename__ = "user_activity"
    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.String(10))
    product_id   = db.Column(db.String(10))
    action       = db.Column(db.String(30))
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
    session_data = db.Column(db.Text)


class Order(db.Model):
    __tablename__ = "orders"
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"))
    total      = db.Column(db.Float)
    status     = db.Column(db.String(30), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items_json = db.Column(db.Text)   # JSON list of {product_id, qty, price}
