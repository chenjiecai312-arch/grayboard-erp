with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. DBProduceOrder 模型加 craft（在 sales_order_id 后面）
content = content.replace(
    '    sales_order_id = Column(Integer, nullable=True)\n    produce_date = Column(String(20))',
    '    sales_order_id = Column(Integer, nullable=True)\n    craft = Column(String(200), nullable=True)\n    produce_date = Column(String(20))'
)

# 2. ProduceOrderCreate 加 craft
content = content.replace(
    '    sales_order_id: Optional[int] = None\n    produce_date: Optional[str] = None',
    '    sales_order_id: Optional[int] = None\n    craft: Optional[str] = None\n    produce_date: Optional[str] = None'
)

# 3. ProduceOrderOut 加 craft
content = content.replace(
    '    sales_order_id: Optional[int] = None\n    produce_date: Optional[str] = None',
    '    sales_order_id: Optional[int] = None\n    craft: Optional[str] = None\n    produce_date: Optional[str] = None'
)

# 4. create 接口赋值
content = content.replace(
    '        sales_order_id=item.sales_order_id,\n        produce_date=item.produce_date or datetime.now().strftime("%Y-%m-%d"),',
    '        sales_order_id=item.sales_order_id,\n        craft=item.craft,\n        produce_date=item.produce_date or datetime.now().strftime("%Y-%m-%d"),'
)

# 5. update 接口赋值
content = content.replace(
    '    order.sales_order_id = item.sales_order_id\n    order.produce_date = item.produce_date',
    '    order.sales_order_id = item.sales_order_id\n    order.craft = item.craft\n    order.produce_date = item.produce_date'
)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('后端生产工艺字段加完成')
