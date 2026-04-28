"""
PubMed search tool - fetches real medical literature.
Uses NCBI E-utilities API (free, no key required).
"""

import requests
import xml.etree.ElementTree as ET


def search_pubmed(query: str, max_results: int = 5) -> list:
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    search_params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "json",
        "sort": "relevance",
    }

    try:
        search_resp = requests.get(f"{base_url}/esearch.fcgi", params=search_params, timeout=10)
        ids = search_resp.json().get("esearchresult", {}).get("idlist", [])

        if not ids:
            return []

        fetch_resp = requests.get(f"{base_url}/efetch.fcgi", params={
            "db": "pubmed", "id": ",".join(ids), "retmode": "xml"
        }, timeout=10)

        root = ET.fromstring(fetch_resp.content)
        articles = []

        for article in root.findall(".//PubmedArticle"):
            title_el = article.find(".//ArticleTitle")
            abstract_el = article.find(".//AbstractText")
            year_el = article.find(".//PubDate/Year")
            pmid_el = article.find(".//PMID")

            authors = []
            for author in article.findall(".//Author")[:3]:
                last = author.find("LastName")
                if last is not None:
                    authors.append(last.text)

            pmid = pmid_el.text if pmid_el is not None else ""
            articles.append({
                "title": title_el.text if title_el is not None else "No title",
                "abstract": abstract_el.text[:500] if abstract_el is not None and abstract_el.text else "No abstract",
                "authors": ", ".join(authors) if authors else "Unknown",
                "year": year_el.text if year_el is not None else "Unknown",
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                "pmid": pmid,
            })

        return articles

    except Exception as e:
        print(f"PubMed error: {e}")
        return []


def format_articles_for_agent(articles: list) -> str:
    if not articles:
        return "No articles found."
    lines = []
    for i, a in enumerate(articles, 1):
        lines.append(
            f"[{i}] {a['title']}\n"
            f"    Authors: {a['authors']} ({a['year']})\n"
            f"    Abstract: {a['abstract']}\n"
            f"    URL: {a['url']}\n"
        )
    return "\n".join(lines)