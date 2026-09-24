import os
import json
import pandas as pd
from openai import OpenAI


# ============================================
# STEP 1: Connect to OpenAI
# ============================================

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)


# ============================================
# STEP 2: Read PubMed Excel file
# ============================================

input_file = "alzheimer_pubmed_papers.xlsx"

df = pd.read_excel(input_file)

print("Papers loaded:", len(df))


# ============================================
# STEP 3: Prepare list for AI extraction
# ============================================

results = []

for index, row in df.iterrows():

    print(f"\nProcessing paper {index + 1}/{len(df)}")

    abstract = row["Abstract"]

    # Skip papers without an abstract
    if pd.isna(abstract) or not str(abstract).strip():
        print("No abstract — skipping.")
        continue

    # ========================================
    # AI prompt
    # ========================================

    prompt = f"""
You are a biomedical research assistant.

Analyze the following scientific abstract about Alzheimer's disease.

Extract the following information:

1. Biomarkers
2. Genes
3. Proteins
4. Drugs or therapeutic compounds
5. Molecular pathways
6. Diseases or conditions
7. Main research finding

Return ONLY valid JSON using exactly this structure:

{{
    "biomarkers": [],
    "genes": [],
    "proteins": [],
    "drugs": [],
    "pathways": [],
    "diseases": [],
    "main_finding": ""
}}

Scientific abstract:

{abstract}
"""

    try:

        # ====================================
        # Send request to OpenAI
        # ====================================

        response = client.responses.create(
            model="gpt-5-mini",
            input=prompt
        )

        answer = response.output_text

        # ====================================
        # Convert AI response to JSON
        # ====================================

        extracted = json.loads(answer)

    except Exception as e:

        print("AI error:", e)

        extracted = {
            "biomarkers": [],
            "genes": [],
            "proteins": [],
            "drugs": [],
            "pathways": [],
            "diseases": [],
            "main_finding": "Extraction failed"
        }


    # ========================================
    # Save result
    # ========================================

    results.append({

        "PMID": row["PMID"],

        "Title": row["Title"],

        "Journal": row["Journal"],

        "Year": row["Year"],

        "Biomarkers":
            ", ".join(extracted.get("biomarkers", [])),

        "Genes":
            ", ".join(extracted.get("genes", [])),

        "Proteins":
            ", ".join(extracted.get("proteins", [])),

        "Drugs":
            ", ".join(extracted.get("drugs", [])),

        "Pathways":
            ", ".join(extracted.get("pathways", [])),

        "Diseases":
            ", ".join(extracted.get("diseases", [])),

        "Main Finding":
            extracted.get("main_finding", "")
    })


# ============================================
# STEP 4: Create final DataFrame
# ============================================

output = pd.DataFrame(results)


# ============================================
# STEP 5: Save Excel file
# ============================================

output_file = "alzheimer_ai_extracted.xlsx"

output.to_excel(
    output_file,
    index=False
)


# ============================================
# DONE
# ============================================

print("\n====================================")
print("🎉 AI EXTRACTION COMPLETE!")
print("====================================")

print("Papers processed:", len(output))

print("Output file:")
print(output_file)