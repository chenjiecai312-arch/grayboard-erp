with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. DBRawRoll 模型加 ton_price
content = content.replace(
    '    stock_weight = Column(Float)\n    remark = Column(String)',
    '    stock_weight = Column(Float)\n    ton_price = Column(Float, default=0)  # 吨价（元/吨）\n    remark = Column(String)'
)

# 2. RawRollCreate 模型加 ton_price
content = content.replace(
    '    weight: float\n    remark: Optional[str] = None',
    '    weight: float\n    ton_price: float = 0\n    remark: Optional[str] = None'
)

# 3. RawRollOut 模型加 ton_price
content = content.replace(
    '    stock_weight:float\n    remark:Optional[str]=None',
    '    stock_weight:float\n    ton_price:float=0\n    remark:Optional[str]=None'
)

# 4. create_rawroll 里加 ton_price
content = content.replace(
    '        stock_weight=data["weight"],\n        remark=data["remark"]',
    '        stock_weight=data["weight"],\n        ton_price=data.get("ton_price", 0),\n        remark=data["remark"]'
)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('后端吨价模型加完成')
