import sqlite3

DATABASE = "neuro_biosensors.db"

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

print("====================================")
print("DATABASE QUALITY CHECK")
print("====================================")


# 1. Total papers
cursor.execute("""
SELECT COUNT(*)
FROM papers
""")

papers = cursor.fetchone()[0]

print()
print("Total papers:", papers)


# 2. Total AI extractions
cursor.execute("""
SELECT COUNT(*)
FROM extractions
""")

extractions = cursor.fetchone()[0]

print("Total extractions:", extractions)


# 3. Total performance records
cursor.execute("""
SELECT COUNT(*)
FROM performance
""")

performance = cursor.fetchone()[0]

print("Performance records:", performance)


# 4. Disease distribution
print()
print("------------------------------------")
print("PAPERS BY DISEASE")
print("------------------------------------")

cursor.execute("""
SELECT disease, COUNT(*)
FROM papers
GROUP BY disease
ORDER BY COUNT(*) DESC
""")

for disease, count in cursor.fetchall():

    print(f"{disease}: {count}")


# 5. Biomarker distribution
print()
print("------------------------------------")
print("TOP BIOMARKERS")
print("------------------------------------")

cursor.execute("""
SELECT biomarker, COUNT(*)
FROM extractions
WHERE biomarker != ''
GROUP BY biomarker
ORDER BY COUNT(*) DESC
LIMIT 20
""")

for biomarker, count in cursor.fetchall():

    print(f"{biomarker}: {count}")


# 6. Sensor types
print()
print("------------------------------------")
print("SENSOR TYPES")
print("------------------------------------")

cursor.execute("""
SELECT sensor_type, COUNT(*)
FROM extractions
WHERE sensor_type != ''
GROUP BY sensor_type
ORDER BY COUNT(*) DESC
""")

for sensor, count in cursor.fetchall():

    print(f"{sensor}: {count}")


# 7. Sample types
print()
print("------------------------------------")
print("SAMPLE TYPES")
print("------------------------------------")

cursor.execute("""
SELECT sample_type, COUNT(*)
FROM extractions
WHERE sample_type != ''
GROUP BY sample_type
ORDER BY COUNT(*) DESC
""")

for sample, count in cursor.fetchall():

    print(f"{sample}: {count}")


# 8. Nanomaterials
print()
print("------------------------------------")
print("TOP NANOMATERIALS")
print("------------------------------------")

cursor.execute("""
SELECT nanomaterial, COUNT(*)
FROM extractions
WHERE nanomaterial != ''
GROUP BY nanomaterial
ORDER BY COUNT(*) DESC
LIMIT 20
""")

for material, count in cursor.fetchall():

    print(f"{material}: {count}")


# 9. Missing biomarkers
cursor.execute("""
SELECT COUNT(*)
FROM extractions
WHERE biomarker = ''
""")

missing_biomarkers = cursor.fetchone()[0]

print()
print("------------------------------------")
print("DATA COMPLETENESS")
print("------------------------------------")

print(
    "Missing biomarker:",
    missing_biomarkers
)

print(
    "Biomarker coverage:",
    round(
        ((extractions - missing_biomarkers)
        / extractions) * 100, 2
    ) if extractions else 0,
    "%"
)


# 10. Papers without extraction
cursor.execute("""
SELECT COUNT(*)
FROM papers p
LEFT JOIN extractions e
ON p.id = e.paper_id
WHERE e.paper_id IS NULL
""")

not_processed = cursor.fetchone()[0]

print(
    "Papers without extraction:",
    not_processed
)


print()
print("====================================")
print("CHECK COMPLETE")
print("====================================")

conn.close()