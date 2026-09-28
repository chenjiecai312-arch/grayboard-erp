import sqlite3
conn = sqlite3.connect('grayboard.db')
c = conn.cursor()

# 加排单日期字段
try:
    c.execute('ALTER TABLE produce_order ADD COLUMN schedule_date VARCHAR(20)')
    print('加 schedule_date 字段成功')
except Exception as e:
    print(f'schedule_date 可能已存在: {e}')

conn.commit()
conn.close()
