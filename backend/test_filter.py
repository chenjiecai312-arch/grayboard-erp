import urllib.request
import urllib.parse
import json
import traceback

try:
    # 测试状态筛选
    params = urllib.parse.urlencode({'search_field': 'status', 'search_value': '草稿'})
    url = f'http://localhost:8000/api/sales_order?{params}'
    print(f'请求URL: {url}')

    with urllib.request.urlopen(url) as res:
        data = json.loads(res.read().decode())

    print(f'\n筛选"草稿"结果：共 {len(data)} 条')
    for d in data:
        print(f'  {d["order_no"]} - 状态:{d["status"]} - {d["customer_name"]}')
except Exception as e:
    print(f'筛选请求出错: {e}')
    traceback.print_exc()

# 再测试不筛选
print('\n--- 不筛选（全部）---')
with urllib.request.urlopen('http://localhost:8000/api/sales_order') as res:
    all_data = json.loads(res.read().decode())
print(f'全部：共 {len(all_data)} 条')
for d in all_data:
    print(f'  {d["order_no"]} - 状态:{d["status"]} - {d["customer_name"]}')
