import sqlite3

DATABASE = "neuro_biosensors.db"

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

print("====================================")
print("DATABASE NORMALIZATION")
print("====================================")


# ============================================
# CREATE NORMALIZED TABLE
# ============================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS normalized_extractions (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    paper_id INTEGER UNIQUE,

    disease TEXT,

    biomarker TEXT,

    sensor_type TEXT,

    detection_method TEXT,

    bioreceptor TEXT,

    nanomaterial TEXT,

    electrode_material TEXT,

    sample_type TEXT,

    lod_value REAL,

    lod_unit TEXT,

    loq_value REAL,

    loq_unit TEXT,

    linear_range TEXT,

    sensitivity TEXT,

    main_finding TEXT,

    FOREIGN KEY (paper_id)
        REFERENCES papers(id)

)
""")


# ============================================
# COPY AI DATA
# ============================================

cursor.execute("""
SELECT
    e.paper_id,
    p.disease,
    e.biomarker,
    e.sensor_type,
    e.detection_method,
    e.bioreceptor,
    e.nanomaterial,
    e.electrode_material,
    e.sample_type,
    perf.lod_value,
    perf.lod_unit,
    perf.loq_value,
    perf.loq_unit,
    perf.linear_range,
    perf.sensitivity,
    e.main_finding

FROM extractions e

JOIN papers p
    ON e.paper_id = p.id

LEFT JOIN performance perf
    ON e.paper_id = perf.paper_id
""")


rows = cursor.fetchall()

print("Records found:", len(rows))


# ============================================
# NORMALIZATION FUNCTION
# ============================================

def normalize_text(value):

    if value is None:
        return ""

    value = str(value).strip()

    if value == "":
        return ""

    return value


# ============================================
# INSERT NORMALIZED DATA
# ============================================

inserted = 0

for row in rows:

    (
        paper_id,
        disease,
        biomarker,
        sensor_type,
        detection_method,
        bioreceptor,
        nanomaterial,
        electrode_material,
        sample_type,
        lod_value,
        lod_unit,
        loq_value,
        loq_unit,
        linear_range,
        sensitivity,
        main_finding
    ) = row


    # ----------------------------------------
    # Basic text normalization
    # ----------------------------------------

    disease = normalize_text(disease)
    biomarker = normalize_text(biomarker)
    sensor_type = normalize_text(sensor_type)
    detection_method = normalize_text(detection_method)
    bioreceptor = normalize_text(bioreceptor)
    nanomaterial = normalize_text(nanomaterial)
    electrode_material = normalize_text(electrode_material)
    sample_type = normalize_text(sample_type)
    linear_range = normalize_text(linear_range)
    sensitivity = normalize_text(sensitivity)
    main_finding = normalize_text(main_finding)


    # ----------------------------------------
    # Biomarker normalization
    # ----------------------------------------

    lower = biomarker.lower()

    if "amyloid" in lower and "42" in lower:
        biomarker = "Amyloid-beta 42"

    elif "amyloid" in lower and "40" in lower:
        biomarker = "Amyloid-beta 40"

    elif "alpha-synuclein" in lower or "α-synuclein" in lower:
        biomarker = "Alpha-synuclein"

    elif lower in ["tau", "total tau"]:
        biomarker = "Tau"

    elif "p-tau" in lower or "phosphorylated tau" in lower:
        biomarker = "Phosphorylated Tau"

    elif "neurofilament" in lower or "nfl" in lower:
        biomarker = "Neurofilament light chain (NfL)"


    # ----------------------------------------
    # Sensor normalization
    # ----------------------------------------

    lower = sensor_type.lower()

    if "electrochemical" in lower:
        sensor_type = "Electrochemical"

    elif "optical" in lower:
        sensor_type = "Optical"

    elif "immunosensor" in lower:
        sensor_type = "Immunosensor"

    elif "aptasensor" in lower or "aptamer" in lower:
        sensor_type = "Aptasensor"

    elif "fet" in lower:
        sensor_type = "FET"

    elif "wearable" in lower:
        sensor_type = "Wearable"


    # ----------------------------------------
    # Insert
    # ----------------------------------------

    cursor.execute("""
    INSERT OR REPLACE INTO normalized_extractions
    (
        paper_id,
        disease,
        biomarker,
        sensor_type,
        detection_method,
        bioreceptor,
        nanomaterial,
        electrode_material,
        sample_type,
        lod_value,
        lod_unit,
        loq_value,
        loq_unit,
        linear_range,
        sensitivity,
        main_finding
    )

    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,

    (
        paper_id,
        disease,
        biomarker,
        sensor_type,
        detection_method,
        bioreceptor,
        nanomaterial,
        electrode_material,
        sample_type,
        lod_value,
        lod_unit,
        loq_value,
        loq_unit,
        linear_range,
        sensitivity,
        main_finding
    ))

    inserted += 1


conn.commit()


# ============================================
# SUMMARY
# ============================================

cursor.execute("""
SELECT COUNT(*)
FROM normalized_extractions
""")

count = cursor.fetchone()[0]

print()
print("====================================")
print("NORMALIZATION COMPLETE")
print("====================================")

print("Normalized records:", count)

print()
print("Tables now available:")

print("papers")
print("extractions")
print("performance")
print("normalized_extractions")

conn.close()