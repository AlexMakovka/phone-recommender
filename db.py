import sqlite3
import os
import csv
from datetime import datetime

DB_PATH = "database.db"


def get_connection():
    """
    Returns a connection to the SQLite database.
    """
    conn = sqlite3.connect(DB_PATH)
    return conn


def init_db():
    """
    Creates tables if they do not exist:
    - phones: smartphone catalog
    - interactions: user interaction history
    """
    conn = get_connection()
    cur = conn.cursor()

    # Phones table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS phones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        camera INTEGER NOT NULL,
        battery INTEGER NOT NULL,
        ram INTEGER NOT NULL,
        screen REAL NOT NULL,
        price INTEGER NOT NULL,
        image_name TEXT
    )
    """)

    # Interaction history table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS interactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        user TEXT NOT NULL,
        preferences TEXT,
        recommended_phones TEXT
    )
    """)

    conn.commit()
    conn.close()


def seed_phones_from_csv(csv_path="data/phones.csv"):
    """
    One-time population of the phones table from a CSV file if the table is empty.
    """
    if not os.path.exists(csv_path):
        print(f"[seed_phones_from_csv] File {csv_path} not found, skipping import.")
        return

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM phones")
    count = cur.fetchone()[0]
    if count > 0:
        # Table already has data – do nothing
        conn.close()
        return

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    for row in rows:
        name = row["Name"]
        camera = int(row["Camera"])
        battery = int(row["Battery"])
        ram = int(row["RAM"])
        screen = float(row["Screen"])
        price = int(row["Price"])

        # Generate image filename based on model name
        # Example: "PhotoMaster 3000" -> "PhotoMaster_3000.jpg"
        image_name = name.replace(" ", "_") + ".jpg"

        cur.execute(
            """
            INSERT INTO phones (name, camera, battery, ram, screen, price, image_name)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (name, camera, battery, ram, screen, price, image_name),
        )

    conn.commit()
    conn.close()
    print(f"[seed_phones_from_csv] Imported {len(rows)} phones.")


def get_all_phones():
    """
    Returns a list of phones in the same format as CSV:
    list of dictionaries with keys Name, Camera, Battery, RAM, Screen, Price.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT name, camera, battery, ram, screen, price, image_name
        FROM phones
    """)
    rows = cur.fetchall()
    conn.close()

    phones = []
    for name, camera, battery, ram, screen, price, image_name in rows:
        phones.append({
            "Name": name,
            "Camera": camera,
            "Battery": battery,
            "RAM": ram,
            "Screen": screen,
            "Price": price,
            "Image": image_name,  # for future use if needed
        })

    return phones


def log_interaction(user_id, user_prefs, recommended_phones):
    """
    Saves a recommendation record into the interactions table.
    """
    conn = get_connection()
    cur = conn.cursor()

    ts = datetime.now().isoformat(timespec="seconds")
    prefs_str = ";".join(user_prefs) if user_prefs else ""
    rec_names = ";".join([p["Name"] for p in recommended_phones]) if recommended_phones else ""

    user_str = user_id if user_id else "guest"

    cur.execute(
        """
        INSERT INTO interactions (timestamp, user, preferences, recommended_phones)
        VALUES (?, ?, ?, ?)
        """,
        (ts, user_str, prefs_str, rec_names),
    )

    conn.commit()
    conn.close()


def get_user_history(user_id, limit=10):
    """
    Returns the last `limit` interaction records for the specified user (by name).
    Each record format:
    {
        "timestamp": ...,
        "preferences": [...],
        "recommended_phones": [...]
    }
    """
    if not user_id:
        return []

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT timestamp, preferences, recommended_phones
        FROM interactions
        WHERE user = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (user_id, limit),
    )

    rows = cur.fetchall()
    conn.close()

    history = []
    for ts, prefs_str, rec_str in rows:
        prefs = prefs_str.split(";") if prefs_str else []
        recs = rec_str.split(";") if rec_str else []
        history.append({
            "timestamp": ts,
            "preferences": prefs,
            "recommended_phones": recs,
        })

    return history
