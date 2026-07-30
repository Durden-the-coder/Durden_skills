from __future__ import annotations

import re
import sys

import requests
from bs4 import BeautifulSoup

import _enrich_doi_impl as implementation


def strict_publisher_page(session: requests.Session, doi: str) -> dict:
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
        evidence = []
        for selector in (
            'meta[name="citation_abstract"]',
            'meta[name="dc.description"]',
            'meta[name="description"]',
            'meta[property="og:description"]',
        ):
            node = soup.select_one(selector)
            if node and node.get("content"):
                evidence.append(implementation.clean(node["content"]))
        for selector in (
            "#Abs1-content",
            "section[data-title='Abstract'] .c-article-section__content",
            "section[data-title='Abstract']",
        ):
            evidence.extend(implementation.clean(node.get_text(" ", strip=True)) for node in soup.select(selector))
        if not any(value for value in evidence) and "nature.com" in response.url:
            lead = soup.select_one(".c-article-section__content > p")
            if lead:
                evidence.append(implementation.clean(lead.get_text(" ", strip=True)))
        best = max((value for value in evidence if value), key=len, default="")
        date_node = soup.select_one('meta[name="citation_online_date"], meta[name="citation_publication_date"]')
        return {
            "status": response.status_code,
            "final_url": response.url,
            "title": implementation.clean(soup.title.get_text(" ", strip=True)) if soup.title else "",
            "abstract": best,
            "publication_date": date_node.get("content", "") if date_node else "",
            "challenge": bool(re.search(r"verify you are human|access denied|captcha", soup.get_text(" ", strip=True), re.I)),
        }
    except Exception as exc:
        return {"status": None, "error": f"{type(exc).__name__}: {exc}", "abstract": ""}


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    implementation.publisher_page = strict_publisher_page
    raise SystemExit(implementation.main())

