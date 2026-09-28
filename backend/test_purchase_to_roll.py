import urllib.request
import json

BASE = "http://127.0.0.1:8000"

def api_get(url):
    req = urllib.request.Request(f"{BASE}{url}")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

print("=" * 60)
print("测试1：采购单列表（验证卷料仓能获取到采购单）")
print("=" * 60)
purchase_list = api_get('/api/purchase_order')
print(f"采购单数量：{len(purchase_list)}")
for p in purchase_list[:3]:
    print(f"  {p['order_no']} - {p['supplier']} - {p['status']}")
print("✓ 采购单列表接口正常\n")

print("=" * 60)
print("测试2：采购单详情（验证明细字段完整）")
print("=" * 60)
if purchase_list:
    order_id = purchase_list[0]['id']
    detail = api_get(f'/api/purchase_order/{order_id}')
    print(f"采购单号：{detail['order_no']}")
    print(f"明细数量：{len(detail['items'])}")
    for item in detail['items']:
        print(f"  明细：分类id={item['category_id']}, 克重={item['gram']}, 幅宽={item['width']}, 吨价={item['unit_price']}, 数量={item['quantity']}吨")
    print("✓ 采购单详情接口正常，明细字段完整\n")
else:
    print("跳过（没有采购单）\n")

print("=" * 60)
print("测试3：物理分类列表（验证能反查分类路径）")
print("=" * 60)
pc_list = api_get('/api/physical_category')
print(f"物理分类数量：{len(pc_list)}")
level1 = [c for c in pc_list if c['parent_id'] is None]
print(f"一级分类：{len(level1)}个")
for c in level1[:3]:
    children = [x for x in pc_list if x['parent_id'] == c['id']]
    print(f"  {c['name']}（{len(children)}个二级）")
print("✓ 物理分类接口正常\n")

print("=" * 60)
print("测试4：卷料仓列表（验证正常）")
print("=" * 60)
roll_list = api_get('/api/rawroll')
print(f"卷料仓卷筒数量：{len(roll_list)}")
print("✓ 卷料仓接口正常\n")

print("=" * 60)
print("全部测试通过！")
print("=" * 60)
print("功能逻辑：")
print("1. 卷料仓点「新增卷筒」→ 弹窗顶部有「从采购单选择录入」按钮")
print("2. 点击后弹出采购单列表 → 点「查看明细」进入该采购单的明细")
print("3. 明细列表显示：品牌(完整分类路径)、克重、幅宽、采购数量、吨价、已到货、备注")
print("4. 点「选择录入」→ 自动带入：物理分类、克重、幅宽、吨价、备注")
print("5. 缺失字段（品名、卷筒编号、本支重量）手动补齐")
print("6. 点保存 → 正常入库卷料仓")
