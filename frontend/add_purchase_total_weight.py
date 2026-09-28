with open('src/PurchaseOrder.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 在合计金额旁边加合计吨重
content = content.replace(
    '''          <div style={{ textAlign: 'right', marginBottom: 16 }}>
            <Button onClick={addItemRow} style={{ marginRight: 16 }}>+ 添加一行</Button>
            <span style={{ fontWeight: 600, fontSize: 16 }}>合计金额：¥{totalAmount.toFixed(2)}</span>
          </div>''',
    '''          <div style={{ textAlign: 'right', marginBottom: 16 }}>
            <Button onClick={addItemRow} style={{ marginRight: 16 }}>+ 添加一行</Button>
            <span style={{ fontWeight: 600, fontSize: 15, marginRight: 24 }}>合计吨重：{items.reduce((sum, i) => sum + Number(i.quantity || 0), 0).toFixed(3)} 吨</span>
            <span style={{ fontWeight: 600, fontSize: 15 }}>合计金额：¥{totalAmount.toFixed(2)}</span>
          </div>'''
)

with open('src/PurchaseOrder.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('采购单加合计吨重完成')
