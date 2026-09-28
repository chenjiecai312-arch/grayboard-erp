import sqlite3
conn = sqlite3.connect('grayboard.db')
c = conn.cursor()

try:
    c.execute('ALTER TABLE produce_order ADD COLUMN sales_order_id INTEGER')
    print('加 sales_order_id 字段成功')
except Exception as e:
    print(f'sales_order_id 可能已存在: {e}')

conn.commit()
conn.close()
