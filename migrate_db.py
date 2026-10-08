import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "store.db")

def upgrade_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check columns of products table
    cursor.execute("PRAGMA table_info(products)")
    cols = [col[1] for col in cursor.fetchall()]

    new_cols = {
        "mrp": "REAL",
        "discount_pct": "INTEGER DEFAULT 0",
        "rating": "REAL DEFAULT 4.0",
        "review_count": "INTEGER DEFAULT 100",
        "brand": "TEXT",
        "image_url": "TEXT",
    }

    for col_name, col_type in new_cols.items():
        if col_name not in cols:
            cursor.execute(f"ALTER TABLE products ADD COLUMN {col_name} {col_type}")

    # Add shoe products from reference image
    shoes = [
        (
            101,
            "Nike Revolution 7",
            "shoes",
            2799.0,
            "Lightweight road running shoes with plush foam cushioning and breathable mesh upper.",
            0,
            4995.0,
            44,
            4.5,
            2100,
            "Nike",
            "/static/images/nike_revolution_7.jpg"
        ),
        (
            102,
            "Adidas Galaxy 6",
            "shoes",
            2499.0,
            "Everyday running sneakers featuring Cloudfoam midsole and durable rubber outsole.",
            0,
            4999.0,
            50,
            4.4,
            1800,
            "Adidas",
            "/static/images/adidas_galaxy_6.jpg"
        ),
        (
            103,
            "Puma Softride Enzo",
            "shoes",
            2699.0,
            "Progressive training running shoe with Softride EVA cushioning for extreme all-day comfort.",
            0,
            4499.0,
            40,
            4.3,
            1200,
            "Puma",
            "/static/images/puma_softride_enzo.jpg"
        ),
        (
            104,
            "ASICS Gel-Contend 8",
            "shoes",
            2949.0,
            "Engineered running shoe with rearfoot GEL technology and AMPLIFOAM midsole cushioning.",
            0,
            5499.0,
            46,
            4.5,
            1600,
            "ASICS",
            "/static/images/asics_gel_contend_8.jpg"
        ),
        # Laptops under 60k
        (
            201,
            "ASUS Vivobook 15 Intel Core i5",
            "laptops",
            49990.0,
            "Thin and light 15.6 inch FHD laptop, 16GB RAM, 512GB SSD, Windows 11.",
            0,
            62990.0,
            21,
            4.4,
            850,
            "ASUS",
            "/static/images/laptop.jpg"
        ),
        (
            202,
            "HP Pavilion 14 AMD Ryzen 5",
            "laptops",
            54990.0,
            "Portable performance laptop with IPS display, backlit keyboard, fast charge.",
            0,
            69990.0,
            21,
            4.5,
            1100,
            "HP",
            "/static/images/laptop.jpg"
        ),
        (
            203,
            "Lenovo IdeaPad Slim 3 12th Gen",
            "laptops",
            42990.0,
            "Everyday multitasker laptop with Dolby Audio and military-grade durability.",
            0,
            59990.0,
            28,
            4.3,
            920,
            "Lenovo",
            "/static/images/laptop.jpg"
        ),
        # Smartphones under 20k
        (
            301,
            "OnePlus Nord CE 3 Lite 5G",
            "smartphones",
            17999.0,
            "108MP camera, 67W SUPERVOOC charging, 120Hz display, 5000mAh battery.",
            0,
            19999.0,
            10,
            4.4,
            4300,
            "OnePlus",
            "/static/images/smartphone.jpg"
        ),
        (
            302,
            "Redmi Note 13 5G",
            "smartphones",
            16499.0,
            "Super slim AMOLED 120Hz screen, 108MP triple camera, Dimensity 6080.",
            0,
            20999.0,
            21,
            4.3,
            3100,
            "Redmi",
            "/static/images/smartphone.jpg"
        ),
        (
            303,
            "Samsung Galaxy M34 5G",
            "smartphones",
            18999.0,
            "120Hz Super AMOLED display, 50MP No Shake OIS camera, 6000mAh monster battery.",
            0,
            24499.0,
            22,
            4.4,
            2800,
            "Samsung",
            "/static/images/smartphone.jpg"
        ),
        # Headphones
        (
            401,
            "Sony WH-CH520 Wireless",
            "headphones",
            4490.0,
            "50 hours battery life, multipoint connection, DSEE sound upscaling.",
            0,
            5990.0,
            25,
            4.5,
            5200,
            "Sony",
            "/static/images/headphones.jpg"
        ),
        (
            402,
            "boAt Nirvana 751 ANC",
            "headphones",
            3999.0,
            "Active Noise Cancellation up to 33dB, 65 hours playback, ASAP Charge.",
            0,
            7990.0,
            50,
            4.3,
            3400,
            "boAt",
            "/static/images/headphones.jpg"
        ),
    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO products (id, name, category, price, description, is_organic, mrp, discount_pct, rating, review_count, brand, image_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, shoes)

    # Update existing products with images if they don't have one
    cursor.execute("UPDATE products SET image_url = '/static/images/honey.png' WHERE category = 'honey' AND (image_url IS NULL OR image_url = '')")
    cursor.execute("UPDATE products SET image_url = '/static/images/oats.png' WHERE category IN ('grains', 'snacks') AND (image_url IS NULL OR image_url = '')")
    cursor.execute("UPDATE products SET rating = 4.5, review_count = 140 WHERE rating IS NULL")

    conn.commit()
    conn.close()
    print("Database upgrade completed successfully!")

if __name__ == "__main__":
    upgrade_database()
