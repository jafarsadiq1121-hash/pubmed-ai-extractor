import sqlite3
import json
import ollama
import time

DATABASE = "neuro_biosensors.db"
MODEL = "llama3.2:3b"

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

# Find papers that have not been processed
cursor.execute("""
SELECT
    p.id,
    p.pmid,
    p.disease,
    p.title,
    p.abstract
FROM papers p
LEFT JOIN extractions e
    ON p.id = e.paper_id
WHERE e.paper_id IS NULL
ORDER BY p.disease, p.pmid
""")

papers = cursor.fetchall()

print("=" * 50)
print("PROCESSING MISSING NEURODEGENERATIVE PAPERS")
print("=" * 50)

print("Unprocessed papers:", len(papers))

success = 0
failed = 0
skipped = 0


def extract_information(disease, title, abstract):

    prompt = f"""
You are a biomedical literature extraction assistant.

Extract information explicitly supported by this
research paper's title and abstract.

Disease: {disease}
Title: {title}
Abstract: {abstract}

Return ONLY valid JSON using exactly this structure:

{{
    "biomarker": "",
    "sensor_type": "",
    "detection_method": "",
    "bioreceptor": "",
    "nanomaterial": "",
    "electrode_material": "",
    "sample_type": "",
    "lod_value": null,
    "lod_unit": "",
    "loq_value": null,
    "loq_unit": "",
    "linear_range": "",
    "sensitivity": "",
    "main_finding": ""
}}

Rules:
1. Never invent information.
2. Use empty strings for unreported text fields.
3. Use null for unreported LOD and LOQ values.
4. LOD and LOQ values must be numbers only.
5. Keep measurement units in their respective unit fields.
6. Return JSON only.
"""

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        format="json"
    )

    return response["message"]["content"]


def parse_json(response_text):

    try:
        data = json.loads(response_text)

        required_fields = [
            "biomarker",
            "sensor_type",
            "detection_method",
            "bioreceptor",
            "nanomaterial",
            "electrode_material",
            "sample_type",
            "lod_value",
            "lod_unit",
            "loq_value",
            "loq_unit",
            "linear_range",
            "sensitivity",
            "main_finding"
        ]

        # Check that the response contains all required fields
        for field in required_fields:
            if field not in data:
                return None

        return data

    except (json.JSONDecodeError, TypeError):
        return None


for index, paper in enumerate(papers, start=1):

    paper_id, pmid, disease, title, abstract = paper

    print()
    print("-" * 50)
    print(f"Paper {index}/{len(papers)}")
    print("PMID:", pmid)
    print("Disease:", disease)
    print("Title:", (title or "")[:100])

    # Skip papers without abstracts
    if not abstract or not abstract.strip():

        print("Skipped: abstract unavailable.")
        skipped += 1
        continue

    try:

        response_text = extract_information(
            disease,
            title,
            abstract
        )

        data = parse_json(response_text)

        if data is None:
            print("Failed: invalid JSON or missing fields.")
            failed += 1
            continue

        # Use a transaction so both records are saved together.
        # Recheck the extraction record before inserting.
        cursor.execute(
            "SELECT 1 FROM extractions WHERE paper_id = ?",
            (paper_id,)
        )

        if cursor.fetchone():
            print("Skipped: extraction already exists.")
            skipped += 1
            continue

        cursor.execute("""
            INSERT INTO extractions
            (
                paper_id,
                biomarker,
                sensor_type,
                detection_method,
                bioreceptor,
                nanomaterial,
                electrode_material,
                sample_type,
                main_finding
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            paper_id,
            data["biomarker"],
            data["sensor_type"],
            data["detection_method"],
            data["bioreceptor"],
            data["nanomaterial"],
            data["electrode_material"],
            data["sample_type"],
            data["main_finding"]
        ))

        cursor.execute("""
            INSERT INTO performance
            (
                paper_id,
                lod_value,
                lod_unit,
                loq_value,
                loq_unit,
                linear_range,
                sensitivity
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            paper_id,
            data["lod_value"],
            data["lod_unit"],
            data["loq_value"],
            data["loq_unit"],
            data["linear_range"],
            data["sensitivity"]
        ))

        conn.commit()

        success += 1
        print("SUCCESS: extraction and performance data saved.")

    except Exception as error:

        conn.rollback()
        failed += 1

        print("ERROR:", error)

    time.sleep(0.2)


# Final database counts
cursor.execute("SELECT COUNT(*) FROM extractions")
extraction_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM performance")
performance_count = cursor.fetchone()[0]

cursor.execute("""
SELECT COUNT(*)
FROM papers p
LEFT JOIN extractions e ON p.id = e.paper_id
WHERE e.paper_id IS NULL
""")

remaining = cursor.fetchone()[0]

print()
print("=" * 50)
print("PROCESSING SUMMARY")
print("=" * 50)

print("Successfully processed:", success)
print("Failed:", failed)
print("Skipped:", skipped)
print("Extraction records:", extraction_count)
print("Performance records:", performance_count)
print("Papers still without extraction:", remaining)

conn.close()