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
    # log_entries_emp1 = relationship(
    #     'LogEntries', foreign_keys='LogEntries.emp1_id', back_populates='emp1', uselist=True)
    # log_entries_emp2 = relationship(
    #     'LogEntries', foreign_keys='LogEntries.emp2_id', back_populates='emp2', uselist=True)

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
    log_sub_entries = relationship("LogSubEntries", back_populates="materials")

    history_requisition = relationship(
        "HistoryRequisition", back_populates="materials")
    history_mat_return = relationship(
        "HistoryMaterialReturn", back_populates="materials")
    history_orders = relationship("HistoryOrders", back_populates="materials")


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
    # r_slots = relationship("ReturnSlot", back_populates="slots")
    __allow_unmapped__ = True


class Requisition(Base):
    __tablename__ = "requisition"

    req_id = Column(Integer, primary_key=True,
                    nullable=False, autoincrement=True)
    slot_id = Column(Integer, ForeignKey(
        "slots.slot_id", ondelete='CASCADE'), nullable=False)
    m_id = Column(Integer, ForeignKey("materials.id"))
    qty_req = Column(Integer, nullable=False)

    consum_qty = Column(Integer, nullable=False, default=0)
    issue_qty = Column(Integer, nullable=False, default=0)

    materials = relationship("Material", back_populates="requisition")
    slots = relationship("Slot", back_populates="requisition")
    mat_return = relationship("MaterialReturn", back_populates="requisition")

    __allow_unmapped__ = True


# for returning material
class ReturnSlot(Base):
    __tablename__ = 'r_slots'

    slot_id = Column(Integer, primary_key=True,
                     nullable=False, autoincrement=True)
    req_slot_id = Column(Integer, ForeignKey(
        "history_req_slots.slot_id", ondelete='SET NULL'), nullable=True)
    remarks = Column(String(255), nullable=True)
    ret_time = Column(TIMESTAMP(timezone=True),
                      nullable=False, server_default=text('now()'))

    ret_by = Column(Integer, ForeignKey("employees.id"), nullable=True)
    approved = Column(Boolean, nullable=False, default=False)

    mat_return = relationship(
        "MaterialReturn", back_populates="r_slots", cascade='all, delete-orphan')
    history_req_slots = relationship(
        "HistoryReqSlot", back_populates="r_slots")
    __allow_unmapped__ = True


class MaterialReturn(Base):
    __tablename__ = "mat_return"

    ret_id = Column(Integer, primary_key=True,
                    nullable=False, autoincrement=True)
    slot_id = Column(Integer, ForeignKey(
        "r_slots.slot_id", ondelete='CASCADE'), nullable=False)

    # for requisitions mapping
    old_req_id = Column(Integer, ForeignKey(
        "requisition.req_id", ondelete='SET NULL'), nullable=True)
    req_id = Column(Integer, ForeignKey(
        "history_requisition.req_id", ondelete='SET NULL'), nullable=True)
    m_id = Column(Integer, ForeignKey("materials.id"))
    qty_ret = Column(Integer, nullable=False)

    materials = relationship("Material", back_populates="mat_return")
    r_slots = relationship("ReturnSlot", back_populates="mat_return")
    requisition = relationship(
        "Requisition", back_populates="mat_return")
    history_requisition = relationship(
        "HistoryRequisition", back_populates="mat_return")

    __allow_unmapped__ = True


class Batches(Base):
    __tablename__ = 'batches'

    batch_id = Column(Integer, primary_key=True,
                      nullable=False, autoincrement=True)
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

    __allow_unmapped__ = True



class Prod_Handover(Base):
    __tablename__ = "prod_handover"

    handover_id = Column(Integer, primary_key=True,
                         nullable=False, autoincrement=True)
    batch_id = Column(Integer, ForeignKey(
        "batches.batch_id", ondelete='CASCADE'), nullable=False)
    prod_id = Column(Integer, ForeignKey("products.id"))
    qty = Column(Integer, nullable=False)

    products = relationship("Products", back_populates="prod_handover")
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


class Transports(Base):
    __tablename__ = "transports"

    tran_id = Column(Integer, primary_key=True,
                     nullable=False, autoincrement=True)
    veh_no = Column(String(255), nullable=False)
    name = Column(String(255), nullable=True)
    # place = Column(String(255), nullable=True)

    dis_details = relationship("Dispatches", back_populates="transports")
    history_dis_details = relationship(
        "HistoryDispatches", back_populates="transports")

    __allow_unmapped__ = True


class Drivers(Base):
    __tablename__ = "drivers"

    drv_id = Column(Integer, primary_key=True,
                    nullable=False, autoincrement=True)
    name = Column(String(255), nullable=True)
    phone = Column(String(10), nullable=True, index=True, unique=True)
    license_no = Column(String(25), nullable=True)

    dis_details = relationship("Dispatches", back_populates="drivers")
    history_dis_details = relationship(
        "HistoryDispatches", back_populates="drivers")

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
    # p_name = Column(String(255), nullable=False)
    prod_id = Column(Integer, ForeignKey("products.id"))
    qty = Column(Integer, nullable=False)
    checked_qty = Column(Integer, nullable=False, server_default="0")

    dis_id = Column(Integer, ForeignKey(
        "dis_details.dis_id", ondelete='CASCADE'), nullable=True)

    products = relationship("Products", back_populates="consignments")
    dis_details = relationship("Dispatches", back_populates="consignments")

    __allow_unmapped__ = True


