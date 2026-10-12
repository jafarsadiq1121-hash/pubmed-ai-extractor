import sqlite3
import json
import ollama
import time

DATABASE = "neuro_biosensors.db"
MODEL = "llama3.2:3b"

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

# ------------------------------------------------
# Get papers that have not been processed yet
# ------------------------------------------------

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
""")

papers = cursor.fetchall()

print("====================================")
print("NEURODEGENERATIVE BIOSENSOR AI MINING")
print("====================================")

print("Papers waiting for extraction:", len(papers))


# ------------------------------------------------
# AI PROMPT
# ------------------------------------------------

def extract_information(disease, title, abstract):

    prompt = f"""
You are a biomedical literature extraction assistant.

Analyze the following research paper about a
neurodegenerative disease and biosensor.

Disease:
{disease}

Title:
{title}

Abstract:
{abstract}

Extract ONLY information explicitly supported
by the title or abstract.

Return ONLY valid JSON.

Use exactly this structure:

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

1. Do not invent information.
2. If information is not reported, use "".
3. Numeric LOD and LOQ values should be numbers only.
4. Put their units in the corresponding unit field.
5. Return JSON only.
"""

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]


# ------------------------------------------------
# Clean JSON response
# ------------------------------------------------

def parse_json(text):

    text = text.strip()

    # Remove markdown code fences if the model adds them
    if text.startswith("```"):
        lines = text.splitlines()

        if lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    try:
        return json.loads(text)

    except json.JSONDecodeError:

        # Try to find JSON between { and }
        start = text.find("{")
        end = text.rfind("}")

        if start != -1 and end != -1:

            try:
                return json.loads(
                    text[start:end + 1]
                )

            except:
                return None

        return None


# ------------------------------------------------
# Process papers
# ------------------------------------------------

success = 0
failed = 0

for index, paper in enumerate(papers, start=1):

    paper_id = paper[0]
    pmid = paper[1]
    disease = paper[2]
    title = paper[3]
    abstract = paper[4]

    print()
    print("------------------------------------")
    print(f"Processing {index}/{len(papers)}")
    print("Disease:", disease)
    print("PMID:", pmid)
    print("Title:", title[:100])
    print("------------------------------------")

    # Skip papers without abstracts
    if not abstract:

        print("No abstract available — skipped.")

        failed += 1
        continue

    try:

        ai_response = extract_information(
            disease,
            title,
            abstract
        )

        data = parse_json(ai_response)

        if data is None:

            print("JSON parsing failed.")

            failed += 1
            continue


        # ------------------------------------------------
        # Insert extraction
        # ------------------------------------------------

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

            data.get("biomarker", ""),

            data.get("sensor_type", ""),

            data.get("detection_method", ""),

            data.get("bioreceptor", ""),

            data.get("nanomaterial", ""),

            data.get("electrode_material", ""),

            data.get("sample_type", ""),

            data.get("main_finding", "")

        ))


        # ------------------------------------------------
        # Insert performance data
        # ------------------------------------------------

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

            data.get("lod_value"),

            data.get("lod_unit", ""),

            data.get("loq_value"),

            data.get("loq_unit", ""),

            data.get("linear_range", ""),

            data.get("sensitivity", "")

        ))


        conn.commit()

        success += 1

        print("AI extraction saved.")

    except Exception as e:

        print("ERROR:", e)

        failed += 1


    # Small pause
    time.sleep(0.2)


# ------------------------------------------------
# Final summary
# ------------------------------------------------

cursor.execute(
    "SELECT COUNT(*) FROM extractions"
)

extraction_count = cursor.fetchone()[0]


cursor.execute(
    "SELECT COUNT(*) FROM performance"
)

performance_count = cursor.fetchone()[0]


print()
print("====================================")
print("AI EXTRACTION COMPLETE")
print("====================================")

print("Successful:", success)
print("Failed:", failed)

print()
print("Extraction records:", extraction_count)
print("Performance records:", performance_count)

print()
print("Database:", DATABASE)

conn.close()