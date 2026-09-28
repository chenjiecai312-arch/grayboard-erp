with open('src/ProductWarehouse.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. import 加 useRef
content = content.replace(
    "import React, { useState, useEffect } from 'react';",
    "import React, { useState, useEffect, useRef } from 'react';"
)

# 2. 加自动保存相关 state（在 editForm 后面）
content = content.replace(
    '''  const [editForm] = Form.useForm();

  // 入库''',
    '''  const [editForm] = Form.useForm();

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
      const values = editForm.getFieldsValue();
      const catPath = values.category_path;
      const category_id = catPath && catPath.length > 0 ? catPath[catPath.length - 1] : null;
      const payload = {
        product_name_id: Number(values.product_name_id) || null,
        customer_id: values.customer_id ? Number(values.customer_id) : null,
        category_id,
        work_order_no: values.work_order_no || null,
        spec: values.spec || "",
        actual_gram: Number(values.actual_gram) || 0,
        nominal_gram: Number(values.nominal_gram) || 0,
        quantity: Number(values.quantity) || 0,
        unit: values.unit || "令",
        remark: values.remark || ""
      };
      if (editingId) {
        await api.put(`/api/product/${editingId}`, payload);
      } else {
        const res = await api.post("/api/product", payload);
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

  const closeEditModal = () => {
    if (autoSaveTimer.current) clearTimeout(autoSaveTimer.current);
    setEditModalOpen(false);
    setSaveStatus('idle');
    setLastSavedTime(null);
    isInitialLoad.current = true;
  };

  // 入库'''
)

# 3. handleSave 成功后重置状态
content = content.replace(
    '''      setEditModalOpen(false);
      loadData();
    } catch (err) {
      if (err.errorFields) return;
      message.error(err.response?.data?.detail || "保存失败")
    }
  };

  // ========== 入库 ==========''',
    '''      if (autoSaveTimer.current) clearTimeout(autoSaveTimer.current);
      setSaveStatus('saved');
      setLastSavedTime(new Date().toLocaleTimeString('zh-CN', {hour:'2-digit', minute:'2-digit', second:'2-digit'}));
      setEditModalOpen(false);
      loadData();
    } catch (err) {
      if (err.errorFields) return;
      message.error(err.response?.data?.detail || "保存失败")
    }
  };

  // ========== 入库 =========='''
)

# 4. 找到打开编辑弹窗的函数，加重置初始加载标记
# 先找 openEdit 函数
content = content.replace(
    '''  const openEdit = (record) => {
    setEditingId(record.id);''',
    '''  const openEdit = (record) => {
    setEditingId(record.id);
    setSaveStatus('idle');
    setLastSavedTime(null);'''
)

# 新增成品的函数也加
content = content.replace(
    '''  const openAdd = () => {
    setEditingId(null);''',
    '''  const openAdd = () => {
    setEditingId(null);
    setSaveStatus('idle');
    setLastSavedTime(null);'''
)

# 在 openAdd/openEdit 的 setEditModalOpen(true) 后面加 setTimeout
content = content.replace(
    '''    setEditModalOpen(true);
  };

  // ========== 入库 ==========''',
    '''    setEditModalOpen(true);
    setTimeout(() => { isInitialLoad.current = false; }, 500);
  };

  // ========== 入库 =========='''
)

# 5. 弹窗标题加保存状态，onCancel 改用 closeEditModal，Form 加 onValuesChange
content = content.replace(
    '''      <Modal open={editModalOpen} title={editingId ? "编辑成品" : "新增成品"}
        onCancel={() => setEditModalOpen(false)} onOk={handleSave} width={600}>
        <Form form={editForm} layout="vertical">''',
    '''      <Modal open={editModalOpen}
        title={
          <div style={{display:'flex', alignItems:'center', gap:12}}>
            <span>{editingId ? "编辑成品" : "新增成品"}</span>
            {saveStatus === 'saving' && <span style={{fontSize:13, color:'#fa8c16'}}>正在保存...</span>}
            {saveStatus === 'saved' && <span style={{fontSize:13, color:'#52c41a'}}>✓ 已保存 {lastSavedTime || ''}</span>}
            {saveStatus === 'error' && <span style={{fontSize:13, color:'#ff4d4f'}}>保存失败，请检查必填项</span>}
          </div>
        }
        onCancel={closeEditModal} onOk={handleSave} width={600}>
        <Form form={editForm} layout="vertical" onValuesChange={() => triggerAutoSave()}>'''
)

with open('src/ProductWarehouse.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('成品仓自动保存功能加完成')
