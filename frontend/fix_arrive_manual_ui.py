with open('src/PurchaseOrder.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# ========== 1. 修改 openArrive 初始化，加 rolls 和 showRolls ==========
content = content.replace(
    '''      setArriveItems(res.data.items.map(i => ({
        ...i,
        checked: false,
        arrive_quantity: 0,
        roll_count: 1
      })));''',
    '''      setArriveItems(res.data.items.map(i => ({
        ...i,
        checked: false,
        arrive_quantity: 0,
        roll_count: 1,
        rolls: [],
        showRolls: false
      })));'''
)

# ========== 2. 修改 updateArriveItem，勾选时自动展开明细并加一行 ==========
content = content.replace(
    '''  // 更新到货明细
  const updateArriveItem = (idx, field, value) => {
    const newItems = [...arriveItems];
    newItems[idx][field] = value;
    setArriveItems(newItems);
  };''',
    '''  // 更新到货明细
  const updateArriveItem = (idx, field, value) => {
    const newItems = [...arriveItems];
    newItems[idx][field] = value;
    // 勾选时自动展开明细面板，并默认添加1支空行
    if (field === 'checked' && value === true) {
      newItems[idx].showRolls = true;
      if (newItems[idx].rolls.length === 0) {
        newItems[idx].rolls = [{ roll_no: '', weight: null, remark: '' }];
      }
    }
    // 取消勾选时清空明细、折叠
    if (field === 'checked' && value === false) {
      newItems[idx].showRolls = false;
      newItems[idx].rolls = [];
      newItems[idx].arrive_quantity = 0;
      newItems[idx].roll_count = 1;
    }
    setArriveItems(newItems);
  };

  // 展开/折叠卷筒明细面板
  const toggleRollsPanel = (idx) => {
    const newItems = [...arriveItems];
    newItems[idx].showRolls = !newItems[idx].showRolls;
    setArriveItems(newItems);
  };

  // 添加一支卷筒行
  const addRollRow = (itemIdx) => {
    const newItems = [...arriveItems];
    newItems[itemIdx].rolls = [...newItems[itemIdx].rolls, { roll_no: '', weight: null, remark: '' }];
    newItems[itemIdx].roll_count = newItems[itemIdx].rolls.length;
    setArriveItems(newItems);
  };

  // 删除一支卷筒行
  const removeRollRow = (itemIdx, rollIdx) => {
    const newItems = [...arriveItems];
    newItems[itemIdx].rolls = newItems[itemIdx].rolls.filter((_, i) => i !== rollIdx);
    newItems[itemIdx].roll_count = newItems[itemIdx].rolls.length;
    // 重新汇总重量
    const totalW = newItems[itemIdx].rolls.reduce((s, r) => s + (Number(r.weight) || 0), 0);
    newItems[itemIdx].arrive_quantity = Number(totalW.toFixed(6));
    setArriveItems(newItems);
  };

  // 更新某支卷筒字段，自动汇总总重量
  const updateRollRow = (itemIdx, rollIdx, field, value) => {
    const newItems = [...arriveItems];
    newItems[itemIdx].rolls[rollIdx][field] = value;
    // 自动汇总各支重量到本次到货(吨)
    const totalW = newItems[itemIdx].rolls.reduce((s, r) => s + (Number(r.weight) || 0), 0);
    newItems[itemIdx].arrive_quantity = Number(totalW.toFixed(6));
    newItems[itemIdx].roll_count = newItems[itemIdx].rolls.length;
    setArriveItems(newItems);
  };'''
)

# ========== 3. 修改 confirmArrive，传 rolls 明细 ==========
content = content.replace(
    '''      const payload = {
        items: checkedItems.map(i => ({
          item_id: i.id,
          arrive_quantity: Number(i.arrive_quantity),
          roll_count: Number(i.roll_count || 1)
        }))
      };''',
    '''      const payload = {
        items: checkedItems.map(i => {
          // 有手动录入的有效卷筒明细就传 rolls
          const validRolls = (i.rolls || []).filter(r => r.roll_no && r.weight && Number(r.weight) > 0)
            .map(r => ({ roll_no: r.roll_no, weight: Number(r.weight), remark: r.remark || null }));
          return {
            item_id: i.id,
            arrive_quantity: Number(i.arrive_quantity),
            roll_count: Number(i.roll_count || 1),
            rolls: validRolls.length > 0 ? validRolls : null
          };
        })
      };'''
)

# ========== 4. 重写弹窗明细列表 UI，加展开明细面板 ==========
old_list_ui = '''              {arriveItems.map((item, idx) => (
                <div key={idx} style={{ display: 'flex', borderBottom: idx < arriveItems.length - 1 ? '1px solid #f0f0f0' : 'none', alignItems: 'center' }}>
                  <div style={{ width: 40, padding: '4px', textAlign: 'center' }}>
                    <input type="checkbox" checked={item.checked} onChange={e => updateArriveItem(idx, 'checked', e.target.checked)} />
                  </div>
                  <div style={{ flex: 1.5, padding: '4px' }}>
                    {item.category_id ? getCategoryPath(item.category_id) : <span style={{color:'#999'}}>未选择分类</span>}
                  </div>
                  <div style={{ width: 70, padding: '4px' }}>{item.gram}</div>
                  <div style={{ width: 70, padding: '4px' }}>{item.width}</div>
                  <div style={{ width: 90, padding: '4px' }}>{item.quantity} 吨</div>
                  <div style={{ width: 90, padding: '4px', color: item.arrived_quantity > 0 ? '#52c41a' : '#999' }}>{item.arrived_quantity || 0} 吨</div>
                  <div style={{ width: 100, padding: '4px' }}>
                    <InputNumber
                      value={item.arrive_quantity}
                      onChange={v => updateArriveItem(idx, 'arrive_quantity', v)}
                      style={{ width: '100%' }}
                      disabled={!item.checked}
                      step="0.001"
                      min="0"
                    />
                  </div>
                  <div style={{ width: 80, padding: '4px' }}>
                    <InputNumber
                      value={item.roll_count}
                      onChange={v => updateArriveItem(idx, 'roll_count', v)}
                      style={{ width: '100%' }}
                      disabled={!item.checked}
                      min="1"
                    />
                  </div>
                </div>
              ))}'''

new_list_ui = '''              {arriveItems.map((item, idx) => (
                <div key={idx}>
                  <div style={{ display: 'flex', borderBottom: item.showRolls ? '1px solid #e8e8e8' : (idx < arriveItems.length - 1 ? '1px solid #f0f0f0' : 'none'), alignItems: 'center' }}>
                    <div style={{ width: 40, padding: '4px', textAlign: 'center' }}>
                      <input type="checkbox" checked={item.checked} onChange={e => updateArriveItem(idx, 'checked', e.target.checked)} />
                    </div>
                    <div style={{ flex: 1.5, padding: '4px' }}>
                      {item.category_id ? getCategoryPath(item.category_id) : <span style={{color:'#999'}}>未选择分类</span>}
                    </div>
                    <div style={{ width: 70, padding: '4px' }}>{item.gram}</div>
                    <div style={{ width: 70, padding: '4px' }}>{item.width}</div>
                    <div style={{ width: 90, padding: '4px' }}>{item.quantity} 吨</div>
                    <div style={{ width: 90, padding: '4px', color: item.arrived_quantity > 0 ? '#52c41a' : '#999' }}>{item.arrived_quantity || 0} 吨</div>
                    <div style={{ width: 100, padding: '4px' }}>
                      <InputNumber
                        value={item.arrive_quantity}
                        onChange={v => updateArriveItem(idx, 'arrive_quantity', v)}
                        style={{ width: '100%' }}
                        disabled={!item.checked}
                        step="0.001"
                        min="0"
                      />
                    </div>
                    <div style={{ width: 90, padding: '4px' }}>
                      <Button size="small" type="link" disabled={!item.checked} onClick={() => toggleRollsPanel(idx)} style={{padding:0}}>
                        {item.rolls.length}支 {item.showRolls ? '▲' : '▼'}
                      </Button>
                    </div>
                  </div>

                  {/* 展开的卷筒明细录入区域 */}
                  {item.checked && item.showRolls && (
                    <div style={{ background: '#fafcff', padding: '10px 16px', borderBottom: idx < arriveItems.length - 1 ? '1px solid #f0f0f0' : 'none' }}>
                      <div style={{ display: 'flex', fontSize: 12, color: '#666', fontWeight: 600, marginBottom: 6 }}>
                        <div style={{ width: 40 }}>序号</div>
                        <div style={{ flex: 1.5 }}>卷筒编号（手动输入）</div>
                        <div style={{ width: 130 }}>本支重量(吨)</div>
                        <div style={{ flex: 1.5 }}>备注</div>
                        <div style={{ width: 60 }}>操作</div>
                      </div>
                      {item.rolls.map((roll, rIdx) => (
                        <div key={rIdx} style={{ display: 'flex', alignItems: 'center', marginBottom: 6 }}>
                          <div style={{ width: 40, color: '#999' }}>{rIdx + 1}</div>
                          <div style={{ flex: 1.5, paddingRight: 8 }}>
                            <Input size="small" placeholder="如 JD20260926001" value={roll.roll_no}
                              onChange={e => updateRollRow(idx, rIdx, 'roll_no', e.target.value)} />
                          </div>
                          <div style={{ width: 130, paddingRight: 8 }}>
                            <InputNumber size="small" style={{ width: '100%' }} placeholder="0.000" step="0.001" min="0.001"
                              value={roll.weight} onChange={v => updateRollRow(idx, rIdx, 'weight', v)} />
                          </div>
                          <div style={{ flex: 1.5, paddingRight: 8 }}>
                            <Input size="small" placeholder="选填" value={roll.remark}
                              onChange={e => updateRollRow(idx, rIdx, 'remark', e.target.value)} />
                          </div>
                          <div style={{ width: 60 }}>
                            <Button size="small" danger type="link" style={{padding:0}} onClick={() => removeRollRow(idx, rIdx)}>删除</Button>
                          </div>
                        </div>
                      ))}
                      <div style={{ display: 'flex', alignItems: 'center', marginTop: 4 }}>
                        <Button size="small" onClick={() => addRollRow(idx)}>+ 添加一支</Button>
                        <span style={{ marginLeft: 16, fontSize: 13, color: '#1890ff', fontWeight: 600 }}>
                          合计：{item.rolls.length} 支，{Number(item.arrive_quantity || 0).toFixed(3)} 吨
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              ))}'''

content = content.replace(old_list_ui, new_list_ui)

# ========== 5. 更新提示文字 ==========
content = content.replace(
    '勾选实际到货的明细，输入到货数量和支数，确认后自动入库卷料仓生成卷筒',
    '勾选到货明细，逐支录入卷筒编号和实际重量（每支重量可不同），确认后自动入库卷料仓'
)

with open('src/PurchaseOrder.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('前端到货明细手动录入功能完成')
