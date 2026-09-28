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

print("=" * 65)
print("测试：手动录入每支卷筒明细到货（编号不同、重量不同）")
print("=" * 65)

pc_list = api_get('/api/physical_category')
leaf_cats = [c for c in pc_list if c['parent_id'] is not None and not any(x['parent_id'] == c['id'] for x in pc_list)]
cat_id = leaf_cats[0]['id'] if leaf_cats else None
print(f"使用分类id：{cat_id}")

payload = {
    "supplier": "手动明细测试供应商",
    "delivery_address": "测试地址",
    "order_date": "2026-09-26",
    "maker": "测试员",
    "total_amount": 20000,
    "items": [
        {"category_id": cat_id, "gram": 350, "width": 787, "unit": "吨", "quantity": 10, "unit_price": 2000, "amount": 20000}
    ]
}
order = api_post('/api/purchase_order', payload)
# 创建接口可能不返回items，重新查询详情
order_detail = api_get(f"/api/purchase_order/{order['id']}")
order = order_detail
item_id = order['items'][0]['id']
print(f"采购单创建成功：{order['order_no']} (id={order['id']})")

manual_rolls = [
    {"roll_no": "TEST-ROLL-001", "weight": 3.521, "remark": "第一支"},
    {"roll_no": "TEST-ROLL-002", "weight": 3.487, "remark": "第二支"},
    {"roll_no": "TEST-ROLL-003", "weight": 2.990, "remark": "第三支"}
]
total_weight = sum(r['weight'] for r in manual_rolls)
print(f"\n手动录入 {len(manual_rolls)} 支卷筒：")
for r in manual_rolls:
    print(f"  编号 {r['roll_no']}：{r['weight']} 吨")
print(f"  合计重量：{total_weight:.3f} 吨")

arrive_payload = {
    "items": [
        {"item_id": item_id, "arrive_quantity": total_weight, "roll_count": 3, "rolls": manual_rolls}
    ]
}
result = api_post(f"/api/purchase_order/{order['id']}/arrive", arrive_payload)

print(f"\n到货接口返回：生成 {result['count']} 支卷筒")
for r in result['created_rolls']:
    print(f"  id={r['id']}，编号={r['raw_no']}，重量={r['weight']} 吨")

print("\n" + "=" * 65)
print("验证结果")
print("=" * 65)
rolls = result['created_rolls']
success = True

expected_nos = ["TEST-ROLL-001", "TEST-ROLL-002", "TEST-ROLL-003"]
actual_nos = [r['raw_no'] for r in rolls]
if actual_nos == expected_nos:
    print("✓ 编号正确：使用了手动输入的编号（不是系统自动生成）")
else:
    print(f"✗ 编号错误：期望{expected_nos}，实际{actual_nos}")
    success = False

expected_weights = [3.521, 3.487, 2.990]
actual_weights = [r['weight'] for r in rolls]
if actual_weights == expected_weights:
    print("✓ 重量正确：每支使用了手动输入的不同重量（不是平均分配）")
else:
    print(f"✗ 重量错误：期望{expected_weights}，实际{actual_weights}")
    success = False

actual_total = sum(actual_weights)
if abs(actual_total - total_weight) < 0.001:
    print(f"✓ 总重量正确：{actual_total:.3f} 吨")
else:
    print(f"✗ 总重量错误：期望{total_weight}，实际{actual_total}")
    success = False

all_rolls = api_get('/api/rawroll')
test_rolls_in_db = [r for r in all_rolls if r['raw_no'] in expected_nos]
if len(test_rolls_in_db) == 3:
    print("✓ 3支卷筒已成功入库卷料仓，可查询")
    for r in test_rolls_in_db:
        if r['stock_weight'] != r['weight']:
            print(f"  ✗ {r['raw_no']} 库存重量异常")
            success = False
else:
    print(f"✗ 卷料仓只找到 {len(test_rolls_in_db)}/3 支测试卷筒")
    success = False

updated_order = api_get(f"/api/purchase_order/{order['id']}")
print(f"✓ 采购单状态：{updated_order['status']}（采购10吨，到货{total_weight:.3f}吨）")

print("\n" + "=" * 65)
if success:
    print("✅ 全部测试通过！手动录入到货明细功能正常")
else:
    print("❌ 存在失败项，需要修复")
print("=" * 65)
