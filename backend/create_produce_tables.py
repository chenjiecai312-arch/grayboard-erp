import sqlite3
conn = sqlite3.connect('grayboard.db')
c = conn.cursor()

# 生产工单主表
c.execute('''CREATE TABLE IF NOT EXISTS produce_order (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_no VARCHAR(50),
    customer_id INTEGER,
    customer_name VARCHAR(200),
    produce_date VARCHAR(20),
    layers INTEGER DEFAULT 1,
    total_amount FLOAT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'draft',
    remark TEXT,
    created_at VARCHAR(50)
)''')
print('produce_order 表创建成功')

# 生产工单明细表（每层领什么料）
c.execute('''CREATE TABLE IF NOT EXISTS produce_order_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    layer_no INTEGER,
    roll_id INTEGER,
    roll_name VARCHAR(200),
    quantity FLOAT DEFAULT 0,
    unit_price FLOAT DEFAULT 0,
    amount FLOAT DEFAULT 0,
    remark TEXT
)''')
print('produce_order_item 表创建成功')

# 领料/退料记录表
c.execute('''CREATE TABLE IF NOT EXISTS produce_material_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    item_id INTEGER,
    type VARCHAR(20),
    material_type VARCHAR(20),
    material_id INTEGER,
    quantity FLOAT,
    created_at VARCHAR(50)
)''')
print('produce_material_log 表创建成功')

conn.commit()
conn.close()
