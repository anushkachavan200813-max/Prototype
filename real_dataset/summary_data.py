import pandas as pd

df = pd.read_csv("real_dataset/clean_material_data.csv")

print("Measurement summary:")
print(df[["OTR (cm3/m2day)", "WVTR (g/m2day)"]].describe())

print("\nRows by base material:")
print(df["Base Material"].value_counts())

print("\nRows by type:")
print(df["Type"].value_counts())

print("\nRows by secondary material (including missing):")
print(df["Secondary Material"].fillna("Missing").value_counts())

print("\nExact duplicate rows:", df.duplicated().sum())

print("\nFull summary by base material:")
material_summary = df.groupby("Base Material")[
    ["OTR (cm3/m2day)", "WVTR (g/m2day)"]
].agg(["count", "min", "median", "max"])

print(material_summary.to_string())

print("\nFull summary by type:")
type_summary = df.groupby("Type")[
    ["OTR (cm3/m2day)", "WVTR (g/m2day)"]
].agg(["count", "min", "median", "max"])

print(type_summary.to_string())