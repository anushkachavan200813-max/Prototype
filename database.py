
import sqlite3
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "smartpack.db"


def get_connection():
    """Create a connection to the SQLite database."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def create_tables(connection):
    """Create the food and packaging material tables."""

    connection.execute("""
        CREATE TABLE IF NOT EXISTS food_commodities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            moisture_content REAL,
            fat_content REAL,
            ph REAL,
            respiration_category TEXT,
            packaging_concerns TEXT
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS packaging_materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            material_type TEXT NOT NULL,
            oxygen_barrier TEXT,
            moisture_barrier TEXT,
            sealability TEXT,
            mechanical_strength TEXT,
            breathability TEXT,
            recyclability TEXT,
            cost_category TEXT,
            source_status TEXT NOT NULL,
            limitations TEXT
        )
    """)

    connection.commit()


def seed_foods(connection):
    """Insert example food commodities if they do not exist."""

    foods = [
        (
            "Potato Chips",
            2.0,
            35.0,
            6.0,
            "not_applicable",
            "Sensitive to oxygen, moisture and crushing"
        ),
        (
            "Biscuits",
            4.0,
            15.0,
            7.0,
            "not_applicable",
            "Moisture protection and breakage prevention"
        ),
        (
            "Mango",
            82.0,
            0.4,
            4.0,
            "high",
            "Respiration, ventilation and physical protection"
        ),
        (
            "Milk Powder",
            4.0,
            26.0,
            6.5,
            "not_applicable",
            "Moisture and oxygen protection"
        ),
        (
            "Fresh Spinach",
            92.0,
            0.4,
            6.5,
            "high",
            "Respiration, ventilation and moisture management"
        )
    ]

    connection.executemany("""
        INSERT OR IGNORE INTO food_commodities
        (
            name,
            moisture_content,
            fat_content,
            ph,
            respiration_category,
            packaging_concerns
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, foods)

    connection.commit()


def seed_materials(connection):
    """
    Insert illustrative material categories.

    These are example qualitative classifications for the prototype.
    They are not measured specifications or validated recommendations.
    """

    materials = [
        (
            "LDPE",
            "Polymer film",
            "medium",
            "high",
            "excellent",
            "medium",
            "low",
            "limited",
            "low",
            "illustrative",
            "Actual performance depends on grade, thickness and conditions."
        ),
        (
            "HDPE",
            "Polymer film",
            "medium",
            "high",
            "good",
            "high",
            "low",
            "limited",
            "low",
            "illustrative",
            "Actual performance depends on grade, thickness and conditions."
        ),
        (
            "PET",
            "Polymer film",
            "high",
            "medium",
            "limited",
            "high",
            "low",
            "limited",
            "medium",
            "illustrative",
            "PET alone may not provide the required heat-sealing layer."
        ),
        (
            "Metallized PET Laminate",
            "Multilayer laminate",
            "very_high",
            "very_high",
            "good",
            "high",
            "very_low",
            "limited",
            "medium",
            "illustrative",
            "Performance depends on metallization, laminate and seal integrity."
        ),
        (
            "Aluminum Foil Laminate",
            "Multilayer laminate",
            "very_high",
            "very_high",
            "good",
            "high",
            "very_low",
            "limited",
            "high",
            "illustrative",
            "Requires appropriate laminate structure and sealing validation."
        ),
        (
            "Breathable Film",
            "Permeable polymer film",
            "low",
            "low",
            "varies",
            "medium",
            "high",
            "varies",
            "medium",
            "illustrative",
            "Permeability and ventilation must be matched to produce respiration."
        ),
        (
            "Biodegradable Film",
            "Biodegradable polymer film",
            "varies",
            "varies",
            "varies",
            "varies",
            "varies",
            "depends_on_system",
            "medium",
            "illustrative",
            "Properties and disposal requirements vary by formulation."
        ),
        (
            "Paper-Based Packaging",
            "Paper or board",
            "low",
            "low",
            "varies",
            "medium",
            "high",
            "often_recyclable",
            "low",
            "illustrative",
            "Coatings or liners may alter barrier performance and recyclability."
        )
    ]

    connection.executemany("""
        INSERT OR IGNORE INTO packaging_materials
        (
            name,
            material_type,
            oxygen_barrier,
            moisture_barrier,
            sealability,
            mechanical_strength,
            breathability,
            recyclability,
            cost_category,
            source_status,
            limitations
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, materials)

    connection.commit()


def initialize_database():
    """Create and populate the database."""

    connection = get_connection()

    try:
        create_tables(connection)
        seed_foods(connection)
        seed_materials(connection)
    finally:
        connection.close()


def get_all_foods():
    """Return all stored food commodities."""

    connection = get_connection()

    try:
        return connection.execute("""
            SELECT *
            FROM food_commodities
            ORDER BY name
        """).fetchall()
    finally:
        connection.close()


def get_all_materials():
    """Return all stored packaging materials."""

    connection = get_connection()

    try:
        return connection.execute("""
            SELECT *
            FROM packaging_materials
            ORDER BY name
        """).fetchall()
    finally:
        connection.close()


if __name__ == "__main__":
    initialize_database()
    print("SmartPack AI database initialized successfully.")
    print(f"Database location: {DATABASE_PATH}")
    print(f"Food commodities: {len(get_all_foods())}")
    print(f"Packaging materials: {len(get_all_materials())}")