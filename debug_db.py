import sqlite3

conn = sqlite3.connect('smartcart.db')
cursor = conn.cursor()

print("=== USERS ===")
cursor.execute("SELECT user_id, username, email FROM users")
for row in cursor.fetchall():
    print(row)

print("\n=== CART ITEMS ===")
cursor.execute("SELECT * FROM cart_items")
for row in cursor.fetchall():
    print(row)

print("\n=== WISHLIST ITEMS ===")
cursor.execute("SELECT * FROM wishlist_items")
for row in cursor.fetchall():
    print(row)

print("\n=== CART TABLE SCHEMA ===")
cursor.execute("PRAGMA table_info(cart_items)")
for row in cursor.fetchall():
    print(row)

print("\n=== WISHLIST TABLE SCHEMA ===")
cursor.execute("PRAGMA table_info(wishlist_items)")
for row in cursor.fetchall():
    print(row)

conn.close()