import sqlite3

conn = sqlite3.connect('database.db')
cur = conn.cursor()

phones = [
    # --- Samsung ---
    ("Samsung Galaxy S24", 50, 4000, 8, 6.2, 799, "s24.jpg"),
    ("Samsung Galaxy S24 Ultra", 200, 5000, 12, 6.8, 1299, "s24_ultra.jpg"),
    ("Samsung Galaxy S24+", 50, 4900, 12, 6.7, 999, "s24_plus.jpg"),
    ("Samsung Galaxy A55", 50, 5000, 8, 6.6, 399, "a55.jpg"),
    ("Samsung Galaxy A35", 50, 5000, 6, 6.6, 299, "a35.jpg"),
    ("Samsung Galaxy M34", 50, 6000, 6, 6.5, 249, "m34.jpg"),

    # --- Apple ---
    ("iPhone 15", 48, 3349, 6, 6.1, 799, "iphone15.jpg"),
    ("iPhone 15 Plus", 48, 4383, 6, 6.7, 899, "iphone15plus.jpg"),
    ("iPhone 15 Pro", 48, 3274, 8, 6.1, 999, "iphone15pro.jpg"),
    ("iPhone 15 Pro Max", 48, 4422, 8, 6.7, 1199, "iphone15promax.jpg"),
    ("iPhone 14", 12, 3279, 6, 6.1, 699, "iphone14.jpg"),
    ("iPhone 13", 12, 3227, 4, 6.1, 599, "iphone13.jpg"),

    # --- Xiaomi ---
    ("Xiaomi 14", 50, 4610, 12, 6.36, 899, "xiaomi14.jpg"),
    ("Xiaomi 14 Ultra", 50, 5000, 16, 6.73, 1299, "xiaomi14_ultra.jpg"),
    ("Xiaomi Redmi Note 13 Pro", 200, 5100, 8, 6.67, 299, "note13pro.jpg"),
    ("Xiaomi Redmi Note 13", 108, 5000, 6, 6.67, 199, "note13.jpg"),
    ("Xiaomi Poco X6 Pro", 64, 5000, 12, 6.67, 349, "poco_x6_pro.jpg"),
    ("Xiaomi Poco F6", 50, 5000, 12, 6.67, 499, "poco_f6.jpg"),

    # --- Google ---
    ("Google Pixel 8", 50, 4575, 8, 6.2, 699, "pixel8.jpg"),
    ("Google Pixel 8 Pro", 50, 5050, 12, 6.7, 999, "pixel8pro.jpg"),
    ("Google Pixel 7a", 64, 4385, 8, 6.1, 349, "pixel7a.jpg"),

    # --- OnePlus ---
    ("OnePlus 12", 50, 5400, 12, 6.82, 799, "oneplus12.jpg"),
    ("OnePlus 12R", 50, 5500, 8, 6.78, 499, "oneplus12r.jpg"),
    ("OnePlus Nord 3", 50, 5000, 8, 6.74, 449, "nord3.jpg"),

    # --- Nothing ---
    ("Nothing Phone 2", 50, 4700, 8, 6.7, 599, "nothing2.jpg"),
    ("Nothing Phone 2a", 50, 5000, 8, 6.7, 349, "nothing2a.jpg"),

    # --- Vivo ---
    ("Vivo V30", 50, 5000, 12, 6.78, 499, "vivo_v30.jpg"),
    ("Vivo X100", 50, 5000, 12, 6.78, 899, "vivo_x100.jpg"),

    # --- Realme ---
    ("Realme GT Neo 5", 50, 5000, 12, 6.74, 399, "gt_neo_5.jpg"),
    ("Realme 12 Pro+", 64, 5000, 8, 6.7, 379, "realme12pro.jpg"),

    # --- Honor ---
    ("Honor Magic 6 Pro", 50, 5600, 12, 6.8, 1099, "magic6pro.jpg"),

    # --- Motorola ---
    ("Motorola Edge 40", 50, 4400, 8, 6.55, 499, "edge40.jpg"),
]

cur.executemany("""
    INSERT INTO phones (name, camera, battery, ram, screen, price, image_name)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", phones)

conn.commit()
conn.close()
print("Done! 30 real smartphones have been added to the database.")
