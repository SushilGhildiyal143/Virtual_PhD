import arxiv
import time

ARXIV_DELAY = 1
MAX_RETRIES = 3


def normalize_title(title):
    return title.lower().strip().replace(" ", "")


def _in_year_range(year, start_year, end_year):
    if year is None:
        return False
    return start_year <= int(year) <= end_year


def search_arxiv_safe(query, max_results, start_year=None, end_year=None):
    papers = []
    capped = min(max_results * 3, 1000)

    for attempt in range(MAX_RETRIES):
        try:
            search = arxiv.Search(query=query, max_results=capped)

            for result in search.results():
                year = result.published.year if result.published else None
                if start_year is not None and end_year is not None and not _in_year_range(year, start_year, end_year):
                    continue

                papers.append(
                    {
                        "title": result.title,
                        "pdf_url": result.pdf_url,
                        "source": "arxiv",
                        "year": year,
                    }
                )

                if len(papers) >= max_results:
                    break

                time.sleep(ARXIV_DELAY)

            return papers

        except Exception as e:
            print(f"[arXiv Retry {attempt + 1}] Error:", e)
            time.sleep(6)

    return []


def search_papers(query, max_results=10, start_year=None, end_year=None):
    seen_titles = set()
    final_papers = []

    print("\nSearching arXiv (rate-limited)...")
    arxiv_papers = search_arxiv_safe(query, max_results, start_year, end_year)
    print(f"arXiv fetched: {len(arxiv_papers)}")

    for paper in arxiv_papers:
        title = paper.get("title", "")
        norm = normalize_title(title)

        if norm in seen_titles:
            continue

        seen_titles.add(norm)

        if not paper.get("pdf_url"):
            continue

        final_papers.append(paper)

        if len(final_papers) >= max_results:
            break

    print(f"\nFinal unique papers: {len(final_papers)}")
    return final_papers
