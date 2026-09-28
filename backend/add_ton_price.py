import sqlite3
conn = sqlite3.connect('grayboard.db')
c = conn.cursor()
# 给 raw_roll 表加 ton_price 字段
try:
    c.execute('ALTER TABLE raw_roll ADD COLUMN ton_price FLOAT DEFAULT 0')
    print('raw_roll 表加 ton_price 字段成功')
except Exception as e:
    print(f'字段可能已存在: {e}')
conn.commit()
conn.close()
