import sqlite3
conn = sqlite3.connect('grayboard.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS supplier (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name VARCHAR(200) NOT NULL,
  contact VARCHAR(100),
  phone VARCHAR(50),
  address VARCHAR(500),
  payment_term VARCHAR(100),
  salesman VARCHAR(50),
  tax_no VARCHAR(100),
  level VARCHAR(50),
  remark TEXT,
  created_at VARCHAR(30)
)
''')
print('supplier 表创建成功')

conn.commit()
conn.close()
