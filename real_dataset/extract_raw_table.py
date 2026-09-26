from docx import Document
import csv
from pathlib import Path

input_file = Path("real_dataset/41538_2026_741_MOESM1_ESM.docx")
output_file = Path("real_dataset/semi-processed_2.csv")

doc = Document(input_file)

# In this document, Supplementary Table 4 is the fourth table.
table = doc.tables[3]

# The CSV header is embedded in the first table cell after the table title.
first_cell_lines = table.rows[0].cells[0].text.splitlines()
header_line = next(
    (line.strip() for line in first_cell_lines if line.strip().startswith(",Doc,")),
    None
)

if header_line is None:
    raise ValueError("Could not find the raw CSV header in Supplementary Table 4.")

header = next(csv.reader([header_line]))

with output_file.open("w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(header)

    written = 0
    for row in table.rows[1:]:
        raw_line = row.cells[0].text.strip()
        if not raw_line:
            continue

        values = next(csv.reader([raw_line]))
        writer.writerow(values)
        written += 1

print("Saved raw table rows:", written)
print("Number of columns:", len(header))
print("Output file:", output_file)