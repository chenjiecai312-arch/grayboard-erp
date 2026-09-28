with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 加 customer_id 筛选参数
old = '''def list_sales_order(
    customer_name: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    q = db.query(DBSalesOrder)
    if customer_name:
        q = q.filter(DBSalesOrder.customer_name.like(f"%{customer_name}%"))'''

new = '''def list_sales_order(
    customer_name: Optional[str] = None,
    customer_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    q = db.query(DBSalesOrder)
    if customer_id:
        q = q.filter(DBSalesOrder.customer_id == customer_id)
    if customer_name:
        q = q.filter(DBSalesOrder.customer_name.like(f"%{customer_name}%"))'''

content = content.replace(old, new)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('客户筛选参数加完成')
