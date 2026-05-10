import pandas as pd
import random
import csv

random.seed(42)

categories = {
    "Electronics": {
        "Smartphone": ["Apple","Samsung","OnePlus","Sony","Asus","Dell","HP","Bose"],
        "Laptop":     ["Dell","HP","Asus","Lenovo","Apple","Acer","MSI"],
        "Headphones": ["Sony","Bose","JBL","Sennheiser","boAt","Noise"],
        "Camera":     ["Canon","Nikon","Sony","Fujifilm","GoPro"],
        "Tablet":     ["Apple","Samsung","Lenovo","Microsoft"],
        "Smartwatch": ["Apple","Samsung","Garmin","Fitbit","Noise","boAt"],
        "TV":         ["Samsung","LG","Sony","Mi","OnePlus","Vu"],
        "Speaker":    ["JBL","Sony","Bose","boAt","Marshall"],
    },
    "Fashion": {
        "T-Shirt":    ["Nike","Adidas","H&M","Zara","Puma","Levis"],
        "Jeans":      ["Levis","Wrangler","Pepe","Zara","H&M"],
        "Shoes":      ["Nike","Adidas","Reebok","Puma","Skechers","Bata"],
        "Dress":      ["Zara","H&M","Mango","Forever21","FabIndia"],
        "Jacket":     ["Nike","Adidas","H&M","Zara","Puma"],
        "Bag":        ["Wildcraft","Skybags","VIP","Samsonite","Lavie"],
        "Watch":      ["Titan","Fastrack","Casio","Fossil","Seiko"],
        "Saree":      ["FabIndia","Nalli","Kanchipuram","Taneira"],
        "Kurta":      ["FabIndia","Biba","W","Aurelia","Manyavar"],
    },
    "Beauty": {
        "Skincare":   ["Loreal","Neutrogena","Olay","Ponds","Himalaya","Mamaearth"],
        "Makeup":     ["Loreal","Maybelline","MAC","Lakme","NYX","Colorbar"],
        "Perfume":    ["Fogg","AXE","Nike","Versace","Davidoff","Park Avenue"],
        "Haircare":   ["Loreal","Pantene","Dove","TRESemme","Mamaearth"],
        "Lipstick":   ["Lakme","Maybelline","MAC","Colorbar","NYX"],
    },
    "Books": {
        "Fiction":     ["Penguin","HarperCollins","Bloomsbury","Rupa","Pan Macmillan"],
        "Non-Fiction": ["Penguin","HarperCollins","Rupa","Westland","Juggernaut"],
        "Textbook":    ["Pearson","Oxford","McGraw-Hill","Wiley","S.Chand"],
        "Children":    ["Penguin","Scholastic","Puffin","CBT","Pratham"],
    },
    "Sports": {
        "Cricket":  ["SG","Kookaburra","Gray-Nicolls","MRF","SS"],
        "Football": ["Nike","Adidas","Puma","Cosco","Nivia"],
        "Fitness":  ["Decathlon","Reebok","Adidas","Cosco","Nivia"],
        "Yoga":     ["Decathlon","Strauss","Boldfit","Nivia","Vector X"],
        "Cycling":  ["Hero","Hercules","Firefox","Trek","Giant"],
    },
    "Toys": {
        "Action Figures": ["Hasbro","Mattel","Funskool","Playskool","LEGO"],
        "Board Games":    ["Hasbro","Mattel","Milton","Funskool","Pressman"],
        "Lego":           ["LEGO","Mega Bloks","K'NEX","Cobi"],
        "Soft Toys":      ["Hasbro","Mattel","Soft Buddies","Archies","Hallmark"],
    },
    "Grocery": {
        "Snacks":    ["Nestle","Lays","Haldirams","Bingo","Too Yumm"],
        "Beverages": ["Nestle","Pepsi","Coca-Cola","Red Bull","Tropicana"],
        "Dairy":     ["Amul","Mother Dairy","Nestle","Britannia","Milma"],
        "Spices":    ["MDH","Everest","Catch","Badshah","Eastern"],
    },
    "Home": {
        "Furniture": ["IKEA","Pepperfry","Urban Ladder","Godrej","Durian"],
        "Kitchen":   ["Prestige","Hawkins","Inalsa","Pigeon","Butterfly"],
        "Bedding":   ["Bombay Dyeing","Raymond","Spaces","D'Decor","Trident"],
        "Lighting":  ["Philips","Syska","Havells","Crompton","Wipro"],
        "Decor":     ["FabIndia","Chumbak","Pepperfry","Jaypore","Craftsvilla"],
    },
    "Health": {
        "Supplements":    ["HealthKart","Optimum Nutrition","MuscleBlaze","GNC","Himalaya"],
        "Medical Devices":["Omron","Dr. Morepen","Microlife","Accusure","Beurer"],
    },
    "Auto": {
        "Car Accessories": ["Bosch","3M","Michelin","Castrol","Meguiar's"],
        "Bike Accessories":["Studds","Steelbird","Vega","LS2","Royal Enfield"],
    },
}

