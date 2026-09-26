
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


# Paths relative to this script
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "training_data.csv"
MODEL_FILE = BASE_DIR / "packaging_model.pkl"


def train_model():
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_FILE}\n"
            "Check that training_data.csv is inside the ml folder."
        )

    data = pd.read_csv(DATA_FILE)

    # The model learns from the food and packaging properties.
    # The label is the example outcome we want it to predict.
    target_column = "label"
    categorical_features = [
        "food",
        "respiration_category",
        "storage_type",
        "material",
        "oxygen_barrier",
        "moisture_barrier",
        "sealability",
        "mechanical_strength",
        "breathability",
    ]
    numeric_features = [
        "moisture_content",
        "fat_content",
        "ph",
        "shelf_life_days",
        "storage_temp_c",
        "relative_humidity",
    ]

    required_columns = categorical_features + numeric_features + [target_column]
    missing_columns = [
        column for column in required_columns if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            "The CSV is missing these required columns: "
            + ", ".join(missing_columns)
        )

    data = data[required_columns].dropna()

    X = data[categorical_features + numeric_features]
    y = data[target_column]

    if y.nunique() < 2:
        raise ValueError("The dataset must contain at least two label classes.")

    # Keep a small test set aside to demonstrate evaluation.
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    # Convert text categories into numeric columns for the model.
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                categorical_features,
            ),
            ("numeric", "passthrough", numeric_features),
        ]
    )

    model_pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=100,
                    random_state=42,
                    class_weight="balanced",
                ),
            ),
        ]
    )

    model_pipeline.fit(X_train, y_train)

    predictions = model_pipeline.predict(X_test)

    print("\nModel evaluation (illustrative dataset only)")
    print("---------------------------------------------")
    print(f"Test accuracy: {accuracy_score(y_test, predictions):.2f}")
    print("\nClassification report:")
    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0,
        )
    )

    # Save both the trained pipeline and the expected input columns.
    saved_model = {
        "pipeline": model_pipeline,
        "categorical_features": categorical_features,
        "numeric_features": numeric_features,
        "classes": list(model_pipeline.classes_),
    }

    joblib.dump(saved_model, MODEL_FILE)

    print(f"\nTrained model saved to: {MODEL_FILE}")


if __name__ == "__main__":
    train_model()