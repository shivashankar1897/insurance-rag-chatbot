import json
from pathlib import Path

import fitz  # PyMuPDF
import pandas as pd
from docx import Document


# ---------------------------------------------------------------------
# Load document metadata
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
METADATA_FILE = PROJECT_ROOT / "data" / "document_metadata.json"

if not METADATA_FILE.exists():
    raise FileNotFoundError(
        f"Metadata file not found: {METADATA_FILE}"
    )

with open(METADATA_FILE, "r", encoding="utf-8") as f:
    DOCUMENT_METADATA = json.load(f)


def get_document_metadata(file_name: str) -> dict:
    """
    Return metadata for a document.

    Raises an error if metadata is missing.
    """

    if file_name not in DOCUMENT_METADATA:
        raise ValueError(
            f"No metadata found for '{file_name}'. "
            "Please add it to document_metadata.json."
        )

    return DOCUMENT_METADATA[file_name]


def build_document(text: str, file_path: str, document_type: str):
    """
    Build the standard document dictionary.
    """

    file_name = Path(file_path).name

    metadata = get_document_metadata(file_name)

    return {
        "text": text.strip(),
        "source": file_name,
        "type": document_type,
        "tenant_id": metadata["tenant_id"],
        "plan_name": metadata["plan_name"],
        "section_name": metadata["section_name"],
    }


# ---------------------------------------------------------------------
# Individual parsers
# ---------------------------------------------------------------------

def parse_pdf(file_path: str):
    """
    Parse a PDF file into plain text.
    """

    doc = fitz.open(file_path)

    text = ""

    for page in doc:
        text += page.get_text()

    doc.close()

    return build_document(
        text=text,
        file_path=file_path,
        document_type="pdf",
    )


def parse_docx(file_path: str):
    """
    Parse a DOCX file into plain text.
    """

    doc = Document(file_path)

    paragraphs = [
        p.text.strip()
        for p in doc.paragraphs
        if p.text.strip()
    ]

    return build_document(
        text="\n".join(paragraphs),
        file_path=file_path,
        document_type="docx",
    )


def parse_txt(file_path: str):
    """
    Parse a TXT file into plain text.
    """

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    return build_document(
        text=text,
        file_path=file_path,
        document_type="txt",
    )


def parse_csv(file_path: str):
    """
    Parse a CSV file into one document per row.
    """

    df = pd.read_csv(file_path)

    file_name = Path(file_path).name
    metadata = get_document_metadata(file_name)

    documents = []

    for row_index, row in df.iterrows():

        row_text = " | ".join(map(str, row.values))

        text = row_text.lower()

        if "star senior citizen" in text:
            plan_name = "Star Senior Citizen"

        elif "star comprehensive" in text:
            plan_name = "Star Comprehensive"

        elif "bajaj health guard" in text:
            plan_name = "Bajaj Health Guard Family"

        elif "hdfc" in text:
            plan_name = "HDFC Ergo"

        else:
            plan_name = metadata["plan_name"]

        documents.append(
            {
                "text": row_text,
                "source": file_name,
                "type": "csv",
                "tenant_id": metadata["tenant_id"],
                "plan_name": plan_name,
                "section_name": metadata["section_name"],
                "row_number": row_index,
            }
        )

    return documents


def parse_xlsx(file_path: str):
    """
    Parse an Excel file into plain text.
    """

    excel = pd.ExcelFile(file_path)

    rows = []

    for sheet in excel.sheet_names:

        df = pd.read_excel(excel, sheet_name=sheet)

        rows.append(f"Sheet: {sheet}")

        for _, row in df.iterrows():
            rows.append(" | ".join(map(str, row.values)))

    return build_document(
        text="\n".join(rows),
        file_path=file_path,
        document_type="xlsx",
    )


# ---------------------------------------------------------------------
# Load all supported documents
# ---------------------------------------------------------------------

def load_documents(data_folder: str):
    """
    Load all supported documents from a folder recursively.
    """

    documents = []

    parser_map = {
        ".pdf": parse_pdf,
        ".docx": parse_docx,
        ".txt": parse_txt,
        ".csv": parse_csv,
        ".xlsx": parse_xlsx,
    }

    for file in Path(data_folder).rglob("*"):

        if not file.is_file():
            continue

        parser = parser_map.get(file.suffix.lower())

        if parser is None:
            continue

        try:
            parsed = parser(str(file))

            # Some parsers return a single document,
            # CSV parser returns a list of documents.
            if isinstance(parsed, list):
                documents.extend(parsed)
            else:
                documents.append(parsed)

        except Exception as e:
            print(f"Failed to parse {file.name}: {e}")

    return documents