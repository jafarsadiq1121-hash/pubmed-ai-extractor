import pandas as pd
import re

# ============================================
# FILES
# ============================================

input_file = "biosensor_data_of_2026_papers.xlsx"
output_file = "biosensor_data_cleaned.xlsx"

# ============================================
# LOAD DATA
# ============================================

print("Loading Excel file...")

df = pd.read_excel(input_file)

print("Rows:", len(df))
print("Columns:", df.columns.tolist())

# ============================================
# BASIC TEXT CLEANING
# ============================================

text_columns = [
    "Disease",
    "Biomarker",
    "Sensor Type",
    "Detection Method",
    "Bioreceptor",
    "Nanomaterial",
    "Electrode Material",
    "Sample Type",
]

for col in text_columns:
    if col in df.columns:

        df[col] = (
            df[col]
            .fillna("Not reported")
            .astype(str)
            .str.strip()
        )

        # Remove repeated spaces
        df[col] = df[col].str.replace(
            r"\s+",
            " ",
            regex=True
        )

# ============================================
# BIOMARKER STANDARDIZATION
# ============================================

if "Biomarker" in df.columns:

    def clean_biomarker(value):

        v = value.lower().strip()

        # Amyloid beta
        if (
            "amyloid" in v
            or "aβ" in v
            or "a-beta" in v
            or "amyloid-β" in v
        ):
            return "Amyloid-β"

        # Tau
        if "tau" in v:
            return "Tau"

        # GFAP
        if "gfap" in v:
            return "GFAP"

        # Neurofilament
        if (
            "neurofilament" in v
            or "nfl" in v
        ):
            return "Neurofilament light (NfL)"

        # AChE
        if (
            "acetylcholinesterase" in v
            or "ache" in v
        ):
            return "Acetylcholinesterase (AChE)"

        # BACE1
        if "bace" in v:
            return "BACE1"

        return value.strip()

    df["Biomarker"] = df["Biomarker"].apply(clean_biomarker)

# ============================================
# SENSOR TYPE STANDARDIZATION
# ============================================

if "Sensor Type" in df.columns:

    def clean_sensor(value):

        v = value.lower().strip()

        if "electrochemical" in v:
            return "Electrochemical"

        if (
            "optical" in v
            or "fluorescen" in v
            or "colorimetric" in v
            or "surface plasmon" in v
        ):
            return "Optical"

        if (
            "fet" in v
            or "field effect" in v
        ):
            return "FET"

        if "aptasensor" in v:
            return "Aptasensor"

        if "immunosensor" in v:
            return "Immunosensor"

        if "wearable" in v:
            return "Wearable"

        return value.strip()

    df["Sensor Type"] = df["Sensor Type"].apply(clean_sensor)

# ============================================
# SAMPLE TYPE STANDARDIZATION
# ============================================

if "Sample Type" in df.columns:

    def clean_sample(value):

        v = value.lower().strip()

        if "serum" in v:
            return "Serum"

        if "plasma" in v:
            return "Plasma"

        if "cerebrospinal" in v or v == "csf":
            return "CSF"

        if "blood" in v:
            return "Blood"

        if "saliva" in v:
            return "Saliva"

        if "urine" in v:
            return "Urine"

        if "sweat" in v:
            return "Sweat"

        return value.strip()

    df["Sample Type"] = df["Sample Type"].apply(clean_sample)

# ============================================
# DETECTION METHOD STANDARDIZATION
# ============================================

if "Detection Method" in df.columns:

    def clean_method(value):

        v = value.lower().strip()

        if "impedance" in v or "eis" in v:
            return "EIS"

        if (
            "differential pulse" in v
            or "dpv" in v
        ):
            return "DPV"

        if (
            "square wave" in v
            or "swv" in v
        ):
            return "SWV"

        if "amperometric" in v:
            return "Amperometry"

        if "voltammetric" in v:
            return "Voltammetry"

        if "fluorescen" in v:
            return "Fluorescence"

        if "colorimetric" in v:
            return "Colorimetric"

        if "surface plasmon" in v or "spr" in v:
            return "SPR"

        return value.strip()

    df["Detection Method"] = df["Detection Method"].apply(clean_method)

# ============================================
# REMOVE DUPLICATE PAPERS
# ============================================

if "PMID" in df.columns:

    before = len(df)

    df = df.drop_duplicates(
        subset=["PMID"],
        keep="first"
    )

    after = len(df)

    print("Duplicate papers removed:", before - after)

# ============================================
# SAVE CLEAN DATA
# ============================================

df.to_excel(
    output_file,
    index=False
)

print()
print("====================================")
print("CLEANING COMPLETE")
print("====================================")

print("Rows:", len(df))
print("Created:", output_file)

# ============================================
# SHOW IMPORTANT CATEGORIES
# ============================================

print()
print("BIOMARKERS:")
print(df["Biomarker"].value_counts().to_string())

print()
print("SENSOR TYPES:")
print(df["Sensor Type"].value_counts().to_string())

print()
print("DETECTION METHODS:")
print(df["Detection Method"].value_counts().to_string())

print()
print("SAMPLE TYPES:")
print(df["Sample Type"].value_counts().to_string())