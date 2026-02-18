from pypdf import PdfReader

PDF_PATH = "microscopy.pdf"

CHUNK_SIZE = 1500   # characters per chunk (simple + reliable)
OVERLAP = 200       # overlap between chunks
MAX_PAGES = None    # set e.g. 5 to test quickly, or None for all pages


def extract_pages(pdf_path: str, max_pages=None):
    reader = PdfReader(pdf_path)
    pages = []
    for i, page in enumerate(reader.pages):
        if max_pages is not None and i >= max_pages:
            break
        text = (page.extract_text() or "").replace("\n", " ").strip()
        if text:
            pages.append({"page": i + 1, "text": text})
    return pages


def chunk_text(text: str, chunk_size: int, overlap: int):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap
        if start < 0:
            start = 0
    return chunks


def make_chunks(pages, chunk_size=1500, overlap=200):
    all_chunks = []
    for p in pages:
        for j, ch in enumerate(chunk_text(p["text"], chunk_size, overlap)):
            all_chunks.append({
                "page_start": p["page"],
                "page_end": p["page"],
                "chunk_id": f"p{p['page']}_c{j}",
                "content": ch
            })
    return all_chunks


if __name__ == "__main__":
    pages = extract_pages(PDF_PATH, MAX_PAGES)
    chunks = make_chunks(pages, CHUNK_SIZE, OVERLAP)

    print(f"Pages extracted: {len(pages)}")
    print(f"Total chunks: {len(chunks)}")
    print("-" * 60)

    # show first 2 chunks
    for c in chunks[:2]:
        print(f"\nChunk {c['chunk_id']} (page {c['page_start']}):")
        print(c["content"][:800])
