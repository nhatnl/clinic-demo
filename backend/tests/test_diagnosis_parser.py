import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.parse_icd10cm_data import parse_icd10cm_data


class DiagnosisParserTests(unittest.TestCase):
    def test_parent_child_limit_and_invalid_limit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "codes.xml").write_text(
                "<root><chapter><section><diag><name>A00</name>"
                "<diag><name>A00.0</name></diag></diag></section>"
                "</chapter></root>",
                encoding="utf-8",
            )
            (root / "order.txt").write_text(
                "".join(
                    f"{'':6}{code:<7} {valid} {name:<60} {description}\n"
                    for code, valid, name, description in (
                        ("A00", 0, "Cholera", "Parent diagnosis"),
                        ("A000", 1, "Classical cholera", "Child diagnosis"),
                    )
                ),
                encoding="utf-8",
            )
            with patch("scripts.parse_icd10cm_data.DATA_DIR", root):
                rows = parse_icd10cm_data(xml_filename="codes.xml", txt_filename="order.txt")
                self.assertEqual(
                    [
                        (row.code, row.parent_code, row.is_valid_for_submission)
                        for row in rows
                    ],
                    [("A00", None, False), ("A00.0", "A00", True)],
                )
                self.assertEqual(len(parse_icd10cm_data(1, "codes.xml", "order.txt")), 1)
                self.assertEqual(parse_icd10cm_data(0, "codes.xml", "order.txt"), [])
                with self.assertRaisesRegex(ValueError, "non-negative"):
                    parse_icd10cm_data(-1, "codes.xml", "order.txt")


if __name__ == "__main__":
    unittest.main()
