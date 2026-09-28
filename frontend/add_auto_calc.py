with open('src/ProduceOrder.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 加自动计算用量的函数（在 handleSave 前面）
content = content.replace(
    '  const handleSave = async () => {',
    '''  // 自动计算每层用量
  const autoCalcQuantity = () => {
    const values = form.getFieldsValue();
    const qty = Number(values.quantity) || 0;
    const width = Number(values.spec_width) || 0;
    const length = Number(values.spec_length) || 0;
    const lossStr = values.loss_limit || '2%';
    const lossRate = parseFloat(lossStr) / 100 || 0.02;

    if (!qty || !width || !length) {
      message.warning('请先填写数量、规格宽、规格长');
      return;
    }

    const newItems = items.map(item => {
      const roll = rollList.find(r => r.id === item.roll_id);
      if (!roll) return item;
      const gram = Number(roll.gram) || 0;
      // 用量(吨) = 张数 × 宽(m) × 长(m) × 克重(g/m²) / 1,000,000 × (1+损耗率)
      const usage = qty * (width / 1000) * (length / 1000) * gram / 1000000 * (1 + lossRate);
      const usageFixed = Math.round(usage * 1000) / 1000;
      return {
        ...item,
        quantity: usageFixed,
        amount: usageFixed * (item.unit_price || 0)
      };
    });

    setItems(newItems);
    message.success('已自动计算每层用量');
  };

  const handleSave = async () => {'''
)

# 2. 在配料明细标题旁边加按钮
content = content.replace(
    '''          <div style={{ marginBottom: 8, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <b>配料明细（共 {items.length} 层）</b>
            <Button size="small" type="dashed" onClick={addLayer}>+ 加一层</Button>
          </div>''',
    '''          <div style={{ marginBottom: 8, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <b>配料明细（共 {items.length} 层）</b>
            <Space>
              <Button size="small" type="primary" onClick={autoCalcQuantity}>自动计算用量</Button>
              <Button size="small" type="dashed" onClick={addLayer}>+ 加一层</Button>
            </Space>
          </div>'''
)

# 3. 加个提示说明
content = content.replace(
    '''          <div style={{ border: '1px solid #d9d9d9', borderRadius: 4, padding: 8, marginBottom: 16, maxHeight: 300, overflowY: 'auto' }}>''',
    '''          <div style={{ marginBottom: 8, fontSize: 12, color: '#999' }}>
            提示：填好数量、规格宽长、损耗上限，选好每层原料后，点"自动计算用量"自动算出每层卷筒用量（含损耗）
          </div>
          <div style={{ border: '1px solid #d9d9d9', borderRadius: 4, padding: 8, marginBottom: 16, maxHeight: 300, overflowY: 'auto' }}>'''
)

with open('src/ProduceOrder.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('自动计算用量功能加完成')
