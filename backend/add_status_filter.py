with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 加 status 到 field_map
old = '''        field_map = {
            "order_no": DBSalesOrder.order_no,
            "customer_name": DBSalesOrder.customer_name,
            "salesman": DBSalesOrder.salesman,
            "receiver": DBSalesOrder.receiver,
            "delivery_date": DBSalesOrder.delivery_date,
        }'''
new = '''        field_map = {
            "order_no": DBSalesOrder.order_no,
            "customer_name": DBSalesOrder.customer_name,
            "salesman": DBSalesOrder.salesman,
            "receiver": DBSalesOrder.receiver,
            "delivery_date": DBSalesOrder.delivery_date,
            "status": DBSalesOrder.status,
        }'''
content = content.replace(old, new)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('后端状态筛选加完成')
