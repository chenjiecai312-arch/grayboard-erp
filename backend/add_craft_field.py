import sqlite3
conn = sqlite3.connect('grayboard.db')
c = conn.cursor()

try:
    c.execute('ALTER TABLE produce_order ADD COLUMN craft VARCHAR(200)')
    print('加 craft 字段成功')
except Exception as e:
    print(f'craft 可能已存在: {e}')

conn.commit()
conn.close()
