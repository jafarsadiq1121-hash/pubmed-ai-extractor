
import json
import pandas as pd
import ollama


# ============================================
# 1. Load PubMed data
# ============================================

input_file =  "alzheimer_biosensor_pubmed.xlsx"
output_file = "biosensor_data_2026_papers.xlsx"
df = pd.read_excel(input_file)

print("====================================")
print("ALZHEIMER'S BIOSENSOR MINING")
print("====================================")
print("Total papers:", len(df))


# ============================================
# 2. Store results
# ============================================

results = []


# ============================================
# 3. Function to safely parse AI JSON
# ============================================

def clean_json_response(answer):

    answer = answer.strip()

    # Remove Markdown code fences
    answer = answer.replace("```json", "")
    answer = answer.replace("```", "")

    answer = answer.strip()

    # Find the first JSON object
    start = answer.find("{")
    end = answer.rfind("}")

    if start != -1 and end != -1:

        answer = answer[start:end + 1]

    return json.loads(answer)


# ============================================
# 4. Process papers
# ============================================

for index, row in df.iterrows():

    print()
    print("------------------------------------")
    print(f"Processing paper {index + 1}/{len(df)}")
    print("------------------------------------")

    abstract = row["Abstract"]

    if pd.isna(abstract) or not str(abstract).strip():

        print("No abstract found. Skipping.")

        continue


    # ========================================
    # 5. AI prompt
    # ========================================

    prompt = f"""
You are an expert biomedical literature-mining assistant
specialized in Alzheimer's disease and biosensors.

Analyze the scientific abstract below.

Extract ONLY information explicitly supported by the abstract.

Do NOT invent information.

Extract:

1. Disease
2. Biomarker / analyte
3. Sensor type
4. Detection method
5. Bioreceptor
6. Nanomaterial
7. Electrode material
8. Sample type
9. Limit of detection (LOD)
10. Limit of quantification (LOQ)
11. Linear detection range
12. Sensitivity
13. Main finding

If a field is not reported, return an empty string.

Return ONLY a JSON object.

Do NOT write explanations.
Do NOT use Markdown.
Do NOT put ``` around the JSON.

The JSON must have exactly these fields:

{{
    "disease": "",
    "biomarker": "",
    "sensor_type": "",
    "detection_method": "",
    "bioreceptor": "",
    "nanomaterial": "",
    "electrode_material": "",
    "sample_type": "",
    "lod": "",
    "loq": "",
    "linear_range": "",
    "sensitivity": "",
    "main_finding": ""
}}

ABSTRACT:

{abstract}
"""


    # ========================================
    # 6. Send to Ollama
    # ========================================

    try:

        response = ollama.chat(

            model="llama3.2:3b",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            format="json"
        )

        answer = response["message"]["content"]

        print("AI response received.")


        # ====================================
        # 7. Parse JSON
        # ====================================

        try:

            extracted = clean_json_response(answer)

        except Exception as e:

            print("JSON parsing failed.")

            print("Raw AI response:")
            print(answer)

            extracted = {

                "disease": "",
                "biomarker": "",
                "sensor_type": "",
                "detection_method": "",
                "bioreceptor": "",
                "nanomaterial": "",
                "electrode_material": "",
                "sample_type": "",
                "lod": "",
                "loq": "",
                "linear_range": "",
                "sensitivity": "",
                "main_finding": "JSON parsing failed"

            }


    except Exception as e:

        print("AI ERROR:", e)

        extracted = {

            "disease": "",
            "biomarker": "",
            "sensor_type": "",
            "detection_method": "",
            "bioreceptor": "",
            "nanomaterial": "",
            "electrode_material": "",
            "sample_type": "",
            "lod": "",
            "loq": "",
            "linear_range": "",
            "sensitivity": "",
            "main_finding": "AI extraction failed"

        }


    # ========================================
    # 8. Save result
    # ========================================

    results.append({

        "PMID": row["PMID"],

        "Title": row["Title"],

        "Journal": row["Journal"],

        "Year": row["Year"],

        "Disease":
            extracted.get("disease", ""),

        "Biomarker":
            extracted.get("biomarker", ""),

        "Sensor Type":
            extracted.get("sensor_type", ""),

        "Detection Method":
            extracted.get("detection_method", ""),

        "Bioreceptor":
            extracted.get("bioreceptor", ""),

        "Nanomaterial":
            extracted.get("nanomaterial", ""),

        "Electrode Material":
            extracted.get("electrode_material", ""),

        "Sample Type":
            extracted.get("sample_type", ""),

        "LOD":
            extracted.get("lod", ""),

        "LOQ":
            extracted.get("loq", ""),

        "Linear Range":
            extracted.get("linear_range", ""),

        "Sensitivity":
            extracted.get("sensitivity", ""),

        "Main Finding":
            extracted.get("main_finding", "")

    })


# ============================================
# 9. Create DataFrame
# ============================================

output = pd.DataFrame(results)


# ============================================
# 10. Save database
# ============================================

output_file = "biosensor_data_of_2026_papers.xlsx"

output.to_excel(
    output_file,
    index=False
)


# ============================================
# 11. Finished
# ============================================

print()
print("====================================")
print("🎉 BIOSENSOR MINING COMPLETE!")
print("====================================")

print("Papers processed:", len(output))

print()
print("Created:")
print(output_file)