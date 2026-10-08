import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "store.db")


def create_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            price REAL NOT NULL,
            description TEXT,
            is_organic INTEGER DEFAULT 0,
            mrp REAL,
            discount_pct INTEGER DEFAULT 0,
            rating REAL DEFAULT 4.5,
            review_count INTEGER DEFAULT 100,
            brand TEXT DEFAULT '',
            image_url TEXT DEFAULT '/static/images/honey.png'
        )
    """)

    # Ensure any missing columns exist
    cursor.execute("PRAGMA table_info(products)")
    existing_cols = [col[1] for col in cursor.fetchall()]
    new_cols = {
        "mrp": "REAL",
        "discount_pct": "INTEGER DEFAULT 0",
        "rating": "REAL DEFAULT 4.5",
        "review_count": "INTEGER DEFAULT 100",
        "brand": "TEXT DEFAULT ''",
        "image_url": "TEXT DEFAULT '/static/images/honey.png'",
    }
    for col_name, col_type in new_cols.items():
        if col_name not in existing_cols:
            cursor.execute(f"ALTER TABLE products ADD COLUMN {col_name} {col_type}")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            rating REAL,
            reviewer_name TEXT,
            review_text TEXT,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            price REAL NOT NULL,
            ordered_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            messages TEXT NOT NULL
        )
    """)

    products = [
        # =========================================================================
        # 1. FOOTWEAR & RUNNING SHOES
        # =========================================================================
        (101, "Nike Revolution 7",           "shoes",       2799.0, "Lightweight road running shoes with plush foam cushioning and breathable mesh.", 0, 4995.0, 44, 4.5, 2100, "Nike", "/static/images/nike_revolution_7.jpg"),
        (102, "Adidas Galaxy 6",            "shoes",       2499.0, "Everyday running sneakers featuring Cloudfoam midsole and durable outsole.",       0, 4999.0, 50, 4.4, 1800, "Adidas", "/static/images/adidas_galaxy_6.jpg"),
        (103, "Puma Softride Enzo",         "shoes",       2699.0, "Progressive running shoes with Softride EVA cushioning for extreme comfort.",      0, 4499.0, 40, 4.3, 1200, "Puma", "/static/images/puma_softride_enzo.jpg"),
        (104, "ASICS Gel-Contend 8",        "shoes",       2949.0, "Engineered running shoe with rearfoot GEL technology and AMPLIFOAM midsole.",     0, 5499.0, 46, 4.5, 1600, "ASICS", "/static/images/asics_gel_contend_8.jpg"),
        (105, "Nike Air Jordan 1 Low",      "shoes",       8995.0, "Iconic low-top streetwear sneakers inspired by the 1985 classic original.",       0, 10995.0, 18, 4.8, 3400, "Nike", "/static/images/sneakers.jpg"),
        (106, "New Balance 574 Core",       "shoes",       6499.0, "Timeless heritage runner with ENCAP midsole cushioning and suede mesh upper.",    0, 8999.0, 28, 4.6, 1420, "New Balance", "/static/images/sneakers.jpg"),
        (107, "Skechers Go Walk 6",         "shoes",       3799.0, "High-rebound ULTRA GO cushioned slip-on walking shoes with Air-Cooled Goga Mat.", 0, 5999.0, 37, 4.5, 980, "Skechers", "/static/images/sneakers.jpg"),
        (108, "Puma Smash v2 Sneaker",      "shoes",       1999.0, "Classic clean tennis-inspired suede low-top casual trainers.",                     0, 3999.0, 50, 4.2, 2300, "Puma", "/static/images/puma_softride_enzo.jpg"),
        (109, "Adidas Ultraboost Light",    "shoes",      11999.0, "Flagship running sneakers with 30% lighter BOOST material and Continental sole.", 0, 18999.0, 37, 4.7, 1150, "Adidas", "/static/images/adidas_galaxy_6.jpg"),
        (110, "Nike Pegasus 40 Running",    "shoes",       7499.0, "Springy energized road runner with dual Zoom Air units and engineered mesh.",    0, 11495.0, 35, 4.6, 1890, "Nike", "/static/images/nike_revolution_7.jpg"),

        # =========================================================================
        # 2. LAPTOPS & COMPUTERS
        # =========================================================================
        (201, "ASUS Vivobook 15 Intel i5",   "laptops",    49990.0, "Thin and light 15.6 inch FHD laptop, 16GB RAM, 512GB SSD, Windows 11.",           0, 62990.0, 21, 4.4,  850, "ASUS", "/static/images/laptop.jpg"),
        (202, "HP Pavilion 14 Ryzen 5",      "laptops",    54990.0, "Portable performance laptop with IPS display, backlit keyboard, fast charge.",    0, 69990.0, 21, 4.5, 1100, "HP", "/static/images/laptop.jpg"),
        (203, "Lenovo IdeaPad Slim 3",       "laptops",    42990.0, "Everyday multitasker laptop with Dolby Audio and military-grade durability.",     0, 59990.0, 28, 4.3,  920, "Lenovo", "/static/images/laptop.jpg"),
        (204, "Apple MacBook Air M2",        "laptops",    84990.0, "Supercharged M2 chip, 13.6-inch Liquid Retina display, 18-hour battery, 8GB/256GB.", 0, 99900.0, 15, 4.8, 4200, "Apple", "/static/images/laptop.jpg"),
        (205, "Dell Inspiron 15 3520",       "laptops",    38990.0, "Reliable home and office laptop, Intel Core i3 12th Gen, 8GB RAM, 512GB SSD.",   0, 49990.0, 22, 4.2,  740, "Dell", "/static/images/laptop.jpg"),
        (206, "Acer Predator Helios Neo 16", "laptops",    99990.0, "Intel Core i7 13th Gen, RTX 4050 6GB GPU, 165Hz IPS WUXGA gaming beast.",        0, 129990.0, 23, 4.7,  610, "Acer", "/static/images/laptop.jpg"),
        (207, "Lenovo Yoga Slim 7 Intel Evo","laptops",    74990.0, "Ultra-premium aluminum body, OLED 2.8K display, Core i7, 16GB RAM, 1TB SSD.",     0, 94990.0, 21, 4.6,  390, "Lenovo", "/static/images/laptop.jpg"),
        (208, "HP Victus Gaming Laptop 15",  "laptops",    59990.0, "AMD Ryzen 5 5600H, NVIDIA RTX 3050 4GB graphics, 144Hz display, 16GB RAM.",     0, 76990.0, 22, 4.4, 1250, "HP", "/static/images/laptop.jpg"),

        # =========================================================================
        # 3. SMARTPHONES & MOBILES
        # =========================================================================
        (301, "OnePlus Nord CE 3 Lite 5G",  "smartphones", 17999.0, "108MP camera, 67W SUPERVOOC charging, 120Hz display, 5000mAh battery.",          0, 19999.0, 10, 4.4, 4300, "OnePlus", "/static/images/smartphone.jpg"),
        (302, "Redmi Note 13 5G",           "smartphones", 16499.0, "Super slim AMOLED 120Hz screen, 108MP triple camera, Dimensity 6080.",            0, 20999.0, 21, 4.3, 3100, "Redmi", "/static/images/smartphone.jpg"),
        (303, "Samsung Galaxy M34 5G",      "smartphones", 18999.0, "120Hz Super AMOLED display, 50MP No Shake OIS camera, 6000mAh monster battery.",  0, 24499.0, 22, 4.4, 2800, "Samsung", "/static/images/smartphone.jpg"),
        (304, "Apple iPhone 15 128GB",      "smartphones", 69999.0, "Dynamic Island, 48MP Main camera with 2x Telephoto, USB-C, A16 Bionic chip.",     0, 79600.0, 12, 4.7, 6500, "Apple", "/static/images/smartphone.jpg"),
        (305, "Google Pixel 7a 5G",         "smartphones", 34999.0, "Google Tensor G2 chip, legendary Pixel camera with Real Tone, wireless charging.",0, 43999.0, 20, 4.5, 2100, "Google", "/static/images/smartphone.jpg"),
        (306, "Samsung Galaxy S23 FE 5G",   "smartphones", 44999.0, "Pro-grade triple camera with 3x optical zoom, IP68 water resistance, Gorilla Glass.", 0, 59999.0, 25, 4.5, 1950, "Samsung", "/static/images/smartphone.jpg"),
        (307, "Realme Narzo 60 5G",         "smartphones", 14999.0, "90Hz Super AMOLED screen, 64MP street photography camera, vegan leather back.",    0, 17999.0, 17, 4.2, 2400, "Realme", "/static/images/smartphone.jpg"),
        (308, "Motorola Edge 50 Fusion",    "smartphones", 22999.0, "144Hz curved pOLED display, 50MP Sony LYTIA sensor, IP68 underwater protection.",0, 27999.0, 18, 4.6, 1750, "Motorola", "/static/images/smartphone.jpg"),

        # =========================================================================
        # 4. WIRELESS AUDIO & HEADPHONES
        # =========================================================================
        (401, "Sony WH-CH520 Wireless",     "headphones",   4490.0, "50 hours battery life, multipoint connection, DSEE sound upscaling.",              0,  5990.0, 25, 4.5, 5200, "Sony", "/static/images/headphones.jpg"),
        (402, "boAt Nirvana 751 ANC",       "headphones",   3999.0, "Active Noise Cancellation up to 33dB, 65 hours playback, ASAP Charge.",             0,  7990.0, 50, 4.3, 3400, "boAt", "/static/images/headphones.jpg"),
        (403, "Sony WH-1000XM5 ANC",        "headphones",  26990.0, "Industry leading noise cancellation with two processors and 8 microphones.",       0, 34990.0, 23, 4.8, 3800, "Sony", "/static/images/headphones.jpg"),
        (404, "Apple AirPods Pro (2nd Gen)","headphones",  20990.0, "Active Noise Cancellation, Adaptive Audio, Transparency mode, USB-C MagSafe case.",0, 24900.0, 16, 4.8, 5900, "Apple", "/static/images/headphones.jpg"),
        (405, "JBL Tune 760NC Wireless",    "headphones",   5499.0, "JBL Pure Bass sound, active noise cancelling, 35-hour battery with BT and NC.",   0,  7999.0, 31, 4.4, 2100, "JBL", "/static/images/headphones.jpg"),
        (406, "OnePlus Buds Pro 2",         "headphones",   8999.0, "Dual drivers co-created with Dynaudio, 48dB Smart Adaptive Noise Cancellation.",   0, 11999.0, 25, 4.5, 1650, "OnePlus", "/static/images/headphones.jpg"),
        (407, "boAt Airdopes 141 TWS",      "headphones",   1299.0, "42 hours playback time, Beast Mode 80ms low latency for gaming, ENx mic.",       0,  4490.0, 71, 4.1, 8900, "boAt", "/static/images/headphones.jpg"),

        # =========================================================================
        # 5. HOME & KITCHEN ESSENTIALS
        # =========================================================================
        (501, "Philips Digital Air Fryer",  "kitchen",      6499.0, "Rapid Air Technology, 4.1 Liter capacity, 90% less oil cooking, touch screen.",     0,  9995.0, 35, 4.6, 3800, "Philips", "/static/images/kitchen.jpg"),
        (502, "Prestige Iris 750W Mixer",   "kitchen",      3299.0, "Heavy-duty 750 watt motor, 3 stainless steel jars plus transparent juicer jar.",   0,  6195.0, 47, 4.3, 5200, "Prestige", "/static/images/kitchen.jpg"),
        (503, "Kent Grand Plus RO Purifier","kitchen",     14999.0, "RO + UV + UF + TDS control mineral water purifier with 9L storage tank.",          0, 19500.0, 23, 4.4, 2900, "Kent", "/static/images/kitchen.jpg"),
        (504, "Pigeon Cruise Induction",    "kitchen",      1599.0, "1800W induction cooktop with 7 preset Indian cooking menus and auto-off.",         0,  3195.0, 50, 4.2, 4100, "Pigeon", "/static/images/kitchen.jpg"),
        (505, "Instant Pot Duo 7-in-1",     "kitchen",      8999.0, "Electric pressure cooker, slow cooker, rice cooker, steamer, sauté, yogurt maker.",0, 12999.0, 31, 4.7, 1850, "Instant Pot", "/static/images/kitchen.jpg"),
        (506, "Dyson V8 Cordless Vacuum",   "kitchen",     29900.0, "Powerful cord-free suction, de-tangling Motorbar cleaner head, up to 40 min run.", 0, 39900.0, 25, 4.7, 1400, "Dyson", "/static/images/kitchen.jpg"),
        (507, "Havells 15L Water Geyser",   "kitchen",      6899.0, "Feroglas coated tank with high density PUF insulation, 8 bar pressure rating.",    0, 11990.0, 42, 4.3, 1600, "Havells", "/static/images/kitchen.jpg"),
        (508, "Morphy Richards 20L Solo Oven","kitchen",    5299.0, "20-liter solo microwave with 5 power levels and defrost function.",                 0,  8495.0, 38, 4.3, 2100, "Morphy Richards", "/static/images/kitchen.jpg"),

        # =========================================================================
        # 6. SMARTWATCHES & WEARABLES
        # =========================================================================
        (601, "Apple Watch SE (2nd Gen)",   "smartwatch",  24900.0, "Crash Detection, Heart rate tracking, Sleep Stages, Retina display, 50m water resist.",0, 29900.0, 17, 4.7, 2400, "Apple", "/static/images/smartwatch.jpg"),
        (602, "Samsung Galaxy Watch 6",     "smartwatch",  19999.0, "Sapphire crystal glass, Advanced Sleep Coaching, ECG and Blood Pressure monitor.",0, 33999.0, 41, 4.5, 1350, "Samsung", "/static/images/smartwatch.jpg"),
        (603, "Noise ColorFit Pro 5",       "smartwatch",   3499.0, "1.85-inch AMOLED display with Always-On, BT calling, Post-training recovery score.",0,  7999.0, 56, 4.3, 4900, "Noise", "/static/images/smartwatch.jpg"),
        (604, "boAt Wave Call 2",           "smartwatch",   1499.0, "1.83-inch HD display, Bluetooth calling with dial pad, 700+ active fitness modes.", 0,  6990.0, 79, 4.1, 7200, "boAt", "/static/images/smartwatch.jpg"),
        (605, "Amazfit GTR 4 Superspeed",   "smartwatch",  14999.0, "Dual-band circularly-polarized GPS, 14-day battery life, 150+ sports tracking.",  0, 23999.0, 38, 4.5,  980, "Amazfit", "/static/images/smartwatch.jpg"),
        (606, "Garmin Forerunner 55 GPS",   "smartwatch",  18990.0, "Dedicated runner watch with Garmin Coach, pace guidance, and daily workout recommendations.", 0, 22990.0, 17, 4.7,  820, "Garmin", "/static/images/smartwatch.jpg"),

        # =========================================================================
        # 7. GAMING & ACCESSORIES
        # =========================================================================
        (701, "PS5 DualSense Controller",   "gaming",       5490.0, "Haptic feedback, dynamic adaptive triggers, built-in microphone for PS5 and PC.", 0,  6390.0, 14, 4.8, 3100, "Sony", "/static/images/gaming.jpg"),
        (702, "Logitech G502 HERO Mouse",   "gaming",       3895.0, "HERO 25K gaming sensor, 11 programmable buttons, adjustable weights RGB.",         0,  5495.0, 29, 4.7, 6400, "Logitech", "/static/images/gaming.jpg"),
        (703, "Redragon K552 Mech Keyboard","gaming",       2699.0, "Compact 87-key tenkeyless mechanical gaming keyboard with dust-proof red switches.",0,  3999.0, 33, 4.4, 4500, "Redragon", "/static/images/gaming.jpg"),
        (704, "Xbox Wireless Controller",   "gaming",       5190.0, "Textured grip on triggers and bumpers, hybrid D-pad, button mapping, 3.5mm jack.",0,  5990.0, 13, 4.6, 2800, "Microsoft", "/static/images/gaming.jpg"),

        # =========================================================================
        # 8. ORGANIC FOOD, GROCERIES & SUPERFOODS
        # =========================================================================
        (1,  "Organic Raw Honey",            "honey",        499.0, "Pure organic raw honey, unfiltered and cold-pressed",                1,  699.0, 28, 4.6, 240, "Nature's Sweet", "/static/images/honey.png"),
        (2,  "Wildflower Honey",             "honey",        399.0, "Natural wildflower honey from local beekeepers",                     0,  499.0, 20, 3.8, 180, "BeeWild",       "/static/images/honey.png"),
        (3,  "Organic Manuka Honey",         "honey",       1499.0, "Premium organic Manuka honey from New Zealand, MGO 400+",            1, 1999.0, 25, 4.8, 510, "Manuka Pure",   "/static/images/honey.png"),
        (4,  "Clover Honey",                 "honey",        299.0, "Classic clover honey, smooth and sweet",                             0,  349.0, 14, 3.5,  95, "SweetFarm",     "/static/images/honey.png"),
        (5,  "Organic Buckwheat Honey",      "honey",        599.0, "Dark and robust organic buckwheat honey, antioxidant-rich",          1,  799.0, 25, 4.6, 160, "Forest Gold",   "/static/images/honey.png"),
        (6,  "Orange Blossom Honey",         "honey",        499.0, "Light and floral orange blossom honey",                              0,  599.0, 17, 4.2, 130, "Citrus Bloom",  "/static/images/honey.png"),
        (7,  "Organic Acacia Honey",         "honey",        549.0, "Light and mild organic acacia honey, low glycemic index",            1,  699.0, 21, 4.7, 310, "EcoBees",       "/static/images/honey.png"),
        (8,  "Creamed Honey",                "honey",        379.0, "Smooth creamed honey with spreadable texture",                       0,  449.0, 15, 4.0, 115, "Velvet Honey",  "/static/images/honey.png"),
        (9,  "Organic Extra Virgin Olive Oil","oil",         849.0, "Cold-pressed organic EVOO from Mediterranean olives",               1, 1199.0, 29, 4.7, 420, "Oliva Organics", "/static/images/honey.png"),
        (10, "Coconut Oil",                  "oil",          399.0, "Refined coconut oil, great for high-heat cooking",                   0,  499.0, 20, 3.7, 190, "CocoCare",      "/static/images/honey.png"),
        (11, "Organic Flaxseed Oil",         "oil",          499.0, "Cold-pressed organic flaxseed oil, rich in omega-3",                 1,  649.0, 23, 4.5, 230, "NutriSeed",     "/static/images/honey.png"),
        (12, "Avocado Oil",                  "oil",          899.0, "Cold-pressed avocado oil, high smoke point",                         0, 1149.0, 22, 4.3, 175, "AvoGold",       "/static/images/honey.png"),
        (13, "Organic Almonds",              "nuts",         449.0, "Raw organic almonds, unsalted, non-GMO certified",                   1,  599.0, 25, 4.8, 380, "PureNuts",      "/static/images/oats.png"),
        (14, "Roasted Cashews",              "nuts",         399.0, "Lightly salted dry-roasted cashews",                                 0,  499.0, 20, 4.0, 210, "NutHouse",      "/static/images/oats.png"),
        (15, "Organic Chia Seeds",           "seeds",        299.0, "Organic black chia seeds, high in fiber and omega-3",                1,  399.0, 25, 4.5, 290, "SuperSeeds",    "/static/images/oats.png"),
        (16, "Mixed Nuts",                   "nuts",         549.0, "Premium mix of walnuts, pecans, almonds and Brazil nuts",            0,  699.0, 21, 3.8, 140, "Orchard Select","/static/images/oats.png"),
        (17, "Organic Quinoa",               "grains",       399.0, "Organic white quinoa, complete protein, gluten-free",                1,  499.0, 20, 4.7, 340, "AncientGrains", "/static/images/oats.png"),
        (18, "Rolled Oats",                  "grains",       199.0, "Whole grain rolled oats, great for porridge and baking",             0,  249.0, 20, 4.3, 410, "Hearty Harvest","/static/images/oats.png"),
        (19, "Organic Brown Rice",           "grains",       279.0, "Long-grain organic brown rice, naturally gluten-free",               1,  349.0, 20, 4.5, 260, "Field Green",   "/static/images/oats.png"),
        (20, "Steel-Cut Oats",               "grains",       249.0, "Traditional steel-cut oats, low GI, hearty texture",                 0,  299.0, 17, 3.8, 180, "Highland Mills","/static/images/oats.png"),
        (21, "Organic Green Tea",            "tea",          449.0, "Japanese organic sencha green tea, 50 bags",                         1,  599.0, 25, 4.7, 520, "Zen Leaf",      "/static/images/honey.png"),
        (22, "Chamomile Tea",                "tea",          329.0, "Dried chamomile flowers, caffeine-free, soothing",                   0,  399.0, 18, 4.2, 210, "Calm Herbal",   "/static/images/honey.png"),
        (23, "Organic Ethiopian Coffee",     "coffee",       799.0, "Single-origin organic Arabica, medium roast whole bean",             1,  999.0, 20, 4.8, 620, "Highland Roast","/static/images/honey.png"),
        (24, "Dark Roast Espresso Blend",    "coffee",       599.0, "Bold dark roast espresso blend, ground",                             0,  749.0, 20, 4.0, 310, "Barista Craft", "/static/images/honey.png"),
        (25, "Organic Granola",              "snacks",       349.0, "Organic oat granola with honey, almonds and dried cranberries",      1,  449.0, 22, 4.5, 190, "SunHarvest",    "/static/images/oats.png"),
        (26, "Rice Cakes",                   "snacks",       149.0, "Lightly salted brown rice cakes, low calorie snack",                 0,  199.0, 25, 3.9, 110, "FitBite",       "/static/images/oats.png"),
        (27, "Organic Dried Mango",          "snacks",       299.0, "Unsweetened organic dried mango slices, no preservatives",           1,  399.0, 25, 4.7, 240, "Tropical Pure", "/static/images/honey.png"),
        (28, "Trail Mix",                    "snacks",       329.0, "Classic trail mix with raisins, almonds, chocolate chips and peanuts",0, 399.0, 18, 4.1, 150, "Summit Foods",  "/static/images/oats.png"),
        (29, "Organic Almond Milk",          "dairy-alt",    249.0, "Unsweetened organic almond milk, fortified with calcium & B12",      1,  299.0, 17, 4.5, 310, "PlantPure",     "/static/images/oats.png"),
        (30, "Barista Oat Milk",             "dairy-alt",    229.0, "Barista-style micro-foaming oat milk, perfect for coffee and tea",   0,  279.0, 18, 4.4, 280, "OatCrafters",   "/static/images/oats.png"),
        (31, "Organic Coconut Milk",         "dairy-alt",    199.0, "Full-fat creamy organic coconut milk, ideal for curries and soups",  1,  249.0, 20, 4.5, 230, "Isle Organics", "/static/images/honey.png"),
        (32, "Soy Milk",                     "dairy-alt",    179.0, "Unsweetened high-protein soy milk made from non-GMO soybeans",       0,  219.0, 18, 4.0, 170, "SoyFresh",      "/static/images/oats.png"),
    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO products (
            id, name, category, price, description, is_organic, mrp, discount_pct, rating, review_count, brand, image_url
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, products)

    # =========================================================================
    # REVIEWS
    # =========================================================================
    reviews = [
        # Shoes
        (101, 5.0, "Rahul Sharma",    "Super lightweight and very comfortable for 5km daily jogs! Soles absorb impact nicely."),
        (101, 4.5, "Pooja Verma",     "Great fit, true to size, and excellent breathability in summer."),
        (101, 4.0, "Manish Jain",     "Very stylish black look. Traction on wet tarmac is pretty reliable."),
        (102, 4.5, "Vikas Gupta",     "Classic Adidas comfort. Cloudfoam feels plush underfoot."),
        (102, 4.5, "Amit Patel",      "Good everyday running shoe. Durable build that lasts."),
        (102, 4.0, "Kiran Rao",       "Comfortable padding around the ankle. Good value under 3k."),
        (103, 4.5, "Sneha Reddy",     "Looks awesome and feels very snug. Softride cushioning is super soft."),
        (103, 4.0, "Arjun Nair",      "Great style for gym training and light treadmill runs."),
        (104, 5.0, "Karan Malhotra",  "Rearfoot GEL cushioning really saves knees during long road runs. Top tier support!"),
        (104, 4.5, "Deepak Joshi",    "Excellent stability and arch support for flat feet."),
        (105, 5.0, "Aayush K",        "Classic Jordan 1 design. The leather quality is premium and turns heads everywhere."),
        (105, 4.5, "Tanya Sen",       "Looks fire with jeans and cargo pants. Super durable sneaker."),
        (106, 5.0, "Rohan Bose",      "New Balance 574 is unmatched for all-day walking comfort. Love the retro styling."),
        (107, 4.5, "Sunita Mehra",    "Bought for morning walks. Ultra lightweight and easy slip-on."),
        (108, 4.5, "Nikhil Roy",      "Great everyday casual wear sneaker. Suede looks rich."),
        (109, 5.0, "Abhishek Menon",  "Ultraboost energy return is phenomenal. Worth every single rupee for serious runners."),
        (110, 4.5, "Siddharth D",     "The Pegasus 40 is a true workhorse trainer. 400km logged and still going strong."),

        # Laptops
        (201, 4.5, "Anand Krishnan",  "Fast boot time with SSD, 16GB RAM handles dozens of Chrome tabs with ease."),
        (201, 4.0, "Neha Chawla",     "Battery backup is around 6-7 hours. Clean screen and comfortable keyboard."),
        (202, 4.5, "Gaurav Bansal",   "Ryzen 5 runs cool and silent. Screen color reproduction is vibrant."),
        (203, 4.5, "Divya Pillai",    "Affordable, durable, and handles university assignments seamlessly."),
        (204, 5.0, "Prateek Saxena",  "M2 MacBook Air is perfection. Silent fanless design, 18hr battery, and sleek Midnight color."),
        (204, 5.0, "Shruti Das",      "Liquid Retina display is stunning. Trackpad is the best in the industry."),
        (205, 4.0, "Harish V",        "Reliable Dell build for office spreadsheets and remote meetings."),
        (206, 5.0, "Rishi Aggarwal",  "Helios Neo 16 runs Cyberpunk and Valorant at ultra settings easily! Thermals stay under 75C."),
        (207, 4.5, "Pallavi S",       "OLED screen is gorgeous for Netflix and design work. Very light to carry."),
        (208, 4.5, "Varun Kapoor",    "Budget gaming king! RTX 3050 delivers solid 60+ FPS on all modern games."),

        # Smartphones
        (301, 4.5, "Varun Sinha",     "Camera is sharp and the 67W charging tops up 0-80% in 30 minutes!"),
        (301, 4.0, "Aditi Roy",       "Clean OxygenOS software experience. No bloatware or stutters."),
        (302, 4.5, "Manoj Kumar",     "Bezel-less AMOLED screen looks like a 40k phone. Very thin and light in hand."),
        (303, 4.5, "Suresh Nambiar",  "6000mAh battery easily lasts 2 full days of heavy use. OIS camera is great at night."),
        (304, 5.0, "Akash Trivedi",   "Dynamic Island is so intuitive. 48MP photos have DSLR-like detail and natural colors."),
        (304, 5.0, "Simran B",        "USB-C convenience at last. Smooth performance and gorgeous display brightness."),
        (305, 4.5, "Devendra G",      "Pixel camera is magic. Night Sight and portrait mode are unmatched."),
        (306, 4.5, "Meenakshi T",     "Flagship feel with Samsung One UI and great telephoto zoom."),
        (307, 4.0, "Kartik R",        "Leather orange back finish feels luxury. Good daily driver."),
        (308, 5.0, "Naveen P",        "144Hz curved screen is ultra smooth. Clean Motorola Android experience."),

        # Wireless Audio
        (401, 5.0, "Meera Iyer",      "Battery never dies! 50 hours is real, charged it once in 2 weeks."),
        (401, 4.0, "Ashwin S",        "Comfortable on ears for zoom calls. Clear mic clarity."),
        (402, 4.5, "Tanvi Mehta",     "ANC blocks air conditioner and traffic hum effectively. Good bass punch."),
        (403, 5.0, "Vikram Singhania","Best noise cancelling headphones on earth. Flight engine noise completely vanishes."),
        (403, 5.0, "Ananya Ghosh",    "Super lightweight headband. Mic quality in noisy cafes is crystal clear."),
        (404, 5.0, "Rohit Nanda",     "Transparency mode is so natural you forget you're wearing earbuds."),
        (405, 4.5, "Preeti Shah",     "Classic punchy JBL bass. Folds easily into my backpack."),
        (406, 4.5, "Saurabh V",       "Dynaudio spatial audio is immersive for movies."),
        (407, 4.0, "Chirag M",        "Insane value for ₹1,299. Battery life and loud sound are top notch."),

        # Kitchen & Home
        (501, 5.0, "Archana Deshmukh","Crispy French fries and samosas with just 1 spoon of oil! Cleanup takes 2 minutes."),
        (501, 4.5, "Kavita Rao",      "Touch presets make it foolproof. Essential kitchen appliance."),
        (502, 4.5, "Bhavna Parekh",   "750W motor crushes dry spices and idli batter without heating up."),
        (503, 4.5, "Rajesh Mathur",   "Water tastes sweet and pure. TDS controller keeps essential minerals."),
        (504, 4.5, "Geeta Sharma",    "Safe, fast, and heats water/milk in half the time of gas stoves."),
        (505, 5.0, "Smita Kulkarni",  "Instant Pot changed our weeknight dinners. Pulao and dal makhani ready in minutes."),
        (506, 5.0, "Jaideep Mukerji", "Dyson suction picks up pet hair effortlessly from carpets and hardwood floors."),
        (507, 4.5, "Umesh Chandra",   "Heats water in 10 minutes. Holds heat for hours thanks to PUF insulation."),
        (508, 4.5, "Latika Sen",      "Compact microwave, ideal for reheating and baking mug cakes."),

        # Smartwatches
        (601, 5.0, "Farhan Khan",     "Apple Watch seamlessness with iPhone is unmatched. Heart tracking gives peace of mind."),
        (602, 4.5, "Shalini Nair",    "Galaxy Watch 6 screen is bright outdoors. Sleep coaching tips actually helped my sleep."),
        (603, 4.5, "Jatin Dua",       "AMOLED screen looks crisp. Bluetooth calling is loud and clear."),
        (604, 4.0, "Alok Shukla",     "Great battery for a calling smartwatch. 4-5 days on single charge."),
        (605, 4.5, "Sameer Qureshi",  "GPS accuracy on trails is pinpoint. 14 day battery life is amazing."),
        (606, 5.0, "Virendra Bedi",   "Forerunner 55 pace guidance helped me complete my first half marathon!"),

        # Gaming
        (701, 5.0, "Yashvardhan K",   "DualSense adaptive triggers give weapon recoil feel in shooters. Remarkable innovation."),
        (702, 5.0, "Sahil Grover",    "G502 HERO thumb rest and scroll wheel are legendary. Best mouse for CS2 and productivity."),
        (703, 4.5, "Omkar Patil",     "Satisfying clicky mechanical red switch feel without paying 8k."),
        (704, 4.5, "Tushar Anand",    "Xbox controller ergonomics feel natural. Works instantly on Windows 11 PC via Bluetooth."),

        # Organic Foods & Groceries
        (1, 5.0, "Alice Brown",       "Amazing raw honey! Unfiltered texture with authentic aroma."),
        (1, 4.5, "Bob Wilson",        "Pure quality, crystalizes naturally in cold weather as real honey should."),
        (3, 5.0, "Henry Davis",       "Authentic New Zealand Manuka honey. Great for sore throats."),
        (9, 5.0, "Brian Taylor",      "Peppery kick at the back of throat proves it's genuine high-polyphenol cold pressed EVOO."),
        (13, 5.0, "Rita Sengupta",    "Crisp, sweet, and perfectly whole raw California almonds."),
        (15, 4.5, "Xena Cooper",      "Gels up nicely in overnight chia pudding. High fiber."),
        (17, 5.0, "Chloe Martin",     "Cooks fluffy and non-sticky. Clean organic grain."),
        (18, 4.5, "Finn Adams",       "Healthy rolled oats, quick wholesome breakfast."),
        (21, 5.0, "Phil Harrison",    "Delicate Japanese sencha flavor, calming with zero bitterness."),
        (23, 5.0, "Uri Goldman",      "Single-origin Ethiopian Yirgacheffe notes of bergamot and blueberry. Outstanding beans!"),
    ]

    cursor.execute("DELETE FROM reviews")
    cursor.executemany(
        "INSERT INTO reviews (product_id, rating, reviewer_name, review_text) VALUES (?, ?, ?, ?)",
        reviews,
    )

    conn.commit()
    conn.close()
    print(f"Database successfully updated with {len(products)} products and {len(reviews)} reviews at: {DB_PATH}")


if __name__ == "__main__":
    create_database()
