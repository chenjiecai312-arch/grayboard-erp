import sqlite3
conn = sqlite3.connect('grayboard.db')
c = conn.cursor()

# 采购单主表
c.execute('''
CREATE TABLE IF NOT EXISTS purchase_order (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_no VARCHAR(50),
  supplier VARCHAR(200),
  delivery_address VARCHAR(200),
  order_date VARCHAR(20),
  remark TEXT,
  maker VARCHAR(50),
  checker VARCHAR(50),
  status VARCHAR(20) DEFAULT 'draft',
  total_amount FLOAT DEFAULT 0,
  created_at VARCHAR(30)
)
''')
print('purchase_order 表创建成功')

# 采购单明细表
c.execute('''
CREATE TABLE IF NOT EXISTS purchase_order_item (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id INTEGER,
  category_id INTEGER,
  gram FLOAT,
  width FLOAT,
  unit VARCHAR(20) DEFAULT '吨',
  quantity FLOAT DEFAULT 0,
  unit_price FLOAT DEFAULT 0,
  amount FLOAT DEFAULT 0,
  delivery_date VARCHAR(20),
  remark VARCHAR(200),
  arrived_quantity FLOAT DEFAULT 0,
  status VARCHAR(20) DEFAULT 'pending'
)
''')
print('purchase_order_item 表创建成功')

conn.commit()
conn.close()
print('采购单数据库表全部创建完成')
