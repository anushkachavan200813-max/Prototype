
from flask import Flask, render_template, request

from database import initialize_database, get_all_foods, get_all_materials
from recommendation import recommend_materials
from io import BytesIO
from xml.sax.saxutils import escape

from flask import send_file
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)

import pandas as pd
from pathlib import Path


app = Flask(__name__)

initialize_database()


@app.route("/")
def home():
    foods = get_all_foods()
    return render_template("index.html", foods=foods)

@app.route("/materials")
def materials():
    materials_list = get_all_materials()

    summary_path = (
        Path(__file__).resolve().parent
        / "real_dataset"
        / "wvp_summary_25C_50RH.csv"
    )

    if summary_path.exists():
        wvp_summary = pd.read_csv(summary_path).to_dict(orient="records")
    else:
        wvp_summary = []

    return render_template(
        "material.html",
        materials=materials_list,
        wvp_summary=wvp_summary
    )


@app.route("/recommend", methods=["POST"])
def recommend():
    food_id = request.form.get("food_id", "").strip()

    details = {
        "shelf_life_days": request.form.get("shelf_life_days", "").strip(),
        "storage_type": request.form.get("storage_type", "").strip(),
        "storage_temp_c": request.form.get("storage_temp_c", "").strip(),
        "relative_humidity": request.form.get("relative_humidity", "").strip()
    }

    try:
        if not food_id or any(value == "" for value in details.values()):
            return "Please fill in all fields.", 400

        details["shelf_life_days"] = int(details["shelf_life_days"])
        details["storage_temp_c"] = float(details["storage_temp_c"])
        details["relative_humidity"] = float(details["relative_humidity"])

        if details["shelf_life_days"] <= 0:
            return "Shelf life must be greater than zero.", 400
        if not 0 <= details["relative_humidity"] <= 100:
            return "Relative humidity must be between 0 and 100.", 400

        foods = get_all_foods()
        food = next(
            (item for item in foods if str(item["id"]) == food_id),
            None
        )

        if food is None:
            return "Selected food was not found.", 404

        # Create results BEFORE passing them to the template.
        results = recommend_materials(
            food_id=int(food_id),
            top_n=5,
            details=details
        )

        print("Selected food ID:", food_id)
        print("Materials in database:", len(get_all_materials()))
        print("Recommendation results:", results)
        print("Number of results:", len(results) if results else 0)

        return render_template(
            "results.html",
            results=results,
            food=food,
            food_id=food_id,
            details=details
        )

    except Exception as error:
        app.logger.exception("Unexpected error during recommendation.")
        return f"Recommendation failed: {error}", 500

@app.route("/report", methods=["POST"])
def download_report():
    food_id = request.form.get("food_id", "").strip()

    details = {
        "shelf_life_days": request.form.get("shelf_life_days", "").strip(),
        "storage_type": request.form.get("storage_type", "").strip(),
        "storage_temp_c": request.form.get("storage_temp_c", "").strip(),
        "relative_humidity": request.form.get("relative_humidity", "").strip()
    }

    # Check that all required values are present and numeric fields are valid.
    try:
        if not food_id or any(value == "" for value in details.values()):
            return "Please provide all screening details.", 400

        details["shelf_life_days"] = int(details["shelf_life_days"])
        details["storage_temp_c"] = float(details["storage_temp_c"])
        details["relative_humidity"] = float(details["relative_humidity"])

        if details["shelf_life_days"] <= 0:
            return "Shelf life must be greater than zero.", 400
        if not 0 <= details["relative_humidity"] <= 100:
            return "Relative humidity must be between 0 and 100.", 400

        foods = get_all_foods()
        food = next((item for item in foods if str(item["id"]) == food_id), None)

        if food is None:
            return "Selected food was not found.", 404

        results = recommend_materials(
            food_id=int(food_id),
            top_n=5,
            details=details
        )

    except (ValueError, TypeError):
        return "Please enter valid numeric values.", 400

    # Build the PDF in memory.
    pdf_buffer = BytesIO()
    document = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("SmartPack AI — Screening Report", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "Food: " + escape(str(food["name"])),
        styles["Normal"]
    ))
    story.append(Paragraph(
        "Target shelf life: " + escape(str(details["shelf_life_days"])) + " days",
        styles["Normal"]
    ))
    story.append(Paragraph(
        "Storage: " + escape(str(details["storage_type"])),
        styles["Normal"]
    ))
    story.append(Paragraph(
        "Storage temperature: " + escape(str(details["storage_temp_c"])) + " °C",
        styles["Normal"]
    ))
    story.append(Paragraph(
        "Relative humidity: " + escape(str(details["relative_humidity"])) + "%",
        styles["Normal"]
    ))
    story.append(Spacer(1, 16))

    table_data = [["Material", "Model screening", "Demo score", "Data status"]]

    for item in results:
        table_data.append([
            Paragraph(escape(str(item.get("material_name", "—"))), styles["BodyText"]),
            Paragraph(escape(str(item.get("prediction", "—"))), styles["BodyText"]),
            Paragraph(
                escape(
                    str(round(float(item["score"]) * 100, 1) if item.get("score") is not None else "—")
                    + ("%" if item.get("score") is not None else "")
                ),
                styles["BodyText"]
            ),
            Paragraph(escape(str(item.get("source_status", "Illustrative"))), styles["BodyText"])
        ])

    results_table = Table(table_data, repeatRows=1, colWidths=[130, 130, 75, 130])
    results_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 6)
    ]))
    story.append(results_table)
    story.append(Spacer(1, 14))

    story.append(Paragraph(
        "<b>Important:</b> This is an academic prototype. The model uses "
        "illustrative demonstration data. Its outputs are preliminary screening "
        "results, not validated packaging recommendations, food-safety advice, "
        "or proof of regulatory compliance. Confirm material suitability through "
        "qualified testing and applicable standards before real-world use.",
        styles["BodyText"]
    ))

    document.build(story)
    pdf_buffer.seek(0)

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name="smartpack_screening_report.pdf",
        mimetype="application/pdf"
    )

if __name__ == "__main__":
    app.run(debug=True)