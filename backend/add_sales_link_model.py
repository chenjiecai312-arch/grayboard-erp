with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. DBProduceOrder 模型加 sales_order_id（在 schedule_date 后面）
content = content.replace(
    '    schedule_date = Column(String(20))\n    produce_date = Column(String(20))',
    '    schedule_date = Column(String(20))\n    sales_order_id = Column(Integer, nullable=True)\n    produce_date = Column(String(20))'
)

# 2. ProduceOrderCreate 加 sales_order_id
content = content.replace(
    '    schedule_date: Optional[str] = None\n    produce_date: Optional[str] = None',
    '    schedule_date: Optional[str] = None\n    sales_order_id: Optional[int] = None\n    produce_date: Optional[str] = None'
)

# 3. ProduceOrderOut 加 sales_order_id
content = content.replace(
    '    checker: Optional[str] = None\n    schedule_date: Optional[str] = None\n    produce_date: Optional[str] = None',
    '    checker: Optional[str] = None\n    schedule_date: Optional[str] = None\n    sales_order_id: Optional[int] = None\n    produce_date: Optional[str] = None'
)

# 4. create 接口赋值
content = content.replace(
    '        schedule_date=item.schedule_date,\n        produce_date=item.produce_date or datetime.now().strftime("%Y-%m-%d"),',
    '        schedule_date=item.schedule_date,\n        sales_order_id=item.sales_order_id,\n        produce_date=item.produce_date or datetime.now().strftime("%Y-%m-%d"),'
)

# 5. update 接口赋值
content = content.replace(
    '    order.schedule_date = item.schedule_date\n    order.produce_date = item.produce_date',
    '    order.schedule_date = item.schedule_date\n    order.sales_order_id = item.sales_order_id\n    order.produce_date = item.produce_date'
)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('后端销售单关联字段加完成')
