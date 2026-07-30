# Journal source strategies

Use only the 18 journals in `journal-priority.json`. Among clinical journals, cover NEJM and The Lancet only.

| Journals | Preferred discovery | Evidence enrichment | Required exception |
|---|---|---|---|
| Nature; Nature Cell Biology; Nature Medicine; Nature Biotechnology; Nature Genetics | Official research/current-issue lists; RSS as trigger | Official article page, then PubMed/Europe PMC | Paginate lists; RSS has no abstract |
| Nature Methods | Official research-article list plus `nmeth.rss` | Direct `nature.com/articles/<DOI suffix>` page, then PubMed/Europe PMC | Preserve online date and article type; official lead text can make an abstract-free item screenable |
| Nature Communications | Official research-articles/articles pages | Official article page, Crossref, PubMed | Never use its eight-item RSS alone |
| Nature Machine Intelligence | Official lists; RSS as trigger | Official article page, then Crossref | PubMed coverage is weak |
| Cell; Developmental Cell; Cell Stem Cell; Cancer Cell | PubMed/Europe PMC and Crossref union when publisher pages return 403 | PubMed/Europe PMC, then OpenAlex | Research-like missing evidence becomes `needs_evidence` |
| Cell Metabolism | PubMed/Europe PMC first-publication-date discovery plus Crossref union | Europe PMC type and correction links first; then abstract cascade | Exclude errata/corrections before abstract checks |
| Science; Science Advances; Science Translational Medicine | Crossref and PubMed union when official sources return 403 | Prefer the source carrying the abstract | A zero in one source is not a confirmed empty window |
| NEJM | Official RSS/eTOC | PubMed, then OpenAlex | RSS description is citation text, not an abstract |
| The Lancet | PubMed and Crossref union when publisher sources return 403 | PubMed, then another auditable source | Corrections/editorials may be excluded by title/type |

## Nature Methods adapter

1. Enumerate the official research-article list for coverage; use RSS only as a freshness trigger.
2. Merge PubMed/Europe PMC and Crossref records by DOI.
3. Build `https://www.nature.com/articles/<DOI suffix>` for `10.1038/...` DOIs.
4. Extract first-online date, article type, abstract, or one bounded official lead paragraph.
5. Use PubMed/Europe PMC when it supplies a fuller abstract.

## Cell Metabolism adapter

1. Discover by ISSN `1550-4131`/`1932-7420` through PubMed or Europe PMC using first-publication/electronic dates; union with Crossref.
2. Preserve `pubTypeList` and `commentCorrectionList` or their PubMed XML equivalents.
3. Exclude `Published Erratum`, `Correction`, `Retraction of Publication`, and `Retracted Publication` before requiring an abstract.
4. For genuine original research without an abstract, run `scripts/enrich_doi.py`; retain unresolved research-like records as `needs_evidence`.
5. Regression examples: `10.1016/j.cmet.2026.07.017` and `10.1016/j.cmet.2026.07.013` are published errata, not new research.

## Track handling

- Track A: original research first published inside the configured half-open time window.
- Track B issue journals: identify the latest volume and issue and preserve its evidence.
- Track B continuous journals: use the latest dated publisher batch; otherwise label the boundary provisional.
- Render a work once even when it belongs to both tracks.

## Source quality

- `direct`: publisher list or feed discovery.
- `reconciled`: two metadata sources support the same DOI/title.
- `single_source`: one source supplies enough screening evidence.
- `needs_evidence`: the available text cannot support a safe decision.
- `source_unavailable`: no usable discovery response for that journal.

