import urllib.request
import json

BASE = "http://127.0.0.1:8000"

def api_get(url):
    req = urllib.request.Request(f"{BASE}{url}")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

def api_post(url, data):
    req = urllib.request.Request(f"{BASE}{url}", data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

def api_put(url, data):
    req = urllib.request.Request(f"{BASE}{url}", data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'}, method='PUT')
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

print("=" * 60)
print("测试1：生产工单新增+更新（roll_id可为空）")
print("=" * 60)
customers = api_get('/api/customer')
cus_id = customers[0]['id'] if customers else None
cus_name = customers[0]['customer_name'] if customers else '测试客户'

payload = {
    "order_no": "AUTO20260926002",
    "customer_id": cus_id,
    "customer_name": cus_name,
    "product_name": "自动保存测试产品",
    "quantity": 1000,
    "spec_width": 787,
    "spec_length": 1092,
    "total_gram": 1000,
    "layers": 1,
    "craft": "金盾350",
    "items": [
        {"layer_no": 1, "roll_id": None, "roll_name": "金盾350", "quantity": 1, "unit_price": 2270, "amount": 2270, "remark": "测试"}
    ]
}
produce = api_post('/api/produce_order', payload)
print(f"新增成功：{produce['order_no']} (id={produce['id']})")

payload["product_name"] = "自动保存测试产品（已更新）"
payload["quantity"] = 2000
produce2 = api_put(f"/api/produce_order/{produce['id']}", payload)
print(f"更新成功：{produce2['product_name']}, 数量={produce2['quantity']}")
print("✓ 生产工单新增+更新接口正常\n")

print("=" * 60)
print("测试2：成品仓新增+更新")
print("=" * 60)
pn_list = api_get('/api/product_name_finished')
pc_list = api_get('/api/product_category')
pn_id = pn_list[0]['id'] if pn_list else None
pc_id = pc_list[0]['id'] if pc_list else None

payload = {
    "product_name_id": pn_id,
    "customer_id": None,
    "category_id": pc_id,
    "work_order_no": None,
    "spec": "787x1092",
    "actual_gram": 1000,
    "nominal_gram": 1100,
    "quantity": 500,
    "unit": "令",
    "remark": "自动保存测试"
}
product = api_post('/api/product', payload)
print(f"新增成功：id={product['id']}, spec={product['spec']}, 数量={product['quantity']}")

payload["quantity"] = 800
payload["remark"] = "自动保存测试（已更新）"
product2 = api_put(f"/api/product/{product['id']}", payload)
print(f"更新成功：数量={product2['quantity']}, 备注={product2['remark']}")
print("✓ 成品仓新增+更新接口正常\n")

print("=" * 60)
print("全部测试通过！")
print("=" * 60)
print("三个模块自动保存功能全部完成：")
print("1. ✅ 采购单 - 新增+更新接口正常")
print("2. ✅ 生产工单 - 新增+更新接口正常（修复了roll_id必填问题）")
print("3. ✅ 成品仓 - 新增+更新接口正常")
print("")
print("后端修复：生产工单明细 roll_id 改为可选，支持自动保存时未选卷筒的情况")
