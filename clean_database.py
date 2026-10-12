import pandas as pd

# ============================================
# LOAD DATABASE
# ============================================

input_file = "alzheimer_biosensor_database.xlsx"

df = pd.read_excel(input_file)

print("Original rows:", len(df))


# ============================================
# REMOVE DUPLICATE PAPERS
# ============================================

df = df.drop_duplicates(subset=["PMID"])

print("After removing duplicates:", len(df))


# ============================================
# CLEAN TEXT COLUMNS
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
    "LOD",
    "LOQ",
    "Linear Range",
    "Sensitivity",
    "Main Finding"
]

for column in text_columns:

    if column in df.columns:

        df[column] = (
            df[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )


# ============================================
# STANDARDIZE SENSOR TYPES
# ============================================

if "Sensor Type" in df.columns:

    df["Sensor Type"] = (
        df["Sensor Type"]
        .str.lower()
        .replace({

            "electrochemical biosensor":
                "Electrochemical",

            "electrochemical sensor":
                "Electrochemical",

            "optical biosensor":
                "Optical",

            "optical sensor":
                "Optical",

            "wearable biosensor":
                "Wearable",

            "fet biosensor":
                "FET",

            "field effect transistor":
                "FET"

        })
    )


# ============================================
# STANDARDIZE DETECTION METHODS
# ============================================

if "Detection Method" in df.columns:

    df["Detection Method"] = (
        df["Detection Method"]
        .str.lower()
        .replace({

            "differential pulse voltammetry":
                "DPV",

            "square wave voltammetry":
                "SWV",

            "electrochemical impedance spectroscopy":
                "EIS",

            "cyclic voltammetry":
                "CV",

            "amperometric":
                "Amperometry",

            "fluorescence detection":
                "Fluorescence"

        })
    )


# ============================================
# SAVE CLEAN DATABASE
# ============================================

output_file = "alzheimer_biosensor_clean.xlsx"

df.to_excel(
    output_file,
    index=False
)


# ============================================
# SUMMARY
# ============================================

print()
print("====================================")
print("CLEANING COMPLETE")
print("====================================")

print("Final rows:", len(df))

print()
print("Created:")
print(output_file)