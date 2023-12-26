from sqlalchemy import Column, Boolean, Integer, String, TIMESTAMP, ForeignKey, text, Double
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

    prod_raw_inventories = relationship(
        "PManagerMatInventory", back_populates="materials")
    buff_raw_inventories = relationship(
        "BufferRawMaterialInventory", back_populates="materials")
    raw_inventories = relationship(
        "RawMaterialInventory", back_populates="materials")
    requisition = relationship("Requisition", back_populates="materials")
    mat_return = relationship("MaterialReturn", back_populates="materials")
    orders = relationship("Orders", back_populates="materials")


class RawMaterialInventory(Base):
    __tablename__ = "raw_inventories"

    m_id = Column(Integer, ForeignKey("materials.id"), primary_key=True)
    avail_qty = Column(Integer, nullable=False)

    materials = relationship("Material", back_populates="raw_inventories")


class BufferRawMaterialInventory(Base):
    __tablename__ = "buff_raw_inventories"

    m_id = Column(Integer, ForeignKey("materials.id"), primary_key=True)
    avail_qty = Column(Integer, nullable=False)

    materials = relationship("Material", back_populates="buff_raw_inventories")


class PManagerMatInventory(Base):
    __tablename__ = "prod_raw_inventories"

    m_id = Column(Integer, ForeignKey("materials.id"), primary_key=True)
    avail_qty = Column(Integer, nullable=False)

    materials = relationship("Material", back_populates="prod_raw_inventories")


class Slot(Base):
    __tablename__ = 'slots'

    slot_id = Column(Integer, primary_key=True,
                     nullable=False, autoincrement=True)
    remarks = Column(String(255), nullable=True)
    req_time = Column(TIMESTAMP(timezone=True),
                      nullable=False, server_default=text('now()'))
    req_by = Column(Integer, ForeignKey("employees.id"), nullable=True)
    issued_by = Column(Integer, ForeignKey("employees.id"), nullable=True)
    issue_time = Column(TIMESTAMP(timezone=True),
                        nullable=True)
    issue_status = Column(Boolean, nullable=False, default=False)

    requisition = relationship(
        "Requisition", back_populates="slots", cascade='all, delete-orphan')
    r_slots = relationship("ReturnSlot", back_populates="slots")
    batches = relationship("Batches", back_populates="slots")
    __allow_unmapped__ = True


class Requisition(Base):
    __tablename__ = "requisition"

    req_id = Column(Integer, primary_key=True,
                    nullable=False, autoincrement=True)
    slot_id = Column(Integer, ForeignKey(
        "slots.slot_id", ondelete='CASCADE'), nullable=False)
    m_id = Column(Integer, ForeignKey("materials.id"))
    qty_req = Column(Integer, nullable=False)

    issue_qty = Column(Integer, nullable=False, default=0)

    materials = relationship("Material", back_populates="requisition")
    slots = relationship("Slot", back_populates="requisition")

    __allow_unmapped__ = True


# for returning material
class ReturnSlot(Base):
    __tablename__ = 'r_slots'

    slot_id = Column(Integer, primary_key=True,
                     nullable=False, autoincrement=True)
    req_slot_id = Column(Integer, ForeignKey("slots.slot_id"), nullable=False)
    remarks = Column(String(255), nullable=True)
    ret_time = Column(TIMESTAMP(timezone=True),
                      nullable=False, server_default=text('now()'))

    ret_by = Column(Integer, ForeignKey("employees.id"), nullable=True)
    approved = Column(Boolean, nullable=False, default=False)

    mat_return = relationship(
        "MaterialReturn", back_populates="r_slots", cascade='all, delete-orphan')
    slots = relationship("Slot", back_populates="r_slots")
    __allow_unmapped__ = True


class MaterialReturn(Base):
    __tablename__ = "mat_return"

    ret_id = Column(Integer, primary_key=True,
                    nullable=False, autoincrement=True)
    slot_id = Column(Integer, ForeignKey(
        "r_slots.slot_id", ondelete='CASCADE'), nullable=False)
    m_id = Column(Integer, ForeignKey("materials.id"))
    qty_ret = Column(Integer, nullable=False)

    materials = relationship("Material", back_populates="mat_return")
    r_slots = relationship("ReturnSlot", back_populates="mat_return")

    __allow_unmapped__ = True


class Batches(Base):
    __tablename__ = 'batches'

    batch_id = Column(Integer, primary_key=True,
                      nullable=False, autoincrement=True)
    req_slot_id = Column(Integer, ForeignKey("slots.slot_id"), nullable=False)

    remarks = Column(String(255), nullable=True)
    handover_by = Column(Integer, ForeignKey("employees.id"), nullable=False)
    is_recieved = Column(Boolean, nullable=False, default=False)
    recieved_by = Column(Integer, ForeignKey("employees.id"), nullable=True)
    recieved_time = Column(TIMESTAMP(timezone=True),
                           nullable=True)
    mfg = Column(TIMESTAMP(timezone=True), nullable=False,
                 server_default=text('now()'))

    prod_handover = relationship(
        "Prod_Handover", back_populates="batches", cascade='all, delete-orphan')
    slots = relationship("Slot", back_populates="batches")

    __allow_unmapped__ = True


