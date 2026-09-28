with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 把 roll_id 改成 Optional
content = content.replace(
    '''class ProduceOrderItemCreate(BaseModel):
    layer_no: int
    roll_id: int
    roll_name: str = ""''',
    '''class ProduceOrderItemCreate(BaseModel):
    layer_no: int
    roll_id: Optional[int] = None
    roll_name: str = ""'''
)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('生产工单明细 roll_id 改可选完成')
