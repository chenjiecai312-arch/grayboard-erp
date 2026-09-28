with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    '''    amount: float
    ref_type: Optional[str] = None
    ref_no: Optional[str] = None
    operator: Optional[str] = None
    remark: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class FinanceReceivableOut(BaseModel):''',
    '''    amount: float
    ref_type: Optional[str] = None
    ref_id: Optional[int] = None
    ref_no: Optional[str] = None
    operator: Optional[str] = None
    remark: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class FinanceReceivableOut(BaseModel):'''
)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('FinanceTransactionOut 补 ref_id 完成')
