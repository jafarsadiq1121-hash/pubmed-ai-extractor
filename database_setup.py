import sqlite3

DATABASE = "neuro_biosensors.db"

# Connect to database
conn = sqlite3.connect(DATABASE)

cursor = conn.cursor()


# ============================================
# PAPERS TABLE
# ============================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS papers (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    pmid TEXT UNIQUE,

    disease TEXT,

    title TEXT,

    journal TEXT,

    year INTEGER,

    abstract TEXT,

    doi TEXT

)
""")


# ============================================
# EXTRACTIONS TABLE
# ============================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS extractions (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    paper_id INTEGER,

    biomarker TEXT,

    sensor_type TEXT,

    detection_method TEXT,

    bioreceptor TEXT,

    nanomaterial TEXT,

    electrode_material TEXT,

    sample_type TEXT,

    main_finding TEXT,

    FOREIGN KEY (paper_id)
        REFERENCES papers(id)

)
""")


# ============================================
# PERFORMANCE TABLE
# ============================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS performance (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    paper_id INTEGER,

    lod_value REAL,

    lod_unit TEXT,

    loq_value REAL,

    loq_unit TEXT,

    linear_range TEXT,

    sensitivity TEXT,

    FOREIGN KEY (paper_id)
        REFERENCES papers(id)

)
""")


# ============================================
# CREATE INDEXES
# ============================================

cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_pmid
ON papers(pmid)
""")


cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_disease
ON papers(disease)
""")


cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_biomarker
ON extractions(biomarker)
""")


# Save
conn.commit()

# Close
conn.close()


print("====================================")
print("DATABASE CREATED")
print("====================================")

print("Database:", DATABASE)

print()
print("Tables created:")
print("1. papers")
print("2. extractions")
print("3. performance")