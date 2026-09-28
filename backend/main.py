from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from fastapi import Body

app = FastAPI()

#跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

#sqlite数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./grayboard.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ----------------数据库表定义----------------

class DBCustomer(Base):
    __tablename__ = "customer"
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    contact = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    address = Column(String, nullable=False)
    payment_terms = Column(Integer, default=0)   # 账期（天）
    salesperson = Column(String, nullable=False)  # 所属业务员
    tax_no = Column(String, nullable=True)         # 税号/付款人信息（非必填）
    customer_level = Column(String, nullable=True) # 客户评级（非必填，S/A/B/C/D）


# 成品分类（独立四级，和卷筒仓 physical_category 分开）
class DBProductCategory(Base):
    __tablename__ = "product_category"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    parent_id = Column(Integer, nullable=True)
    warn_threshold = Column(Float, nullable=True)


# 成品品名（独立，和卷筒仓 product_name 分开）
class DBProductNameFinished(Base):
    __tablename__ = "product_name_finished"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)


class DBRawRoll(Base):
    __tablename__ = "raw_roll"
    id = Column(Integer, primary_key=True, index=True)
    raw_no = Column(String)
    product_name_id = Column(Integer)
    category_id = Column(Integer, nullable=True)
    width = Column(Float)
    gram = Column(Float)
    weight = Column(Float)
    stock_weight = Column(Float)
    ton_price = Column(Float, default=0)  # 吨价（元/吨）
    remark = Column(String)


# 辅料分类（一级）
class DBAuxCategory(Base):
    __tablename__ = "aux_category"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)


# 辅料物料
class DBAuxMaterial(Base):
    __tablename__ = "aux_material"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    category_id = Column(Integer, nullable=True)
    quantity = Column(Float, default=0)
    unit = Column(String(20), default="个")
    remark = Column(String, default="")


# 两级物理分类（卷筒仓用）
class DBPhysicalCategory(Base):
    __tablename__ = "physical_category"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="分类名称")
    parent_id = Column(Integer, nullable=True, comment="父分类id，null=一级分类")
    warn_threshold = Column(Float, nullable=True)


class DBProductName(Base):
    __tablename__ = "product_name"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)


# 成品库存
class DBProduct(Base):
    __tablename__ = "product"
    id = Column(Integer, primary_key=True, index=True)
    product_name_id = Column(Integer)
    category_id = Column(Integer, nullable=True)
    customer_id = Column(Integer, nullable=True)       # 关联客户档案
    work_order_no = Column(String, nullable=True)
    spec = Column(String, default="")
    actual_gram = Column(Float, default=0)
    nominal_gram = Column(Float, default=0)
    quantity = Column(Float, default=0)
    pending_out_qty = Column(Float, default=0)
    unit = Column(String(20), default="令")
    remark = Column(String, default="")


# 待出库记录
class DBPendingOut(Base):
    __tablename__ = "pending_out"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Float, nullable=False)
    reason = Column(String, default="")
    status = Column(String(20), default="pending")
    created_at = Column(String, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


# 销售订单主表
class DBSalesOrder(Base):
    __tablename__ = "sales_order"
    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(50), unique=True, nullable=False)  # 订单编号 XS-YYYYMMDD-序号
    customer_id = Column(Integer, nullable=True)                  # 关联客户档案
    customer_name = Column(String, nullable=False)                # 客户名称（冗余）
    customer_order_no = Column(String, nullable=True)             # 客户订单号
    receiver = Column(String, nullable=True)                       # 收货人
    receiver_phone = Column(String, nullable=True)                 # 收货人电话
    delivery_address = Column(String, nullable=True)               # 送货地址
    delivery_date = Column(String, nullable=False)                 # 送货日期 YYYY-MM-DD
    total_amount = Column(Float, default=0)                        # 合计金额
    status = Column(String(20), default="pending")                 # pending待发货 / shipped已发货 / completed已完成 / cancelled已取消
    maker = Column(String, nullable=True)                           # 制单人
    salesman = Column(String, nullable=True)                        # 业务员
    remark = Column(String, default="")                             # 备注
    created_at = Column(String, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


# 销售订单明细表
class DBSalesOrderItem(Base):
    __tablename__ = "sales_order_item"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, nullable=False, index=True)
    line_no = Column(Integer, default=1)                            # 行号
    product_id = Column(Integer, nullable=True)                    # 关联成品库存ID（直接锁定具体成品）
    product_name = Column(String, nullable=False)                   # 货品名称
    spec = Column(String, nullable=True)                             # 规格MM
    length = Column(Float, default=0)                                # 长(mm)
    width = Column(Float, default=0)                                 # 宽(mm)
    nominal_gram = Column(Float, default=0)                          # 虚克(g)
    actual_gram = Column(Float, default=0)                           # 实克(g)
    unit = Column(String(20), default="张")                         # 单位
    quantity = Column(Float, default=0)                              # 数量
    ton_price = Column(Float, default=0)                             # 吨价(元/吨)
    price = Column(Float, default=0)                                 # 单价(元/张)
    unit_price = Column(Float, default=0)                            # 单价(元/张) - 同price，前端用
    amount = Column(Float, default=0)                                # 金额
    cost = Column(Float, default=0)                                  # 成本(元/张)
    waste_rate = Column(Float, default=3)                            # 损耗率(%)
    lamination_fee = Column(Float, default=300)                      # 裱工费(元/吨)
    cost_layers = Column(Text, nullable=True)                         # 成本层详情(JSON)
    remark = Column(String, default="")                              # 备注


