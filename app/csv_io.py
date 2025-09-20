"""CSV import and export utilities for the IWS BDE system."""
from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from datetime import datetime, date
from typing import Iterable, Mapping

from sqlalchemy.orm import Session

from . import crud, schemas
class CSVImportError(Exception):
    """Raised when CSV data cannot be imported."""


@dataclass
class ImportSummary:
    """Data structure describing the result of a CSV import."""

    inserted: int = 0
    updated: int = 0

    def as_dict(self) -> dict[str, int]:
        return {"inserted": self.inserted, "updated": self.updated}


def _parse_bool(value: str | None, default: bool = True) -> bool:
    if value is None or value == "":
        return default
    return str(value).strip().lower() in {"true", "1", "yes", "ja", "y"}


def _parse_int(value: str | None) -> int | None:
    if value is None or value == "":
        return None
    return int(value)


def _parse_float(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def _parse_date(value: str | None) -> date | None:
    if value is None or value == "":
        return None
    return date.fromisoformat(value)


def _parse_datetime(value: str | None) -> datetime | None:
    if value is None or value == "":
        return None
    return datetime.fromisoformat(value)


def _format_value(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _write_csv(fieldnames: list[str], rows: Iterable[Mapping[str, object]]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow({field: _format_value(row.get(field)) for field in fieldnames})
    return buffer.getvalue()


def export_employees(db: Session) -> str:
    fieldnames = ["personnel_number", "first_name", "last_name", "department", "role", "active"]
    employees = crud.list_employees(db)
    rows = (
        {
            "personnel_number": employee.personnel_number,
            "first_name": employee.first_name,
            "last_name": employee.last_name,
            "department": employee.department,
            "role": employee.role,
            "active": employee.active,
        }
        for employee in employees
    )
    return _write_csv(fieldnames, rows)


def export_machines(db: Session) -> str:
    fieldnames = ["code", "name", "description", "location", "active"]
    machines = crud.list_machines(db)
    rows = (
        {
            "code": machine.code,
            "name": machine.name,
            "description": machine.description,
            "location": machine.location,
            "active": machine.active,
        }
        for machine in machines
    )
    return _write_csv(fieldnames, rows)


def export_work_orders(db: Session) -> str:
    fieldnames = ["order_number", "customer", "article", "quantity", "due_date", "status"]
    work_orders = crud.list_work_orders(db)
    rows = (
        {
            "order_number": order.order_number,
            "customer": order.customer,
            "article": order.article,
            "quantity": order.quantity,
            "due_date": order.due_date,
            "status": order.status,
        }
        for order in work_orders
    )
    return _write_csv(fieldnames, rows)


def export_operations(db: Session) -> str:
    fieldnames = [
        "code",
        "description",
        "order_number",
        "machine_code",
        "standard_time_minutes",
        "is_active",
    ]
    operations = crud.list_operations(db)
    rows = (
        {
            "code": operation.code,
            "description": operation.description,
            "order_number": operation.work_order.order_number if operation.work_order else "",
            "machine_code": operation.machine.code if operation.machine else "",
            "standard_time_minutes": operation.standard_time_minutes,
            "is_active": operation.is_active,
        }
        for operation in operations
    )
    return _write_csv(fieldnames, rows)


def export_activity_records(db: Session) -> str:
    fieldnames = [
        "id",
        "start_time",
        "end_time",
        "personnel_number",
        "operation_code",
        "quantity_good",
        "quantity_reject",
        "status",
        "comment",
    ]
    records = crud.list_activity_records(db)
    rows = (
        {
            "id": record.id,
            "start_time": record.start_time,
            "end_time": record.end_time,
            "personnel_number": record.employee.personnel_number,
            "operation_code": record.operation.code,
            "quantity_good": record.quantity_good,
            "quantity_reject": record.quantity_reject,
            "status": record.status,
            "comment": record.comment,
        }
        for record in records
    )
    return _write_csv(fieldnames, rows)


def import_employees(db: Session, file_obj: io.TextIOBase) -> ImportSummary:
    reader = csv.DictReader(file_obj)
    summary = ImportSummary()
    for row in reader:
        personnel_number = (row.get("personnel_number") or "").strip()
        if not personnel_number:
            raise CSVImportError("Missing personnel_number in employee import")
        payload = schemas.EmployeeCreate(
            personnel_number=personnel_number,
            first_name=(row.get("first_name") or "").strip(),
            last_name=(row.get("last_name") or "").strip(),
            department=row.get("department") or None,
            role=row.get("role") or None,
            active=_parse_bool(row.get("active"), True),
        )
        existing = crud.get_employee_by_personnel_number(db, personnel_number)
        if existing:
            update = schemas.EmployeeUpdate(**payload.model_dump(exclude={"personnel_number"}))
            crud.update_employee(db, existing, update)
            summary.updated += 1
        else:
            crud.create_employee(db, payload)
            summary.inserted += 1
    return summary


def import_machines(db: Session, file_obj: io.TextIOBase) -> ImportSummary:
    reader = csv.DictReader(file_obj)
    summary = ImportSummary()
    for row in reader:
        code = (row.get("code") or "").strip()
        if not code:
            raise CSVImportError("Missing code in machine import")
        payload = schemas.MachineCreate(
            code=code,
            name=(row.get("name") or "").strip(),
            description=row.get("description") or None,
            location=row.get("location") or None,
            active=_parse_bool(row.get("active"), True),
        )
        existing = crud.get_machine_by_code(db, code)
        if existing:
            update = schemas.MachineUpdate(**payload.model_dump(exclude={"code"}))
            crud.update_machine(db, existing, update)
            summary.updated += 1
        else:
            crud.create_machine(db, payload)
            summary.inserted += 1
    return summary


def import_work_orders(db: Session, file_obj: io.TextIOBase) -> ImportSummary:
    reader = csv.DictReader(file_obj)
    summary = ImportSummary()
    for row in reader:
        order_number = (row.get("order_number") or "").strip()
        if not order_number:
            raise CSVImportError("Missing order_number in work order import")
        payload = schemas.WorkOrderCreate(
            order_number=order_number,
            customer=row.get("customer") or None,
            article=row.get("article") or None,
            quantity=_parse_int(row.get("quantity")),
            due_date=_parse_date(row.get("due_date")),
            status=(row.get("status") or "open").strip() or "open",
        )
        existing = crud.get_work_order_by_number(db, order_number)
        if existing:
            update = schemas.WorkOrderUpdate(
                **payload.model_dump(exclude={"order_number"})
            )
            crud.update_work_order(db, existing, update)
            summary.updated += 1
        else:
            crud.create_work_order(db, payload)
            summary.inserted += 1
    return summary


def import_operations(db: Session, file_obj: io.TextIOBase) -> ImportSummary:
    reader = csv.DictReader(file_obj)
    summary = ImportSummary()
    for row in reader:
        code = (row.get("code") or "").strip()
        if not code:
            raise CSVImportError("Missing code in operation import")
        order_number = (row.get("order_number") or "").strip()
        if not order_number:
            raise CSVImportError("Missing order_number for operation import")
        work_order = crud.get_work_order_by_number(db, order_number)
        if not work_order:
            raise CSVImportError(f"Work order '{order_number}' not found for operation {code}")
        machine_code = (row.get("machine_code") or "").strip()
        machine_id = None
        if machine_code:
            machine = crud.get_machine_by_code(db, machine_code)
            if not machine:
                raise CSVImportError(f"Machine '{machine_code}' not found for operation {code}")
            machine_id = machine.id
        payload = schemas.OperationCreate(
            code=code,
            description=row.get("description") or None,
            work_order_id=work_order.id,
            machine_id=machine_id,
            standard_time_minutes=_parse_float(row.get("standard_time_minutes")),
            is_active=_parse_bool(row.get("is_active"), True),
        )
        existing = crud.get_operation_by_code(db, code)
        if existing:
            update = schemas.OperationUpdate(
                **payload.model_dump(exclude={"code"})
            )
            crud.update_operation(db, existing, update)
            summary.updated += 1
        else:
            crud.create_operation(db, payload)
            summary.inserted += 1
    return summary


def import_activity_records(db: Session, file_obj: io.TextIOBase) -> ImportSummary:
    reader = csv.DictReader(file_obj)
    summary = ImportSummary()
    for row in reader:
        start_time = _parse_datetime(row.get("start_time"))
        if not start_time:
            raise CSVImportError("Missing or invalid start_time in activity import")
        employee_number = (row.get("personnel_number") or "").strip()
        if not employee_number:
            raise CSVImportError("Missing personnel_number in activity import")
        employee = crud.get_employee_by_personnel_number(db, employee_number)
        if not employee:
            raise CSVImportError(f"Employee '{employee_number}' not found")
        operation_code = (row.get("operation_code") or "").strip()
        if not operation_code:
            raise CSVImportError("Missing operation_code in activity import")
        operation = crud.get_operation_by_code(db, operation_code)
        if not operation:
            raise CSVImportError(f"Operation '{operation_code}' not found")
        payload = schemas.ActivityRecordCreate(
            start_time=start_time,
            end_time=_parse_datetime(row.get("end_time")),
            employee_id=employee.id,
            operation_id=operation.id,
            quantity_good=_parse_int(row.get("quantity_good")) or 0,
            quantity_reject=_parse_int(row.get("quantity_reject")) or 0,
            status=(row.get("status") or "completed").strip() or "completed",
            comment=row.get("comment") or None,
        )
        record_id = _parse_int(row.get("id"))
        if record_id:
            existing = crud.get_activity_record(db, record_id)
            if not existing:
                raise CSVImportError(f"Activity record with id {record_id} not found")
            update = schemas.ActivityRecordUpdate(**payload.model_dump())
            crud.update_activity_record(db, existing, update)
            summary.updated += 1
        else:
            crud.create_activity_record(db, payload)
            summary.inserted += 1
    return summary


EXPORTERS = {
    "employees": export_employees,
    "machines": export_machines,
    "work_orders": export_work_orders,
    "operations": export_operations,
    "activity_records": export_activity_records,
}


IMPORTERS = {
    "employees": import_employees,
    "machines": import_machines,
    "work_orders": import_work_orders,
    "operations": import_operations,
    "activity_records": import_activity_records,
}
