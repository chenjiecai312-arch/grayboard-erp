import sqlite3
conn = sqlite3.connect('grayboard.db')
c = conn.cursor()

# 给 produce_order 表加字段
new_columns = [
    ('po_no', 'VARCHAR(50)'),
    ('product_name', 'VARCHAR(200)'),
    ('quantity', 'FLOAT DEFAULT 0'),
    ('spec_width', 'FLOAT DEFAULT 0'),
    ('spec_length', 'FLOAT DEFAULT 0'),
    ('total_gram', 'FLOAT DEFAULT 0'),
    ('customer_order_no', 'VARCHAR(100)'),
    ('thickness', 'VARCHAR(50)'),
    ('humidity', 'VARCHAR(50)'),
    ('brand', 'VARCHAR(100)'),
    ('size_error', 'VARCHAR(50)'),
    ('diagonal_error', 'VARCHAR(50)', '2MM内'),
    ('package_method', 'VARCHAR(100)'),
    ('loss_limit', 'VARCHAR(20)', '2%'),
    ('maker', 'VARCHAR(50)'),
    ('checker', 'VARCHAR(50)')
]

for col in new_columns:
    try:
        if len(col) == 3:
            c.execute(f'ALTER TABLE produce_order ADD COLUMN {col[0]} {col[1]} DEFAULT "{col[2]}"')
        else:
            c.execute(f'ALTER TABLE produce_order ADD COLUMN {col[0]} {col[1]}')
        print(f'加字段 {col[0]} 成功')
    except Exception as e:
        print(f'字段 {col[0]} 可能已存在: {e}')

conn.commit()
conn.close()
