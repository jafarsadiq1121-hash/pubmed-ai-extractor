import requests
import xml.etree.ElementTree as ET
import pandas as pd

# --------------------------------
# STEP 1: Search PubMed
# --------------------------------

query = "Alzheimer's disease"

search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

search_params = {
    "db": "pubmed",
    "term": query,
    "retmode": "json",
    "retmax": 20
}

response = requests.get(search_url, params=search_params)

data = response.json()

pmids = data["esearchresult"]["idlist"]

print("PMIDs found:", pmids)


# --------------------------------
# STEP 2: Retrieve paper details
# --------------------------------

fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

fetch_params = {
    "db": "pubmed",
    "id": ",".join(pmids),
    "retmode": "xml"
}

response = requests.get(fetch_url, params=fetch_params)

root = ET.fromstring(response.text)


# --------------------------------
# STEP 3: Extract information
# --------------------------------

papers = []

for article in root.findall(".//PubmedArticle"):

    pmid = article.findtext(".//PMID")

    title = article.findtext(".//ArticleTitle")

    journal = article.findtext(".//Journal/Title")

    year = article.findtext(".//PubDate/Year")

    abstract_parts = article.findall(".//AbstractText")

    abstract = " ".join(
        part.text or "" for part in abstract_parts
    )

    papers.append({
        "PMID": pmid,
        "Title": title,
        "Journal": journal,
        "Year": year,
        "Abstract": abstract
    })


# --------------------------------
# STEP 4: Create Excel file
# --------------------------------

df = pd.DataFrame(papers)

df.to_excel("alzheimer_pubmed_papers.xlsx", index=False)

print("\nDone! 🎉")
print("Saved:", len(papers), "papers")

print("\nExcel file:")
print("alzheimer_pubmed_papers.xlsx")