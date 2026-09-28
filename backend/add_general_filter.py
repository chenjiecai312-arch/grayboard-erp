with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 加通用筛选参数
old = '''def list_sales_order(
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
        q = q.filter(DBSalesOrder.customer_name.like(f"%{customer_name}%"))
    if status:
        q = q.filter(DBSalesOrder.status == status)
    if start_date:
        q = q.filter(DBSalesOrder.delivery_date >= start_date)
    if end_date:
        q = q.filter(DBSalesOrder.delivery_date <= end_date)'''

new = '''def list_sales_order(
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
        field_map = {
            "order_no": DBSalesOrder.order_no,
            "customer_name": DBSalesOrder.customer_name,
            "salesman": DBSalesOrder.salesman,
            "receiver": DBSalesOrder.receiver,
            "delivery_date": DBSalesOrder.delivery_date,
        }
        if search_field in field_map:
            q = q.filter(field_map[search_field].like(f"%{search_value}%"))'''

content = content.replace(old, new)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('通用筛选后端完成')
