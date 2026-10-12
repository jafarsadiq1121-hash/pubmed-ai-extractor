import requests
import pandas as pd
import xml.etree.ElementTree as ET


# ============================================
# SETTINGS
# ============================================

RETMAX = 50

OUTPUT_FILE = "alzheimer_biosensor_pubmed.xlsx"


# ============================================
# PUBMED SEARCH QUERY
# ============================================

query = '''
(
    "Alzheimer Disease"[MeSH Terms]
    OR "Alzheimer's disease"
    OR "Alzheimer disease"
)
AND
(
    biosensor
    OR "bio sensor"
    OR "electrochemical sensor"
    OR "electrochemical biosensor"
    OR "optical biosensor"
    OR "wearable biosensor"
    OR immunosensor
    OR aptasensor
    OR "FET biosensor"
)
'''


# ============================================
# STEP 1 — SEARCH PUBMED
# ============================================

search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

search_params = {
    "db": "pubmed",
    "term": query,
    "retmode": "json",
    "retmax": RETMAX
}

print("Searching PubMed...")

response = requests.get(
    search_url,
    params=search_params,
    timeout=30
)

response.raise_for_status()

data = response.json()

pmids = data["esearchresult"]["idlist"]

print()
print("Papers found:", len(pmids))


if not pmids:
    print("No papers found.")
    exit()


# ============================================
# STEP 2 — FETCH PUBMED RECORDS
# ============================================

fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

fetch_params = {
    "db": "pubmed",
    "id": ",".join(pmids),
    "retmode": "xml"
}

print()
print("Downloading paper information...")

response = requests.get(
    fetch_url,
    params=fetch_params,
    timeout=60
)

response.raise_for_status()

xml_text = response.text


# ============================================
# STEP 3 — CHECK XML
# ============================================

print()
print("XML downloaded.")
print("XML length:", len(xml_text))


# ============================================
# STEP 4 — PARSE XML
# ============================================

root = ET.fromstring(xml_text)

papers = []


# IMPORTANT:
# PubMed records are inside PubmedArticleSet

articles = root.findall(".//PubmedArticle")

print("PubMed articles detected:", len(articles))


# ============================================
# STEP 5 — EXTRACT EACH PAPER
# ============================================

for article in articles:

    # ----------------------------------------
    # PMID
    # ----------------------------------------

    pmid_element = article.find(".//PMID")

    if pmid_element is not None:
        pmid = pmid_element.text
    else:
        pmid = ""


    # ----------------------------------------
    # TITLE
    # ----------------------------------------

    title_element = article.find(".//ArticleTitle")

    if title_element is not None:
        title = "".join(title_element.itertext())
    else:
        title = ""


    # ----------------------------------------
    # JOURNAL
    # ----------------------------------------

    journal_element = article.find(
        ".//Journal/Title"
    )

    if journal_element is not None:
        journal = journal_element.text or ""
    else:
        journal = ""


    # ----------------------------------------
    # ABSTRACT
    # ----------------------------------------

    abstract_parts = []

    for abstract_element in article.findall(
        ".//Abstract/AbstractText"
    ):

        text = "".join(
            abstract_element.itertext()
        )

        if text:
            abstract_parts.append(text)

    abstract = " ".join(abstract_parts)


    # ----------------------------------------
    # PUBLICATION YEAR
    # ----------------------------------------

    year = ""


    # First try JournalIssue PubDate
    year_element = article.find(
        ".//JournalIssue/PubDate/Year"
    )

    if (
        year_element is not None
        and year_element.text
    ):

        year = year_element.text.strip()


    # Second possibility
    if not year:

        year_element = article.find(
            ".//PubDate/Year"
        )

        if (
            year_element is not None
            and year_element.text
        ):

            year = year_element.text.strip()


    # Third possibility: MedlineDate
    if not year:

        medline_date = article.find(
            ".//PubDate/MedlineDate"
        )

        if (
            medline_date is not None
            and medline_date.text
        ):

            date_text = medline_date.text.strip()

            if (
                len(date_text) >= 4
                and date_text[:4].isdigit()
            ):

                year = date_text[:4]


    # ----------------------------------------
    # VALIDATE YEAR
    # ----------------------------------------

    if (
        not year.isdigit()
        or len(year) != 4
    ):

        year = ""


    # ----------------------------------------
    # SAVE PAPER
    # ----------------------------------------

    papers.append({

        "PMID": pmid,

        "Title": title,

        "Journal": journal,

        "Year": year,

        "Abstract": abstract

    })


# ============================================
# STEP 6 — CREATE DATAFRAME
# ============================================

df = pd.DataFrame(papers)


# ============================================
# STEP 7 — YEAR AS NUMERIC
# ============================================

if not df.empty:

    df["Year"] = pd.to_numeric(
        df["Year"],
        errors="coerce"
    ).astype("Int64")


# ============================================
# STEP 8 — YEAR CHECK
# ============================================

print()
print("====================================")
print("YEAR CHECK")
print("====================================")

if not df.empty:

    print(
        df["Year"]
        .value_counts()
        .sort_index()
        .to_string()
    )

else:

    print("No papers were extracted.")


# ============================================
# STEP 9 — SAVE EXCEL
# ============================================

df.to_excel(
    OUTPUT_FILE,
    index=False
)


# ============================================
# STEP 10 — FINAL REPORT
# ============================================

print()
print("====================================")
print("PUBMED DOWNLOAD COMPLETE")
print("====================================")

print("Papers saved:", len(df))

if not df.empty:

    print(
        "Papers with year:",
        df["Year"].notna().sum()
    )

    print(
        "Papers without year:",
        df["Year"].isna().sum()
    )

print()
print("Created:")
print(OUTPUT_FILE)