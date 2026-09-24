import unittest
from datetime import UTC, datetime

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from src.consultations.models import Consultation, ConsultationDiagnosis
from src.database import get_session
from src.diagnosis.model import Diagnosis
from src.main import app
from src.patients.models import Patient


class ConsultationApiTest(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        SQLModel.metadata.create_all(
            self.engine,
            tables=[
                Patient.__table__,
                Diagnosis.__table__,
                Consultation.__table__,
                ConsultationDiagnosis.__table__,
            ],
        )
        with Session(self.engine) as session:
            session.add_all([
                Patient(id=1, name="An Nguyen", age=32),
                Patient(id=2, name="Binh Tran", age=45),
                Diagnosis(
                    code="A00.0", name="Cholera", description="Cholera",
                    is_valid_for_submission=True,
                ),
                Diagnosis(
                    code="B01.1", name="Varicella", description=None,
                    is_valid_for_submission=True,
                ),
                Diagnosis(code="A00", name="Cholera category", description=None),
            ])
            session.commit()

        def override_session():
            with Session(self.engine) as session:
                yield session

        app.dependency_overrides[get_session] = override_session
        self.client = TestClient(app)

    def tearDown(self) -> None:
        self.client.close()
        app.dependency_overrides.clear()
        self.engine.dispose()

    def create(self, patient_id=1, note="Follow up", codes=None):
        return self.client.post(
            "/consultation",
            json={
                "patient_id": patient_id,
                "note": note,
                "diagnosis_codes": codes if codes is not None else ["A00.0"],
            },
        )

    def count(self):
        with Session(self.engine) as session:
            return len(session.exec(select(Consultation)).all())

    def test_create_persists_patient_and_all_diagnoses(self) -> None:
        response = self.create(
            note="  Prescribe oral rehydration  ",
            codes=[" a00.0 ", "b01.1"],
        )
        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["note"], "Prescribe oral rehydration")
        self.assertEqual(body["patient"], {"id": 1, "name": "An Nguyen", "age": 32})
        self.assertEqual({item["code"] for item in body["diagnoses"]}, {"A00.0", "B01.1"})
        self.assertEqual(body["diagnoses"][0].keys(), {"code", "name", "description"})
        self.assertIn("created_at", body)
        self.assertIn("updated_at", body)

        with Session(self.engine) as session:
            stored = session.get(Consultation, body["id"])
            self.assertEqual(stored.patient_id, 1)
            self.assertEqual({diagnosis.code for diagnosis in stored.diagnoses}, {"A00.0", "B01.1"})

    def test_missing_references_do_not_create_partial_records(self) -> None:
        missing_patient = self.create(patient_id=99)
        self.assertEqual(missing_patient.status_code, 404)
        self.assertEqual(missing_patient.json(), {"detail": "Patient not found"})
        missing_code = self.create(codes=["A00.0", "Z99.9"])
        self.assertEqual(missing_code.status_code, 404)
        self.assertEqual(missing_code.json(), {"detail": "Diagnosis code not found"})
        category = self.create(codes=["A00"])
        self.assertEqual(category.status_code, 404)
        self.assertEqual(self.count(), 0)

    def test_invalid_input_is_rejected_without_writes(self) -> None:
        cases = [
            {"patient_id": 0},
            {"patient_id": -1},
            {"note": "  "},
            {"diagnosis_codes": []},
            {"diagnosis_codes": ["A00.0", " a00.0 "]},
            {"diagnosis_codes": ["TOO-LONG-CODE"]},
            {"diagnosis_codes": ["   "]},
        ]
        for changes in cases:
            with self.subTest(changes=changes):
                body = {"patient_id": 1, "note": "Follow up", "diagnosis_codes": ["A00.0"]}
                body.update(changes)
                self.assertEqual(self.client.post("/consultation", json=body).status_code, 422)
        self.assertEqual(self.count(), 0)

    def test_list_filters_and_newest_first(self) -> None:
        first = self.create().json()
        second = self.create(patient_id=2, codes=["B01.1"]).json()
        third = self.create(codes=["B01.1"]).json()
        with Session(self.engine) as session:
            for item, day in ((first, 1), (second, 2), (third, 3)):
                consultation = session.get(Consultation, item["id"])
                consultation.created_at = datetime(2026, 9, day, tzinfo=UTC)
                session.add(consultation)
            session.commit()

        def ids(params=None):
            response = self.client.get("/consultation", params=params)
            self.assertEqual(response.status_code, 200)
            return [item["id"] for item in response.json()]

        self.assertEqual(ids(), [third["id"], second["id"], first["id"]])
        self.assertEqual(ids({"patient": "  nGuYeN  "}), [third["id"], first["id"]])
        self.assertEqual(ids({"diagnosis_code": " b01.1 "}), [third["id"], second["id"]])
        self.assertEqual(ids({"patient": "Nguyen", "diagnosis_code": "B01.1"}), [third["id"]])
        self.assertEqual(ids({"patient": "Nobody"}), [])

    def test_query_length_validation(self) -> None:
        for params in (
            {"patient": ""},
            {"patient": "x" * 51},
            {"diagnosis_code": ""},
            {"diagnosis_code": "x" * 9},
        ):
            with self.subTest(params=params):
                self.assertEqual(self.client.get("/consultation", params=params).status_code, 422)

    def test_diagnosis_lookup_finds_codes_and_names(self) -> None:
        by_code = self.client.get("/diagnosis/", params={"search": "a00"})
        self.assertEqual(by_code.status_code, 200)
        self.assertEqual([item["code"] for item in by_code.json()], ["A00", "A00.0"])
        self.assertFalse(by_code.json()[0]["is_valid_for_submission"])
        self.assertTrue(by_code.json()[1]["is_valid_for_submission"])
        by_name = self.client.get("/diagnosis/", params={"search": "varicella"})
        self.assertEqual([item["code"] for item in by_name.json()], ["B01.1"])
        self.assertEqual(self.client.get("/diagnosis/", params={"search": "  "}).json(), [])
        self.assertEqual(self.client.get("/diagnosis/").status_code, 422)
        self.assertEqual(
            self.client.get("/diagnosis/", params={"search": "x" * 101}).status_code,
            422,
        )


if __name__ == "__main__":
    unittest.main()
