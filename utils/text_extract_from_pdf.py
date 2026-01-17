import io
import fitz
import PyPDF2


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes), strict=False)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception:
        return ""


def extract_text_with_inline_urls(pdf_bytes: bytes) -> str:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    output = []

    for page in doc:
        links = page.get_links()
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if block["type"] != 0:
                continue

            for line in block["lines"]:
                line_text = ""

                for span in line["spans"]:
                    span_text = span["text"]
                    span_rect = fitz.Rect(span["bbox"])

                    # Check if span overlaps a link
                    for link in links:
                        if "uri" in link and span_rect.intersects(fitz.Rect(link["from"])):
                            span_text += f" ({link['uri']})"
                            break

                    line_text += span_text

                output.append(line_text)

        output.append("\n")

    return "\n".join(output).strip()

# Function to extract text from uploaded file (PDF or TXT)
def extract_text_from_file(uploaded_file):
    if isinstance(uploaded_file, str):
        return uploaded_file

    file_bytes = uploaded_file.read()

    if uploaded_file.content_type == "application/pdf":
        return extract_text_from_pdf(file_bytes)

    try:
        return file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return ""
   

# Function to read local PDF file for testing
def read_local_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()