with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 状态筛选特殊处理：中文转英文
old = '''    # 通用字段筛选
    if search_field and search_value:
        field_map = {
            "order_no": DBSalesOrder.order_no,
            "customer_name": DBSalesOrder.customer_name,
            "salesman": DBSalesOrder.salesman,
            "receiver": DBSalesOrder.receiver,
            "delivery_date": DBSalesOrder.delivery_date,
            "status": DBSalesOrder.status,
        }
        if search_field in field_map:
            q = q.filter(field_map[search_field].like(f"%{search_value}%"))'''

new = '''    # 通用字段筛选
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
                q = q.filter(field_map[search_field].like(f"%{search_value}%"))'''

content = content.replace(old, new)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('状态中文筛选修复完成')
