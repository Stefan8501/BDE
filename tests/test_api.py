from __future__ import annotations

import io
from datetime import datetime

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

# Set up an in-memory database for the tests
engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_full_bde_workflow():
    # Create master data
    employee_payload = {
        "personnel_number": "1000",
        "first_name": "Max",
        "last_name": "Mustermann",
        "department": "Produktion",
        "role": "Facharbeiter",
        "active": True,
    }
    response = client.post("/employees", json=employee_payload)
    assert response.status_code == 201
    employee_id = response.json()["id"]

    machine_payload = {
        "code": "M-01",
        "name": "CNC Drehmaschine",
        "description": "Präzisionsmaschine",
        "location": "Halle A",
        "active": True,
    }
    response = client.post("/machines", json=machine_payload)
    assert response.status_code == 201
    machine_id = response.json()["id"]

    work_order_payload = {
        "order_number": "WO-2024-001",
        "customer": "Automotive AG",
        "article": "Welle",
        "quantity": 500,
        "status": "released",
    }
    response = client.post("/work-orders", json=work_order_payload)
    assert response.status_code == 201
    work_order_id = response.json()["id"]

    operation_payload = {
        "code": "OP-10",
        "description": "Drehen",
        "work_order_id": work_order_id,
        "machine_id": machine_id,
        "standard_time_minutes": 12.5,
        "is_active": True,
    }
    response = client.post("/operations", json=operation_payload)
    assert response.status_code == 201
    operation_id = response.json()["id"]

    activity_payload = {
        "start_time": datetime(2024, 2, 15, 6, 30).isoformat(),
        "end_time": datetime(2024, 2, 15, 14, 30).isoformat(),
        "employee_id": employee_id,
        "operation_id": operation_id,
        "quantity_good": 120,
        "quantity_reject": 3,
        "status": "completed",
        "comment": "Schicht sauber abgeschlossen",
    }
    response = client.post("/activity-records", json=activity_payload)
    assert response.status_code == 201

    # Export CSV for operations
    response = client.get("/csv/operations")
    assert response.status_code == 200
    assert "code,description,order_number" in response.text
    assert "OP-10" in response.text

    # Update employee via CSV import
    employee_csv = io.StringIO()
    employee_csv.write(
        "personnel_number,first_name,last_name,department,role,active\n"
        "1000,Max,Mustermann,Produktion,Teamleiter,true\n"
    )
    employee_csv.seek(0)
    files = {"file": ("employees.csv", employee_csv.read(), "text/csv")}
    response = client.post("/csv/employees", files=files)
    assert response.status_code == 200
    assert response.json() == {"inserted": 0, "updated": 1}

    # Import an additional machine via CSV
    machine_csv_content = (
        "code,name,description,location,active\n"
        "M-02,Fräse,Hochgeschwindigkeitsfräse,Halle B,true\n"
    )
    files = {"file": ("machines.csv", machine_csv_content, "text/csv")}
    response = client.post("/csv/machines", files=files)
    assert response.status_code == 200
    assert response.json()["inserted"] == 1

    # Validate that the employee has been updated via REST endpoint
    response = client.get("/employees")
    assert response.status_code == 200
    data = response.json()
    assert any(emp["role"] == "Teamleiter" for emp in data)


def test_unknown_csv_entity():
    response = client.get("/csv/unknown")
    assert response.status_code == 404
