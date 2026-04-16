import os
from PyPDF2 import PdfReader

PDF_DIR = "server/data/papers"
TEXT_DIR = "server/data/text"


def extract_text_from_pdfs(pdf_dir=PDF_DIR, text_dir=TEXT_DIR, clear_existing=False):
    os.makedirs(text_dir, exist_ok=True)

    if clear_existing:
        for file in os.listdir(text_dir):
            if file.endswith(".txt"):
                try:
                    os.remove(os.path.join(text_dir, file))
                except Exception:
                    pass

    for file in os.listdir(pdf_dir):
        if not file.endswith(".pdf"):
            continue

        pdf_path = os.path.join(pdf_dir, file)
        text_path = os.path.join(text_dir, file.replace(".pdf", ".txt"))
        try:
            reader = PdfReader(pdf_path)
            text = ""

            for page in reader.pages:
                text += page.extract_text() or ""

            with open(text_path, "w", encoding="utf-8") as f:
                f.write(text)

            print("Parsed:", file)
        except Exception as e:
            print(f"Skipped (parse error): {file} | {e}")
