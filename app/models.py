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
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
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
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    phone = Column(String(10), nullable=True, unique=True, index=True)
    is_active = Column(Boolean, nullable=False, default=False)

    __allow_unmapped__ = True


class Emp_requests(Base):
    __tablename__ = "requests"
    req_id = Column(Integer, primary_key=True,
                    nullable=False, autoincrement=True)
    emp_id = Column(Integer, ForeignKey(
        "employees.id", ondelete='CASCADE'), nullable=False)
    employee = relationship("Employees")

    __allow_unmapped__ = True









# phase 2 here
class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True,
                      nullable=False, autoincrement=True)
    material = Column(String(255), nullable=False)
    umo = Column(String(255), nullable=True)
    g_no = Column(Integer, nullable=False)
    __allow_unmapped__ = True

    requisition = relationship("Requisition", back_populates="materials")


# class MaterialIssued(Base):
#     __tablename__ = "mat_issued"

#     issue_id = Column(Integer, primary_key=True,
#                       nullable=False, autoincrement=True)
#     m_id = Column(Integer, ForeignKey("materials.id"))
#     qty_issued = Column(Integer, nullable=False)
#     remarks = Column(String(255), nullable=True)
#     issued_by = Column(Integer, ForeignKey("employees.id"), nullable=True)
#     issue_time = Column(TIMESTAMP(timezone=True),
#                         nullable=False, server_default=text('now()'))

#     material = relationship("Material", back_populates="mat_issued")
#     __allow_unmapped__ = True

class Slot(Base):
    __tablename__ = 'slots'

    slot_id = Column(Integer, primary_key=True,
                    nullable=False, autoincrement=True)
    remarks = Column(String(255), nullable=True)
    req_time = Column(TIMESTAMP(timezone=True),
                      nullable=False, server_default=text('now()'))
    req_by = Column(Integer, ForeignKey("employees.id"), nullable=True)
    issue_status = Column(Integer, nullable=False, default=0)

    requisition = relationship("Requisition", back_populates="slots")

    __allow_unmapped__ = True

class Requisition(Base):
    __tablename__ = "requisition"

    req_id = Column(Integer, primary_key=True,
                    nullable=False, autoincrement=True)
    slot_id = Column(Integer,ForeignKey("slots.slot_id"), nullable=False)
    m_id = Column(Integer, ForeignKey("materials.id"))
    qty_req = Column(Integer, nullable=False,)

    issue_qty = Column(Integer, nullable=False, default=0)
    issued_by = Column(Integer, ForeignKey("employees.id"), nullable=True)

    materials = relationship("Material", back_populates="requisition")
    slots = relationship("Slot", back_populates="requisition")

    __allow_unmapped__ = True


class MaterialReturn(Base):
    __tablename__ = "mat_return"

    ret_id = Column(Integer, primary_key=True,
                       nullable=False, autoincrement=True)
    m_id = Column(Integer, ForeignKey("materials.id"))
    qty_ret = Column(Integer, nullable=False,)
    remarks = Column(String(255), nullable=True)
    ret_by = Column(Integer, ForeignKey("employees.id"), nullable=True)
    ret_time = Column(TIMESTAMP(timezone=True),
                      nullable=False, server_default=text('now()'))
    # material = relationship("Material", back_populates="mat_return")
    __allow_unmapped__ = True


# class Prod_Handover(Base):
#     __tablename__ = "prod_handover"

#     prod_id = Column(Integer, primary_key=True,
#                      nullable=False, autoincrement=True)
#     batch_no = Column(Integer, nullable=True)
#     product = Column(String(255), nullable=False)
#     qty = Column(Integer, nullable=False)
#     remarks = Column(String(255), nullable=True)
#     prod_manager = Column(Integer, ForeignKey("employees.id"), nullable=True)
#     recieved_by = Column(Integer, ForeignKey("employees.id"), nullable=True)
#     mfg = Column(TIMESTAMP(timezone=True), nullable=False,
#                  server_default=text('now()'))
#     __allow_unmapped__ = True


# # gate keeper tables: accesed by gatekeeper
# class Purchases(Base):
#     __tablename__ = "pur_details"

