"""CRUD helper functions for the BDE domain objects."""
from __future__ import annotations

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import models, schemas


class CRUDException(Exception):
    """Raised when a CRUD operation cannot be completed."""


# Employee helpers

def list_employees(db: Session) -> Sequence[models.Employee]:
    return db.scalars(select(models.Employee).order_by(models.Employee.personnel_number)).all()


def get_employee(db: Session, employee_id: int) -> models.Employee | None:
    return db.get(models.Employee, employee_id)


def get_employee_by_personnel_number(db: Session, personnel_number: str) -> models.Employee | None:
    stmt = select(models.Employee).where(models.Employee.personnel_number == personnel_number)
    return db.scalar(stmt)


def create_employee(db: Session, payload: schemas.EmployeeCreate) -> models.Employee:
    employee = models.Employee(**payload.model_dump())
    db.add(employee)
    try:
        db.commit()
    except IntegrityError as exc:  # pragma: no cover - defensive programming
        db.rollback()
        raise CRUDException("Employee with this personnel number already exists") from exc
    db.refresh(employee)
    return employee


def update_employee(db: Session, employee: models.Employee, payload: schemas.EmployeeUpdate) -> models.Employee:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(employee, field, value)
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


def delete_employee(db: Session, employee: models.Employee) -> None:
    db.delete(employee)
    db.commit()


# Machine helpers

def list_machines(db: Session) -> Sequence[models.Machine]:
    return db.scalars(select(models.Machine).order_by(models.Machine.code)).all()


def get_machine(db: Session, machine_id: int) -> models.Machine | None:
    return db.get(models.Machine, machine_id)


def get_machine_by_code(db: Session, code: str) -> models.Machine | None:
    stmt = select(models.Machine).where(models.Machine.code == code)
    return db.scalar(stmt)


def create_machine(db: Session, payload: schemas.MachineCreate) -> models.Machine:
    machine = models.Machine(**payload.model_dump())
    db.add(machine)
    try:
        db.commit()
    except IntegrityError as exc:  # pragma: no cover
        db.rollback()
        raise CRUDException("Machine with this code already exists") from exc
    db.refresh(machine)
    return machine


def update_machine(db: Session, machine: models.Machine, payload: schemas.MachineUpdate) -> models.Machine:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(machine, field, value)
    db.add(machine)
    db.commit()
    db.refresh(machine)
    return machine


def delete_machine(db: Session, machine: models.Machine) -> None:
    db.delete(machine)
    db.commit()


# Work order helpers

def list_work_orders(db: Session) -> Sequence[models.WorkOrder]:
    return db.scalars(select(models.WorkOrder).order_by(models.WorkOrder.order_number)).all()


def get_work_order(db: Session, work_order_id: int) -> models.WorkOrder | None:
    return db.get(models.WorkOrder, work_order_id)


def get_work_order_by_number(db: Session, order_number: str) -> models.WorkOrder | None:
    stmt = select(models.WorkOrder).where(models.WorkOrder.order_number == order_number)
    return db.scalar(stmt)


def create_work_order(db: Session, payload: schemas.WorkOrderCreate) -> models.WorkOrder:
    work_order = models.WorkOrder(**payload.model_dump())
    db.add(work_order)
    try:
        db.commit()
    except IntegrityError as exc:  # pragma: no cover
        db.rollback()
        raise CRUDException("Work order with this number already exists") from exc
    db.refresh(work_order)
    return work_order


def update_work_order(db: Session, work_order: models.WorkOrder, payload: schemas.WorkOrderUpdate) -> models.WorkOrder:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(work_order, field, value)
    db.add(work_order)
    db.commit()
    db.refresh(work_order)
    return work_order


def delete_work_order(db: Session, work_order: models.WorkOrder) -> None:
    db.delete(work_order)
    db.commit()


# Operation helpers

def list_operations(db: Session) -> Sequence[models.Operation]:
    return db.scalars(select(models.Operation).order_by(models.Operation.code)).all()


def get_operation(db: Session, operation_id: int) -> models.Operation | None:
    return db.get(models.Operation, operation_id)


def get_operation_by_code(db: Session, code: str) -> models.Operation | None:
    stmt = select(models.Operation).where(models.Operation.code == code)
    return db.scalar(stmt)


def create_operation(db: Session, payload: schemas.OperationCreate) -> models.Operation:
    operation = models.Operation(**payload.model_dump())
    db.add(operation)
    try:
        db.commit()
    except IntegrityError as exc:  # pragma: no cover
        db.rollback()
        raise CRUDException("Operation with this code already exists") from exc
    db.refresh(operation)
    return operation


def update_operation(db: Session, operation: models.Operation, payload: schemas.OperationUpdate) -> models.Operation:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(operation, field, value)
    db.add(operation)
    db.commit()
    db.refresh(operation)
    return operation


def delete_operation(db: Session, operation: models.Operation) -> None:
    db.delete(operation)
    db.commit()


# Activity record helpers

def list_activity_records(db: Session) -> Sequence[models.ActivityRecord]:
    return db.scalars(select(models.ActivityRecord).order_by(models.ActivityRecord.start_time.desc())).all()


def get_activity_record(db: Session, record_id: int) -> models.ActivityRecord | None:
    return db.get(models.ActivityRecord, record_id)


def create_activity_record(db: Session, payload: schemas.ActivityRecordCreate) -> models.ActivityRecord:
    activity = models.ActivityRecord(**payload.model_dump())
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


def update_activity_record(db: Session, activity: models.ActivityRecord, payload: schemas.ActivityRecordUpdate) -> models.ActivityRecord:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(activity, field, value)
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


def delete_activity_record(db: Session, activity: models.ActivityRecord) -> None:
    db.delete(activity)
    db.commit()
