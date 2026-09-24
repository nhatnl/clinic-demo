import argparse
import sys
import xml.etree.ElementTree as ET
from itertools import islice
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from src.diagnosis.model import Diagnosis  # noqa: E402

DATA_DIR = BACKEND_DIR / "docs/data"
DEFAULT_XML_FILENAME = "icd10c-tabular-April-1-2026.xml"
DEFAULT_TXT_FILENAME = "icd10cm-order-April-1-2026.txt"


def walk(diag, order_data, parent_code=None):
    code = diag.findtext("name")
    is_valid, name, description = order_data[code.replace(".", "")]

    yield Diagnosis(
        code=code,
        name=name,
        description=description,
        is_valid_for_submission=is_valid,
        parent_code=parent_code,
    )

    for child in diag.findall("diag"):
        yield from walk(child, order_data, code)


def parse_icd10cm_data(
    limit: int | None = None,
    xml_filename: str = DEFAULT_XML_FILENAME,
    txt_filename: str = DEFAULT_TXT_FILENAME,
):
    if limit is not None and limit < 0:
        raise ValueError("limit must be non-negative")

    txt_path = DATA_DIR / txt_filename

    with txt_path.open(encoding="utf-8") as order_file:
        order_data = {
            line[6:13].strip(): (
                line[14] == "1",
                line[16:76].strip(),
                line[77:].strip(),
            )
            for line in order_file
        }
    xml_path = DATA_DIR / xml_filename

    root = ET.parse(xml_path).getroot()
    diagnoses = (
        diagnosis
        for section in root.findall("./chapter/section")
        for diag in section.findall("diag")
        for diagnosis in walk(diag, order_data)
    )
    return list(islice(diagnoses, limit))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    parser.add_argument("--xml", default=DEFAULT_XML_FILENAME)
    parser.add_argument("--txt", default=DEFAULT_TXT_FILENAME)
    args = parser.parse_args()

    rows = parse_icd10cm_data(args.limit, args.xml, args.txt)
    print(len(rows))
    print(rows[:3])
