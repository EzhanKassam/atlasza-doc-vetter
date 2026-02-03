from pypdf import PdfReader

def extract_pdf_text(path: str, max_chars: int) -> str:
    reader = PdfReader(path)
    parts = []
    for page in reader.pages:
        t = page.extract_text() or ""
        if t.strip():
            parts.append(t)
        if sum(len(p) for p in parts) > max_chars:
            break
    text = "\n\n".join(parts)
    return text[:max_chars]