class Prod_Handover(Base):
    __tablename__ = "prod_handover"

    handover_id = Column(Integer, primary_key=True,
                         nullable=False, autoincrement=True)
    batch_id = Column(Integer, ForeignKey(
        "batches.batch_id", ondelete='CASCADE'), nullable=False)
    p_name = Column(String(255), nullable=False)
    qty = Column(Integer, nullable=False)

    batches = relationship("Batches", back_populates="prod_handover")

    __allow_unmapped__ = True


# gate keeper tables: accesed by gatekeeper
class Purchases(Base):
    __tablename__ = "purchases"

    pur_id = Column(Integer, primary_key=True,
                    nullable=False, autoincrement=True)
    supp_name = Column(String(255), nullable=True)
    t_amount = Column(Double, nullable=False)
    invoice = Column(String(50), nullable=False)
    vehicle = Column(String(50), nullable=False)
    pur_time = Column(TIMESTAMP(timezone=True),
                      nullable=False, server_default=text('now()'))

    remarks = Column(String(255), nullable=True)
    pur_by = Column(Integer, ForeignKey("employees.id"), nullable=True)
    recieved_by = Column(Integer, ForeignKey("employees.id"), nullable=True)
    exp_date = Column(TIMESTAMP(timezone=True),
                      nullable=True,)
    recv_time = Column(TIMESTAMP(timezone=True),
                       nullable=True,)
    recieved = Column(Boolean, nullable=False, server_default="false")

    orders = relationship(
        "Orders", back_populates="purchases", cascade='all, delete-orphan')

    __allow_unmapped__ = True


class Orders(Base):
    __tablename__ = "orders"

    ord_id = Column(Integer, primary_key=True,
                    nullable=False, autoincrement=True)
    m_id = Column(Integer, ForeignKey("materials.id"))
    ord_qty = Column(Integer, nullable=False)
    recieved_qty = Column(Integer, nullable=False, server_default="0")

    pur_id = Column(Integer, ForeignKey(
        "purchases.pur_id", ondelete='CASCADE'), nullable=True)

    materials = relationship("Material", back_populates="orders")
    purchases = relationship("Purchases", back_populates="orders")

    __allow_unmapped__ = True


# class Consignments(Base):
#     __tablename__ = "consignment"

#     cg_id = Column(Integer, primary_key=True,
#                    nullable=False, autoincrement=True)
#     remarks = Column(String(255), nullable=True)
#     dis_id = Column(Integer, ForeignKey("dis_details.dis_id"), nullable=True)
#     gk_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
#     recv_time = Column(TIMESTAMP(timezone=True),
#                        nullable=False, server_default=text('now()'))
#     __allow_unmapped__ = True


# # main tales for records
# #for stock manageryy


class Transports(Base):
    __tablename__ = "transports"

    tran_id = Column(Integer, primary_key=True,
                     nullable=False, autoincrement=True)
    veh_no = Column(String(255), nullable=False)
    name = Column(String(255), nullable=True)
    # place = Column(String(255), nullable=True)

    dis_details = relationship("Dispatches", back_populates="transports")

    __allow_unmapped__ = True


class Drivers(Base):
    __tablename__ = "drivers"

    drv_id = Column(Integer, primary_key=True,
                    nullable=False, autoincrement=True)
    name = Column(String(255), nullable=True)
    phone = Column(String(10), nullable=True, index=True, unique=True)
    license_no = Column(String(25), nullable=True)

    dis_details = relationship("Dispatches", back_populates="drivers")

    __allow_unmapped__ = True


class Dispatches(Base):
    __tablename__ = "dis_details"

    dis_id = Column(Integer, primary_key=True,
                    nullable=False, autoincrement=True)
    buyer = Column(String(100), nullable=True)
    invoice = Column(String(50), nullable=False)
    inv_value = Column(Integer, nullable=False)
    dis_by = Column(Integer, ForeignKey("employees.id"), nullable=True)
    checked_by = Column(Integer, ForeignKey("employees.id"), nullable=True)

    trans_id = Column(Integer, ForeignKey("transports.tran_id"), nullable=True)
    driv_id = Column(Integer, ForeignKey("drivers.drv_id"), nullable=True)
    dis_time = Column(TIMESTAMP(timezone=True),
                      nullable=False, server_default=text('now()'))
    recv_time = Column(TIMESTAMP(timezone=True),
                       nullable=True,)
    checkout = Column(Boolean, nullable=False, server_default="false")

    consignments = relationship(
        "Consignments", back_populates="dis_details", cascade='all, delete-orphan')
    drivers = relationship("Drivers", back_populates="dis_details")
    transports = relationship("Transports", back_populates="dis_details")

    __allow_unmapped__ = True


class Consignments(Base):
    __tablename__ = "consignments"

    cg_id = Column(Integer, primary_key=True,
                   nullable=False, autoincrement=True)
    p_name = Column(String(255), nullable=False)
    qty = Column(Integer, nullable=False)
    checked_qty = Column(Integer, nullable=False, server_default="0")

    dis_id = Column(Integer, ForeignKey(
        "dis_details.dis_id", ondelete='CASCADE'), nullable=True)

    dis_details = relationship("Dispatches", back_populates="consignments")

    __allow_unmapped__ = True

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
