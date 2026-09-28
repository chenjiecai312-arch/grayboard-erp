with open('src/PurchaseOrder.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. import 加 useRef
content = content.replace(
    "import React, { useState, useEffect } from 'react';",
    "import React, { useState, useEffect, useRef } from 'react';"
)

# 2. 加自动保存相关 state（在 arriveItems 后面）
content = content.replace(
    '''  const [arriveItems, setArriveItems] = useState([]);

  const loadData = async () => {''',
    '''  const [arriveItems, setArriveItems] = useState([]);

  // 自动保存相关
  const [saveStatus, setSaveStatus] = useState('idle'); // idle / saving / saved / error
  const [lastSavedTime, setLastSavedTime] = useState(null);
  const autoSaveTimer = useRef(null);
  const isInitialLoad = useRef(true);

  // 触发自动保存（防抖800ms）
  const triggerAutoSave = () => {
    if (isInitialLoad.current) return;
    if (autoSaveTimer.current) clearTimeout(autoSaveTimer.current);
    setSaveStatus('saving');
    autoSaveTimer.current = setTimeout(() => {
      doAutoSave();
    }, 800);
  };

  // 执行自动保存
  const doAutoSave = async () => {
    try {
      const values = form.getFieldsValue();
      const payload = {
        ...values,
        order_date: values.order_date ? (values.order_date.format ? values.order_date.format('YYYY-MM-DD') : values.order_date) : null,
        total_amount: items.reduce((sum, i) => sum + Number(i.amount || 0), 0),
        items: items.map(i => ({
          ...i,
          delivery_date: i.delivery_date || null
        }))
      };

      if (editId) {
        await api.put(`/api/purchase_order/${editId}`, payload);
      } else {
        const res = await api.post('/api/purchase_order', payload);
        setEditId(res.data.id);
      }
      setSaveStatus('saved');
      setLastSavedTime(new Date().toLocaleTimeString('zh-CN', {hour:'2-digit', minute:'2-digit', second:'2-digit'}));
      loadData();
    } catch (e) {
      setSaveStatus('error');
      console.error('自动保存失败:', e);
    }
  };

  // 关闭弹窗时清除定时器
  const closeModal = () => {
    if (autoSaveTimer.current) clearTimeout(autoSaveTimer.current);
    setModalOpen(false);
    setSaveStatus('idle');
    setLastSavedTime(null);
    isInitialLoad.current = true;
  };

  const loadData = async () => {'''
)

# 3. openAdd 里重置初始加载标记
content = content.replace(
    '''    setItems([{ category_id: null, gram: 0, width: 0, unit: '吨', quantity: 0, unit_price: 0, amount: 0, delivery_date: '', remark: '' }]);
    setModalOpen(true);
  };

  // 打开编辑''',
    '''    setItems([{ category_id: null, gram: 0, width: 0, unit: '吨', quantity: 0, unit_price: 0, amount: 0, delivery_date: '', remark: '' }]);
    setSaveStatus('idle');
    setLastSavedTime(null);
    setModalOpen(true);
    setTimeout(() => { isInitialLoad.current = false; }, 500);
  };

  // 打开编辑'''
)

# 4. openEdit 里重置初始加载标记
content = content.replace(
    '''      })) : [{ category_id: null, gram: 0, width: 0, unit: '吨', quantity: 0, unit_price: 0, amount: 0, delivery_date: '', remark: '' }]);
      setModalOpen(true);
    } catch (e) {
      message.error('加载详情失败');
    }
  };''',
    '''      })) : [{ category_id: null, gram: 0, width: 0, unit: '吨', quantity: 0, unit_price: 0, amount: 0, delivery_date: '', remark: '' }]);
      setSaveStatus('idle');
      setLastSavedTime(null);
      setModalOpen(true);
      setTimeout(() => { isInitialLoad.current = false; }, 500);
    } catch (e) {
      message.error('加载详情失败');
    }
  };'''
)

# 5. addItemRow/removeItemRow/updateItemRow 触发自动保存
content = content.replace(
    '''  const addItemRow = () => {
    setItems([...items, { category_id: null, gram: 0, width: 0, unit: '吨', quantity: 0, unit_price: 0, amount: 0, delivery_date: '', remark: '' }]);
  };''',
    '''  const addItemRow = () => {
    setItems([...items, { category_id: null, gram: 0, width: 0, unit: '吨', quantity: 0, unit_price: 0, amount: 0, delivery_date: '', remark: '' }]);
    triggerAutoSave();
  };'''
)

content = content.replace(
    '''  const removeItemRow = (idx) => {
    if (items.length <= 1) return;
    setItems(items.filter((_, i) => i !== idx));
  };''',
    '''  const removeItemRow = (idx) => {
    if (items.length <= 1) return;
    setItems(items.filter((_, i) => i !== idx));
    triggerAutoSave();
  };'''
)

content = content.replace(
    '''    setItems(newItems);
  };

  // 合计金额''',
    '''    setItems(newItems);
    triggerAutoSave();
  };

  // 合计金额'''
)

# 6. handleSave 成功后重置状态
content = content.replace(
    '''      if (editId) {
        await api.put(`/api/purchase_order/${editId}`, payload);
        message.success('修改成功');
      } else {''',
    '''      if (editId) {
        await api.put(`/api/purchase_order/${editId}`, payload);
        message.success('保存成功');
      } else {'''
)

content = content.replace(
    '''      setModalOpen(false);
      loadData();
    } catch (e) {
      if (e.errorFields) return;
      message.error(e.response?.data?.detail || '保存失败');
    }
  };''',
    '''      if (autoSaveTimer.current) clearTimeout(autoSaveTimer.current);
      setSaveStatus('saved');
      setLastSavedTime(new Date().toLocaleTimeString('zh-CN', {hour:'2-digit', minute:'2-digit', second:'2-digit'}));
      setModalOpen(false);
      loadData();
    } catch (e) {
      if (e.errorFields) return;
      message.error(e.response?.data?.detail || '保存失败');
    }
  };'''
)

# 7. 弹窗标题加保存状态，onCancel 改用 closeModal
content = content.replace(
    '''      <Modal
        open={modalOpen}
        title={editId ? '编辑采购单' : '新建采购单'}
        onCancel={() => setModalOpen(false)}
        footer={null}
        width={1200}
      >
        <Form form={form} layout="vertical">''',
    '''      <Modal
        open={modalOpen}
        title={
          <div style={{display:'flex', alignItems:'center', gap:12}}>
            <span>{editId ? '编辑采购单' : '新建采购单'}</span>
            {saveStatus === 'saving' && <span style={{fontSize:13, color:'#fa8c16'}}>正在保存...</span>}
            {saveStatus === 'saved' && <span style={{fontSize:13, color:'#52c41a'}}>✓ 已保存 {lastSavedTime || ''}</span>}
            {saveStatus === 'error' && <span style={{fontSize:13, color:'#ff4d4f'}}>保存失败，请检查必填项</span>}
          </div>
        }
        onCancel={closeModal}
        footer={null}
        width={1200}
      >
        <Form form={form} layout="vertical" onValuesChange={() => triggerAutoSave()}>'''
)

with open('src/PurchaseOrder.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('采购单自动保存功能加完成')
