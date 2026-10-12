import requests
import sqlite3
import xml.etree.ElementTree as ET
import time

# ============================================
# DATABASE
# ============================================

DATABASE = "neuro_biosensors.db"

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

# ============================================
# DISEASES
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
# BIOSENSOR SEARCH TERMS
# ============================================

biosensor_terms = """
(
    biosensor
    OR "electrochemical biosensor"
    OR "electrochemical sensor"
    OR "optical biosensor"
    OR "wearable biosensor"
    OR immunosensor
    OR aptasensor
    OR "FET biosensor"
)
"""

# Number of papers per disease
RETMAX = 100

SEARCH_URL = (
    "https://eutils.ncbi.nlm.nih.gov/"
    "entrez/eutils/esearch.fcgi"
)

FETCH_URL = (
    "https://eutils.ncbi.nlm.nih.gov/"
    "entrez/eutils/efetch.fcgi"
)


# ============================================
# FUNCTION: SEARCH PUBMED
# ============================================

def search_pubmed(query):

    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": RETMAX
    }

    response = requests.get(
        SEARCH_URL,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    return data["esearchresult"]["idlist"]


# ============================================
# FUNCTION: FETCH PAPERS
# ============================================

def fetch_papers(pmids):

    if not pmids:
        return []

    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml"
    }

    response = requests.get(
        FETCH_URL,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return ET.fromstring(response.text)


# ============================================
# START
# ============================================

print("====================================")
print("PUBMED → SQLITE")
print("====================================")

total_new = 0
total_existing = 0


# ============================================
# PROCESS EACH DISEASE
# ============================================

for disease, disease_query in diseases.items():

    print()
    print("------------------------------------")
    print("Disease:", disease)
    print("------------------------------------")

    query = f"""
    ({disease_query})
    AND
    {biosensor_terms}
    """

    try:

        pmids = search_pubmed(query)

        print("PubMed papers found:", len(pmids))

        if not pmids:
            continue

        root = fetch_papers(pmids)

        disease_new = 0
        disease_existing = 0


        # ====================================
        # PROCESS ARTICLES
        # ====================================

        for article in root.findall(".//PubmedArticle"):

            # -------------------------------
            # PMID
            # -------------------------------

            pmid_element = article.find(".//PMID")

            if pmid_element is None:
                continue

            pmid = pmid_element.text


            # -------------------------------
            # CHECK IF PAPER ALREADY EXISTS
            # -------------------------------

            cursor.execute(
                "SELECT id FROM papers WHERE pmid = ?",
                (pmid,)
            )

            existing = cursor.fetchone()

            if existing:

                disease_existing += 1
                total_existing += 1

                continue


            # -------------------------------
            # TITLE
            # -------------------------------

            title_element = article.find(
                ".//ArticleTitle"
            )

            title = ""

            if title_element is not None:

                title = "".join(
                    title_element.itertext()
                )


            # -------------------------------
            # ABSTRACT
            # -------------------------------

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


            # -------------------------------
            # JOURNAL
            # -------------------------------

            journal_element = article.find(
                ".//Journal/Title"
            )

            journal = ""

            if journal_element is not None:

                journal = journal_element.text


            # -------------------------------
            # YEAR
            # -------------------------------

            year = None

            year_element = article.find(
                ".//PubDate/Year"
            )

            if year_element is not None:

                try:
                    year = int(
                        year_element.text
                    )

                except:
                    year = None


            # -------------------------------
            # DOI
            # -------------------------------

            doi = ""

            for article_id in article.findall(
                ".//ArticleId"
            ):

                id_type = article_id.attrib.get(
                    "IdType"
                )

                if id_type == "doi":

                    doi = article_id.text

                    break


            # =================================
            # INSERT INTO SQLITE
            # =================================

            cursor.execute(
                """
                INSERT INTO papers
                (
                    pmid,
                    disease,
                    title,
                    journal,
                    year,
                    abstract,
                    doi
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    pmid,
                    disease,
                    title,
                    journal,
                    year,
                    abstract,
                    doi
                )
            )


            disease_new += 1
            total_new += 1


        conn.commit()


        print(
            "New papers added:",
            disease_new
        )

        print(
            "Already in database:",
            disease_existing
        )


        # Be polite to NCBI
        time.sleep(1)


    except Exception as e:

        print(
            "ERROR:",
            e
        )


# ============================================
# FINAL SUMMARY
# ============================================

cursor.execute(
    "SELECT COUNT(*) FROM papers"
)

total_database = cursor.fetchone()[0]


print()
print("====================================")
print("IMPORT COMPLETE")
print("====================================")

print(
    "New papers added:",
    total_new
)

print(
    "Already existed:",
    total_existing
)

print(
    "Total papers in database:",
    total_database
)


# ============================================
# DISEASE SUMMARY
# ============================================

print()
print("Disease distribution:")
print("------------------------------------")

cursor.execute(
    """
    SELECT disease, COUNT(*)
    FROM papers
    GROUP BY disease
    ORDER BY COUNT(*) DESC
    """
)

for disease, count in cursor.fetchall():

    print(
        f"{disease}: {count}"
    )


# ============================================
# CLOSE DATABASE
# ============================================

conn.close()

print()
print("Database:")
print(DATABASE)