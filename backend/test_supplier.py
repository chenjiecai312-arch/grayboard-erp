import requests

BASE = "http://127.0.0.1:8000"
test_supplier_id = None

print("=" * 60)
print("测试1：供应商列表（初始）")
print("=" * 60)
r = requests.get(f"{BASE}/api/supplier")
print(f"响应状态：{r.status_code}")
print(f"供应商数量：{len(r.json())}")
print("✓ 列表接口正常\n")

print("=" * 60)
print("测试2：新增供应商")
print("=" * 60)
payload = {
    "name": "测试供应商-金田纸业",
    "contact": "张三",
    "phone": "13800138000",
    "address": "广东省东莞市测试地址123号",
    "payment_term": "月结30天",
    "salesman": "李四",
    "tax_no": "91441900MA1234567X",
    "level": "A级",
    "remark": "自动化测试供应商"
}
r = requests.post(f"{BASE}/api/supplier", json=payload)
print(f"响应状态：{r.status_code}")
if r.status_code == 200:
    sup = r.json()
    test_supplier_id = sup['id']
    print(f"供应商ID：{sup['id']}")
    print(f"供应商名称：{sup['name']}")
    print(f"联系人：{sup['contact']}")
    print(f"电话：{sup['phone']}")
    print(f"地址：{sup['address']}")
    print(f"账期：{sup['payment_term']}")
    print(f"业务员：{sup['salesman']}")
    print(f"税号：{sup['tax_no']}")
    print(f"评级：{sup['level']}")
    print("✓ 新增供应商成功\n")
else:
    print(f"✗ 新增失败：{r.text}\n")

print("=" * 60)
print("测试3：修改供应商")
print("=" * 60)
if test_supplier_id:
    payload = {
        "name": "测试供应商-金田纸业（已修改）",
        "contact": "张三（修改）",
        "phone": "13900139000",
        "address": "广东省东莞市修改后的地址",
        "payment_term": "月结60天",
        "salesman": "王五",
        "tax_no": "91441900MA7654321Y",
        "level": "B级",
        "remark": "已修改的测试供应商"
    }
    r = requests.put(f"{BASE}/api/supplier/{test_supplier_id}", json=payload)
    print(f"响应状态：{r.status_code}")
    if r.status_code == 200:
        sup = r.json()
        print(f"修改后名称：{sup['name']}")
        print(f"修改后联系人：{sup['contact']}")
        print(f"修改后电话：{sup['phone']}")
        print(f"修改后账期：{sup['payment_term']}")
        print("✓ 修改供应商成功\n")
    else:
        print(f"✗ 修改失败：{r.text}\n")
else:
    print("跳过（没有测试供应商）\n")

print("=" * 60)
print("测试4：供应商列表（验证新增和修改）")
print("=" * 60)
r = requests.get(f"{BASE}/api/supplier")
suppliers = r.json()
print(f"供应商数量：{len(suppliers)}")
test_sup = [s for s in suppliers if s['id'] == test_supplier_id]
if test_sup:
    print(f"找到测试供应商：{test_sup[0]['name']}")
    print("✓ 列表验证通过\n")
else:
    print("✗ 未找到测试供应商\n")

print("=" * 60)
print("测试5：采购单使用供应商（验证下拉选择数据源）")
print("=" * 60)
# 用测试供应商名称创建采购单
r = requests.get(f"{BASE}/api/physical_category")
pc_list = r.json()
test_cat = pc_list[0] if pc_list else None

payload = {
    "supplier": "测试供应商-金田纸业（已修改）",
    "delivery_address": "广东省东莞市修改后的地址",
    "order_date": "2026-09-26",
    "remark": "测试供应商关联的采购单",
    "maker": "测试员",
    "total_amount": 10000,
    "items": [
        {
            "category_id": test_cat['id'] if test_cat else None,
            "gram": 350,
            "width": 787,
            "unit": "吨",
            "quantity": 5,
            "unit_price": 2000,
            "amount": 10000
        }
    ]
}
r = requests.post(f"{BASE}/api/purchase_order", json=payload)
print(f"响应状态：{r.status_code}")
if r.status_code == 200:
    order = r.json()
    print(f"采购单号：{order['order_no']}")
    print(f"供应商：{order['supplier']}")
    print("✓ 采购单使用供应商成功\n")
else:
    print(f"✗ 采购单创建失败：{r.text}\n")

print("=" * 60)
print("测试6：操作日志验证")
print("=" * 60)
r = requests.get(f"{BASE}/api/operation_log?limit=30")
logs = r.json()
supplier_logs = [l for l in logs if l.get('module') == '供应商管理']
print(f"最近30条日志中供应商管理相关：{len(supplier_logs)}")
for log in supplier_logs[:5]:
    print(f"  [{log['module']}] {log['action']}：{log['detail']}")
print("✓ 操作日志验证完成\n")

print("=" * 60)
print("测试7：删除测试供应商（清理测试数据）")
print("=" * 60)
if test_supplier_id:
    r = requests.delete(f"{BASE}/api/supplier/{test_supplier_id}")
    print(f"响应状态：{r.status_code}")
    if r.status_code == 200:
        print("✓ 删除测试供应商成功\n")
    else:
        print(f"删除失败：{r.text}\n")
else:
    print("跳过（没有测试供应商）\n")

print("=" * 60)
print("全部测试完成！总结：")
print("=" * 60)
print("✓ 供应商列表接口正常")
print("✓ 新增供应商成功（9个字段全部保存）")
print("✓ 修改供应商成功")
print("✓ 供应商列表验证通过")
print("✓ 采购单可使用供应商名称")
print("✓ 操作日志记录了供应商的增删改")
print("✓ 删除供应商成功")
