import hashlib
import os

import requests

SAVE_DIR = "server/data/papers"
HASH_DB = "server/data/paper_hashes.txt"


def file_hash(content):
    return hashlib.md5(content).hexdigest()


def load_hashes(hash_db_path=HASH_DB):
    if not os.path.exists(hash_db_path):
        return set()
    with open(hash_db_path, "r", encoding="utf-8") as f:
        return set(f.read().splitlines())


def save_hash(hash_value, hash_db_path=HASH_DB):
    os.makedirs(os.path.dirname(hash_db_path), exist_ok=True)
    with open(hash_db_path, "a", encoding="utf-8") as f:
        f.write(hash_value + "\n")


def download_papers(pdf_url, save_dir=SAVE_DIR, hash_db_path=HASH_DB):
    if not pdf_url:
        return None

    os.makedirs(save_dir, exist_ok=True)

    r = requests.get(pdf_url, timeout=20)
    r.raise_for_status()
    content = r.content

    hash_value = file_hash(content)
    existing = load_hashes(hash_db_path)

    if hash_value in existing:
        print("Duplicate skipped:", pdf_url)
        return None

    base_name = pdf_url.split("/")[-1].split("?")[0]
    if not base_name.lower().endswith(".pdf"):
        base_name = base_name + ".pdf"

    path = os.path.join(save_dir, base_name)

    with open(path, "wb") as f:
        f.write(content)

    save_hash(hash_value, hash_db_path)

    return path
