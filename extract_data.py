from docx import Document
import csv
from pathlib import Path

input_file = Path("real_dataset/41538_2026_741_MOESM1_ESM.docx")
output_file = Path("real_dataset/raw_material_data.csv")

doc = Document(input_file)
rows = []

for table in doc.tables:
    for row in table.rows:
        values = [cell.text.strip().replace("\n", " ") for cell in row.cells]

        # Skip completely empty rows
        if any(values):
            # Avoid adding repeated column-header rows
            if values[0].strip().lower() == "doc":
                if not rows:
                    rows.append(values)
                continue

            rows.append(values)

if rows:
    with output_file.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerows(rows)

    print(f"Saved {len(rows) - 1} data rows to: {output_file}")
else:
    print("No table rows were found. Check the document structure.")