from sqlalchemy import Column, Boolean, Integer, String, TIMESTAMP, ForeignKey, text
from sqlalchemy.orm import relationship

from .database import Base

class Employees(Base):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    role = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    phone = Column(String(10), nullable=True, unique=True, index=True)
    is_active = Column(Boolean, nullable=False, default=False)

    # def as_dict(self):
    #     return {col.name: getattr(self, col.name) for col in self.__table__.columns if col.name != 'password'}

    __allow_unmapped__ = True


class Owners(Base):
    __tablename__ = 'owners'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    phone = Column(String(10), nullable=True, unique=True, index=True)
    is_active = Column(Boolean, nullable=False, default=False)

    __allow_unmapped__ = True


class Emp_requests(Base):
    __tablename__ = "requests"

    req_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    emp_id  = Column(Integer, ForeignKey("employees.id", ondelete='CASCADE'), nullable=False)

    employee = relationship("Employees")

    __allow_unmapped__ = True