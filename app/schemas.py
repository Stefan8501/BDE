"""Pydantic schemas for API payloads."""
from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class EmployeeBase(BaseModel):
    personnel_number: str = Field(min_length=1, max_length=50)
    first_name: str = Field(min_length=1, max_length=120)
    last_name: str = Field(min_length=1, max_length=120)
    department: str | None = Field(default=None, max_length=120)
    role: str | None = Field(default=None, max_length=120)
    active: bool = True


class EmployeeCreate(EmployeeBase):
    """Schema used to create new employees."""


class EmployeeUpdate(BaseModel):
    first_name: str | None = Field(default=None, max_length=120)
    last_name: str | None = Field(default=None, max_length=120)
    department: str | None = Field(default=None, max_length=120)
    role: str | None = Field(default=None, max_length=120)
    active: bool | None = None


class EmployeeRead(EmployeeBase):
    id: int

    model_config = {"from_attributes": True}


class MachineBase(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=250)
    location: str | None = Field(default=None, max_length=120)
    active: bool = True


class MachineCreate(MachineBase):
    """Schema used to create machines."""


class MachineUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=120)
    description: str | None = Field(default=None, max_length=250)
    location: str | None = Field(default=None, max_length=120)
    active: bool | None = None


class MachineRead(MachineBase):
    id: int

    model_config = {"from_attributes": True}


class WorkOrderBase(BaseModel):
    order_number: str = Field(min_length=1, max_length=50)
    customer: str | None = Field(default=None, max_length=120)
    article: str | None = Field(default=None, max_length=120)
    quantity: int | None = Field(default=None, ge=0)
    due_date: date | None = None
    status: str | None = Field(default="open", max_length=50)


class WorkOrderCreate(WorkOrderBase):
    """Schema used to create work orders."""


class WorkOrderUpdate(BaseModel):
    customer: str | None = Field(default=None, max_length=120)
    article: str | None = Field(default=None, max_length=120)
    quantity: int | None = Field(default=None, ge=0)
    due_date: date | None = None
    status: str | None = Field(default=None, max_length=50)


class WorkOrderRead(WorkOrderBase):
    id: int

    model_config = {"from_attributes": True}


class OperationBase(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    description: str | None = Field(default=None, max_length=250)
    work_order_id: int
    machine_id: int | None = None
    standard_time_minutes: float | None = Field(default=None, ge=0)
    is_active: bool = True


class OperationCreate(OperationBase):
    """Schema used to create operations."""


class OperationUpdate(BaseModel):
    description: str | None = Field(default=None, max_length=250)
    work_order_id: int | None = None
    machine_id: int | None = None
    standard_time_minutes: float | None = Field(default=None, ge=0)
    is_active: bool | None = None


class OperationRead(OperationBase):
    id: int

    model_config = {"from_attributes": True}


class ActivityRecordBase(BaseModel):
    start_time: datetime
    end_time: datetime | None = None
    employee_id: int
    operation_id: int
    quantity_good: int = Field(default=0, ge=0)
    quantity_reject: int = Field(default=0, ge=0)
    status: str | None = Field(default="completed", max_length=50)
    comment: str | None = Field(default=None, max_length=250)


class ActivityRecordCreate(ActivityRecordBase):
    """Schema used to create activity records."""


class ActivityRecordUpdate(BaseModel):
    start_time: datetime | None = None
    end_time: datetime | None = None
    employee_id: int | None = None
    operation_id: int | None = None
    quantity_good: int | None = Field(default=None, ge=0)
    quantity_reject: int | None = Field(default=None, ge=0)
    status: str | None = Field(default=None, max_length=50)
    comment: str | None = Field(default=None, max_length=250)


class ActivityRecordRead(ActivityRecordBase):
    id: int

    model_config = {"from_attributes": True}
