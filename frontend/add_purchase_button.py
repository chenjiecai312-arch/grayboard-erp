with open('src/RollWarehouse.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 函数签名加 props
content = content.replace(
    'export default function RollWarehouse() {',
    'export default function RollWarehouse({ onNavigate }) {'
)

# 2. 按钮行加采购单按钮
content = content.replace(
    '''        <Button type="primary" onClick={() => setModalOpen(true)}>新增卷筒</Button>
        <Button onClick={() => setPnModal(true)}>新建品名</Button>''',
    '''        <Button type="primary" onClick={() => setModalOpen(true)}>新增卷筒</Button>
        <Button onClick={() => setPnModal(true)}>新建品名</Button>
        <Button onClick={() => onNavigate && onNavigate('purchase')}>采购单列表</Button>'''
)

with open('src/RollWarehouse.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('RollWarehouse 采购单按钮加完成')
