"""FastAPI application exposing the IWS BDE system."""
from __future__ import annotations

import io

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from . import crud, csv_io, models, schemas
from .database import Base, engine, get_db

# Ensure the database schema exists as soon as the application module is imported.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="IWS BDE Plattform",
    description=(
        "Betriebsdatenerfassungssystem für die IWS GmbH basierend auf modernen "
        "Standards."
    ),
    version="0.1.0",
)


@app.get("/", tags=["System"])
def root() -> dict[str, str]:
    """Return a short introduction for the API."""

    return {
        "name": "IWS BDE Plattform",
        "documentation": "/docs",
        "csv_endpoints": "/csv/{entity}",
    }


@app.get("/health", tags=["System"])
def health() -> dict[str, str]:
    """Basic health endpoint."""

    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Employee endpoints
# ---------------------------------------------------------------------------


@app.get("/employees", response_model=list[schemas.EmployeeRead], tags=["Employee"])
def list_employees(db: Session = Depends(get_db)):
    return crud.list_employees(db)


@app.post(
    "/employees",
    response_model=schemas.EmployeeRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Employee"],
)
def create_employee(payload: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_employee(db, payload)
    except crud.CRUDException as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc


@app.get("/employees/{employee_id}", response_model=schemas.EmployeeRead, tags=["Employee"])
def read_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = crud.get_employee(db, employee_id)
    if not employee:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Employee not found")
    return employee


@app.put("/employees/{employee_id}", response_model=schemas.EmployeeRead, tags=["Employee"])
def update_employee(
    employee_id: int, payload: schemas.EmployeeUpdate, db: Session = Depends(get_db)
):
    employee = crud.get_employee(db, employee_id)
    if not employee:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Employee not found")
    return crud.update_employee(db, employee, payload)


@app.delete("/employees/{employee_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Employee"])
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = crud.get_employee(db, employee_id)
    if not employee:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Employee not found")
    crud.delete_employee(db, employee)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# Machine endpoints
# ---------------------------------------------------------------------------


@app.get("/machines", response_model=list[schemas.MachineRead], tags=["Machine"])
def list_machines(db: Session = Depends(get_db)):
    return crud.list_machines(db)


@app.post(
    "/machines",
    response_model=schemas.MachineRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Machine"],
)
def create_machine(payload: schemas.MachineCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_machine(db, payload)
    except crud.CRUDException as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc


@app.get("/machines/{machine_id}", response_model=schemas.MachineRead, tags=["Machine"])
def read_machine(machine_id: int, db: Session = Depends(get_db)):
    machine = crud.get_machine(db, machine_id)
    if not machine:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Machine not found")
    return machine


@app.put("/machines/{machine_id}", response_model=schemas.MachineRead, tags=["Machine"])
def update_machine(
    machine_id: int, payload: schemas.MachineUpdate, db: Session = Depends(get_db)
):
    machine = crud.get_machine(db, machine_id)
    if not machine:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Machine not found")
    return crud.update_machine(db, machine, payload)


@app.delete("/machines/{machine_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Machine"])
def delete_machine(machine_id: int, db: Session = Depends(get_db)):
    machine = crud.get_machine(db, machine_id)
    if not machine:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Machine not found")
    crud.delete_machine(db, machine)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# Work order endpoints
# ---------------------------------------------------------------------------


@app.get("/work-orders", response_model=list[schemas.WorkOrderRead], tags=["WorkOrder"])
def list_work_orders(db: Session = Depends(get_db)):
    return crud.list_work_orders(db)


