with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. DBProduceOrder 模型加字段
old_model = '''class DBProduceOrder(Base):
    __tablename__ = "produce_order"
    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(50))
    customer_id = Column(Integer)
    customer_name = Column(String(200))
    produce_date = Column(String(20))
    layers = Column(Integer, default=1)
    total_amount = Column(Float, default=0)
    status = Column(String(20), default="draft")  # draft草稿/picking领料中/producing生产中/finished已完成
    remark = Column(Text)
    created_at = Column(String, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))'''

new_model = '''class DBProduceOrder(Base):
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
    produce_date = Column(String(20))
    layers = Column(Integer, default=1)
    total_amount = Column(Float, default=0)
    status = Column(String(20), default="draft")
    remark = Column(Text)
    created_at = Column(String, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))'''

content = content.replace(old_model, new_model)

# 2. ProduceOrderCreate 加字段
old_create = '''class ProduceOrderCreate(BaseModel):
    order_no: Optional[str] = None
    customer_id: Optional[int] = None
    customer_name: Optional[str] = None
    produce_date: Optional[str] = None
    layers: int = 1
    total_amount: float = 0
    status: str = "draft"
    remark: Optional[str] = None
    items: List[ProduceOrderItemCreate] = []'''

new_create = '''class ProduceOrderCreate(BaseModel):
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
    produce_date: Optional[str] = None
    layers: int = 1
    total_amount: float = 0
    status: str = "draft"
    remark: Optional[str] = None
    items: List[ProduceOrderItemCreate] = []'''

content = content.replace(old_create, new_create)

# 3. ProduceOrderOut 加字段
old_out = '''class ProduceOrderOut(BaseModel):
    id: int
    order_no: Optional[str] = None
    customer_id: Optional[int] = None
    customer_name: Optional[str] = None
    produce_date: Optional[str] = None
    layers: int
    total_amount: float
    status: str
    remark: Optional[str] = None
    created_at: Optional[str] = None
    items: List[ProduceOrderItemOut] = []
    model_config = ConfigDict(from_attributes=True)'''

new_out = '''class ProduceOrderOut(BaseModel):
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
    produce_date: Optional[str] = None
    layers: int
    total_amount: float
    status: str
    remark: Optional[str] = None
    created_at: Optional[str] = None
    items: List[ProduceOrderItemOut] = []
    model_config = ConfigDict(from_attributes=True)'''

content = content.replace(old_out, new_out)

# 4. create 接口里赋值新字段
old_create_order = '''    order = DBProduceOrder(
        order_no=order_no,
        customer_id=item.customer_id,
        customer_name=item.customer_name,
        produce_date=item.produce_date or datetime.now().strftime("%Y-%m-%d"),
        layers=item.layers,
        total_amount=total_amount,
        status=item.status,
        remark=item.remark
    )'''

new_create_order = '''    order = DBProduceOrder(
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
        produce_date=item.produce_date or datetime.now().strftime("%Y-%m-%d"),
        layers=item.layers,
        total_amount=total_amount,
        status=item.status,
        remark=item.remark
    )'''

content = content.replace(old_create_order, new_create_order)

# 5. update 接口里赋值新字段
old_update = '''    order.customer_id = item.customer_id
    order.customer_name = item.customer_name
    order.produce_date = item.produce_date
    order.layers = item.layers
    order.total_amount = total_amount
    order.status = item.status
    order.remark = item.remark'''

new_update = '''    order.po_no = item.po_no
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
    order.produce_date = item.produce_date
    order.layers = item.layers
    order.total_amount = total_amount
    order.status = item.status
    order.remark = item.remark'''

content = content.replace(old_update, new_update)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('生产工单后端字段加完成')
