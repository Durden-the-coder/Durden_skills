from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup


USER_AGENT = "BiomedicalJournalWatch/3.0 (source-enrichment audit)"
NON_RESEARCH_TYPES = {
    "Published Erratum",
    "Correction",
    "Retraction of Publication",
    "Retracted Publication",
}


def clean(value: str | None) -> str:
    if not value:
        return ""
    return " ".join(BeautifulSoup(value, "lxml").get_text(" ", strip=True).split())


def get_json(session: requests.Session, url: str, params: dict | None = None) -> tuple[int | None, dict, str]:
    try:
        response = session.get(url, params=params, timeout=30)
        if response.status_code >= 400:
            return response.status_code, {}, response.text[:200]
        return response.status_code, response.json(), ""
    except Exception as exc:
        return None, {}, f"{type(exc).__name__}: {exc}"


def openalex_abstract(index: dict | None) -> str:
    if not index:
        return ""
    positions: list[tuple[int, str]] = []
    for word, offsets in index.items():
        positions.extend((int(offset), word) for offset in offsets)
    return " ".join(word for _, word in sorted(positions))


def crossref(session: requests.Session, doi: str) -> dict:
    status, payload, error = get_json(session, f"https://api.crossref.org/works/{quote(doi, safe='')}")
    item = payload.get("message", {})
    return {
        "status": status,
        "error": error,
        "title": " ".join((item.get("title") or [""])[0].split()),
        "abstract": clean(item.get("abstract")),
        "published_online": (item.get("published-online") or {}).get("date-parts", [[]])[0],
        "type": item.get("subtype") or item.get("type") or "",
    }


def europe_pmc(session: requests.Session, doi: str) -> dict:
    status, payload, error = get_json(
        session,
        "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
        {"query": f'DOI:"{doi}"', "format": "json", "resultType": "core", "pageSize": 5},
    )
    results = payload.get("resultList", {}).get("result", [])
    item = results[0] if results else {}
    pub_types = (item.get("pubTypeList") or {}).get("pubType", [])
    corrections = (item.get("commentCorrectionList") or {}).get("commentCorrection", [])
    return {
        "status": status,
        "error": error,
        "matched": bool(item),
        "title": clean(item.get("title")),
        "abstract": clean(item.get("abstractText")),
        "first_publication_date": item.get("firstPublicationDate") or "",
        "publication_types": pub_types,
        "corrections": corrections,
        "pmid": item.get("pmid") or "",
    }


def openalex(session: requests.Session, doi: str) -> dict:
    status, payload, error = get_json(
        session, f"https://api.openalex.org/works/https://doi.org/{quote(doi, safe='/')}"
    )
    return {
        "status": status,
        "error": error,
        "title": clean(payload.get("title")),
        "abstract": openalex_abstract(payload.get("abstract_inverted_index")),
        "publication_date": payload.get("publication_date") or "",
        "type": payload.get("type") or "",
    }


def semantic_scholar(session: requests.Session, doi: str) -> dict:
    status, payload, error = get_json(
        session,
        f"https://api.semanticscholar.org/graph/v1/paper/DOI:{quote(doi, safe='/')}",
        {"fields": "title,abstract,publicationDate,externalIds"},
    )
    return {
        "status": status,
        "error": error,
        "title": clean(payload.get("title")),
        "abstract": clean(payload.get("abstract")),
        "publication_date": payload.get("publicationDate") or "",
    }


def publisher_page(session: requests.Session, doi: str) -> dict:
    try:
        response = session.get(
            f"https://doi.org/{doi}",
            timeout=35,
            allow_redirects=True,
            headers={
                "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.7",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36",
            },
        )
        soup = BeautifulSoup(response.content, "lxml")
        abstracts = []
        for selector in (
            'meta[name="citation_abstract"]',
            'meta[name="dc.description"]',
            'meta[name="description"]',
            'meta[property="og:description"]',
        ):
            node = soup.select_one(selector)
            if node and node.get("content"):
                abstracts.append(clean(node["content"]))
        for selector in ("#Abs1-content", "section[data-title='Abstract']", ".c-article-section__content"):
            abstracts.extend(clean(node.get_text(" ", strip=True)) for node in soup.select(selector))
        best = max(abstracts, key=len, default="")
        date_node = soup.select_one('meta[name="citation_online_date"], meta[name="citation_publication_date"]')
        return {
            "status": response.status_code,
            "final_url": response.url,
            "title": clean(soup.title.get_text(" ", strip=True)) if soup.title else "",
            "abstract": best,
            "publication_date": date_node.get("content", "") if date_node else "",
            "challenge": bool(re.search(r"verify you are human|access denied|captcha", soup.get_text(" ", strip=True), re.I)),
        }
    except Exception as exc:
        return {"status": None, "error": f"{type(exc).__name__}: {exc}", "abstract": ""}


def enrich(session: requests.Session, doi: str) -> dict:
    sources = {
        "publisher": publisher_page(session, doi),
        "europe_pmc": europe_pmc(session, doi),
        "openalex": openalex(session, doi),
        "semantic_scholar": semantic_scholar(session, doi),
        "crossref": crossref(session, doi),
    }
    publication_types = set(sources["europe_pmc"].get("publication_types") or [])
    non_research_type = bool(publication_types & NON_RESEARCH_TYPES)
    usable = [
        {"source": name, "abstract": row.get("abstract", "")}
        for name, row in sources.items()
        if len(row.get("abstract", "")) >= 100
    ]
    usable.sort(key=lambda row: len(row["abstract"]), reverse=True)
    recommendation = "exclude_non_research_type" if non_research_type else ("screenable" if usable else "needs_evidence")
    return {
        "doi": doi.casefold(),
        "non_research_type": non_research_type,
        "recommended_decision": recommendation,
        "screening_evidence": usable[0] if usable else None,
        "sources": sources,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--doi", action="append", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json,*/*;q=0.7"})
    result = {"records": [enrich(session, doi.strip()) for doi in args.doi]}
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