class Products(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    product = Column(String(255), nullable=False)
    g_no = Column(Integer, nullable=False)

    log_sub_entries = relationship("LogSubEntries", back_populates="products")
    prod_handover = relationship("Prod_Handover", back_populates="products")
    consignments = relationship("Consignments", back_populates="products")

    history_prod_handover = relationship(
        "HistoryProd_Handover", back_populates="products")
    history_consignments = relationship(
        "HistoryConsignments", back_populates="products")
    products_inventories = relationship(
        "ProductsInventory", back_populates="products")
    buff_products_inventories = relationship(
        "BufferProductsInventory", back_populates="products")
    prod_products_inventories = relationship(
        "PManagerProductsInventory", back_populates="products")
    __allow_unmapped__ = True


class ProductsInventory(Base):
    __tablename__ = "products_inventories"
    p_id = Column(Integer, ForeignKey("products.id"), primary_key=True)
    avail_qty = Column(Integer, nullable=False)

    products = relationship("Products", back_populates="products_inventories")


class BufferProductsInventory(Base):
    __tablename__ = "buff_products_inventories"
    p_id = Column(Integer, ForeignKey("products.id"), primary_key=True)
    avail_qty = Column(Integer, nullable=False)

    products = relationship("Products", back_populates="buff_products_inventories")


class PManagerProductsInventory(Base):
    __tablename__ = "prod_products_inventories"
    p_id = Column(Integer, ForeignKey("products.id"), primary_key=True)
    avail_qty = Column(Integer, nullable=False)

    products = relationship("Products", back_populates="prod_products_inventories")

# History DATA for logs
class LogEntries(Base):
    __tablename__ = "log_entries"

    log_id = Column(Integer, primary_key=True,
                    nullable=False, autoincrement=True)
    type_id = Column(Integer, nullable=False)
    slot_id = Column(Integer, nullable=False)
    emp1_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    emp2_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    update_time = Column(TIMESTAMP(timezone=True), nullable=True)
    status = Column(Integer, nullable=False)
    map_id = Column(Integer, ForeignKey('log_entries.log_id'), nullable=True)

    log_sub_entries = relationship(
        "LogSubEntries", back_populates="log_entries")

    mapped_entries = relationship('LogEntries', remote_side=[
                                  log_id])  # for self join relationship
    # emp1 = relationship('Employees', foreign_keys=[
    #                     emp1_id], backref='log_entries_emp1', uselist=False)
    # emp2 = relationship('Employees', foreign_keys=[
    #                     emp2_id], backref='log_entries_emp2', uselist=False)

    __allow_unmapped__ = True


class LogSubEntries(Base):
    __tablename__ = "log_sub_entries"

    entry_id = Column(Integer, primary_key=True,
                      nullable=False, autoincrement=True)
    # type_id = Column(Integer, nullable=False)
    log_id = Column(Integer, ForeignKey("log_entries.log_id"))
    m_id = Column(Integer, ForeignKey("materials.id"))
    prod_id = Column(Integer, ForeignKey("products.id"))  # to be a foriegn key
    qty = Column(Integer, nullable=False)
    entry_time = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))

    materials = relationship("Material", back_populates="log_sub_entries")
    products = relationship("Products", back_populates="log_sub_entries")
    log_entries = relationship("LogEntries", back_populates="log_sub_entries")
    __allow_unmapped__ = True


# History transactions between prod and stock
class HistoryReqSlot(Base):
    __tablename__ = 'history_req_slots'

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
    comp_time = Column(TIMESTAMP(timezone=True),
                       nullable=False, server_default=text('now()'))

    r_slots = relationship(
        "ReturnSlot", back_populates="history_req_slots")

    history_requisition = relationship(
        "HistoryRequisition", back_populates="history_req_slots", cascade='all, delete-orphan')
    history_r_slots = relationship(
        "HistoryReturnSlot", back_populates="history_req_slots")
    __allow_unmapped__ = True


class HistoryRequisition(Base):
    __tablename__ = "history_requisition"

    req_id = Column(Integer, primary_key=True,
                    nullable=False, autoincrement=True)
    slot_id = Column(Integer, ForeignKey(
        "history_req_slots.slot_id", ondelete='CASCADE'), nullable=False)
    m_id = Column(Integer, ForeignKey("materials.id"))

    qty_req = Column(Integer, nullable=False)
    consum_qty = Column(Integer, nullable=False, default=0)
    issue_qty = Column(Integer, nullable=False, default=0)

    materials = relationship("Material", back_populates="history_requisition")
    mat_return = relationship(
        "MaterialReturn", back_populates="history_requisition")
    history_req_slots = relationship(
        "HistoryReqSlot", back_populates="history_requisition")
    history_mat_return = relationship(
        "HistoryMaterialReturn", back_populates="history_requisition")

    __allow_unmapped__ = True