# 成本模板表（单独的库，保存常用的纸张组合和参数）
class DBCostTemplate(Base):
    __tablename__ = "cost_template"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)                        # 模板名称
    layers = Column(Text, nullable=False)                             # 成本层详情(JSON)
    waste_rate = Column(Float, default=3)                             # 损耗率(%)
    lamination_fee = Column(Float, default=300)                       # 裱工费(元/吨)
    created_at = Column(String, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    updated_at = Column(String, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


# 操作日志表
class DBOperationLog(Base):
    __tablename__ = "operation_log"
    id = Column(Integer, primary_key=True, index=True)
    module = Column(String(50))          # 模块：成品仓/卷筒仓/销售订单等
    action = Column(String(50))          # 操作：新增/修改/删除/出库/入库等
    target_type = Column(String(50))     # 操作对象类型
    target_id = Column(Integer)          # 操作对象ID
    detail = Column(Text)                # 操作详情
    created_at = Column(String, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


# 生产工单主表
class DBProduceOrder(Base):
    __tablename__ = "produce_order"
    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(50))
    po_no = Column(String(50))
    customer_id = Column(Integer)
    customer_name = Column(String(200))
    product_name = Column(String(200))
    quantity = Column(Float, default=0)
    spec_width = Column(Float, default=0)
    spec_length = Column(Float, default=0)
    total_gram = Column(Float, default=0)
    customer_order_no = Column(String(100))
    thickness = Column(String(50))
    humidity = Column(String(50))
    brand = Column(String(100))
    size_error = Column(String(50))
    diagonal_error = Column(String(50), default="2MM内")
    package_method = Column(String(100))
    loss_limit = Column(String(20), default="2%")
    maker = Column(String(50))
    checker = Column(String(50))
    schedule_date = Column(String(20))
    sales_order_id = Column(Integer, nullable=True)
    craft = Column(String(200), nullable=True)
    produce_date = Column(String(20))
    layers = Column(Integer, default=1)
    total_amount = Column(Float, default=0)
    status = Column(String(20), default="draft")
    remark = Column(Text)
    created_at = Column(String, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


# 生产工单明细表
class DBProduceOrderItem(Base):
    __tablename__ = "produce_order_item"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer)
    layer_no = Column(Integer)
    roll_id = Column(Integer)
    roll_name = Column(String(200))
    quantity = Column(Float, default=0)
    unit_price = Column(Float, default=0)
    amount = Column(Float, default=0)
    remark = Column(Text)


# 领料/退料记录表
class DBProduceMaterialLog(Base):
    __tablename__ = "produce_material_log"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer)
    item_id = Column(Integer)
    type = Column(String(20))  # pick领料/return退料
    material_type = Column(String(20))  # roll卷料/aux辅料
    material_id = Column(Integer)
    quantity = Column(Float)
    created_at = Column(String, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


# =================财务板块表（第一期）=================
# 资金账户（现金/银行/微信等）
class DBFinanceAccount(Base):
    __tablename__ = "finance_account"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)              # 账户名称
    account_type = Column(String(20), default="bank")       # cash现金/bank银行/other其他
    balance = Column(Float, default=0)                      # 当前余额
    remark = Column(String, default="")
    created_at = Column(String, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


# 资金流水（出入账日记账）
class DBFinanceTransaction(Base):
    __tablename__ = "finance_transaction"
    id = Column(Integer, primary_key=True, index=True)
    trans_date = Column(String(20), index=True)             # 日期
    direction = Column(String(10), index=True)             # income收入/expense支出
    category = Column(String(30), default="其他")           # 客户收款/供应商付款/费用报销/其他收入/其他支出
    counterparty = Column(String(200), default="")         # 往来单位
    account_id = Column(Integer, index=True)               # 资金账户
    amount = Column(Float, default=0)                      # 金额
    ref_type = Column(String(20), default="")              # 关联类型 receivable/payable/manual
    ref_id = Column(Integer, nullable=True)
    ref_no = Column(String(50), default="")               # 关联单据号
    operator = Column(String(50), default="")             # 经手人
    remark = Column(String, default="")
    created_at = Column(String, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


# 应收账款（客户欠我的）
class DBFinanceReceivable(Base):
    __tablename__ = "finance_receivable"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, nullable=True)
    customer_name = Column(String(200))
    sales_order_id = Column(Integer, nullable=True, index=True)
    order_no = Column(String(50))                          # 销售单号
    amount = Column(Float, default=0)                      # 应收金额
    received_amount = Column(Float, default=0)             # 已收金额
    balance = Column(Float, default=0)                     # 未收余额
    ship_date = Column(String(20), nullable=True)          # 送出日期
    due_date = Column(String(20), nullable=True)           # 应收日期（账期到期）
    status = Column(String(20), default="unpaid")          # unpaid未收/partial部分收/paid已收
    remark = Column(String, default="")
    created_at = Column(String, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


# 应付账款（我欠供应商的）
class DBFinancePayable(Base):
    __tablename__ = "finance_payable"
    id = Column(Integer, primary_key=True, index=True)
    supplier_name = Column(String(200))
    purchase_order_id = Column(Integer, nullable=True, index=True)
    order_no = Column(String(50))                          # 采购单号
    amount = Column(Float, default=0)                      # 应付金额（随到货累加）
    paid_amount = Column(Float, default=0)                 # 已付金额
    balance = Column(Float, default=0)                     # 未付余额
    arrive_date = Column(String(20), nullable=True)        # 最近到货日期
    due_date = Column(String(20), nullable=True)
    status = Column(String(20), default="unpaid")          # unpaid/partial/paid
    remark = Column(String, default="")
    created_at = Column(String, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


#建表
Base.metadata.create_all(bind=engine)

# ----------------自动补列（兼容旧数据库）----------------
def auto_add_columns():
    inspector = inspect(engine)
    # customer 表补列
    if 'customer' in inspector.get_table_names():
        existing_cols = [c['name'] for c in inspector.get_columns('customer')]
        with engine.connect() as conn:
            if 'payment_terms' not in existing_cols:
                conn.execute(text("ALTER TABLE customer ADD COLUMN payment_terms INTEGER DEFAULT 0"))
            if 'salesperson' not in existing_cols:
                conn.execute(text("ALTER TABLE customer ADD COLUMN salesperson VARCHAR"))
            if 'tax_no' not in existing_cols:
                conn.execute(text("ALTER TABLE customer ADD COLUMN tax_no VARCHAR"))
            if 'customer_level' not in existing_cols:
                conn.execute(text("ALTER TABLE customer ADD COLUMN customer_level VARCHAR"))
            conn.commit()
    # product 表补列
    if 'product' in inspector.get_table_names():
        existing_cols = [c['name'] for c in inspector.get_columns('product')]
        with engine.connect() as conn:
            if 'customer_id' not in existing_cols:
                conn.execute(text("ALTER TABLE product ADD COLUMN customer_id INTEGER"))
            conn.commit()
    # sales_order_item 表补列
    if 'sales_order_item' in inspector.get_table_names():
        existing_cols = [c['name'] for c in inspector.get_columns('sales_order_item')]
        with engine.connect() as conn:
            if 'length' not in existing_cols:
                conn.execute(text("ALTER TABLE sales_order_item ADD COLUMN length FLOAT DEFAULT 0"))
            if 'width' not in existing_cols:
                conn.execute(text("ALTER TABLE sales_order_item ADD COLUMN width FLOAT DEFAULT 0"))
            if 'nominal_gram' not in existing_cols:
                conn.execute(text("ALTER TABLE sales_order_item ADD COLUMN nominal_gram FLOAT DEFAULT 0"))
            if 'actual_gram' not in existing_cols:
                conn.execute(text("ALTER TABLE sales_order_item ADD COLUMN actual_gram FLOAT DEFAULT 0"))
            if 'ton_price' not in existing_cols:
                conn.execute(text("ALTER TABLE sales_order_item ADD COLUMN ton_price FLOAT DEFAULT 0"))
            if 'unit_price' not in existing_cols:
                conn.execute(text("ALTER TABLE sales_order_item ADD COLUMN unit_price FLOAT DEFAULT 0"))
            if 'cost' not in existing_cols:
                conn.execute(text("ALTER TABLE sales_order_item ADD COLUMN cost FLOAT DEFAULT 0"))
            if 'waste_rate' not in existing_cols:
                conn.execute(text("ALTER TABLE sales_order_item ADD COLUMN waste_rate FLOAT DEFAULT 3"))
            if 'lamination_fee' not in existing_cols:
                conn.execute(text("ALTER TABLE sales_order_item ADD COLUMN lamination_fee FLOAT DEFAULT 300"))
            if 'cost_layers' not in existing_cols:
                conn.execute(text("ALTER TABLE sales_order_item ADD COLUMN cost_layers TEXT"))
            conn.commit()

auto_add_columns()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------------pydantic模型----------------

#客户
class CustomerCreate(BaseModel):
    customer_name: str
    contact: str
    phone: str
    address: str
    payment_terms: int = 0
    salesperson: str
    tax_no: Optional[str] = None
    customer_level: Optional[str] = None

class CustomerUpdate(BaseModel):
    customer_name: Optional[str] = None
    contact: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    payment_terms: Optional[int] = None
    salesperson: Optional[str] = None
    tax_no: Optional[str] = None
    customer_level: Optional[str] = None

class CustomerOut(BaseModel):
    id:int
    customer_name:str
    contact:Optional[str]=None
    phone:Optional[str]=None
    address:Optional[str]=None
    payment_terms:Optional[int]=None
    salesperson:Optional[str]=None
    tax_no:Optional[str]=None
    customer_level:Optional[str]=None
    class Config:
        orm_mode=True


# 成品分类
class ProductCategoryCreate(BaseModel):
    name: str
    parent_id: Optional[int] = None
    warn_threshold: Optional[float] = None

class ProductCategoryUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None
    warn_threshold: Optional[float] = None

class ProductCategoryOut(BaseModel):
    id: int
    name: str
    parent_id: Optional[int] = None
    warn_threshold: Optional[float] = None
    model_config = ConfigDict(from_attributes=True)


# 成品品名
class ProductNameFinishedCreate(BaseModel):
    name: str
class ProductNameFinishedOut(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


# 辅料分类
class AuxCategoryCreate(BaseModel):
    name: str
class AuxCategoryOut(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


# 辅料物料
class AuxMaterialCreate(BaseModel):
    name: str
    category_id: Optional[int] = None
    quantity: float = 0
    unit: str = "个"
    remark: Optional[str] = None

class AuxMaterialOut(BaseModel):
    id: int
    name: str
    category_id: Optional[int] = None
    quantity: float
    unit: str
    remark: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class AuxMaterialUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    remark: Optional[str] = None

class AuxAdjust(BaseModel):
    adjust_quantity: float
    reason: Optional[str] = None


#物理分类（卷筒仓）
class PhysicalCategoryCreate(BaseModel):
    name: str
    parent_id: int | None = None
    warn_threshold: float | None = None

class PhysicalCategorySchema(BaseModel):
    id:int
    name:str
    parent_id: int | None
    warn_threshold: float | None = None
    class Config:
        orm_mode=True


#卷筒
class RawRollCreate(BaseModel):
    raw_no: str
    product_name_id: int
    category_id: Optional[int] = None
    width: float
    gram: float
    weight: float
    ton_price: float = 0
    remark: Optional[str] = None

class RawRollOut(BaseModel):
    id:int
    raw_no:str
    product_name_id:int
    category_id:Optional[int]=None
    width:float
    gram:float
    weight:float
    stock_weight:float
    ton_price:float=0
    remark:Optional[str]=None
    class Config:
        orm_mode=True


#品名（卷筒仓）
class ProductNameCreate(BaseModel):
    name:str
class ProductNameOut(BaseModel):
    id:int
    name:str
    class Config:orm_mode=True


# 成品
class ProductCreate(BaseModel):
    product_name_id: int
    category_id: Optional[int] = None
    customer_id: Optional[int] = None
    work_order_no: Optional[str] = None
    spec: Optional[str] = ""
    actual_gram: float = 0
    nominal_gram: float = 0
    quantity: float = 0
    unit: str = "令"
    remark: Optional[str] = None

class ProductOut(BaseModel):
    id: int
    product_name_id: int
    category_id: Optional[int] = None
    customer_id: Optional[int] = None
    work_order_no: Optional[str] = None
    spec: Optional[str] = None
    actual_gram: float
    nominal_gram: float
    quantity: float
    pending_out_qty: float
    unit: str
    remark: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class ProductUpdate(BaseModel):
    product_name_id: Optional[int] = None
    category_id: Optional[int] = None
    customer_id: Optional[int] = None
    work_order_no: Optional[str] = None
    spec: Optional[str] = None
    actual_gram: Optional[float] = None
    nominal_gram: Optional[float] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    remark: Optional[str] = None


# 入库
class StockIn(BaseModel):
    quantity: float
    reason: Optional[str] = None


# 移入待出库
class PendingOutCreate(BaseModel):
    quantity: float
    reason: Optional[str] = None

class PendingOutOut(BaseModel):
    id: int
    product_id: int
    quantity: float
    reason: Optional[str] = None
    status: str
    created_at: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


# 销售订单明细
class SalesOrderItemCreate(BaseModel):
    line_no: int = 1
    product_id: Optional[int] = None
    product_name: str
    spec: Optional[str] = None
    length: float = 0
    width: float = 0
    nominal_gram: float = 0
    actual_gram: float = 0
    unit: str = "张"
    quantity: float = 0
    ton_price: float = 0
    price: float = 0
    unit_price: float = 0
    amount: float = 0
    cost: float = 0
    waste_rate: float = 3
    lamination_fee: float = 300
    cost_layers: Optional[str] = None
    remark: Optional[str] = None

class SalesOrderItemOut(BaseModel):
    id: int
    order_id: int
    line_no: int
    product_id: Optional[int] = None
    product_name: str
    spec: Optional[str] = None
    length: float = 0
    width: float = 0
    nominal_gram: float = 0
    actual_gram: float = 0
    unit: str
    quantity: float
    ton_price: float = 0
    price: float = 0
    unit_price: float = 0
    amount: float
    cost: float = 0
    waste_rate: float = 3
    lamination_fee: float = 300
    cost_layers: Optional[str] = None
    remark: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


# 销售订单主表
class SalesOrderCreate(BaseModel):
    customer_id: Optional[int] = None
    customer_name: str
    customer_order_no: Optional[str] = None
    receiver: Optional[str] = None
    receiver_phone: Optional[str] = None
    delivery_address: Optional[str] = None
    delivery_date: str
    status: str = "pending"
    maker: Optional[str] = None
    salesman: Optional[str] = None
    remark: Optional[str] = None
    tax_included: bool = True
    items: List[SalesOrderItemCreate] = []

class SalesOrderUpdate(BaseModel):
    customer_id: Optional[int] = None
    customer_name: Optional[str] = None
    customer_order_no: Optional[str] = None
    receiver: Optional[str] = None
    receiver_phone: Optional[str] = None
    delivery_address: Optional[str] = None
    delivery_date: Optional[str] = None
    status: Optional[str] = None
    maker: Optional[str] = None
    salesman: Optional[str] = None
    remark: Optional[str] = None
    tax_included: Optional[bool] = None
    items: Optional[List[SalesOrderItemCreate]] = None

class SalesOrderOut(BaseModel):
    id: int
    order_no: str
    customer_id: Optional[int] = None
    customer_name: str
    customer_order_no: Optional[str] = None
    receiver: Optional[str] = None
    receiver_phone: Optional[str] = None
    delivery_address: Optional[str] = None
    delivery_date: str
    total_amount: float
    status: str
    maker: Optional[str] = None
    salesman: Optional[str] = None
    remark: Optional[str] = None
    created_at: Optional[str] = None
    items: List[SalesOrderItemOut] = []
    model_config = ConfigDict(from_attributes=True)


# ----------------操作日志接口----------------
@app.get("/api/operation_log")
def list_logs(limit: int = 200, db: Session = Depends(get_db)):
    logs = db.query(DBOperationLog).order_by(DBOperationLog.id.desc()).limit(limit).all()
    return logs

@app.post("/api/operation_log")
def add_log(module: str, action: str, target_type: str = "", target_id: int = 0, detail: str = "", db: Session = Depends(get_db)):
    log = DBOperationLog(
        module=module,
        action=action,
        target_type=target_type,
        target_id=target_id,
        detail=detail
    )
    db.add(log)
    db.commit()
    return {"ok": True}


# ----------------客户接口----------------

@app.get("/api/customer",response_model=List[CustomerOut])
def list_customer(db:Session=Depends(get_db)):
    return db.query(DBCustomer).order_by(DBCustomer.id.desc()).all()

@app.post("/api/customer",response_model=CustomerOut)
def create_customer(item:CustomerCreate, db:Session=Depends(get_db)):
    obj=DBCustomer(**item.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@app.put("/api/customer/{customer_id}", response_model=CustomerOut)
def update_customer(customer_id:int, item:CustomerUpdate, db:Session=Depends(get_db)):
    obj = db.query(DBCustomer).filter(DBCustomer.id==customer_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="客户不存在")
    for key, value in item.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj

@app.delete("/api/customer/{customer_id}")
def delete_customer(customer_id:int, db:Session=Depends(get_db)):
    obj = db.query(DBCustomer).filter(DBCustomer.id==customer_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="客户不存在")
    # 检查是否有成品关联此客户
    used = db.query(DBProduct).filter(DBProduct.customer_id==customer_id).count()
    if used > 0:
        raise HTTPException(status_code=400, detail=f"该客户下还有 {used} 条成品记录，请先移到其他客户再删除")
    db.delete(obj)
    db.commit()
    return {"ok": True}


# ----------------物理分类接口（卷筒仓）----------------

@app.get("/api/physical_category",response_model=List[PhysicalCategorySchema])
def get_pc(db:Session=Depends(get_db)):
    return db.query(DBPhysicalCategory).all()

@app.delete("/api/physical_category/{cat_id}")
def delete_pc(cat_id:int, db:Session=Depends(get_db)):
    cat = db.query(DBPhysicalCategory).filter(DBPhysicalCategory.id==cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="分类不存在")
    def get_descendant_ids(parent_id):
        ids = [parent_id]
        children = db.query(DBPhysicalCategory).filter(DBPhysicalCategory.parent_id==parent_id).all()
        for c in children:
            ids.extend(get_descendant_ids(c.id))
        return ids
    all_ids = get_descendant_ids(cat_id)
    db.query(DBPhysicalCategory).filter(DBPhysicalCategory.id.in_(all_ids)).delete(synchronize_session=False)
    db.commit()
    return {"ok": True, "deleted_count": len(all_ids)}

@app.post("/api/physical_category",response_model=PhysicalCategorySchema)
def create_pc(item:PhysicalCategoryCreate,db:Session=Depends(get_db)):
    db_item = DBPhysicalCategory(name=item.name, parent_id=item.parent_id, warn_threshold=item.warn_threshold)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.put("/api/physical_category/{cat_id}", response_model=PhysicalCategorySchema)
def update_pc(cat_id:int, item:PhysicalCategoryCreate, db:Session=Depends(get_db)):
    cat = db.query(DBPhysicalCategory).filter(DBPhysicalCategory.id==cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="分类不存在")
    cat.name = item.name
    cat.warn_threshold = item.warn_threshold
    db.commit()
    db.refresh(cat)
    return cat


# ----------------品名接口（卷筒仓）----------------

@app.get("/api/product_name",response_model=List[ProductNameOut])
def list_pn(db:Session=Depends(get_db)):
    return db.query(DBProductName).all()

@app.post("/api/product_name",response_model=ProductNameOut)
def create_pn(item:ProductNameCreate, db:Session=Depends(get_db)):
    obj=DBProductName(name=item.name)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


# ----------------卷筒原料接口----------------

@app.get("/api/rawroll",response_model=List[RawRollOut])
def list_rawroll(db:Session=Depends(get_db)):
    return db.query(DBRawRoll).all()

@app.post("/api/rawroll",response_model=RawRollOut)
def create_rawroll(item:RawRollCreate, db:Session=Depends(get_db)):
    data = item.model_dump()
    obj = DBRawRoll(
        raw_no=data["raw_no"],
        product_name_id=data["product_name_id"],
        category_id=data["category_id"],
        width=data["width"],
        gram=data["gram"],
        weight=data["weight"],
        stock_weight=data["weight"],
        ton_price=data.get("ton_price", 0),
        remark=data["remark"]
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@app.post("/api/rawroll/{roll_id}/reduce_stock", response_model=RawRollOut)
def reduce_rawroll_stock(roll_id:int, reduce_weight:float=Body(...,embed=True), db:Session=Depends(get_db)):
    roll = db.query(DBRawRoll).filter(DBRawRoll.id==roll_id).first()
    if not roll:
        raise HTTPException(status_code=404, detail="卷筒不存在")
    if reduce_weight <= 0:
        raise HTTPException(status_code=400, detail="扣减重量必须大于0")
    if roll.stock_weight < reduce_weight:
        raise HTTPException(status_code=400, detail=f"库存不足，当前剩余:{roll.stock_weight:.3f}吨")
    roll.stock_weight = roll.stock_weight - reduce_weight
    db.commit()
    db.refresh(roll)
    return roll

@app.delete("/api/rawroll/{roll_id}")
def delete_rawroll(roll_id:int, db:Session=Depends(get_db)):
    roll = db.query(DBRawRoll).filter(DBRawRoll.id==roll_id).first()
    if not roll:
        raise HTTPException(status_code=404, detail="卷筒不存在")
    db.delete(roll)
    db.commit()
    return {"ok": True}


# ----------------辅料分类接口----------------

@app.get("/api/aux_category", response_model=List[AuxCategoryOut])
def list_aux_category(db: Session = Depends(get_db)):
    return db.query(DBAuxCategory).all()

@app.post("/api/aux_category", response_model=AuxCategoryOut)
def create_aux_category(item: AuxCategoryCreate, db: Session = Depends(get_db)):
    obj = DBAuxCategory(name=item.name)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@app.delete("/api/aux_category/{cat_id}")
def delete_aux_category(cat_id: int, db: Session = Depends(get_db)):
    cat = db.query(DBAuxCategory).filter(DBAuxCategory.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="分类不存在")
    db.delete(cat)
    db.commit()
    return {"ok": True}


# ----------------成品分类接口（独立）----------------

@app.get("/api/product_category", response_model=List[ProductCategoryOut])
def list_product_category(db: Session = Depends(get_db)):
    return db.query(DBProductCategory).all()

@app.post("/api/product_category", response_model=ProductCategoryOut)
def create_product_category(item: ProductCategoryCreate, db: Session = Depends(get_db)):
    obj = DBProductCategory(**item.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@app.put("/api/product_category/{cat_id}", response_model=ProductCategoryOut)
def update_product_category(cat_id: int, item: ProductCategoryUpdate, db: Session = Depends(get_db)):
    obj = db.query(DBProductCategory).filter(DBProductCategory.id == cat_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="分类不存在")
    for key, value in item.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj

@app.delete("/api/product_category/{cat_id}")
def delete_product_category(cat_id: int, db: Session = Depends(get_db)):
    cat = db.query(DBProductCategory).filter(DBProductCategory.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="分类不存在")
    def get_descendant_ids(pid):
        ids = [pid]
        children = db.query(DBProductCategory).filter(DBProductCategory.parent_id == pid).all()
        for c in children:
            ids.extend(get_descendant_ids(c.id))
        return ids
    all_ids = get_descendant_ids(cat_id)
    db.query(DBProductCategory).filter(DBProductCategory.id.in_(all_ids)).delete(synchronize_session=False)
    db.commit()
    return {"ok": True, "deleted_count": len(all_ids)}


# ----------------成品品名接口（独立）----------------

@app.get("/api/product_name_finished", response_model=List[ProductNameFinishedOut])
def list_pn_finished(db: Session = Depends(get_db)):
    return db.query(DBProductNameFinished).all()

@app.post("/api/product_name_finished", response_model=ProductNameFinishedOut)
def create_pn_finished(item: ProductNameFinishedCreate, db: Session = Depends(get_db)):
    obj = DBProductNameFinished(name=item.name)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@app.delete("/api/product_name_finished/{pn_id}")
def delete_pn_finished(pn_id: int, db: Session = Depends(get_db)):
    obj = db.query(DBProductNameFinished).filter(DBProductNameFinished.id == pn_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="品名不存在")
    db.delete(obj)
    db.commit()
    return {"ok": True}


# ----------------辅料物料接口----------------

@app.get("/api/aux_material", response_model=List[AuxMaterialOut])
def list_aux_material(db: Session = Depends(get_db)):
    return db.query(DBAuxMaterial).all()

@app.post("/api/aux_material", response_model=AuxMaterialOut)
def create_aux_material(item: AuxMaterialCreate, db: Session = Depends(get_db)):
    obj = DBAuxMaterial(**item.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@app.put("/api/aux_material/{item_id}", response_model=AuxMaterialOut)
def update_aux_material(item_id: int, item: AuxMaterialUpdate, db: Session = Depends(get_db)):
    obj = db.query(DBAuxMaterial).filter(DBAuxMaterial.id == item_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="辅料不存在")
    for key, value in item.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj

@app.delete("/api/aux_material/{item_id}")
def delete_aux_material(item_id: int, db: Session = Depends(get_db)):
    obj = db.query(DBAuxMaterial).filter(DBAuxMaterial.id == item_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="辅料不存在")
    db.delete(obj)
    db.commit()
    return {"ok": True}

# 调整库存（正数入库，负数出库）
@app.post("/api/aux_material/{item_id}/adjust", response_model=AuxMaterialOut)
def adjust_aux_material(item_id: int, data: AuxAdjust, db: Session = Depends(get_db)):
    obj = db.query(DBAuxMaterial).filter(DBAuxMaterial.id == item_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="辅料不存在")
    new_qty = obj.quantity + data.adjust_quantity
    if new_qty < 0:
        raise HTTPException(status_code=400, detail=f"库存不足，当前库存：{obj.quantity} {obj.unit}")
    obj.quantity = new_qty
    db.commit()
    db.refresh(obj)
    return obj


# ----------------成品库存接口----------------

@app.get("/api/product", response_model=List[ProductOut])
def list_product(db: Session = Depends(get_db)):
    return db.query(DBProduct).all()

@app.post("/api/product", response_model=ProductOut)
def create_product(item: ProductCreate, db: Session = Depends(get_db)):
    obj = DBProduct(**item.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    # 记录日志
    log = DBOperationLog(module="成品仓", action="新增", target_type="成品", target_id=obj.id, detail=f"新增成品：{obj.spec}，数量{obj.quantity}")
    db.add(log)
    db.commit()
    return obj

@app.put("/api/product/{product_id}", response_model=ProductOut)
def update_product(product_id: int, item: ProductUpdate, db: Session = Depends(get_db)):
    obj = db.query(DBProduct).filter(DBProduct.id == product_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="成品不存在")
    for key, value in item.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
    # 记录日志
    log = DBOperationLog(module="成品仓", action="修改", target_type="成品", target_id=obj.id, detail=f"修改成品：{obj.spec}，修改了{list(item.model_dump(exclude_unset=True).keys())}")
    db.add(log)
    db.commit()
    db.refresh(obj)
    return obj

@app.delete("/api/product/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    obj = db.query(DBProduct).filter(DBProduct.id == product_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="成品不存在")
    if obj.pending_out_qty > 0:
        raise HTTPException(status_code=400, detail="该成品有待出库记录，请先处理后再删除")
    db.delete(obj)
    # 记录日志
    log = DBOperationLog(module="成品仓", action="删除", target_type="成品", target_id=product_id, detail=f"删除成品：{obj.spec}，原库存{obj.quantity}")
    db.add(log)
    db.commit()
    return {"ok": True}

# 入库
@app.post("/api/product/{product_id}/stock_in", response_model=ProductOut)
def stock_in(product_id: int, data: StockIn, db: Session = Depends(get_db)):
    obj = db.query(DBProduct).filter(DBProduct.id == product_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="成品不存在")
    if data.quantity <= 0:
        raise HTTPException(status_code=400, detail="入库数量必须大于0")
    obj.quantity += data.quantity
    # 记录日志
    log = DBOperationLog(module="成品仓", action="入库", target_type="成品", target_id=obj.id, detail=f"入库：{obj.spec}，入库{data.quantity}，现库存{obj.quantity}")
    db.add(log)
    db.commit()
    db.refresh(obj)
    return obj

# 移入待出库（锁定库存，总库存不变，待出库数量增加）
@app.post("/api/product/{product_id}/pending_out", response_model=PendingOutOut)
def create_pending_out(product_id: int, data: PendingOutCreate, db: Session = Depends(get_db)):
    obj = db.query(DBProduct).filter(DBProduct.id == product_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="成品不存在")
    if data.quantity <= 0:
        raise HTTPException(status_code=400, detail="出库数量必须大于0")
    # 可用库存 = 总库存 - 待出库数量
    available = obj.quantity - obj.pending_out_qty
    if available < data.quantity:
        raise HTTPException(status_code=400, detail=f"可用库存不足，当前可用：{available:.2f} {obj.unit}")
    # 总库存不变，待出库数量增加（锁定库存）
    obj.pending_out_qty += data.quantity
    record = DBPendingOut(product_id=product_id, quantity=data.quantity, reason=data.reason or "", status="pending")
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


# ----------------待出库单接口----------------

@app.get("/api/pending_out", response_model=List[PendingOutOut])
def list_pending_out(status: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(DBPendingOut)
    if status:
        q = q.filter(DBPendingOut.status == status)
    return q.order_by(DBPendingOut.id.desc()).all()

# 取消待出库（加回可用库存）
@app.post("/api/pending_out/{record_id}/cancel", response_model=PendingOutOut)
def cancel_pending_out(record_id: int, db: Session = Depends(get_db)):
    record = db.query(DBPendingOut).filter(DBPendingOut.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    if record.status != "pending":
        raise HTTPException(status_code=400, detail="该记录已处理，无法取消")
    product = db.query(DBProduct).filter(DBProduct.id == record.product_id).first()
    if product:
        product.quantity += record.quantity
        product.pending_out_qty -= record.quantity
    record.status = "cancelled"
    
    # 如果是销售订单产生的待出库，把订单打回草稿
    if record.reason and "销售订单" in record.reason:
        # 从 reason 里提取订单号
        import re
        match = re.search(r'销售订单\s+(\S+)', record.reason)
        if match:
            order_no = match.group(1)
            order = db.query(DBSalesOrder).filter(DBSalesOrder.order_no == order_no).first()
            if order and order.status == "pending":
                order.status = "draft"
    
    db.commit()
    db.refresh(record)
    return record

# 确认出库（真正扣减总库存，待出库数量减少）
@app.post("/api/pending_out/{record_id}/confirm", response_model=PendingOutOut)
def confirm_pending_out(record_id: int, db: Session = Depends(get_db)):
    record = db.query(DBPendingOut).filter(DBPendingOut.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    if record.status != "pending":
        raise HTTPException(status_code=400, detail="该记录已处理")
    product = db.query(DBProduct).filter(DBProduct.id == record.product_id).first()
    if product:
        # 总库存减少，待出库数量减少
        product.quantity -= record.quantity
        product.pending_out_qty -= record.quantity
    record.status = "confirmed"
    db.commit()
    db.refresh(record)
    return record


# ----------------销售订单接口----------------

def generate_order_no(db):
    """生成订单编号：XS-YYYYMMDD-序号"""
    today = datetime.now().strftime("%Y%m%d")
    prefix = f"XS-{today}-"
    # 查今天已有多少个订单
    count = db.query(DBSalesOrder).filter(DBSalesOrder.order_no.like(f"{prefix}%")).count()
    return f"{prefix}{count + 1:03d}"


@app.get("/api/sales_order", response_model=List[SalesOrderOut])
def list_sales_order(
    customer_name: Optional[str] = None,
    customer_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    search_field: Optional[str] = None,
    search_value: Optional[str] = None,
    db: Session = Depends(get_db)
):
    q = db.query(DBSalesOrder)
    if customer_id:
        q = q.filter(DBSalesOrder.customer_id == customer_id)
    if customer_name:
        q = q.filter(DBSalesOrder.customer_name.like(f"%{customer_name}%"))
    if status:
        q = q.filter(DBSalesOrder.status == status)
    if start_date:
        q = q.filter(DBSalesOrder.delivery_date >= start_date)
    if end_date:
        q = q.filter(DBSalesOrder.delivery_date <= end_date)
    # 通用字段筛选
    if search_field and search_value:
        if search_field == "status":
            # 状态特殊处理：支持中文和英文
            status_map = {
                "草稿": "draft", "draft": "draft",
                "待出库": "pending", "待发货": "pending", "pending": "pending",
                "已出库": "shipped", "已发货": "shipped", "shipped": "shipped",
                "已完成": "completed", "completed": "completed",
                "已取消": "cancelled", "取消": "cancelled", "cancelled": "cancelled",
            }
            status_val = status_map.get(search_value, search_value)
            q = q.filter(DBSalesOrder.status == status_val)
        else:
            field_map = {
                "order_no": DBSalesOrder.order_no,
                "customer_name": DBSalesOrder.customer_name,
                "salesman": DBSalesOrder.salesman,
                "receiver": DBSalesOrder.receiver,
                "delivery_date": DBSalesOrder.delivery_date,
            }
            if search_field in field_map:
                q = q.filter(field_map[search_field].like(f"%{search_value}%"))
    orders = q.order_by(DBSalesOrder.id.desc()).all()
    # 填充明细
    for order in orders:
        order.items = db.query(DBSalesOrderItem).filter(DBSalesOrderItem.order_id == order.id).order_by(DBSalesOrderItem.line_no).all()
    return orders


@app.post("/api/sales_order", response_model=SalesOrderOut)
def create_sales_order(item: SalesOrderCreate, db: Session = Depends(get_db)):
    # 自动生成编号
    order_no = generate_order_no(db)
    # 计算合计金额
    total_amount = sum((i.quantity or 0) * (i.unit_price or i.price or 0) for i in item.items)
    # 创建主表
    order = DBSalesOrder(
        order_no=order_no,
        customer_id=item.customer_id,
        customer_name=item.customer_name,
        customer_order_no=item.customer_order_no,
        receiver=item.receiver,
        receiver_phone=item.receiver_phone,
        delivery_address=item.delivery_address,
        delivery_date=item.delivery_date,
        total_amount=total_amount,
        status=item.status,
        maker=item.maker,
        salesman=item.salesman,
        remark=item.remark or ""
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    # 创建明细
    for idx, it in enumerate(item.items):
        unit_price = it.unit_price or it.price or 0
        amount = (it.quantity or 0) * unit_price
        detail = DBSalesOrderItem(
            order_id=order.id,
            line_no=it.line_no or idx + 1,
            product_id=it.product_id,
            product_name=it.product_name,
            spec=it.spec,
            length=it.length or 0,
            width=it.width or 0,
            nominal_gram=it.nominal_gram or 0,
            actual_gram=it.actual_gram or 0,
            unit=it.unit or "张",
            quantity=it.quantity or 0,
            ton_price=it.ton_price or 0,
            price=unit_price,
            unit_price=unit_price,
            amount=amount,
            cost=it.cost or 0,
            waste_rate=it.waste_rate if it.waste_rate is not None else 3,
            lamination_fee=it.lamination_fee if it.lamination_fee is not None else 300,
            cost_layers=it.cost_layers,
            remark=it.remark or ""
        )
        db.add(detail)
    db.commit()
    
    # 记录日志
    log = DBOperationLog(module="销售订单", action="新增", target_type="销售订单", target_id=order.id, detail=f"新增订单：{order.order_no}，客户{order.customer_name}，金额{order.total_amount}，状态{order.status}")
    db.add(log)
    db.commit()
    
    # 如果状态是待出库，自动在成品仓锁定库存（创建待出库记录）
    if item.status == "pending":
        items = db.query(DBSalesOrderItem).filter(DBSalesOrderItem.order_id == order.id).all()
        for item_detail in items:
            # 优先用 product_id 锁定具体成品
            p = None
            if item_detail.product_id:
                p = db.query(DBProduct).filter(DBProduct.id == item_detail.product_id).first()
            
            # 如果没有 product_id，就用品名+规格匹配
            if not p and item_detail.product_name:
                # 先找成品品名
                pn = db.query(DBProductNameFinished).filter(DBProductNameFinished.name == item_detail.product_name).first()
                if pn:
                    p = db.query(DBProduct).filter(
                        DBProduct.product_name_id == pn.id,
                        DBProduct.spec == item_detail.spec
                    ).first()
            
            if not p:
                continue
            
            products = [p]
            
            # 按顺序锁定库存：总库存不变，待出库数量增加
            remain = item_detail.quantity
            for p in products:
                if remain <= 0:
                    break
                available = p.quantity - p.pending_out_qty
                if available <= 0:
                    continue
                if available >= remain:
                    # 锁定这部分：总库存不变，待出库数量增加
                    p.pending_out_qty += remain
                    # 创建待出库记录
                    record = DBPendingOut(
                        product_id=p.id,
                        quantity=remain,
                        reason=f"销售订单 {order_no}",
                        status="pending"
                    )
                    db.add(record)
                    remain = 0
                else:
                    p.pending_out_qty += available
                    record = DBPendingOut(
                        product_id=p.id,
                        quantity=available,
                        reason=f"销售订单 {order_no}",
                        status="pending"
                    )
                    db.add(record)
                    remain -= available
        db.commit()
    
    # 返回含明细
    order.items = db.query(DBSalesOrderItem).filter(DBSalesOrderItem.order_id == order.id).order_by(DBSalesOrderItem.line_no).all()
    return order


@app.get("/api/sales_order/{order_id}", response_model=SalesOrderOut)
def get_sales_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(DBSalesOrder).filter(DBSalesOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    order.items = db.query(DBSalesOrderItem).filter(DBSalesOrderItem.order_id == order.id).order_by(DBSalesOrderItem.line_no).all()
    return order


@app.put("/api/sales_order/{order_id}", response_model=SalesOrderOut)
def update_sales_order(order_id: int, item: SalesOrderUpdate, db: Session = Depends(get_db)):
    order = db.query(DBSalesOrder).filter(DBSalesOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    # 更新主表字段
    update_data = item.model_dump(exclude_unset=True, exclude={"items"})
    for key, value in update_data.items():
        setattr(order, key, value)
    # 如果传了明细，先删后增
    if item.items is not None:
        db.query(DBSalesOrderItem).filter(DBSalesOrderItem.order_id == order_id).delete()
        total_amount = 0
        for idx, it in enumerate(item.items):
            unit_price = it.unit_price or it.price or 0
            amount = (it.quantity or 0) * unit_price
            total_amount += amount
            detail = DBSalesOrderItem(
                order_id=order.id,
                line_no=it.line_no or idx + 1,
                product_id=it.product_id,
                product_name=it.product_name,
                spec=it.spec,
                length=it.length or 0,
                width=it.width or 0,
                nominal_gram=it.nominal_gram or 0,
                actual_gram=it.actual_gram or 0,
                unit=it.unit or "张",
                quantity=it.quantity or 0,
                ton_price=it.ton_price or 0,
                price=unit_price,
                unit_price=unit_price,
                amount=amount,
                cost=it.cost or 0,
                waste_rate=it.waste_rate if it.waste_rate is not None else 3,
                lamination_fee=it.lamination_fee if it.lamination_fee is not None else 300,
                cost_layers=it.cost_layers,
                remark=it.remark or ""
            )
            db.add(detail)
        order.total_amount = total_amount
    
    # 如果状态是草稿，自动取消所有待出库记录（库存加回）
    if order.status == "draft":
        all_pending = db.query(DBPendingOut).filter(
            DBPendingOut.reason.like(f"%{order.order_no}%"),
            DBPendingOut.status == "pending"
        ).all()
        for rec in all_pending:
            product = db.query(DBProduct).filter(DBProduct.id == rec.product_id).first()
            if product:
                product.pending_out_qty -= rec.quantity
            rec.status = "cancelled"
    
    # 如果状态是待出库，自动锁定库存
    if order.status == "pending":
        # 先把这个订单之前的待出库记录取消，避免重复锁定
        old_pending = db.query(DBPendingOut).filter(
            DBPendingOut.reason.like(f"%{order.order_no}%"),
            DBPendingOut.status == "pending"
        ).all()
        for rec in old_pending:
            product = db.query(DBProduct).filter(DBProduct.id == rec.product_id).first()
            if product:
                product.pending_out_qty -= rec.quantity
            rec.status = "cancelled"
        
        # 重新根据明细锁定库存
        items = db.query(DBSalesOrderItem).filter(DBSalesOrderItem.order_id == order.id).all()
        for item_detail in items:
            # 优先用 product_id 锁定具体成品
            p = None
            if item_detail.product_id:
                p = db.query(DBProduct).filter(DBProduct.id == item_detail.product_id).first()
            
            # 如果没有 product_id，就用品名+规格匹配
            if not p and item_detail.product_name:
                # 先找成品品名
                pn = db.query(DBProductNameFinished).filter(DBProductNameFinished.name == item_detail.product_name).first()
                if pn:
                    p = db.query(DBProduct).filter(
                        DBProduct.product_name_id == pn.id,
                        DBProduct.spec == item_detail.spec
                    ).first()
            
            if not p:
                continue
            
            products = [p]
            
            # 直接按订单数量创建待出库记录，允许负库存（红色预警）
            p = products[0] if products else None
            if p:
                p.pending_out_qty += item_detail.quantity
                record = DBPendingOut(
                    product_id=p.id,
                    quantity=item_detail.quantity,
                    reason=f"销售订单 {order.order_no}",
                    status="pending"
                )
                db.add(record)
    
    db.commit()
    
    # 记录日志
    log = DBOperationLog(module="销售订单", action="修改", target_type="销售订单", target_id=order.id, detail=f"修改订单：{order.order_no}，客户{order.customer_name}，金额{order.total_amount}，状态{order.status}")
    db.add(log)
    db.commit()
    
    db.refresh(order)
    order.items = db.query(DBSalesOrderItem).filter(DBSalesOrderItem.order_id == order.id).order_by(DBSalesOrderItem.line_no).all()
    return order



# 销售订单出库（完成待出库记录，扣减总库存，状态改为已送出）
@app.post("/api/sales_order/{order_id}/ship", response_model=SalesOrderOut)
def ship_sales_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(DBSalesOrder).filter(DBSalesOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status != "pending":
        raise HTTPException(status_code=400, detail="只有待出库状态的订单才能出库")
    
    # 找到这个订单对应的所有待出库记录（reason里包含订单号）
    pending_records = db.query(DBPendingOut).filter(
        DBPendingOut.reason.like(f"%{order.order_no}%"),
        DBPendingOut.status == "pending"
    ).all()
    
    # 完成这些待出库记录
    for record in pending_records:
        product = db.query(DBProduct).filter(DBProduct.id == record.product_id).first()
        if product:
            # 总库存减少，待出库数量减少
            product.quantity -= record.quantity
            product.pending_out_qty -= record.quantity
        record.status = "confirmed"
    
    # 修改订单状态为已送出
    order.status = "shipped"

    # ===财务联动：生成应收账款（一张销售单一笔，防重复）===
    from datetime import timedelta as _td
    exist_rec = db.query(DBFinanceReceivable).filter(DBFinanceReceivable.sales_order_id == order.id).first()
    if not exist_rec:
        terms = 0
        if order.customer_id:
            _cust = db.query(DBCustomer).filter(DBCustomer.id == order.customer_id).first()
            if _cust:
                terms = int(_cust.payment_terms or 0)
        _due = None
        try:
            _base = datetime.strptime(order.delivery_date, "%Y-%m-%d")
            _due = (_base + _td(days=terms)).strftime("%Y-%m-%d")
        except Exception:
            _due = None
        _rec = DBFinanceReceivable(
            customer_id=order.customer_id,
            customer_name=order.customer_name,
            sales_order_id=order.id,
            order_no=order.order_no,
            amount=order.total_amount or 0,
            received_amount=0,
            balance=order.total_amount or 0,
            ship_date=datetime.now().strftime("%Y-%m-%d"),
            due_date=_due,
            status="unpaid"
        )
        db.add(_rec)

    db.commit()
    db.refresh(order)
    order.items = db.query(DBSalesOrderItem).filter(DBSalesOrderItem.order_id == order_id).order_by(DBSalesOrderItem.line_no).all()
    return order


@app.delete("/api/sales_order/{order_id}")
def delete_sales_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(DBSalesOrder).filter(DBSalesOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    # 先取消所有对应的待出库记录，把库存加回
    all_pending = db.query(DBPendingOut).filter(
        DBPendingOut.reason.like(f"%{order.order_no}%"),
        DBPendingOut.status == "pending"
    ).all()
    for rec in all_pending:
        product = db.query(DBProduct).filter(DBProduct.id == rec.product_id).first()
        if product:
            product.pending_out_qty -= rec.quantity
        rec.status = "cancelled"
    
    # 删除明细
    db.query(DBSalesOrderItem).filter(DBSalesOrderItem.order_id == order_id).delete()
    # 删除主表
    db.delete(order)
    db.commit()
    return {"ok": True}


# ----------------启动（必须在文件最后）----------------


# ----------------采购单数据库表----------------
class DBPurchaseOrder(Base):
    __tablename__ = "purchase_order"
    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(50))
    supplier = Column(String(200))
    delivery_address = Column(String(200))
    order_date = Column(String(20))
    remark = Column(Text)
    maker = Column(String(50))
    checker = Column(String(50))
    status = Column(String(20), default="draft")
    total_amount = Column(Float, default=0)
    created_at = Column(String(30))


class DBPurchaseOrderItem(Base):
    __tablename__ = "purchase_order_item"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer)
    category_id = Column(Integer)
    gram = Column(Float)
    width = Column(Float)
    unit = Column(String(20), default="吨")
    quantity = Column(Float, default=0)
    unit_price = Column(Float, default=0)
    amount = Column(Float, default=0)
    delivery_date = Column(String(20))
    remark = Column(String(200))
    arrived_quantity = Column(Float, default=0)
    status = Column(String(20), default="pending")


# ----------------采购单Pydantic模型----------------
class PurchaseOrderItemCreate(BaseModel):
    category_id: Optional[int] = None
    gram: Optional[float] = 0
    width: Optional[float] = 0
    unit: str = "吨"
    quantity: float = 0
    unit_price: float = 0
    amount: float = 0
    delivery_date: Optional[str] = None
    remark: Optional[str] = None


class PurchaseOrderItemOut(BaseModel):
    id: int
    order_id: int
    category_id: Optional[int] = None
    gram: Optional[float] = 0
    width: Optional[float] = 0
    unit: str = "吨"
    quantity: float
    unit_price: float
    amount: float
    delivery_date: Optional[str] = None
    remark: Optional[str] = None
    arrived_quantity: float
    status: str
    model_config = ConfigDict(from_attributes=True)


class PurchaseOrderCreate(BaseModel):
    order_no: Optional[str] = None
    supplier: Optional[str] = None
    delivery_address: Optional[str] = None
    order_date: Optional[str] = None
    remark: Optional[str] = None
    maker: Optional[str] = None
    checker: Optional[str] = None
    total_amount: Optional[float] = 0
    items: List[PurchaseOrderItemCreate] = []


class PurchaseOrderOut(BaseModel):
    id: int
    order_no: Optional[str] = None
    supplier: Optional[str] = None
    delivery_address: Optional[str] = None
    order_date: Optional[str] = None
    remark: Optional[str] = None
    maker: Optional[str] = None
    checker: Optional[str] = None
    status: str
    total_amount: float
    created_at: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


# 到货确认明细
class PurchaseArriveRoll(BaseModel):
    roll_no: str          # 卷筒编号（手动输入）
    weight: float         # 本支重量（吨，手动输入）
    remark: Optional[str] = None

class PurchaseArriveItem(BaseModel):
    item_id: int
    arrive_quantity: float
    roll_count: int = 1  # 到货支数，默认1支
    rolls: Optional[List[PurchaseArriveRoll]] = None  # 手动录入的每支明细，为空则平均分配


class PurchaseArriveRequest(BaseModel):
    items: List[PurchaseArriveItem]


# ----------------采购单接口----------------
@app.get("/api/purchase_order", response_model=List[PurchaseOrderOut])
def list_purchase_order(db: Session = Depends(get_db)):
    return db.query(DBPurchaseOrder).order_by(DBPurchaseOrder.id.desc()).all()


@app.get("/api/purchase_order/{order_id}")
def get_purchase_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(DBPurchaseOrder).filter(DBPurchaseOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="采购单不存在")
    items = db.query(DBPurchaseOrderItem).filter(DBPurchaseOrderItem.order_id == order_id).all()
    return {**order.__dict__, "items": [i.__dict__ for i in items]}


@app.post("/api/purchase_order", response_model=PurchaseOrderOut)
def create_purchase_order(item: PurchaseOrderCreate, db: Session = Depends(get_db)):
    # 自动生成采购单号
    if not item.order_no:
        prefix = "PO" + datetime.now().strftime("%Y%m%d")
        count = db.query(DBPurchaseOrder).filter(DBPurchaseOrder.order_no.like(f"{prefix}%")).count()
        order_no = f"{prefix}{count + 1:03d}"
    else:
        order_no = item.order_no

    order = DBPurchaseOrder(
        order_no=order_no,
        supplier=item.supplier,
        delivery_address=item.delivery_address,
        order_date=item.order_date or datetime.now().strftime("%Y-%m-%d"),
        remark=item.remark,
        maker=item.maker,
        checker=item.checker,
        status="pending",
        total_amount=item.total_amount or 0,
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    db.add(order)
    db.flush()

    # 保存明细
    for it in item.items:
        db_item = DBPurchaseOrderItem(
            order_id=order.id,
            category_id=it.category_id,
            gram=it.gram,
            width=it.width,
            unit=it.unit,
            quantity=it.quantity,
            unit_price=it.unit_price,
            amount=it.amount,
            delivery_date=it.delivery_date,
            remark=it.remark,
            arrived_quantity=0,
            status="pending"
        )
        db.add(db_item)

    # 操作日志
    log = DBOperationLog(module="卷料仓", action="新增采购单", target_type="采购单", target_id=order.id, detail=f"新增采购单：{order.order_no}，供应商{order.supplier}，金额{order.total_amount}")
    db.add(log)

    db.commit()
    db.refresh(order)
    return order


@app.put("/api/purchase_order/{order_id}", response_model=PurchaseOrderOut)
def update_purchase_order(order_id: int, item: PurchaseOrderCreate, db: Session = Depends(get_db)):
    order = db.query(DBPurchaseOrder).filter(DBPurchaseOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="采购单不存在")

    order.supplier = item.supplier
    order.delivery_address = item.delivery_address
    order.order_date = item.order_date
    order.remark = item.remark
    order.maker = item.maker
    order.checker = item.checker
    order.total_amount = item.total_amount or 0

    # 删除旧明细，重新保存
    db.query(DBPurchaseOrderItem).filter(DBPurchaseOrderItem.order_id == order_id).delete()
    for it in item.items:
        db_item = DBPurchaseOrderItem(
            order_id=order.id,
            category_id=it.category_id,
            gram=it.gram,
            width=it.width,
            unit=it.unit,
            quantity=it.quantity,
            unit_price=it.unit_price,
            amount=it.amount,
            delivery_date=it.delivery_date,
            remark=it.remark,
            arrived_quantity=0,
            status="pending"
        )
        db.add(db_item)

    # 操作日志
    log = DBOperationLog(module="卷料仓", action="修改采购单", target_type="采购单", target_id=order.id, detail=f"修改采购单：{order.order_no}，供应商{order.supplier}")
    db.add(log)

    db.commit()
    db.refresh(order)
    return order


@app.delete("/api/purchase_order/{order_id}")
def delete_purchase_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(DBPurchaseOrder).filter(DBPurchaseOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="采购单不存在")
    db.query(DBPurchaseOrderItem).filter(DBPurchaseOrderItem.order_id == order_id).delete()
    # 操作日志
    log = DBOperationLog(module="卷料仓", action="删除采购单", target_type="采购单", target_id=order_id, detail=f"删除采购单：{order.order_no}，供应商{order.supplier}")
    db.add(log)
    db.delete(order)
    db.commit()
    return {"ok": True}


# 到货确认（自动入库卷料仓）
@app.post("/api/purchase_order/{order_id}/arrive")
def arrive_purchase_order(order_id: int, req: PurchaseArriveRequest, db: Session = Depends(get_db)):
    order = db.query(DBPurchaseOrder).filter(DBPurchaseOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="采购单不存在")

    created_rolls = []
    all_arrived = True
    arrive_amount_total = 0

    for arrive_item in req.items:
        item = db.query(DBPurchaseOrderItem).filter(DBPurchaseOrderItem.id == arrive_item.item_id).first()
        if not item:
            continue
        if arrive_item.arrive_quantity <= 0:
            continue

        # 更新明细已到货数量
        item.arrived_quantity = (item.arrived_quantity or 0) + arrive_item.arrive_quantity
        # 累计本次到货金额（到货吨数 × 采购单价）
        arrive_amount_total += arrive_item.arrive_quantity * (item.unit_price or 0)
        if item.arrived_quantity >= item.quantity:
            item.status = "arrived"
        else:
            item.status = "partial"
            all_arrived = False

        # 生成卷筒记录：优先用手动录入的明细，否则按支数平均分配
        if arrive_item.rolls and len(arrive_item.rolls) > 0:
            roll_detail_list = [{"roll_no": r.roll_no, "weight": r.weight, "remark": r.remark} for r in arrive_item.rolls if r.roll_no and r.weight and r.weight > 0]
        else:
            roll_count = max(1, arrive_item.roll_count)
            per_roll_weight = round(arrive_item.arrive_quantity / roll_count, 6)
            prefix = "JD" + datetime.now().strftime("%Y%m%d%H%M%S")
            roll_detail_list = [{"roll_no": f"{prefix}{i + 1:03d}", "weight": per_roll_weight, "remark": None} for i in range(roll_count)]

        for idx, roll_detail in enumerate(roll_detail_list):
            roll_no = roll_detail["roll_no"]
            per_roll_weight = roll_detail["weight"]
            manual_remark = roll_detail.get("remark")

            # 品名：从物理分类的二级分类获取，如果没有就用"未命名"
            product_name_id = None
            if item.category_id:
                cat = db.query(DBPhysicalCategory).filter(DBPhysicalCategory.id == item.category_id).first()
                if cat:
                    # 找二级分类（parent_id不为null的）
                    if cat.parent_id:
                        # 当前就是二级，找对应的品名
                        pn = db.query(DBProductName).filter(DBProductName.name == cat.name).first()
                        if pn:
                            product_name_id = pn.id
                        else:
                            # 自动创建品名
                            new_pn = DBProductName(name=cat.name)
                            db.add(new_pn)
                            db.flush()
                            product_name_id = new_pn.id
                    else:
                        # 当前是一级，找它的子分类（二级）
                        children = db.query(DBPhysicalCategory).filter(DBPhysicalCategory.parent_id == cat.id).all()
                        if children:
                            child = children[0]
                            pn = db.query(DBProductName).filter(DBProductName.name == child.name).first()
                            if pn:
                                product_name_id = pn.id
                            else:
                                new_pn = DBProductName(name=child.name)
                                db.add(new_pn)
                                db.flush()
                                product_name_id = new_pn.id

            roll = DBRawRoll(
                raw_no=roll_no,
                product_name_id=product_name_id,
                category_id=item.category_id,
                width=item.width,
                gram=item.gram,
                weight=per_roll_weight,
                stock_weight=per_roll_weight,
                ton_price=item.unit_price,
                remark=manual_remark if manual_remark else f"采购单{order.order_no}到货，第{idx+1}/{len(roll_detail_list)}支"
            )
            db.add(roll)
            db.flush()
            created_rolls.append({"id": roll.id, "raw_no": roll_no, "weight": per_roll_weight})
            # 品名查找逻辑在循环内，保持不变

    # ===财务联动：生成应付账款（一张采购单一笔，随到货累加）===
    if arrive_amount_total > 0:
        _today = datetime.now().strftime("%Y-%m-%d")
        exist_pay = db.query(DBFinancePayable).filter(DBFinancePayable.purchase_order_id == order.id).first()
        if exist_pay:
            exist_pay.amount += arrive_amount_total
            exist_pay.balance += arrive_amount_total
            exist_pay.arrive_date = _today
            exist_pay.status = "partial" if (exist_pay.paid_amount or 0) > 0 else "unpaid"
        else:
            _pay = DBFinancePayable(
                supplier_name=order.supplier,
                purchase_order_id=order.id,
                order_no=order.order_no,
                amount=arrive_amount_total,
                paid_amount=0,
                balance=arrive_amount_total,
                arrive_date=_today,
                status="unpaid"
            )
            db.add(_pay)

    # 更新采购单状态
    if all_arrived:
        order.status = "completed"
    else:
        order.status = "partial"

    # 操作日志
    log = DBOperationLog(module="卷料仓", action="采购到货", target_type="采购单", target_id=order.id, detail=f"采购单到货：{order.order_no}，生成{len(created_rolls)}支卷筒，总重量{sum(r['weight'] for r in created_rolls):.3f}吨，应付{arrive_amount_total:.2f}元")
    db.add(log)

    db.commit()
    return {"ok": True, "created_rolls": created_rolls, "count": len(created_rolls)}



# ----------------供应商数据库表----------------
class DBSupplier(Base):
    __tablename__ = "supplier"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    contact = Column(String(100))
    phone = Column(String(50))
    address = Column(String(500))
    payment_term = Column(String(100))
    salesman = Column(String(50))
    tax_no = Column(String(100))
    level = Column(String(50))
    remark = Column(Text)
    created_at = Column(String(30))


# ----------------供应商Pydantic模型----------------
class SupplierCreate(BaseModel):
    name: str
    contact: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    payment_term: Optional[str] = None
    salesman: Optional[str] = None
    tax_no: Optional[str] = None
    level: Optional[str] = None
    remark: Optional[str] = None


class SupplierOut(BaseModel):
    id: int
    name: str
    contact: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    payment_term: Optional[str] = None
    salesman: Optional[str] = None
    tax_no: Optional[str] = None
    level: Optional[str] = None
    remark: Optional[str] = None
    created_at: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


# ----------------供应商接口----------------
@app.get("/api/supplier", response_model=List[SupplierOut])
def list_supplier(db: Session = Depends(get_db)):
    return db.query(DBSupplier).order_by(DBSupplier.id.desc()).all()


@app.post("/api/supplier", response_model=SupplierOut)
def create_supplier(item: SupplierCreate, db: Session = Depends(get_db)):
    obj = DBSupplier(
        name=item.name,
        contact=item.contact,
        phone=item.phone,
        address=item.address,
        payment_term=item.payment_term,
        salesman=item.salesman,
        tax_no=item.tax_no,
        level=item.level,
        remark=item.remark,
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    db.add(obj)
    # 操作日志
    log = DBOperationLog(module="供应商管理", action="新增", target_type="供应商", target_id=obj.id, detail=f"新增供应商：{obj.name}")
    db.add(log)
    db.commit()
    db.refresh(obj)
    return obj


@app.put("/api/supplier/{supplier_id}", response_model=SupplierOut)
def update_supplier(supplier_id: int, item: SupplierCreate, db: Session = Depends(get_db)):
    obj = db.query(DBSupplier).filter(DBSupplier.id == supplier_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="供应商不存在")
    for key, value in item.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
    # 操作日志
    log = DBOperationLog(module="供应商管理", action="修改", target_type="供应商", target_id=obj.id, detail=f"修改供应商：{obj.name}")
    db.add(log)
    db.commit()
    db.refresh(obj)
    return obj


@app.delete("/api/supplier/{supplier_id}")
def delete_supplier(supplier_id: int, db: Session = Depends(get_db)):
    obj = db.query(DBSupplier).filter(DBSupplier.id == supplier_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="供应商不存在")
    # 操作日志
    log = DBOperationLog(module="供应商管理", action="删除", target_type="供应商", target_id=supplier_id, detail=f"删除供应商：{obj.name}")
    db.add(log)
    db.delete(obj)
    db.commit()
    return {"ok": True}


# =================财务板块接口（第一期）=================
# ----------Pydantic模型----------
class FinanceAccountCreate(BaseModel):
    name: str
    account_type: str = "bank"
    balance: float = 0
    remark: Optional[str] = ""

class FinanceAccountOut(BaseModel):
    id: int
    name: str
    account_type: str
    balance: float
    remark: Optional[str] = ""
    model_config = ConfigDict(from_attributes=True)

class FinanceTransactionCreate(BaseModel):
    trans_date: str
    direction: str                                   # income/expense
    category: str = "其他"
    counterparty: Optional[str] = ""
    account_id: int
    amount: float
    ref_type: Optional[str] = "manual"
    ref_no: Optional[str] = ""
    operator: Optional[str] = ""
    remark: Optional[str] = ""

class FinanceTransactionOut(BaseModel):
    id: int
    trans_date: Optional[str] = None
    direction: Optional[str] = None
    category: Optional[str] = None
    counterparty: Optional[str] = None
    account_id: Optional[int] = None
    amount: float
    ref_type: Optional[str] = None
    ref_id: Optional[int] = None
    ref_no: Optional[str] = None
    operator: Optional[str] = None
    remark: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class FinanceReceivableOut(BaseModel):
    id: int
    customer_id: Optional[int] = None
    customer_name: Optional[str] = None
    sales_order_id: Optional[int] = None
    order_no: Optional[str] = None
    amount: float
    received_amount: float
    balance: float
    ship_date: Optional[str] = None
    due_date: Optional[str] = None
    status: str
    remark: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class FinancePayableOut(BaseModel):
    id: int
    supplier_name: Optional[str] = None
    purchase_order_id: Optional[int] = None
    order_no: Optional[str] = None
    amount: float
    paid_amount: float
    balance: float
    arrive_date: Optional[str] = None
    due_date: Optional[str] = None
    status: str
    remark: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class SettleRequest(BaseModel):
    amount: float
    account_id: int
    trans_date: Optional[str] = None
    operator: Optional[str] = ""
    remark: Optional[str] = ""

# ----------资金账户接口----------
@app.get("/api/finance/account", response_model=List[FinanceAccountOut])
def list_finance_account(db: Session = Depends(get_db)):
    return db.query(DBFinanceAccount).order_by(DBFinanceAccount.id).all()

@app.post("/api/finance/account", response_model=FinanceAccountOut)
def create_finance_account(item: FinanceAccountCreate, db: Session = Depends(get_db)):
    obj = DBFinanceAccount(**item.model_dump())
    db.add(obj)
    log = DBOperationLog(module="财务", action="新增账户", target_type="资金账户", detail=f"新增账户：{obj.name}，期初余额{obj.balance}")
    db.add(log)
    db.commit()
    db.refresh(obj)
    return obj

@app.put("/api/finance/account/{account_id}", response_model=FinanceAccountOut)
def update_finance_account(account_id: int, item: FinanceAccountCreate, db: Session = Depends(get_db)):
    obj = db.query(DBFinanceAccount).filter(DBFinanceAccount.id == account_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="账户不存在")
    # 余额由流水驱动，不允许直接改，只改名称/类型/备注
    obj.name = item.name
    obj.account_type = item.account_type
    obj.remark = item.remark
    db.commit()
    db.refresh(obj)
    return obj

@app.delete("/api/finance/account/{account_id}")
def delete_finance_account(account_id: int, db: Session = Depends(get_db)):
    obj = db.query(DBFinanceAccount).filter(DBFinanceAccount.id == account_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="账户不存在")
    tx_count = db.query(DBFinanceTransaction).filter(DBFinanceTransaction.account_id == account_id).count()
    if tx_count > 0:
        raise HTTPException(status_code=400, detail=f"该账户有{tx_count}笔流水记录，不能删除")
    db.delete(obj)
    db.commit()
    return {"ok": True}

# ----------资金流水接口----------
@app.get("/api/finance/transaction", response_model=List[FinanceTransactionOut])
def list_finance_transaction(direction: Optional[str] = None, category: Optional[str] = None,
                             account_id: Optional[int] = None, keyword: Optional[str] = None,
                             start_date: Optional[str] = None, end_date: Optional[str] = None,
                             db: Session = Depends(get_db)):
    q = db.query(DBFinanceTransaction)
    if direction:
        q = q.filter(DBFinanceTransaction.direction == direction)
    if category:
        q = q.filter(DBFinanceTransaction.category == category)
    if account_id:
        q = q.filter(DBFinanceTransaction.account_id == account_id)
    if keyword:
        q = q.filter(DBFinanceTransaction.counterparty.like(f"%{keyword}%"))
    if start_date:
        q = q.filter(DBFinanceTransaction.trans_date >= start_date)
    if end_date:
        q = q.filter(DBFinanceTransaction.trans_date <= end_date)
    return q.order_by(DBFinanceTransaction.trans_date.desc(), DBFinanceTransaction.id.desc()).all()

@app.post("/api/finance/transaction", response_model=FinanceTransactionOut)
def create_finance_transaction(item: FinanceTransactionCreate, db: Session = Depends(get_db)):
    if item.amount <= 0:
        raise HTTPException(status_code=400, detail="金额必须大于0")
    account = db.query(DBFinanceAccount).filter(DBFinanceAccount.id == item.account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="资金账户不存在")
    if item.direction == "expense" and account.balance < item.amount:
        raise HTTPException(status_code=400, detail=f"账户余额不足，当前余额{account.balance:.2f}")
    # 更新账户余额
    account.balance += item.amount if item.direction == "income" else -item.amount
    tx = DBFinanceTransaction(**item.model_dump())
    db.add(tx)
    log = DBOperationLog(module="财务", action="手工记账", target_type="资金流水",
                        detail=f"{'收入' if item.direction=='income' else '支出'}{item.amount}（{item.category}，{item.counterparty}）")
    db.add(log)
    db.commit()
    db.refresh(tx)
    return tx

# ----------应收账款接口----------
@app.get("/api/finance/receivable", response_model=List[FinanceReceivableOut])
def list_finance_receivable(status: Optional[str] = None, keyword: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(DBFinanceReceivable)
    if status:
        q = q.filter(DBFinanceReceivable.status == status)
    if keyword:
        q = q.filter(DBFinanceReceivable.customer_name.like(f"%{keyword}%"))
    return q.order_by(DBFinanceReceivable.id.desc()).all()

@app.post("/api/finance/receivable/{rid}/receive", response_model=FinanceReceivableOut)
def receive_finance(rid: int, data: SettleRequest, db: Session = Depends(get_db)):
    rec = db.query(DBFinanceReceivable).filter(DBFinanceReceivable.id == rid).first()
    if not rec:
        raise HTTPException(status_code=404, detail="应收记录不存在")
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="收款金额必须大于0")
    if data.amount > rec.balance + 1e-6:
        raise HTTPException(status_code=400, detail=f"收款金额不能超过未收余额{rec.balance:.2f}")
    account = db.query(DBFinanceAccount).filter(DBFinanceAccount.id == data.account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="资金账户不存在")
    trans_date = data.trans_date or datetime.now().strftime("%Y-%m-%d")
    # 更新应收
    rec.received_amount += data.amount
    rec.balance -= data.amount
    rec.status = "paid" if rec.balance <= 1e-6 else "partial"
    if rec.balance <= 1e-6:
        rec.balance = 0
    # 更新账户
    account.balance += data.amount
    # 生成流水
    tx = DBFinanceTransaction(trans_date=trans_date, direction="income", category="客户收款",
                              counterparty=rec.customer_name, account_id=account.id, amount=data.amount,
                              ref_type="receivable", ref_id=rec.id, ref_no=rec.order_no,
                              operator=data.operator or "", remark=data.remark or "")
    db.add(tx)
    log = DBOperationLog(module="财务", action="收款", target_type="应收账款", target_id=rec.id,
                        detail=f"收到{rec.customer_name}货款{data.amount}（{rec.order_no}），入{account.name}")
    db.add(log)
    db.commit()
    db.refresh(rec)
    return rec

# ----------应付账款接口----------
@app.get("/api/finance/payable", response_model=List[FinancePayableOut])
def list_finance_payable(status: Optional[str] = None, keyword: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(DBFinancePayable)
    if status:
        q = q.filter(DBFinancePayable.status == status)
    if keyword:
        q = q.filter(DBFinancePayable.supplier_name.like(f"%{keyword}%"))
    return q.order_by(DBFinancePayable.id.desc()).all()

@app.post("/api/finance/payable/{pid}/pay", response_model=FinancePayableOut)
def pay_finance(pid: int, data: SettleRequest, db: Session = Depends(get_db)):
    pay = db.query(DBFinancePayable).filter(DBFinancePayable.id == pid).first()
    if not pay:
        raise HTTPException(status_code=404, detail="应付记录不存在")
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="付款金额必须大于0")
    if data.amount > pay.balance + 1e-6:
        raise HTTPException(status_code=400, detail=f"付款金额不能超过未付余额{pay.balance:.2f}")
    account = db.query(DBFinanceAccount).filter(DBFinanceAccount.id == data.account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="资金账户不存在")
    if account.balance < data.amount:
        raise HTTPException(status_code=400, detail=f"账户余额不足，{account.name}当前余额{account.balance:.2f}")
    trans_date = data.trans_date or datetime.now().strftime("%Y-%m-%d")
    pay.paid_amount += data.amount
    pay.balance -= data.amount
    pay.status = "paid" if pay.balance <= 1e-6 else "partial"
    if pay.balance <= 1e-6:
        pay.balance = 0
    account.balance -= data.amount
    tx = DBFinanceTransaction(trans_date=trans_date, direction="expense", category="供应商付款",
                              counterparty=pay.supplier_name, account_id=account.id, amount=data.amount,
                              ref_type="payable", ref_id=pay.id, ref_no=pay.order_no,
                              operator=data.operator or "", remark=data.remark or "")
    db.add(tx)
    log = DBOperationLog(module="财务", action="付款", target_type="应付账款", target_id=pay.id,
                        detail=f"付给{pay.supplier_name}{data.amount}（{pay.order_no}），出{account.name}")
    db.add(log)
    db.commit()
    db.refresh(pay)
    return pay

# ----------财务汇总看板----------
@app.get("/api/finance/summary")
def finance_summary(db: Session = Depends(get_db)):
    accounts = db.query(DBFinanceAccount).all()
    total_cash = sum(a.balance for a in accounts)
    rec_total = db.query(DBFinanceReceivable).filter(DBFinanceReceivable.status != "paid")
    rec_balance = sum(r.balance for r in rec_total.all())
    pay_balance = sum(p.balance for p in db.query(DBFinancePayable).filter(DBFinancePayable.status != "paid").all())
    today = datetime.now().strftime("%Y-%m-%d")
    overdue_rec = db.query(DBFinanceReceivable).filter(
        DBFinanceReceivable.status != "paid",
        DBFinanceReceivable.due_date < today
    ).all()
    return {
        "total_cash": round(total_cash, 2),
        "receivable_balance": round(rec_balance, 2),
        "payable_balance": round(pay_balance, 2),
        "overdue_count": len(overdue_rec),
        "overdue_amount": round(sum(r.balance for r in overdue_rec), 2),
        "accounts": [{"id": a.id, "name": a.name, "balance": a.balance} for a in accounts]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



# ----------------生产工单接口----------------
class ProduceOrderItemCreate(BaseModel):
    layer_no: int
    roll_id: Optional[int] = None
    roll_name: str = ""
    quantity: float = 0
    unit_price: float = 0
    amount: float = 0
    remark: Optional[str] = None

class ProduceOrderCreate(BaseModel):
    order_no: Optional[str] = None
    po_no: Optional[str] = None
    customer_id: Optional[int] = None
    customer_name: Optional[str] = None
    product_name: Optional[str] = None
    quantity: float = 0
    spec_width: float = 0
    spec_length: float = 0
    total_gram: float = 0
    customer_order_no: Optional[str] = None
    thickness: Optional[str] = None
    humidity: Optional[str] = None
    brand: Optional[str] = None
    size_error: Optional[str] = None
    diagonal_error: Optional[str] = "2MM内"
    package_method: Optional[str] = None
    loss_limit: Optional[str] = "2%"
    maker: Optional[str] = None
    checker: Optional[str] = None
    schedule_date: Optional[str] = None
    sales_order_id: Optional[int] = None
    craft: Optional[str] = None
    produce_date: Optional[str] = None
    layers: int = 1
    total_amount: float = 0
    status: str = "draft"
    remark: Optional[str] = None
    items: List[ProduceOrderItemCreate] = []

class ProduceOrderItemOut(BaseModel):
    id: int
    order_id: int
    layer_no: int
    roll_id: Optional[int] = None
    roll_name: Optional[str] = None
    quantity: float
    unit_price: float
    amount: float
    remark: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class ProduceOrderOut(BaseModel):
    id: int
    order_no: Optional[str] = None
    po_no: Optional[str] = None
    customer_id: Optional[int] = None
    customer_name: Optional[str] = None
    product_name: Optional[str] = None
    quantity: float = 0
    spec_width: float = 0
    spec_length: float = 0
    total_gram: float = 0
    customer_order_no: Optional[str] = None
    thickness: Optional[str] = None
    humidity: Optional[str] = None
    brand: Optional[str] = None
    size_error: Optional[str] = None
    diagonal_error: Optional[str] = None
    package_method: Optional[str] = None
    loss_limit: Optional[str] = None
    maker: Optional[str] = None
    checker: Optional[str] = None
    schedule_date: Optional[str] = None
    sales_order_id: Optional[int] = None
    craft: Optional[str] = None
    produce_date: Optional[str] = None
    layers: int
    total_amount: float
    status: str
    remark: Optional[str] = None
    created_at: Optional[str] = None
    items: List[ProduceOrderItemOut] = []
    model_config = ConfigDict(from_attributes=True)

def generate_produce_order_no(db):
    prefix = "GD" + datetime.now().strftime("%Y%m%d")
    count = db.query(DBProduceOrder).filter(DBProduceOrder.order_no.like(f"{prefix}%")).count()
    return f"{prefix}-{count+1:03d}"

@app.get("/api/produce_order", response_model=List[ProduceOrderOut])
def list_produce_order(db: Session = Depends(get_db)):
    orders = db.query(DBProduceOrder).order_by(DBProduceOrder.id.desc()).all()
    for order in orders:
        order.items = db.query(DBProduceOrderItem).filter(DBProduceOrderItem.order_id == order.id).order_by(DBProduceOrderItem.layer_no).all()
    return orders

@app.post("/api/produce_order", response_model=ProduceOrderOut)
def create_produce_order(item: ProduceOrderCreate, db: Session = Depends(get_db)):
    order_no = item.order_no or generate_produce_order_no(db)
    total_amount = sum((i.quantity or 0) * (i.unit_price or 0) for i in item.items)
    order = DBProduceOrder(
        order_no=order_no,
        po_no=item.po_no,
        customer_id=item.customer_id,
        customer_name=item.customer_name,
        product_name=item.product_name,
        quantity=item.quantity,
        spec_width=item.spec_width,
        spec_length=item.spec_length,
        total_gram=item.total_gram,
        customer_order_no=item.customer_order_no,
        thickness=item.thickness,
        humidity=item.humidity,
        brand=item.brand,
        size_error=item.size_error,
        diagonal_error=item.diagonal_error,
        package_method=item.package_method,
        loss_limit=item.loss_limit,
        maker=item.maker,
        checker=item.checker,
        schedule_date=item.schedule_date,
        sales_order_id=item.sales_order_id,
        craft=item.craft,
        produce_date=item.produce_date or datetime.now().strftime("%Y-%m-%d"),
        layers=item.layers,
        total_amount=total_amount,
        status=item.status,
        remark=item.remark
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    for i in item.items:
        db_item = DBProduceOrderItem(
            order_id=order.id,
            layer_no=i.layer_no,
            roll_id=i.roll_id,
            roll_name=i.roll_name,
            quantity=i.quantity,
            unit_price=i.unit_price,
            amount=i.quantity * i.unit_price,
            remark=i.remark
        )
        db.add(db_item)
    db.commit()
    order.items = db.query(DBProduceOrderItem).filter(DBProduceOrderItem.order_id == order.id).order_by(DBProduceOrderItem.layer_no).all()
    return order

@app.put("/api/produce_order/{order_id}", response_model=ProduceOrderOut)
def update_produce_order(order_id: int, item: ProduceOrderCreate, db: Session = Depends(get_db)):
    order = db.query(DBProduceOrder).filter(DBProduceOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="工单不存在")
    total_amount = sum((i.quantity or 0) * (i.unit_price or 0) for i in item.items)
    order.po_no = item.po_no
    order.customer_id = item.customer_id
    order.customer_name = item.customer_name
    order.product_name = item.product_name
    order.quantity = item.quantity
    order.spec_width = item.spec_width
    order.spec_length = item.spec_length
    order.total_gram = item.total_gram
    order.customer_order_no = item.customer_order_no
    order.thickness = item.thickness
    order.humidity = item.humidity
    order.brand = item.brand
    order.size_error = item.size_error
    order.diagonal_error = item.diagonal_error
    order.package_method = item.package_method
    order.loss_limit = item.loss_limit
    order.maker = item.maker
    order.checker = item.checker
    order.schedule_date = item.schedule_date
    order.sales_order_id = item.sales_order_id
    order.craft = item.craft
    order.produce_date = item.produce_date
    order.layers = item.layers
    order.total_amount = total_amount
    order.status = item.status
    order.remark = item.remark
    # 删除旧明细
    db.query(DBProduceOrderItem).filter(DBProduceOrderItem.order_id == order_id).delete()
    # 加新明细
    for i in item.items:
        db_item = DBProduceOrderItem(
            order_id=order.id,
            layer_no=i.layer_no,
            roll_id=i.roll_id,
            roll_name=i.roll_name,
            quantity=i.quantity,
            unit_price=i.unit_price,
            amount=i.quantity * i.unit_price,
            remark=i.remark
        )
        db.add(db_item)
    db.commit()
    db.refresh(order)
    order.items = db.query(DBProduceOrderItem).filter(DBProduceOrderItem.order_id == order.id).order_by(DBProduceOrderItem.layer_no).all()
    return order

@app.delete("/api/produce_order/{order_id}")
def delete_produce_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(DBProduceOrder).filter(DBProduceOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="工单不存在")
    db.query(DBProduceOrderItem).filter(DBProduceOrderItem.order_id == order_id).delete()
    db.delete(order)
    db.commit()
    return {"ok": True}

# 确认领料：锁定卷料库存（stock_weight减少，记录领料日志）
@app.post("/api/produce_order/{order_id}/pick_material")
def pick_material(order_id: int, db: Session = Depends(get_db)):
    order = db.query(DBProduceOrder).filter(DBProduceOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="工单不存在")
    items = db.query(DBProduceOrderItem).filter(DBProduceOrderItem.order_id == order_id).all()
    for item in items:
        roll = db.query(DBRawRoll).filter(DBRawRoll.id == item.roll_id).first()
        if roll:
            if roll.stock_weight < item.quantity:
                raise HTTPException(status_code=400, detail=f"卷料[{roll.raw_no}]库存不足，当前剩余{roll.stock_weight:.3f}吨")
            roll.stock_weight -= item.quantity
            # 记录领料日志
            log = DBProduceMaterialLog(
                order_id=order_id,
                item_id=item.id,
                type="pick",
                material_type="roll",
                material_id=item.roll_id,
                quantity=item.quantity
            )
            db.add(log)
    order.status = "picking"
    db.commit()
    return {"ok": True, "message": "领料成功，卷料库存已锁定"}

# 退料：把没用完的卷料退回卷料仓
@app.post("/api/produce_order/{order_id}/return_material")
def return_material(order_id: int, db: Session = Depends(get_db), return_items: List[dict] = Body(...)):
    order = db.query(DBProduceOrder).filter(DBProduceOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="工单不存在")
    for ri in return_items:
        item_id = ri.get("item_id")
        quantity = ri.get("quantity", 0)
        if quantity <= 0:
            continue
        item = db.query(DBProduceOrderItem).filter(DBProduceOrderItem.id == item_id).first()
        if item:
            roll = db.query(DBRawRoll).filter(DBRawRoll.id == item.roll_id).first()
            if roll:
                roll.stock_weight += quantity
                log = DBProduceMaterialLog(
                    order_id=order_id,
                    item_id=item_id,
                    type="return",
                    material_type="roll",
                    material_id=item.roll_id,
                    quantity=quantity
                )
                db.add(log)
    order.status = "finished"
    # 操作日志
    log = DBOperationLog(module="生产管理", action="退料", target_type="生产工单", target_id=order_id, detail=f"退料完成：{order.order_no}，退回剩余卷料")
    db.add(log)
    db.commit()
    return {"ok": True, "message": "退料成功"}



# ----------------排单相关接口----------------

class ScheduleRequest(BaseModel):
    ids: list
    schedule_date: str

@app.post("/api/produce_order/schedule")
def schedule_orders(req: ScheduleRequest, db: Session = Depends(get_db)):
    """批量排单：把选中的工单指派到指定日期"""
    orders = db.query(DBProduceOrder).filter(DBProduceOrder.id.in_(req.ids)).all()
    for order in orders:
        order.schedule_date = req.schedule_date
        order.status = "scheduled"
    db.commit()
    for order in orders:
        db.refresh(order)
    # 操作日志
    for order in orders:
        log = DBOperationLog(module="生产管理", action="排单", target_type="生产工单", target_id=order.id, detail=f"排单：{order.order_no}，排单日期{req.schedule_date}")
        db.add(log)
    db.commit()
    return {"ok": True, "count": len(orders)}


@app.post("/api/produce_order/{order_id}/start_production")
def start_production(order_id: int, db: Session = Depends(get_db)):
    """移入待生产：锁定卷料库存"""
    order = db.query(DBProduceOrder).filter(DBProduceOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="工单不存在")

    items = db.query(DBProduceOrderItem).filter(DBProduceOrderItem.order_id == order_id).all()
    for item in items:
        roll = db.query(DBRawRoll).filter(DBRawRoll.id == item.roll_id).first()
        if roll:
            if roll.stock_weight < item.quantity:
                # 拼接完整分类路径
                cat_path = ""
                if roll.category_id:
                    path = []
                    cur = db.query(DBPhysicalCategory).filter(DBPhysicalCategory.id == roll.category_id).first()
                    while cur:
                        path.insert(0, cur.name)
                        cur = db.query(DBPhysicalCategory).filter(DBPhysicalCategory.id == cur.parent_id).first()
                    cat_path = " " + chr(92).join(path) if path else ""
                raise HTTPException(status_code=400, detail=f"卷料 {roll.raw_no}{cat_path} 库存不足，当前剩余 {roll.stock_weight:.3f} 吨")
            roll.stock_weight -= item.quantity

    order.status = "pending"
    # 操作日志
    log = DBOperationLog(module="生产管理", action="移入待生产", target_type="生产工单", target_id=order_id, detail=f"移入待生产：{order.order_no}，锁定卷料库存")
    db.add(log)
    db.commit()
    db.refresh(order)
    return {"ok": True, "status": "pending"}


@app.post("/api/produce_order/{order_id}/finish_production")
def finish_production(order_id: int, db: Session = Depends(get_db)):
    """完成生产：成品自动入库"""
    order = db.query(DBProduceOrder).filter(DBProduceOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="工单不存在")

    # 查找或创建成品品名
    pn = None
    if order.product_name:
        pn = db.query(DBProductNameFinished).filter(DBProductNameFinished.name == order.product_name).first()
        if not pn:
            pn = DBProductNameFinished(name=order.product_name)
            db.add(pn)
            db.commit()
            db.refresh(pn)

    # 创建成品入库记录
    spec = f"{order.spec_width or ''}x{order.spec_length or ''}" if order.spec_width else ""
    product = DBProduct(
        product_name_id=pn.id if pn else None,
        category_id=None,
        work_order_no=order.order_no,
        spec=spec,
        actual_gram=order.total_gram or 0,
        nominal_gram=order.total_gram or 0,
        quantity=order.quantity or 0,
        pending_out_qty=0,
        unit="令",
        remark=f"生产工单 {order.order_no} 自动入库"
    )
    db.add(product)

    order.status = "finished"
    # 操作日志
    log = DBOperationLog(module="生产管理", action="完成生产", target_type="生产工单", target_id=order_id, detail=f"完成生产：{order.order_no}，成品自动入库{order.quantity}令")
    db.add(log)
    db.commit()
    db.refresh(order)
    return {"ok": True, "status": "finished", "product_id": product.id}



# ----------------移出/打回相关接口----------------

@app.post("/api/produce_order/{order_id}/cancel_schedule")
def cancel_schedule(order_id: int, db: Session = Depends(get_db)):
    """取消排单：已排单 → 草稿"""
    order = db.query(DBProduceOrder).filter(DBProduceOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="工单不存在")
    if order.status != "scheduled":
        raise HTTPException(status_code=400, detail="只有已排单状态的工单才能取消排单")
    order.status = "draft"
    order.schedule_date = None
    # 操作日志
    log = DBOperationLog(module="生产管理", action="取消排单", target_type="生产工单", target_id=order_id, detail=f"取消排单：{order.order_no}，工单回到草稿")
    db.add(log)
    db.commit()
    db.refresh(order)
    return {"ok": True, "status": "draft"}


@app.post("/api/produce_order/{order_id}/back_to_draft")
def back_to_draft(order_id: int, db: Session = Depends(get_db)):
    """打回草稿：待生产 → 草稿，同时回滚卷料库存"""
    order = db.query(DBProduceOrder).filter(DBProduceOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="工单不存在")
    if order.status != "pending":
        raise HTTPException(status_code=400, detail="只有待生产状态的工单才能打回草稿")

    # 回滚卷料库存
    items = db.query(DBProduceOrderItem).filter(DBProduceOrderItem.order_id == order_id).all()
    for item in items:
        roll = db.query(DBRawRoll).filter(DBRawRoll.id == item.roll_id).first()
        if roll:
            roll.stock_weight += item.quantity

    order.status = "draft"
    order.schedule_date = None
    # 操作日志
    log = DBOperationLog(module="生产管理", action="打回草稿", target_type="生产工单", target_id=order_id, detail=f"打回草稿：{order.order_no}，卷料库存已退回")
    db.add(log)
    db.commit()
    db.refresh(order)
    return {"ok": True, "status": "draft"}


@app.post("/api/produce_order/{order_id}/reschedule")
def reschedule_order(order_id: int, db: Session = Depends(get_db)):
    """重新排单：待生产 → 已排单（库存保持锁定，可重新选日期）"""
    order = db.query(DBProduceOrder).filter(DBProduceOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="工单不存在")
    if order.status != "pending":
        raise HTTPException(status_code=400, detail="只有待生产状态的工单才能重新排单")
    order.status = "scheduled"
    # 操作日志
    log = DBOperationLog(module="生产管理", action="重新排单", target_type="生产工单", target_id=order_id, detail=f"重新排单：{order.order_no}，移回已排单可重新选日期")
    db.add(log)
    db.commit()
    db.refresh(order)
    return {"ok": True, "status": "scheduled"}
