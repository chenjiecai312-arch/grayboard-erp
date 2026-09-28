import sqlite3
conn = sqlite3.connect('grayboard.db')
c = conn.cursor()

def dump(table, cols):
    print(f"\n===== {table} =====")
    rows = c.execute(f"SELECT {', '.join(cols)} FROM {table} ORDER BY id").fetchall()
    print(f"共 {len(rows)} 条")
    for r in rows:
        print("  ", r)

dump("finance_account", ["id","name","account_type","balance"])
dump("finance_receivable", ["id","order_no","customer_name","amount","received_amount","status","sales_order_id"])
dump("finance_payable", ["id","order_no","supplier_name","amount","paid_amount","status","purchase_order_id"])
print("\n===== finance_transaction 计数 =====")
print("共", c.execute("SELECT COUNT(*) FROM finance_transaction").fetchone()[0], "条")
for r in c.execute("SELECT id,direction,category,counterparty,amount,ref_no FROM finance_transaction ORDER BY id").fetchall():
    print("  ", r)

dump("sales_order", ["id","order_no","customer_name","total_amount","status"])
dump("purchase_order", ["id","order_no","supplier","total_amount","status"])
dump("raw_roll", ["id","raw_no","stock_weight"])
conn.close()
