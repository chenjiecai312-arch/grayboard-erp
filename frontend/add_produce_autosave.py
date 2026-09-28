with open('src/ProduceOrder.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. import 加 useRef
content = content.replace(
    "import React, { useState, useEffect, useMemo } from 'react';",
    "import React, { useState, useEffect, useMemo, useRef } from 'react';"
)

# 2. 加自动保存相关 state（在 salesDetailModalOpen 后面）
content = content.replace(
    '''  const [salesDetailModalOpen, setSalesDetailModalOpen] = useState(false);
  const [currentSalesOrder, setCurrentSalesOrder] = useState(null);''',
    '''  const [salesDetailModalOpen, setSalesDetailModalOpen] = useState(false);
  const [currentSalesOrder, setCurrentSalesOrder] = useState(null);

  // 自动保存相关
  const [saveStatus, setSaveStatus] = useState('idle');
  const [lastSavedTime, setLastSavedTime] = useState(null);
  const autoSaveTimer = useRef(null);
  const isInitialLoad = useRef(true);

  const triggerAutoSave = () => {
    if (isInitialLoad.current) return;
    if (autoSaveTimer.current) clearTimeout(autoSaveTimer.current);
    setSaveStatus('saving');
    autoSaveTimer.current = setTimeout(() => { doAutoSave(); }, 800);
  };

  const doAutoSave = async () => {
    try {
      const values = form.getFieldsValue();
      const customer = customerList.find(c => c.id === values.customer_id);
      const payload = {
        ...values,
        craft: form.getFieldValue('craft') || '',
        produce_date: values.produce_date ? (values.produce_date.format ? values.produce_date.format('YYYY-MM-DD') : values.produce_date) : null,
        customer_name: customer?.customer_name || values.customer_name,
        layers: items.length,
        items: items
      };
      if (editingId) {
        await api.put(`/api/produce_order/${editingId}`, payload);
      } else {
        const res = await api.post('/api/produce_order', payload);
        setEditingId(res.data.id);
      }
      setSaveStatus('saved');
      setLastSavedTime(new Date().toLocaleTimeString('zh-CN', {hour:'2-digit', minute:'2-digit', second:'2-digit'}));
      loadData();
    } catch (e) {
      setSaveStatus('error');
      console.error('自动保存失败:', e);
    }
  };

  const closeProduceModal = () => {
    if (autoSaveTimer.current) clearTimeout(autoSaveTimer.current);
    setModalOpen(false);
    setSaveStatus('idle');
    setLastSavedTime(null);
    isInitialLoad.current = true;
  };'''
)

# 3. openAdd 里重置状态
content = content.replace(
    '''    setItems([{ layer_no: 1, roll_id: null, roll_name: '', quantity: 0, unit_price: 0, amount: 0, remark: '' }]);
    setModalOpen(true);
  };

  const openEdit = (record) => {''',
    '''    setItems([{ layer_no: 1, roll_id: null, roll_name: '', quantity: 0, unit_price: 0, amount: 0, remark: '' }]);
    setSaveStatus('idle');
    setLastSavedTime(null);
    setModalOpen(true);
    setTimeout(() => { isInitialLoad.current = false; }, 500);
  };

  const openEdit = (record) => {'''
)

# 4. openEdit 里重置状态
content = content.replace(
    '''    setItems(record.items.map(i => ({ ...i })));
    setModalOpen(true);
  };''',
    '''    setItems(record.items.map(i => ({ ...i })));
    setSaveStatus('idle');
    setLastSavedTime(null);
    setModalOpen(true);
    setTimeout(() => { isInitialLoad.current = false; }, 500);
  };'''
)

# 5. 所有 setItems 后触发自动保存（找几个关键的 setItems）
# updateItemRow
content = content.replace(
    '''    setItems(newItems);
  };

  // 删除层''',
    '''    setItems(newItems);
    triggerAutoSave();
  };

  // 删除层'''
)

# addLayer
content = content.replace(
    '''    setItems(newItems);
  };

  // 自动计算用量''',
    '''    setItems(newItems);
    triggerAutoSave();
  };

  // 自动计算用量'''
)

# removeLayer
content = content.replace(
    '''    setItems(newItems);
  };

  const handleSave''',
    '''    setItems(newItems);
    triggerAutoSave();
  };

  const handleSave'''
)

# 6. handleSave 成功后重置状态
content = content.replace(
    '''      setModalOpen(false);
      loadData();
    } catch (e) {
      message.error(e.response?.data?.detail || '保存失败');
    }
  };

  const handlePick''',
    '''      if (autoSaveTimer.current) clearTimeout(autoSaveTimer.current);
      setSaveStatus('saved');
      setLastSavedTime(new Date().toLocaleTimeString('zh-CN', {hour:'2-digit', minute:'2-digit', second:'2-digit'}));
      setModalOpen(false);
      loadData();
    } catch (e) {
      message.error(e.response?.data?.detail || '保存失败');
    }
  };

  const handlePick'''
)

# 7. 弹窗标题加保存状态，onCancel 改用 closeProduceModal，Form 加 onValuesChange
content = content.replace(
    '''      <Modal
        open={modalOpen}
        title={editingId ? "编辑生产工单" : "新增生产工单"}
        onCancel={() => setModalOpen(false)}
        footer={null}
        width={1200}
      >
        <Form form={form} layout="vertical">''',
    '''      <Modal
        open={modalOpen}
        title={
          <div style={{display:'flex', alignItems:'center', gap:12}}>
            <span>{editingId ? "编辑生产工单" : "新增生产工单"}</span>
            {saveStatus === 'saving' && <span style={{fontSize:13, color:'#fa8c16'}}>正在保存...</span>}
            {saveStatus === 'saved' && <span style={{fontSize:13, color:'#52c41a'}}>✓ 已保存 {lastSavedTime || ''}</span>}
            {saveStatus === 'error' && <span style={{fontSize:13, color:'#ff4d4f'}}>保存失败，请检查必填项</span>}
          </div>
        }
        onCancel={closeProduceModal}
        footer={null}
        width={1200}
      >
        <Form form={form} layout="vertical" onValuesChange={() => triggerAutoSave()}>'''
)

with open('src/ProduceOrder.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('生产工单自动保存功能加完成')
