with open('src/SalesOrder.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 加状态选项
old = '''          <Select.Option value="delivery_date">送货日期</Select.Option>
        </Select>'''
new = '''          <Select.Option value="delivery_date">送货日期</Select.Option>
          <Select.Option value="status">订单状态</Select.Option>
        </Select>'''
content = content.replace(old, new)

with open('src/SalesOrder.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('状态筛选加完成')
