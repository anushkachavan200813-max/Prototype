import pandas as pd

input_file = "real_dataset/raw_material_data.csv"
output_file = "real_dataset/clean_material_data.csv"

df = pd.read_csv(input_file)

# Convert measurement columns to numbers.
# Remove commas used as thousands separators, e.g. "2,731.40".
for col in ["OTR (cm3/m2day)", "WVTR (g/m2day)"]:
    df[col] = pd.to_numeric(
        df[col].astype(str).str.replace(",", "", regex=False),
        errors="coerce"
    )

# Keep rows that have both measurements.
clean_df = df.dropna(
    subset=["OTR (cm3/m2day)", "WVTR (g/m2day)"]
).copy()

clean_df.to_csv(output_file, index=False)

print("Rows in original file:", len(df))
print("Rows with both measurements:", len(clean_df))
print("Saved cleaned file to:", output_file)