@app.post(
    "/work-orders",
    response_model=schemas.WorkOrderRead,
    status_code=status.HTTP_201_CREATED,
    tags=["WorkOrder"],
)
def create_work_order(payload: schemas.WorkOrderCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_work_order(db, payload)
    except crud.CRUDException as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc


@app.get(
    "/work-orders/{work_order_id}",
    response_model=schemas.WorkOrderRead,
    tags=["WorkOrder"],
)
def read_work_order(work_order_id: int, db: Session = Depends(get_db)):
    work_order = crud.get_work_order(db, work_order_id)
    if not work_order:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Work order not found")
    return work_order


@app.put(
    "/work-orders/{work_order_id}",
    response_model=schemas.WorkOrderRead,
    tags=["WorkOrder"],
)
def update_work_order(
    work_order_id: int, payload: schemas.WorkOrderUpdate, db: Session = Depends(get_db)
):
    work_order = crud.get_work_order(db, work_order_id)
    if not work_order:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Work order not found")
    return crud.update_work_order(db, work_order, payload)


@app.delete(
    "/work-orders/{work_order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["WorkOrder"],
)
def delete_work_order(work_order_id: int, db: Session = Depends(get_db)):
    work_order = crud.get_work_order(db, work_order_id)
    if not work_order:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Work order not found")
    crud.delete_work_order(db, work_order)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# Operation endpoints
# ---------------------------------------------------------------------------


@app.get("/operations", response_model=list[schemas.OperationRead], tags=["Operation"])
def list_operations(db: Session = Depends(get_db)):
    return crud.list_operations(db)


@app.post(
    "/operations",
    response_model=schemas.OperationRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Operation"],
)
def create_operation(payload: schemas.OperationCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_operation(db, payload)
    except crud.CRUDException as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc


@app.get("/operations/{operation_id}", response_model=schemas.OperationRead, tags=["Operation"])
def read_operation(operation_id: int, db: Session = Depends(get_db)):
    operation = crud.get_operation(db, operation_id)
    if not operation:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Operation not found")
    return operation


@app.put(
    "/operations/{operation_id}",
    response_model=schemas.OperationRead,
    tags=["Operation"],
)
def update_operation(
    operation_id: int, payload: schemas.OperationUpdate, db: Session = Depends(get_db)
):
    operation = crud.get_operation(db, operation_id)
    if not operation:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Operation not found")
    return crud.update_operation(db, operation, payload)


@app.delete(
    "/operations/{operation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Operation"],
)
def delete_operation(operation_id: int, db: Session = Depends(get_db)):
    operation = crud.get_operation(db, operation_id)
    if not operation:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Operation not found")
    crud.delete_operation(db, operation)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# Activity record endpoints
# ---------------------------------------------------------------------------


@app.get(
    "/activity-records",
    response_model=list[schemas.ActivityRecordRead],
    tags=["Activity"],
)
def list_activity_records(db: Session = Depends(get_db)):
    return crud.list_activity_records(db)


@app.post(
    "/activity-records",
    response_model=schemas.ActivityRecordRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Activity"],
)
def create_activity_record(
    payload: schemas.ActivityRecordCreate, db: Session = Depends(get_db)
):
    return crud.create_activity_record(db, payload)


@app.get(
    "/activity-records/{record_id}",
    response_model=schemas.ActivityRecordRead,
    tags=["Activity"],
)
def read_activity_record(record_id: int, db: Session = Depends(get_db)):
    record = crud.get_activity_record(db, record_id)
    if not record:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Activity record not found")
    return record


@app.put(
    "/activity-records/{record_id}",
    response_model=schemas.ActivityRecordRead,
    tags=["Activity"],
)
def update_activity_record(
    record_id: int, payload: schemas.ActivityRecordUpdate, db: Session = Depends(get_db)
):
    record = crud.get_activity_record(db, record_id)
    if not record:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Activity record not found")
    return crud.update_activity_record(db, record, payload)


@app.delete(
    "/activity-records/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Activity"],
)
def delete_activity_record(record_id: int, db: Session = Depends(get_db)):
    record = crud.get_activity_record(db, record_id)
    if not record:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Activity record not found")
    crud.delete_activity_record(db, record)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# CSV Import/Export
# ---------------------------------------------------------------------------


@app.get(
    "/csv/{entity}",
    response_class=Response,
    responses={200: {"content": {"text/csv": {}}}},
    tags=["CSV"],
)
def export_entity_csv(entity: str, db: Session = Depends(get_db)):
    exporter = csv_io.EXPORTERS.get(entity)
    if not exporter:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Unknown entity '{entity}'")
    csv_content = exporter(db)
    filename = f"{entity}.csv"
    headers = {"Content-Disposition": f"attachment; filename={filename}"}
    return Response(content=csv_content, media_type="text/csv", headers=headers)


@app.post("/csv/{entity}", tags=["CSV"])
async def import_entity_csv(
    entity: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    importer = csv_io.IMPORTERS.get(entity)
    if not importer:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Unknown entity '{entity}'")
    if file.content_type not in ("text/csv", "application/vnd.ms-excel", None):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Unsupported content type")
    content = (await file.read()).decode("utf-8-sig")
    stream = io.StringIO(content)
    try:
        summary = importer(db, stream)
    except csv_io.CSVImportError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    return summary.as_dict()
