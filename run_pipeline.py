import json
import os
from tqdm import tqdm

from server.tools.idea_extractor import extract_idea
from server.tools.gap_analysis import analyze_gaps
from server.tools.paper_writer import write_paper
from server.tools.search_papers import search_papers
from server.tools.download_papers import download_papers
from server.tools.parse_pdf import extract_text_from_pdfs
from server.tools.novelty_generator import generate_novel_idea

BASE_TEXT_DIR = "server/data/text"
BASE_PAPER_DIR = "server/data/papers"
OUTPUT_DIR = "server/data/outputs"
CONFIG_PATH = "server/data/config/prompt.txt"
DEFAULT_SUBDIR = "MTI_projects"
DEFAULT_QUERY = "Mother Tongue Influence reduction in spoken English using transformer accent conversion"


def load_config():
    config = {
        "query": DEFAULT_QUERY,
        "max_results": 120,
        "start_year": 2022,
        "end_year": 2026,
        "paper_subdir": DEFAULT_SUBDIR,
        "authors": "Rohitesh Kumar and Sushil Ghildiyal",
        "affiliation": "UPES, Dehradun",
        "title": "Transformer-Driven MTI Reduction in Spoken English with Voice Identity Preservation",
        "target_pages": 300,
    }

    if not os.path.exists(CONFIG_PATH):
        return config

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for raw in lines:
        line = raw.strip()
        if not line or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if key in {"max_results", "start_year", "end_year", "target_pages"}:
            try:
                config[key] = int(value)
            except Exception:
                pass
        elif key in config:
            config[key] = value

    return config


def deduplicate_papers(papers):
    seen = set()
    unique = []

    for p in papers:
        title = p.get("title", "").lower().strip()

        if title in seen:
            continue

        seen.add(title)
        unique.append(p)

    return unique


def load_texts(text_dir):
    texts = []

    for file in os.listdir(text_dir):
        if not file.endswith(".txt"):
            continue

        path = os.path.join(text_dir, file)

        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                txt = f.read()
                if txt.strip():
                    texts.append(txt)
        except Exception as e:
            print(f"Error reading {file}: {e}")

    return texts


def main():
    cfg = load_config()

    paper_dir = os.path.join(BASE_PAPER_DIR, cfg["paper_subdir"])
    text_dir = os.path.join(BASE_TEXT_DIR, cfg["paper_subdir"])
    hash_db = os.path.join(BASE_PAPER_DIR, f"paper_hashes_{cfg['paper_subdir']}.txt")

    os.makedirs(paper_dir, exist_ok=True)
    os.makedirs(text_dir, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 60)
    print("RESEARCH PIPELINE STARTED")
    print("=" * 60)

    print(f"\nTopic: {cfg['query']}")
    print(f"Papers requested: {cfg['max_results']}")
    print(f"Year filter: {cfg['start_year']} to {cfg['end_year']}")
    print(f"Paper folder: {paper_dir}")

    print("\nSearching papers...")
    papers = search_papers(
        cfg["query"],
        cfg["max_results"],
        cfg["start_year"],
        cfg["end_year"],
    )
    papers = deduplicate_papers(papers)
    print(f"Unique papers found: {len(papers)}")

    print("\nDownloading papers...")
    downloaded = 0
    for p in tqdm(papers):
        try:
            path = download_papers(p.get("pdf_url"), save_dir=paper_dir, hash_db_path=hash_db)
            if path:
                downloaded += 1
        except Exception as e:
            print("Download error:", e)

    print(f"Downloaded new files: {downloaded}")

    print("\nParsing PDFs...")
    extract_text_from_pdfs(pdf_dir=paper_dir, text_dir=text_dir, clear_existing=True)

    texts = load_texts(text_dir)
    print(f"Parsed documents: {len(texts)}")

    print("\nExtracting structured ideas...")
    ideas = []
    failed = 0

    for text in tqdm(texts):
        try:
            idea = extract_idea(text)
            if isinstance(idea, dict):
                ideas.append(idea)
            else:
                failed += 1
        except Exception as e:
            failed += 1
            print("Idea extraction error:", e)

    print(f"Extracted ideas: {len(ideas)} | Failed: {failed}")

    papers_path = os.path.join(OUTPUT_DIR, "papers.json")
    with open(papers_path, "w", encoding="utf-8") as f:
        json.dump(papers, f, indent=2)

    ideas_path = os.path.join(OUTPUT_DIR, "ideas.json")
    with open(ideas_path, "w", encoding="utf-8") as f:
        json.dump(ideas, f, indent=2)

    print("\nAnalyzing research gaps...")
    gaps = analyze_gaps(json.dumps(ideas, indent=2))

    gaps_path = os.path.join(OUTPUT_DIR, "gaps.txt")
    with open(gaps_path, "w", encoding="utf-8") as f:
        f.write(gaps)

    print("Gap analysis completed")

    print("\nGenerating novel research idea...")
    try:
        novel_idea = generate_novel_idea(gaps)
    except Exception:
        novel_idea = gaps

    novel_idea_path = os.path.join(OUTPUT_DIR, "novel_idea.txt")
    with open(novel_idea_path, "w", encoding="utf-8") as f:
        f.write(novel_idea)

    print("Novel idea ready")

    print("\nGenerating research paper...")
    paper_path = write_paper(
        idea=novel_idea,
        topic=cfg["query"],
        papers=papers,
        authors=cfg["authors"],
        affiliation=cfg["affiliation"],
        title=cfg["title"],
        target_pages=cfg["target_pages"],
        year_start=cfg["start_year"],
        year_end=cfg["end_year"],
    )

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETED")
    print("=" * 60)
    print("Paper saved at:", paper_path)


if __name__ == "__main__":
    main()
