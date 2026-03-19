#!/usr/bin/env python3
"""
Citation Fetch Utility for SER Framework

Fetches verified BibTeX entries from DBLP (primary) and CrossRef (fallback).
Used by writing.draft for post-draft citation verification.

Usage:
    python citation_fetch.py "Attention Is All You Need"
    python citation_fetch.py "Attention Is All You Need" --authors "Vaswani"
    python citation_fetch.py --batch references.txt  # one title per line

Output:
    BibTeX string on success, or "% [VERIFY] title" on failure.
"""

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
from typing import Optional

DBLP_API = "https://dblp.org/search/publ/api"
CROSSREF_API = "https://api.crossref.org/works"
USER_AGENT = "SER-CitationFetch/1.0 (mailto:research@example.com)"
REQUEST_TIMEOUT = 15


def _get_json(url: str) -> Optional[dict]:
    """Fetch JSON from a URL with timeout and error handling."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def fetch_bibtex_dblp(title: str, authors: Optional[str] = None) -> Optional[str]:
    """Search DBLP for a paper and return its BibTeX entry."""
    query = title
    if authors:
        query = f"{authors} {title}"
    params = urllib.parse.urlencode({"q": query, "format": "json", "h": 3})
    url = f"{DBLP_API}?{params}"

    data = _get_json(url)
    if not data:
        return None

    hits = data.get("result", {}).get("hits", {}).get("hit", [])
    if not hits:
        return None

    # Find best match by checking title similarity
    title_lower = title.lower().strip()
    best_hit = None
    for hit in hits:
        info = hit.get("info", {})
        hit_title = info.get("title", "").lower().strip().rstrip(".")
        if title_lower.rstrip(".") in hit_title or hit_title in title_lower:
            best_hit = hit
            break

    if not best_hit:
        # Fall back to first result
        best_hit = hits[0]

    # Fetch BibTeX from DBLP
    info = best_hit.get("info", {})
    bibtex_url = info.get("url")
    if not bibtex_url:
        return None

    bibtex_url = bibtex_url.rstrip("/") + ".bib"
    req = urllib.request.Request(bibtex_url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            return resp.read().decode("utf-8").strip()
    except Exception:
        return None


def fetch_bibtex_crossref(title: str, authors: Optional[str] = None) -> Optional[str]:
    """Search CrossRef for a paper and return a generated BibTeX entry."""
    query = title
    if authors:
        query = f"{authors} {title}"
    params = urllib.parse.urlencode(
        {"query": query, "rows": 3, "select": "DOI,title,author,published-print,container-title,type"}
    )
    url = f"{CROSSREF_API}?{params}"

    data = _get_json(url)
    if not data:
        return None

    items = data.get("message", {}).get("items", [])
    if not items:
        return None

    # Find best match
    title_lower = title.lower().strip()
    best_item = None
    for item in items:
        item_titles = item.get("title", [])
        for t in item_titles:
            if title_lower.rstrip(".") in t.lower() or t.lower().rstrip(".") in title_lower:
                best_item = item
                break
        if best_item:
            break

    if not best_item:
        best_item = items[0]

    # Generate BibTeX from CrossRef metadata
    doi = best_item.get("DOI", "")
    cr_title = best_item.get("title", ["Unknown"])[0]
    cr_authors = best_item.get("author", [])
    cr_year_parts = best_item.get("published-print", {}).get("date-parts", [[None]])
    cr_year = cr_year_parts[0][0] if cr_year_parts and cr_year_parts[0] else "????"
    cr_venue = best_item.get("container-title", [""])[0] if best_item.get("container-title") else ""

    # Build author string
    author_strs = []
    for a in cr_authors:
        given = a.get("given", "")
        family = a.get("family", "")
        if given and family:
            author_strs.append(f"{family}, {given}")
        elif family:
            author_strs.append(family)
    author_str = " and ".join(author_strs) if author_strs else "Unknown"

    # Generate citation key
    first_author = cr_authors[0].get("family", "unknown").lower() if cr_authors else "unknown"
    key = f"{first_author}{cr_year}"

    bibtex = f"""@article{{{key},
  title     = {{{cr_title}}},
  author    = {{{author_str}}},
  year      = {{{cr_year}}},
  journal   = {{{cr_venue}}},
  doi       = {{{doi}}}
}}"""
    return bibtex


def fetch_bibtex(title: str, authors: Optional[str] = None) -> str:
    """
    Fetch BibTeX for a paper title. Tries DBLP first, then CrossRef.

    Returns:
        BibTeX string on success, or "% [VERIFY] {title}" on failure.
    """
    # Try DBLP first (higher quality BibTeX)
    result = fetch_bibtex_dblp(title, authors)
    if result:
        return result

    # Small delay to be respectful to APIs
    time.sleep(0.5)

    # Fallback to CrossRef
    result = fetch_bibtex_crossref(title, authors)
    if result:
        return f"% Source: CrossRef (verify venue/type)\n{result}"

    return f"% [VERIFY] {title}"


def main():
    parser = argparse.ArgumentParser(description="Fetch BibTeX citations from DBLP/CrossRef")
    parser.add_argument("title", nargs="?", help="Paper title to search")
    parser.add_argument("--authors", "-a", help="Author name(s) to narrow search")
    parser.add_argument("--batch", "-b", help="File with one title per line")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    args = parser.parse_args()

    if not args.title and not args.batch:
        parser.print_help()
        sys.exit(1)

    results = []

    if args.batch:
        with open(args.batch) as f:
            titles = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        for i, t in enumerate(titles):
            print(f"[{i+1}/{len(titles)}] Searching: {t}", file=sys.stderr)
            results.append(fetch_bibtex(t))
            if i < len(titles) - 1:
                time.sleep(1)  # Rate limiting
    else:
        results.append(fetch_bibtex(args.title, args.authors))

    output = "\n\n".join(results)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output + "\n")
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
