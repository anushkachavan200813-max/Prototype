
from pathlib import Path
import sqlite3

import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DATABASE_FILE = BASE_DIR / "smartpack.db"
MODEL_FILE = BASE_DIR / "ml" / "packaging_model.pkl"


def get_db_connection():
    connection = sqlite3.connect(DATABASE_FILE)
    connection.row_factory = sqlite3.Row
    return connection


def load_model():
    if not MODEL_FILE.exists():
        raise FileNotFoundError(
            "Trained model not found. Run: python ml/train_model.py"
        )

    return joblib.load(MODEL_FILE)


def get_food(food_id):
    connection = get_db_connection()
    try:
        return connection.execute(
            "SELECT * FROM food_commodities WHERE id = ?",
            (food_id,),
        ).fetchone()
    finally:
        connection.close()


def get_materials():
    connection = get_db_connection()
    try:
        return connection.execute(
            "SELECT * FROM packaging_materials"
        ).fetchall()
    finally:
        connection.close()


def build_model_input(food, material, details):
    return {
        "food": food["name"],
        "moisture_content": float(food["moisture_content"]),
        "fat_content": float(food["fat_content"]),
        "ph": float(food["ph"]),
        "respiration_category": food["respiration_category"],
        "shelf_life_days": details["shelf_life_days"],
        "storage_type": details["storage_type"],
        "storage_temp_c": details["storage_temp_c"],
        "relative_humidity": details["relative_humidity"],
        "material": material["name"],
        "oxygen_barrier": material["oxygen_barrier"],
        "moisture_barrier": material["moisture_barrier"],
        "sealability": material["sealability"],
        "mechanical_strength": material["mechanical_strength"],
        "breathability": material["breathability"],
    }


def recommend_materials(food_id, top_n=5, details=None):
    food = get_food(food_id)
    if food is None:
        raise ValueError("Food item not found in the database.")

    if details is None:
        details = {
            "shelf_life_days": 30,
            "storage_type": "Ambient",
            "storage_temp_c": 25,
            "relative_humidity": 50,
        }

    materials = get_materials()
    if not materials:
        return []

    saved_model = load_model()
    pipeline = saved_model["pipeline"]
    positive_label = "candidate_for_review"

    rows = [
        build_model_input(food, material, details)
        for material in materials
    ]
    input_data = pd.DataFrame(rows)

    predictions = pipeline.predict(input_data)

    candidate_probabilities = None
    if hasattr(pipeline, "predict_proba"):
        classes = list(pipeline.classes_)
        if positive_label in classes:
            candidate_index = classes.index(positive_label)
            candidate_probabilities = pipeline.predict_proba(input_data)[
                :, candidate_index
            ]

    results = []
    for index, material in enumerate(materials):
        prediction = str(predictions[index])
        is_candidate = prediction == positive_label

        score = (
            float(candidate_probabilities[index])
            if candidate_probabilities is not None
            else None
        )

        results.append(
            {
                "material_id": material["id"],
                "material_name": material["name"],
                "prediction": prediction,
                "candidate_for_review": is_candidate,
                "model_score": score,
                "limitations": material["limitations"],
                "source_status": material["source_status"],
            }
        )

    results.sort(
        key=lambda item: (
            item["candidate_for_review"],
            item["model_score"] if item["model_score"] is not None else -1,
        ),
        reverse=True,
    )

    return results[:top_n]


if __name__ == "__main__":
    try:
        example_details = {
            "shelf_life_days": 30,
            "storage_type": "Ambient",
            "storage_temp_c": 25,
            "relative_humidity": 50,
        }

        output = recommend_materials(
            food_id=1,
            top_n=5,
            details=example_details,
        )

        for item in output:
            print(
                item["material_name"],
                "| Prediction:", item["prediction"],
                "| Demo score:", item["model_score"],
            )

    except Exception as error:
        print("Error:", error)