#     pur_id = Column(Integer, primary_key=True,
#                     nullable=False, autoincrement=True)
#     supp = Column(String(255), nullable=True)
#     material = Column(String(255), nullable=False)
#     amount = Column(Integer, nullable=False)
#     invoice = Column(String(255), nullable=False)
#     vehicle = Column(String(255), nullable=False)
#     pur_time = Column(TIMESTAMP(timezone=True),
#                       nullable=False, server_default=text('now()'))

#     __allow_unmapped__ = True


# class Orders(Base):
#     __tablename__ = "orders"

#     ord_id = Column(Integer, primary_key=True,
#                     nullable=False, autoincrement=True)
#     m_id = Column(Integer, ForeignKey("materials.id"))
#     ord_qty = Column(Integer, nullable=False)
#     recieved_qty = Column(Integer, nullable=True)
#     remarks = Column(String(255), nullable=True)
#     pur_id = Column(Integer, ForeignKey("pur_details.pur_id"), nullable=True)
#     gk_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
#     exp_date = Column(TIMESTAMP(timezone=True),
#                        nullable=True,)
#     recv_time = Column(TIMESTAMP(timezone=True),
#                        nullable=True,)

#     __allow_unmapped__ = True


# class Consignments(Base):
#     __tablename__ = "consignment"

#     cg_id = Column(Integer, primary_key=True,
#                    nullable=False, autoincrement=True)
#     product = Column(String(255), nullable=False)
#     cons_qty = Column(Integer, nullable=False)
#     pkg = Column(Integer, nullable=True)
#     batch_no = Column(Integer, nullable=False)
#     remarks = Column(String(255), nullable=True)
#     dis_id = Column(Integer, ForeignKey("dis_details.dis_id"), nullable=True)
#     gk_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
#     recv_time = Column(TIMESTAMP(timezone=True),
#                        nullable=False, server_default=text('now()'))
#     __allow_unmapped__ = True



# # main tales for records
# #for stock manageryy
# class RawMaterials(Base):
#     __tablename__ = "raw_mat"

#     mat_id = Column(Integer, primary_key=True,
#                     nullable=False, autoincrement=True)
#     material = Column(String(255), nullable=False)
#     qty = Column(Integer, nullable=False)
#     pur_id = Column(Integer, ForeignKey("pur_details.pur_id"), nullable=True)
#     __allow_unmapped__ = True


# class Transports(Base):
#     __tablename__ = "transports"

#     tran_id = Column(Integer, primary_key=True,
#                      nullable=False, autoincrement=True)
#     vehicle = Column(String(255), nullable=False)
#     name = Column(String(255), nullable=True)
#     place = Column(String(255), nullable=True)
#     __allow_unmapped__ = True


# class Drivers(Base):
#     __tablename__ = "drivers"

#     drv_id = Column(Integer, primary_key=True,
#                      nullable=False, autoincrement=True)
#     name = Column(String(255), nullable=True)
#     phone = Column(String(10), nullable=True)
#     phone = Column(String(25), nullable=True)
#     __allow_unmapped__ = True


# class Dispatches(Base):
#     __tablename__ = "dis_details"

#     dis_id = Column(Integer, primary_key=True,
#                     nullable=False, autoincrement=True)
#     buyer = Column(String(255), nullable=True)
#     invoice = Column(String(255), nullable=False)
#     inv_value = Column(Integer, nullable=False)
#     trans = Column(Integer, ForeignKey("transports.tran_id"), nullable=True)
#     driv_details = Column(Integer, ForeignKey("drivers.drv_id"), nullable=True)
#     dis_time = Column(TIMESTAMP(timezone=True),
#                       nullable=False, server_default=text('now()'))

#     __allow_unmapped__ = True


# class Products(Base):
#     __tablename__ = "man_prod"

#     man_id = Column(Integer, primary_key=True,
#                     nullable=False, autoincrement=True)
#     product = Column(String(255), nullable=False)
#     qty = Column(Integer, nullable=False)
#     remarks = Column(String(255), nullable=True)
#     mfg = Column(TIMESTAMP(timezone=True), nullable=False,
#                  server_default=text('now()'))
#     dis_id = Column(Integer, ForeignKey("dis_details.dis_id"), nullable=True)
#     __allow_unmapped__ = True
