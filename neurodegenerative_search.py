import requests
import pandas as pd
import time

# ============================================
# NEURODEGENERATIVE DISEASES
# ============================================

diseases = {

    "Alzheimer's disease":
        '"Alzheimer Disease"[MeSH Terms] OR "Alzheimer disease"',

    "Parkinson's disease":
        '"Parkinson Disease"[MeSH Terms] OR "Parkinson disease"',

    "Amyotrophic lateral sclerosis":
        '"Amyotrophic Lateral Sclerosis"[MeSH Terms] OR ALS',

    "Huntington's disease":
        '"Huntington Disease"[MeSH Terms] OR "Huntington disease"',

    "Lewy body dementia":
        '"Lewy Body Disease"[MeSH Terms] OR "Lewy body dementia"',

    "Frontotemporal dementia":
        '"Frontotemporal Dementia"[MeSH Terms] OR "frontotemporal dementia"',

    "Progressive supranuclear palsy":
        '"Progressive Supranuclear Palsy"[MeSH Terms] OR "progressive supranuclear palsy"',

    "Multiple system atrophy":
        '"Multiple System Atrophy"[MeSH Terms] OR "multiple system atrophy"'
}


# ============================================
# BIOSENSOR TERMS
# ============================================

biosensor_terms = """
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
"""


# ============================================
# SETTINGS
# ============================================

RETMAX = 100

search_url = (
    "https://eutils.ncbi.nlm.nih.gov/"
    "entrez/eutils/esearch.fcgi"
)

fetch_url = (
    "https://eutils.ncbi.nlm.nih.gov/"
    "entrez/eutils/efetch.fcgi"
)


# ============================================
# STORE ALL PAPERS
# ============================================

all_papers = []

seen_pmids = set()


# ============================================
# SEARCH EACH DISEASE
# ============================================

for disease_name, disease_query in diseases.items():

    print()
    print("====================================")
    print("SEARCHING:", disease_name)
    print("====================================")

    query = f"""
    (
        {disease_query}
    )
    AND
    {biosensor_terms}
    """

    # ----------------------------------------
    # PubMed search
    # ----------------------------------------

    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": RETMAX
    }

    response = requests.get(
        search_url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    pmids = data["esearchresult"]["idlist"]

    print("Papers found:", len(pmids))


    if not pmids:
        continue


    # ----------------------------------------
    # Fetch paper details
    # ----------------------------------------

    fetch_params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml"
    }

    response = requests.get(
        fetch_url,
        params=fetch_params,
        timeout=30
    )

    response.raise_for_status()


    # ----------------------------------------
    # Parse XML
    # ----------------------------------------

    import xml.etree.ElementTree as ET

    root = ET.fromstring(response.text)


    for article in root.findall(".//PubmedArticle"):

        pmid_element = article.find(".//PMID")

        if pmid_element is None:
            continue

        pmid = pmid_element.text


        # Avoid duplicate papers
        if pmid in seen_pmids:
            continue

        seen_pmids.add(pmid)


        # Title
        title_element = article.find(
            ".//ArticleTitle"
        )

        title = ""

        if title_element is not None:
            title = "".join(
                title_element.itertext()
            )


        # Abstract
        abstract_parts = []

        for abstract_text in article.findall(
            ".//AbstractText"
        ):

            abstract_parts.append(
                "".join(
                    abstract_text.itertext()
                )
            )

        abstract = " ".join(
            abstract_parts
        )


        # Journal
        journal_element = article.find(
            ".//Journal/Title"
        )

        journal = ""

        if journal_element is not None:
            journal = journal_element.text


        # Year
        year = ""

        year_element = article.find(
            ".//PubDate/Year"
        )

        if year_element is not None:

            year = year_element.text

        else:

            medline_date = article.find(
                ".//PubDate/MedlineDate"
            )

            if medline_date is not None:

                year = medline_date.text[:4]


        # Save paper
        all_papers.append({

            "PMID": pmid,

            "Disease": disease_name,

            "Title": title,

            "Journal": journal,

            "Year": year,

            "Abstract": abstract

        })


    # Be polite to NCBI
    time.sleep(1)


# ============================================
# CREATE DATAFRAME
# ============================================

df = pd.DataFrame(all_papers)


# ============================================
# SAVE
# ============================================

output_file = (
    "neurodegenerative_biosensor_pubmed.xlsx"
)

df.to_excel(
    output_file,
    index=False
)


# ============================================
# SUMMARY
# ============================================

print()
print("====================================")
print("SEARCH COMPLETE")
print("====================================")

print(
    "Unique papers collected:",
    len(df)
)

print()
print("Disease distribution:")

if not df.empty:

    print(
        df["Disease"]
        .value_counts()
        .to_string()
    )

print()
print("Created:")
print(output_file)