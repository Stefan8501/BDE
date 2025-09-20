"""SQLAlchemy models for the IWS BDE system."""
from __future__ import annotations

from datetime import datetime, date

from sqlalchemy import Date, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Employee(Base):
    """Employee master data."""

    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    personnel_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(120), nullable=False)
    last_name: Mapped[str] = mapped_column(String(120), nullable=False)
    department: Mapped[str | None] = mapped_column(String(120), default=None)
    role: Mapped[str | None] = mapped_column(String(120), default=None)
    active: Mapped[bool] = mapped_column(default=True)

    activities: Mapped[list[ActivityRecord]] = relationship(
        back_populates="employee",
        cascade="all, delete-orphan",
    )


class Machine(Base):
    """Machine master data."""

    __tablename__ = "machines"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(String(250))
    location: Mapped[str | None] = mapped_column(String(120))
    active: Mapped[bool] = mapped_column(default=True)

    operations: Mapped[list[Operation]] = relationship(
        back_populates="machine",
        cascade="all, delete-orphan",
    )


class WorkOrder(Base):
    """Production order data."""

    __tablename__ = "work_orders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    customer: Mapped[str | None] = mapped_column(String(120))
    article: Mapped[str | None] = mapped_column(String(120))
    quantity: Mapped[int | None] = mapped_column(default=None)
    due_date: Mapped[date | None] = mapped_column(Date, default=None)
    status: Mapped[str | None] = mapped_column(String(50), default="open")

    operations: Mapped[list[Operation]] = relationship(
        back_populates="work_order",
        cascade="all, delete-orphan",
    )


class Operation(Base):
    """Operations that belong to work orders."""

    __tablename__ = "operations"
    __table_args__ = (UniqueConstraint("code", name="uq_operation_code"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(String(250))
    work_order_id: Mapped[int] = mapped_column(ForeignKey("work_orders.id"), nullable=False)
    machine_id: Mapped[int | None] = mapped_column(ForeignKey("machines.id"), default=None)
    standard_time_minutes: Mapped[float | None] = mapped_column(default=None)
    is_active: Mapped[bool] = mapped_column(default=True)

    work_order: Mapped[WorkOrder] = relationship(back_populates="operations")
    machine: Mapped[Machine | None] = relationship(back_populates="operations")
    activities: Mapped[list[ActivityRecord]] = relationship(
        back_populates="operation",
        cascade="all, delete-orphan",
    )


class ActivityRecord(Base):
    """Captured production data."""

    __tablename__ = "activity_records"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[datetime | None] = mapped_column(DateTime, default=None)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False)
    operation_id: Mapped[int] = mapped_column(ForeignKey("operations.id"), nullable=False)
    quantity_good: Mapped[int] = mapped_column(default=0)
    quantity_reject: Mapped[int] = mapped_column(default=0)
    status: Mapped[str | None] = mapped_column(String(50), default="completed")
    comment: Mapped[str | None] = mapped_column(String(250))

    employee: Mapped[Employee] = relationship(back_populates="activities")
    operation: Mapped[Operation] = relationship(back_populates="activities")
