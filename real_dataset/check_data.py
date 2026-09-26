# import pandas as pd

# file_path = "real_dataset/clean_material_data.csv"
# df = pd.read_csv(file_path)

# print("Dataset shape:", df.shape)

# print("\nColumn names:")
# print(df.columns.tolist())

# print("\nData types:")
# print(df.dtypes)

# print("\nFirst 5 rows:")
# print(df.head())

# print("\nMissing values:")
# print(df.isnull().sum())

# for col in ["Base Material", "Type", "Secondary Material"]:
#     if col in df.columns:
#         print(f"\nUnique values in {col}:")
#         print(df[col].dropna().unique())

# import pandas as pd

# df = pd.read_csv("real_dataset/semi-processed_2.csv")

# for col in [
#     "OP_Unit", "OTR_Unit", "PCO2_Unit",
#     "WVTR_Unit", "WVP_Unit",
#     "thickness_Unit", "temperature_Unit", "RH_Unit"
# ]:
#     print(f"\n{col}")
#     print(df[col].value_counts(dropna=False).to_string())

# print("\nRows with measurements:")
# for col in [
#     "OP_Updated_Num", "OTR_Updated_Num", "PCO2_Updated_Num",
#     "WVTR_Updated_Num", "WVP_Updated_Num"
# ]:
#     print(col, df[col].notna().sum())

# import pandas as pd

# df = pd.read_csv("real_dataset/semi-processed_2.csv")

# cols = [
#     "Base Material",
#     "Type",
#     "Secondary Material",
#     "WVP_Updated_Num",
#     "WVP_Unit",
#     "thickness_Updated_Num",
#     "thickness_Unit",
#     "temperature_Updated_Num",
#     "temperature_Unit",
#     "RH_Updated_Num",
#     "RH_Unit"
# ]

# wvp_rows = df[cols].dropna(subset=["WVP_Updated_Num"])

# print("WVP records:")
# print(wvp_rows.to_string(index=False))

# print("\nWVP unit counts:")
# print(wvp_rows["WVP_Unit"].value_counts(dropna=False))

# condition_cols = [
#     "thickness_Updated_Num",
#     "temperature_Updated_Num",
#     "RH_Updated_Num"
# ]

# complete = wvp_rows.dropna(subset=condition_cols)
# print("\nWVP rows with all three condition values:", len(complete))

# import pandas as pd

# df = pd.read_csv("real_dataset/semi-processed_2.csv")

# # Keep WVP values with the main unit and all condition fields recorded
# condition_cols = [
#     "thickness_Updated_Num",
#     "temperature_Updated_Num",
#     "RH_Updated_Num"
# ]

# subset = df[
#     (df["WVP_Unit"] == "gm/m2Pas")
#     & df["WVP_Updated_Num"].notna()
# ].dropna(subset=condition_cols).copy()

# print("Rows in consistent-unit subset:", len(subset))

# print("\nDistinct test conditions:")
# print(
#     subset.groupby(condition_cols, dropna=False)
#     .size()
#     .reset_index(name="row_count")
#     .to_string(index=False)
# )

# print("\nMaterial categories in subset:")
# print(subset["Base Material"].value_counts(dropna=False).to_string())

# import pandas as pd

# df = pd.read_csv("real_dataset/semi-processed_2.csv")

# subset = df[
#     (df["WVP_Unit"] == "gm/m2Pas")
#     & (df["WVP_Updated_Num"].notna())
#     & (df["temperature_Updated_Num"] == 25)
#     & (df["RH_Updated_Num"] == 50)
# ].copy()

# print("Records at 25°C and 50% RH:", len(subset))

# print("\nMaterial counts:")
# print(subset["Base Material"].value_counts(dropna=False).to_string())

# print("\nRecords:")
# print(subset[
#     ["Base Material", "Type", "Secondary Material",
#      "WVP_Updated_Num", "thickness_Updated_Num"]
# ].to_string(index=False))

import pandas as pd

df = pd.read_csv("real_dataset/semi-processed_2.csv")

subset = df[
    (df["WVP_Unit"] == "gm/m2Pas")
    & (df["WVP_Updated_Num"].notna())
    & (df["temperature_Updated_Num"] == 25)
    & (df["RH_Updated_Num"] == 50)
].copy()

summary = (
    subset.groupby("Base Material")["WVP_Updated_Num"]
    .agg(
        record_count="count",
        median_wvp="median",
        minimum_wvp="min",
        maximum_wvp="max"
    )
    .reset_index()
    .sort_values("median_wvp")
)

summary.to_csv(
    "real_dataset/wvp_summary_25C_50RH.csv",
    index=False
)

print(summary.to_string(index=False))
print("\nSaved: real_dataset/wvp_summary_25C_50RH.csv")