image_map = {
    "Smartphone":      "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&h=400&fit=crop",
    "Laptop":          "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&h=400&fit=crop",
    "Headphones":      "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=400&fit=crop",
    "Camera":          "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=400&h=400&fit=crop",
    "Tablet":          "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400&h=400&fit=crop",
    "Smartwatch":      "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=400&fit=crop",
    "TV":              "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=400&h=400&fit=crop",
    "Speaker":         "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=400&h=400&fit=crop",
    "T-Shirt":         "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&h=400&fit=crop",
    "Jeans":           "https://images.unsplash.com/photo-1542272604-787c3835535d?w=400&h=400&fit=crop",
    "Shoes":           "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=400&fit=crop",
    "Dress":           "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=400&h=400&fit=crop",
    "Jacket":          "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400&h=400&fit=crop",
    "Bag":             "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=400&h=400&fit=crop",
    "Watch":           "https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=400&h=400&fit=crop",
    "Saree":           "https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=400&h=400&fit=crop",
    "Kurta":           "https://images.unsplash.com/photo-1614252235316-8c857d38b5f4?w=400&h=400&fit=crop",
    "Skincare":        "https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400&h=400&fit=crop",
    "Makeup":          "https://images.unsplash.com/photo-1512207736890-6ffed8a84e8d?w=400&h=400&fit=crop",
    "Perfume":         "https://images.unsplash.com/photo-1541643600914-78b084683702?w=400&h=400&fit=crop",
    "Haircare":        "https://images.unsplash.com/photo-1526045612212-70caf35c14df?w=400&h=400&fit=crop",
    "Lipstick":        "https://images.unsplash.com/photo-1586495777744-4e6232bf2176?w=400&h=400&fit=crop",
    "Fiction":         "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400&h=400&fit=crop",
    "Non-Fiction":     "https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=400&h=400&fit=crop",
    "Textbook":        "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=400&h=400&fit=crop",
    "Children":        "https://images.unsplash.com/photo-1512499617640-c74ae3a79d37?w=400&h=400&fit=crop",
    "Cricket":         "https://images.unsplash.com/photo-1531415074968-036ba1b575da?w=400&h=400&fit=crop",
    "Football":        "https://images.unsplash.com/photo-1575361204480-aadea25e6e68?w=400&h=400&fit=crop",
    "Fitness":         "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=400&h=400&fit=crop",
    "Yoga":            "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=400&h=400&fit=crop",
    "Cycling":         "https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=400&h=400&fit=crop",
    "Action Figures":  "https://images.unsplash.com/photo-1566576912321-d58ddd7a6088?w=400&h=400&fit=crop",
    "Board Games":     "https://images.unsplash.com/photo-1611996575749-79a3a250f948?w=400&h=400&fit=crop",
    "Lego":            "https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=400&h=400&fit=crop",
    "Soft Toys":       "https://images.unsplash.com/photo-1559454403-b8fb88521f11?w=400&h=400&fit=crop",
    "Snacks":          "https://images.unsplash.com/photo-1621939514649-280e2ee25f60?w=400&h=400&fit=crop",
    "Beverages":       "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&h=400&fit=crop",
    "Dairy":           "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&h=400&fit=crop",
    "Spices":          "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=400&h=400&fit=crop",
    "Furniture":       "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400&h=400&fit=crop",
    "Kitchen":         "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&h=400&fit=crop",
    "Bedding":         "https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af?w=400&h=400&fit=crop",
    "Lighting":        "https://images.unsplash.com/photo-1524484485831-a92ffc0de03f?w=400&h=400&fit=crop",
    "Decor":           "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400&h=400&fit=crop",
    "Supplements":     "https://images.unsplash.com/photo-1550572017-edd951b55104?w=400&h=400&fit=crop",
    "Medical Devices": "https://images.unsplash.com/photo-1559757175-0eb30cd8c063?w=400&h=400&fit=crop",
    "Car Accessories": "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=400&h=400&fit=crop",
    "Bike Accessories":"https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=400&fit=crop",
}

tag_pool = ["trending","bestseller","new arrival","sale","recommended","featured"]

variants = ["Pro","Lite","Ultra","Plus","Elite","Max","Mini","Prime","Go","Air"]

rows = []
pid  = 1

for cat, subcats in categories.items():
    for subcat, brands in subcats.items():
        # roughly distribute 10531 rows across all subcategories
        count = random.randint(180, 260)
        for _ in range(count):
            brand   = random.choice(brands)
            variant = random.choice(variants)
            num     = random.randint(100, 999)
            name    = f"{brand} {subcat} {variant} {num}"
            price   = round(random.uniform(299, 199999), 2)
            mrp     = round(price * random.uniform(1.05, 1.8), 2)
            disc    = round((mrp - price) / mrp * 100, 1)
            rating  = round(random.uniform(3.0, 5.0), 1)
            reviews = random.randint(100, 50000)
            stock   = random.randint(0, 500)
            featured= random.choice([True, False])
            tags    = ",".join(random.sample(tag_pool, 3))
            desc    = (f"Premium quality {subcat} by {brand}. "
                       f"Features advanced technology and elegant design. "
                       f"Ideal for daily use. Comes with 1-year warranty.")
            image   = image_map.get(subcat,
                        "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400&h=400&fit=crop")

            rows.append({
                "product_id":       f"P{pid:06d}",
                "product_name":     name,
                "category":         cat,
                "subcategory":      subcat,
                "brand":            brand,
                "price":            price,
                "mrp":              mrp,
                "discount_percent": disc,
                "description":      desc,
                "rating":           rating,
                "num_reviews":      reviews,
                "image_url":        image,
                "stock":            stock,
                "is_featured":      featured,
                "tags":             tags,
            })
            pid += 1

df = pd.DataFrame(rows)
df.to_csv('data/products.csv', index=False, quoting=csv.QUOTE_ALL)
print(f"✅ Generated {len(df)} products and saved to data/products.csv")