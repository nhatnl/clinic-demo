import argparse

from parse_icd10cm_data import (
    DEFAULT_TXT_FILENAME,
    DEFAULT_XML_FILENAME,
    parse_icd10cm_data,
)
from sqlalchemy.dialects.postgresql import insert
from sqlmodel import Session
from src.database import engine
from src.diagnosis.model import Diagnosis


def import_icd10cm_data(
    limit: int | None = None,
    xml_filename: str = DEFAULT_XML_FILENAME,
    txt_filename: str = DEFAULT_TXT_FILENAME,
):
    diagnoses = parse_icd10cm_data(limit, xml_filename, txt_filename)
    if not diagnoses:
        return 0

    with Session(engine) as session:
        statement = insert(Diagnosis)
        statement = statement.on_conflict_do_update(
            index_elements=[Diagnosis.code],
            set_={
                "name": statement.excluded.name,
                "description": statement.excluded.description,
                "is_valid_for_submission": statement.excluded.is_valid_for_submission,
                "parent_code": statement.excluded.parent_code,
            },
        )
        session.execute(statement, [diagnosis.model_dump() for diagnosis in diagnoses])
        session.commit()

    return len(diagnoses)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    parser.add_argument("--xml", default=DEFAULT_XML_FILENAME)
    parser.add_argument("--txt", default=DEFAULT_TXT_FILENAME)
    args = parser.parse_args()

    count = import_icd10cm_data(args.limit, args.xml, args.txt)
    print(f"Imported {count} diagnoses")