# for returning material
class HistoryReturnSlot(Base):
    __tablename__ = 'history_r_slots'

    slot_id = Column(Integer, primary_key=True,
                     nullable=False, autoincrement=True)
    req_slot_id = Column(Integer, ForeignKey(
        "history_req_slots.slot_id"), nullable=False)
    remarks = Column(String(255), nullable=True)
    ret_time = Column(TIMESTAMP(timezone=True),
                      nullable=False)

    ret_by = Column(Integer, ForeignKey("employees.id"), nullable=True)
    approved = Column(Boolean, nullable=False, default=False)

    history_mat_return = relationship(
        "HistoryMaterialReturn", back_populates="history_r_slots", cascade='all, delete-orphan')
    history_req_slots = relationship(
        "HistoryReqSlot", back_populates="history_r_slots")
    __allow_unmapped__ = True


class HistoryMaterialReturn(Base):
    __tablename__ = "history_mat_return"

    ret_id = Column(Integer, primary_key=True,
                    nullable=False, autoincrement=True)
    slot_id = Column(Integer, ForeignKey(
        "history_r_slots.slot_id", ondelete='CASCADE'), nullable=False)
    # for requisitions mapping
    req_id = Column(Integer, ForeignKey("history_requisition.req_id"))
    m_id = Column(Integer, ForeignKey("materials.id"))
    qty_ret = Column(Integer, nullable=False)

    materials = relationship("Material", back_populates="history_mat_return")
    history_r_slots = relationship(
        "HistoryReturnSlot", back_populates="history_mat_return")
    history_requisition = relationship(
        "HistoryRequisition", back_populates="history_mat_return")

    __allow_unmapped__ = True


class HistoryBatches(Base):
    __tablename__ = 'history_batches'

    batch_id = Column(Integer, primary_key=True,
                      nullable=False, autoincrement=True)
    remarks = Column(String(255), nullable=True)
    handover_by = Column(Integer, ForeignKey("employees.id"), nullable=False)
    is_recieved = Column(Boolean, nullable=False, default=False)
    recieved_by = Column(Integer, ForeignKey("employees.id"), nullable=True)
    recieved_time = Column(TIMESTAMP(timezone=True),
                           nullable=True)
    mfg = Column(TIMESTAMP(timezone=True), nullable=False,
                 server_default=text('now()'))

    history_prod_handover = relationship(
        "HistoryProd_Handover", back_populates="history_batches", cascade='all, delete-orphan')

    __allow_unmapped__ = True


class HistoryProd_Handover(Base):
    __tablename__ = "history_prod_handover"

    handover_id = Column(Integer, primary_key=True,
                         nullable=False, autoincrement=True)
    batch_id = Column(Integer, ForeignKey(
        "history_batches.batch_id", ondelete='CASCADE'), nullable=False)
    prod_id = Column(Integer, ForeignKey("products.id"))
    qty = Column(Integer, nullable=False)

    products = relationship("Products", back_populates="history_prod_handover")
    history_batches = relationship(
        "HistoryBatches", back_populates="history_prod_handover")

    __allow_unmapped__ = True


class HistoryPurchases(Base):
    __tablename__ = "history_purchases"

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

    history_orders = relationship(
        "HistoryOrders", back_populates="history_purchases", cascade='all, delete-orphan')

    __allow_unmapped__ = True


class HistoryOrders(Base):
    __tablename__ = "history_orders"

    ord_id = Column(Integer, primary_key=True,
                    nullable=False, autoincrement=True)
    m_id = Column(Integer, ForeignKey("materials.id"))
    ord_qty = Column(Integer, nullable=False)
    recieved_qty = Column(Integer, nullable=False, server_default="0")

    pur_id = Column(Integer, ForeignKey(
        "history_purchases.pur_id", ondelete='CASCADE'), nullable=True)

    materials = relationship("Material", back_populates="history_orders")
    history_purchases = relationship(
        "HistoryPurchases", back_populates="history_orders")

    __allow_unmapped__ = True


class HistoryDispatches(Base):
    __tablename__ = "history_dis_details"

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

    history_consignments = relationship(
        "HistoryConsignments", back_populates="history_dis_details", cascade='all, delete-orphan')
    drivers = relationship("Drivers", back_populates="history_dis_details")
    transports = relationship(
        "Transports", back_populates="history_dis_details")

    __allow_unmapped__ = True


class HistoryConsignments(Base):
    __tablename__ = "history_consignments"

    cg_id = Column(Integer, primary_key=True,
                   nullable=False, autoincrement=True)
    # p_name = Column(String(255), nullable=False)
    prod_id = Column(Integer, ForeignKey("products.id"))
    qty = Column(Integer, nullable=False)
    checked_qty = Column(Integer, nullable=False, server_default="0")

    dis_id = Column(Integer, ForeignKey(
        "history_dis_details.dis_id", ondelete='CASCADE'), nullable=True)

    products = relationship("Products", back_populates="history_consignments")
    history_dis_details = relationship(
        "HistoryDispatches", back_populates="history_consignments")

    __allow_unmapped__ = True
