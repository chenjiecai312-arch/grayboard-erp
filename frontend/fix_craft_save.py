with open('src/ProduceOrder.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 在 handleSave 里手动加 craft 字段
content = content.replace(
    '''      const payload = {
        ...values,
        customer_name: customer?.customer_name || values.customer_name,
        layers: items.length,
        items: items
      };''',
    '''      const payload = {
        ...values,
        craft: form.getFieldValue('craft') || '',
        customer_name: customer?.customer_name || values.customer_name,
        layers: items.length,
        items: items
      };'''
)

with open('src/ProduceOrder.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('前端保存时加craft字段完成')
