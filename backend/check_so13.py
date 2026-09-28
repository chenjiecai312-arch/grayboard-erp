import sqlite3
conn = sqlite3.connect('grayboard.db')
c = conn.cursor()
print("sales_order id13:")
print(" ", c.execute("SELECT * FROM sales_order WHERE id=13").fetchone())
print("明细:")
for r in c.execute("SELECT * FROM sales_order_item WHERE order_id=13").fetchall():
    print(" ", r)
print("明细数:", c.execute("SELECT COUNT(*) FROM sales_order_item WHERE order_id=13").fetchone()[0])
conn.close()
