import importlib
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from src.diagnosis.model import Diagnosis

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

importer = importlib.import_module("scripts.import_icd10cm_data")


class DiagnosisImportTests(unittest.TestCase):
    def test_empty_import_skips_database(self):
        with patch(
            "scripts.import_icd10cm_data.parse_icd10cm_data", return_value=[]
        ), patch("scripts.import_icd10cm_data.Session") as session:
            self.assertEqual(importer.import_icd10cm_data(0), 0)
            session.assert_not_called()

    def test_import_executes_upsert_and_commits(self):
        diagnosis = Diagnosis(code="A00", name="Cholera", description="Example")
        db = Mock()
        db.__enter__ = Mock(return_value=db)
        db.__exit__ = Mock(return_value=False)
        with patch(
            "scripts.import_icd10cm_data.parse_icd10cm_data",
            return_value=[diagnosis],
        ), patch("scripts.import_icd10cm_data.Session", return_value=db):
            self.assertEqual(importer.import_icd10cm_data(), 1)
        db.execute.assert_called_once()
        self.assertEqual(db.execute.call_args.args[1][0]["code"], "A00")
        db.commit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
