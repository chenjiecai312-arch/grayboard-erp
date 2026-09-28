with open('src/PurchaseOrder.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 把单位从固定文本改成可编辑输入框
content = content.replace(
    '''                <div style={{ width: 60, padding: '4px', textAlign: 'center' }}>{item.unit}</div>''',
    '''                <div style={{ width: 60, padding: '4px' }}>
                  <Input value={item.unit} onChange={e => updateItemRow(idx, 'unit', e.target.value)} style={{ width: '100%' }} placeholder="单位" />
                </div>'''
)

with open('src/PurchaseOrder.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('采购单单位改可自由编辑完成')
