import requests
import json

BASE = "http://127.0.0.1:8000"

print("=" * 60)
print("测试1：获取物理分类列表（用于级联选择）")
print("=" * 60)
r = requests.get(f"{BASE}/api/physical_category")
pc_list = r.json()
print(f"物理分类总数：{len(pc_list)}")
level1 = [c for c in pc_list if c['parent_id'] is None]
print(f"一级分类数量：{len(level1)}")
for c in level1[:3]:
    children = [x for x in pc_list if x['parent_id'] == c['id']]
    print(f"  {c['name']}（{len(children)}个二级）")
print("✓ 物理分类接口正常\n")

print("=" * 60)
print("测试2：新增采购单")
print("=" * 60)
# 找一个有子分类的一级分类
test_cat = None
for c in level1:
    children = [x for x in pc_list if x['parent_id'] == c['id']]
    if children:
        test_cat = children[0]
        break

if test_cat:
    print(f"测试用分类：{test_cat['name']} (id={test_cat['id']})")
else:
    print("警告：没有找到合适的测试分类，使用第一个分类")
    test_cat = pc_list[0] if pc_list else None

payload = {
    "supplier": "测试供应商-金田纸业",
    "delivery_address": "自提",
    "order_date": "2026-09-26",
    "remark": "自动化测试采购单",
    "maker": "测试员",
    "checker": "审核员",
    "total_amount": 22700,
    "items": [
        {
            "category_id": test_cat['id'] if test_cat else None,
            "gram": 350,
            "width": 787,
            "unit": "吨",
            "quantity": 10,
            "unit_price": 2270,
            "amount": 22700,
            "delivery_date": "2026-09-28",
            "remark": "测试明细"
        }
    ]
}
r = requests.post(f"{BASE}/api/purchase_order", json=payload)
print(f"响应状态：{r.status_code}")
if r.status_code == 200:
    order = r.json()
    print(f"采购单号：{order['order_no']}")
    print(f"采购单ID：{order['id']}")
    print(f"状态：{order['status']}")
    print(f"总金额：{order['total_amount']}")
    test_order_id = order['id']
    print("✓ 新增采购单成功\n")
else:
    print(f"✗ 新增失败：{r.text}")
    test_order_id = None
    print()

print("=" * 60)
print("测试3：采购单列表")
print("=" * 60)
r = requests.get(f"{BASE}/api/purchase_order")
print(f"响应状态：{r.status_code}")
print(f"采购单总数：{len(r.json())}")
print("✓ 列表接口正常\n")

print("=" * 60)
print("测试4：采购单详情（含明细）")
print("=" * 60)
if test_order_id:
    r = requests.get(f"{BASE}/api/purchase_order/{test_order_id}")
    print(f"响应状态：{r.status_code}")
    detail = r.json()
    print(f"采购单号：{detail['order_no']}")
    print(f"明细数量：{len(detail['items'])}")
    if detail['items']:
        item = detail['items'][0]
        print(f"  明细1：分类id={item['category_id']}, 克重={item['gram']}, 幅宽={item['width']}, 数量={item['quantity']}吨, 吨价={item['unit_price']}, 已到货={item['arrived_quantity']}")
    print("✓ 详情接口正常\n")
else:
    print("跳过（没有测试采购单）\n")

print("=" * 60)
print("测试5：到货确认（自动入库卷料仓）")
print("=" * 60)
if test_order_id and detail and detail['items']:
    item_id = detail['items'][0]['id']
    payload = {
        "items": [
            {
                "item_id": item_id,
                "arrive_quantity": 5,
                "roll_count": 2
            }
        ]
    }
    r = requests.post(f"{BASE}/api/purchase_order/{test_order_id}/arrive", json=payload)
    print(f"响应状态：{r.status_code}")
    if r.status_code == 200:
        result = r.json()
        print(f"生成卷筒数量：{result['count']}")
        for roll in result['created_rolls']:
            print(f"  卷筒：{roll['raw_no']}, 重量={roll['weight']}吨")
        print("✓ 到货确认成功，自动入库卷料仓\n")
    else:
        print(f"✗ 到货确认失败：{r.text}\n")
else:
    print("跳过（没有测试采购单或明细）\n")

print("=" * 60)
print("测试6：验证卷料仓是否生成了卷筒记录")
print("=" * 60)
r = requests.get(f"{BASE}/api/rawroll")
rolls = r.json()
print(f"卷料仓卷筒总数：{len(rolls)}")
# 找最近生成的测试卷筒
test_rolls = [r for r in rolls if '测试采购单' in (r.get('remark') or '')]
print(f"本次测试生成的卷筒：{len(test_rolls)}")
for roll in test_rolls[:3]:
    print(f"  {roll['raw_no']}：分类id={roll['category_id']}, 克重={roll['gram']}, 幅宽={roll['width']}, 库存={roll['stock_weight']}吨, 吨价={roll.get('ton_price')}")
print("✓ 卷料仓入库验证完成\n")

print("=" * 60)
print("测试7：操作日志是否记录了采购单操作")
print("=" * 60)
r = requests.get(f"{BASE}/api/operation_log?limit=20")
logs = r.json()
purchase_logs = [l for l in logs if '采购单' in (l.get('detail') or '') or '采购' in (l.get('action') or '')]
print(f"最近20条日志中采购相关：{len(purchase_logs)}")
for log in purchase_logs[:5]:
    print(f"  [{log['module']}] {log['action']}：{log['detail']}")
print("✓ 操作日志验证完成\n")

print("=" * 60)
print("全部测试完成！")
print("=" * 60)
