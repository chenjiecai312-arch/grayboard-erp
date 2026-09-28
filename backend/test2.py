import urllib.request
import json

# 测试筛选草稿
url = 'http://localhost:8000/api/sales_order?search_field=status&search_value=%E8%8D%89%E7%A8%BF'
with urllib.request.urlopen(url) as res:
    data = json.loads(res.read())
print(f'筛选"草稿": {len(data)} 条')
for d in data:
    print(f'  {d["order_no"]} - {d["status"]} - {d["customer_name"]}')

# 测试筛选待出库
url2 = 'http://localhost:8000/api/sales_order?search_field=status&search_value=%E5%BE%85%E5%87%BA%E5%BA%93'
with urllib.request.urlopen(url2) as res:
    data2 = json.loads(res.read())
print(f'\n筛选"待出库": {len(data2)} 条')
for d in data2:
    print(f'  {d["order_no"]} - {d["status"]} - {d["customer_name"]}')
