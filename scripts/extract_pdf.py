from pypdf import PdfReader

pdf_path = "microscopy.pdf"

reader = PdfReader(pdf_path)

print(f"Number of pages: {len(reader.pages)}")
print("-" * 50)

for i, page in enumerate(reader.pages[:3]):  # first 3 pages only
    text = page.extract_text()
    print(f"\n--- PAGE {i+1} ---\n")
    print(text[:1000])  # print first 1000 characters
