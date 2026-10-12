import sqlite3
import pandas as pd

DATABASE = "neuro_biosensors.db"

conn = sqlite3.connect(DATABASE)

query = """
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
"""

df = pd.read_sql_query(query, conn)

print("====================================")
print("UNPROCESSED PAPERS")
print("====================================")

print("Total unprocessed:", len(df))

if not df.empty:

    missing_abstracts = (
        df["abstract"].isna()
        | df["abstract"].astype(str).str.strip().eq("")
    )

    print("Missing abstracts:", missing_abstracts.sum())

    print(
        "Papers with abstracts:",
        (~missing_abstracts).sum()
    )

    print("\nPapers by disease:")

    print(
        df.groupby("disease")
        .size()
        .sort_values(ascending=False)
        .to_string()
    )

    output_file = "unprocessed_papers.xlsx"

    df.to_excel(output_file, index=False)

    print("\nCreated:", output_file)

else:

    print("All papers have extraction records.")

conn.close()