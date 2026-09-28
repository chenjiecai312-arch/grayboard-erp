import sqlite3
conn = sqlite3.connect('grayboard.db')
c = conn.cursor()

print("pending_out 列:", [d[1] for d in c.execute("PRAGMA table_info(pending_out)").fetchall()])
print("\n===== pending_out 待出库 =====")
for r in c.execute("SELECT * FROM pending_out ORDER BY id").fetchall():
    print("  ", r)

print("\n===== purchase_order_item (PO001=order4) =====")
for r in c.execute("SELECT id,order_id,category_id,quantity,arrived_quantity FROM purchase_order_item WHERE order_id=4").fetchall():
    print("  ", r)

print("\n===== sales_order_item 各订单 =====")
for r in c.execute("SELECT id,order_id,product_id,product_name,quantity FROM sales_order_item ORDER BY id").fetchall():
    print("  ", r)

print("\n===== product 成品 =====")
pncols = [d[1] for d in c.execute("PRAGMA table_info(product)").fetchall()]
print("product 列:", pncols)
for r in c.execute("SELECT * FROM product ORDER BY id").fetchall():
    print("  ", r)

print("\n===== operation_log 计数 =====")
print("共", c.execute("SELECT COUNT(*) FROM operation_log").fetchone()[0], "条")
conn.close()
