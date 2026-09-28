with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 加模型（在 DBOperationLog 后面）
old_model = '''# 操作日志表
class DBOperationLog(Base):
    __tablename__ = "operation_log"
    id = Column(Integer, primary_key=True, index=True)
    module = Column(String(50))          # 模块：成品仓/卷筒仓/销售订单等
    action = Column(String(50))          # 操作：新增/修改/删除/出库/入库等
    target_type = Column(String(50))     # 操作对象类型
    target_id = Column(Integer)          # 操作对象ID
    detail = Column(Text)                # 操作详情
    created_at = Column(String, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))'''

new_model = '''# 操作日志表
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
    customer_id = Column(Integer)
    customer_name = Column(String(200))
    produce_date = Column(String(20))
    layers = Column(Integer, default=1)
    total_amount = Column(Float, default=0)
    status = Column(String(20), default="draft")  # draft草稿/picking领料中/producing生产中/finished已完成
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
    created_at = Column(String, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))'''

content = content.replace(old_model, new_model)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('生产工单模型加完成')
