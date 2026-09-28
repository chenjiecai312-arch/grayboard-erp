import sqlite3
conn = sqlite3.connect('grayboard.db')
c = conn.cursor()

# 1. 清空财务4表（全新表，全为测试数据）
for t in ['finance_transaction','finance_receivable','finance_payable','finance_account']:
    n = c.execute(f"DELETE FROM {t}").rowcount
    print(f"清空 {t}: {n} 条")

# 2. 删除今天财务测试销售单 id7-12 及明细
n1 = c.execute("DELETE FROM sales_order_item WHERE order_id IN (7,8,9,10,11,12)").rowcount
n2 = c.execute("DELETE FROM sales_order WHERE id IN (7,8,9,10,11,12)").rowcount
print(f"删除测试销售单 {n2} 个，明细 {n1} 条")

# 3. 删除全部采购测试单 id4-12 及明细
n3 = c.execute("DELETE FROM purchase_order_item WHERE order_id IN (4,5,6,7,8,9,10,11,12)").rowcount
n4 = c.execute("DELETE FROM purchase_order WHERE id IN (4,5,6,7,8,9,10,11,12)").rowcount
print(f"删除测试采购单 {n4} 个，明细 {n3} 条")

# 4. 删除测试卷筒 id19-42（TEST-ROLL + 112345651 + E2E）
n5 = c.execute("DELETE FROM raw_roll WHERE id BETWEEN 19 AND 42").rowcount
print(f"删除测试卷筒 {n5} 个")

conn.commit()

print("\n===== 清理后核对 =====")
for t in ['finance_account','finance_receivable','finance_payable','finance_transaction']:
    print(f"  {t}:", c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0], "条")
print("  sales_order:", c.execute("SELECT COUNT(*) FROM sales_order").fetchone()[0], "个")
for r in c.execute("SELECT id,order_no,customer_name,status FROM sales_order").fetchall():
    print("      保留:", r)
print("  purchase_order:", c.execute("SELECT COUNT(*) FROM purchase_order").fetchone()[0], "个")
print("  raw_roll:", c.execute("SELECT COUNT(*) FROM raw_roll").fetchone()[0], "个")
conn.close()
