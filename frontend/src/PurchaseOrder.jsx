import React, { useState, useEffect, useRef } from 'react';
import { Table, Button, Input, Modal, Form, Select, message, DatePicker, Space, InputNumber, Cascader } from 'antd';
import { api } from './api';
import dayjs from 'dayjs';

const STATUS_MAP = {
  draft: { label: '草稿', color: 'default' },
  pending: { label: '待到货', color: 'orange' },
  partial: { label: '部分到货', color: 'blue' },
  completed: { label: '已完成', color: 'green' }
};

export default function PurchaseOrder() {
  const [list, setList] = useState([]);
  const [pcList, setPcList] = useState([]);
  const [supplierList, setSupplierList] = useState([]);
  const [loading, setLoading] = useState(false);

  // 新增/编辑弹窗
  const [modalOpen, setModalOpen] = useState(false);
  const [editId, setEditId] = useState(null);
  const [form] = Form.useForm();
  const [items, setItems] = useState([{ category_id: null, gram: 0, width: 0, unit: '吨', quantity: 0, unit_price: 0, amount: 0, delivery_date: '', remark: '' }]);

  // 到货确认弹窗
  const [arriveModalOpen, setArriveModalOpen] = useState(false);
  const [currentOrder, setCurrentOrder] = useState(null);
  const [arriveItems, setArriveItems] = useState([]);

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

  const loadData = async () => {
    setLoading(true);
    try {
      const [res, pcRes, supplierRes] = await Promise.all([
        api.get('/api/purchase_order'),
        api.get('/api/physical_category'),
        api.get('/api/supplier')
      ]);
      setList(res.data);
      setPcList(pcRes.data);
      setSupplierList(supplierRes.data);
    } catch (e) {
      message.error('加载失败：' + (e.response?.data?.detail || e.message));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // 获取物理分类完整路径（支持任意层级，最多4级）
  const getCategoryPath = (catId) => {
    if (!catId) return '';
    const path = [];
    let current = pcList.find(c => c.id === catId);
    let guard = 0;
    while (current && guard < 10) {
      path.unshift(current.name);
      current = current.parent_id ? pcList.find(c => c.id === current.parent_id) : null;
      guard++;
    }
    return path.join('/');
  };

  // 构建物理分类树形结构（用于级联选择）
  const buildCategoryTree = (parentId = null) => {
    return pcList
      .filter(c => c.parent_id === parentId)
      .map(c => ({
        value: c.id,
        label: c.name,
        children: buildCategoryTree(c.id)
      }));
  };
  const categoryTree = buildCategoryTree();

  // 根据 category_id 反查级联选择路径
  const getCategoryPathValue = (catId) => {
    if (!catId) return undefined;
    const path = [];
    let current = pcList.find(c => c.id === catId);
    while (current) {
      path.unshift(current.id);
      current = current.parent_id ? pcList.find(c => c.id === current.parent_id) : null;
    }
    return path.length > 0 ? path : undefined;
  };

  // 一级分类列表
  const level1List = pcList.filter(c => c.parent_id === null);

  // 打开新增
  const openAdd = () => {
    setEditId(null);
    form.resetFields();
    form.setFieldsValue({ order_date: dayjs() });
    setItems([{ category_id: null, gram: 0, width: 0, unit: '吨', quantity: 0, unit_price: 0, amount: 0, delivery_date: '', remark: '' }]);
    setSaveStatus('idle');
    setLastSavedTime(null);
    setModalOpen(true);
    setTimeout(() => { isInitialLoad.current = false; }, 500);
  };

  // 打开编辑
  const openEdit = async (record) => {
    setEditId(record.id);
    try {
      const res = await api.get(`/api/purchase_order/${record.id}`);
      const data = res.data;
      form.setFieldsValue({
        supplier: data.supplier,
        delivery_address: data.delivery_address,
        order_date: data.order_date ? dayjs(data.order_date) : null,
        remark: data.remark,
        maker: data.maker,
        checker: data.checker
      });
      setItems(data.items && data.items.length > 0 ? data.items.map(i => ({
        category_id: i.category_id,
        gram: i.gram,
        width: i.width,
        unit: i.unit,
        quantity: i.quantity,
        unit_price: i.unit_price,
        amount: i.amount,
        delivery_date: i.delivery_date,
        remark: i.remark
      })) : [{ category_id: null, gram: 0, width: 0, unit: '吨', quantity: 0, unit_price: 0, amount: 0, delivery_date: '', remark: '' }]);
      setSaveStatus('idle');
      setLastSavedTime(null);
      setModalOpen(true);
      setTimeout(() => { isInitialLoad.current = false; }, 500);
    } catch (e) {
      message.error('加载详情失败');
    }
  };

  // 添加明细行
  const addItemRow = () => {
    setItems([...items, { category_id: null, gram: 0, width: 0, unit: '吨', quantity: 0, unit_price: 0, amount: 0, delivery_date: '', remark: '' }]);
    triggerAutoSave();
  };

  // 删除明细行
  const removeItemRow = (idx) => {
    if (items.length <= 1) return;
    setItems(items.filter((_, i) => i !== idx));
    triggerAutoSave();
  };

  // 更新明细行
  const updateItemRow = (idx, field, value) => {
    const newItems = [...items];
    newItems[idx][field] = value;
    // 自动计算金额
    if (field === 'quantity' || field === 'unit_price') {
      newItems[idx].amount = Number((newItems[idx].quantity || 0) * (newItems[idx].unit_price || 0)).toFixed(2);
    }
    setItems(newItems);
    triggerAutoSave();
  };

  // 合计金额
  const totalAmount = items.reduce((sum, i) => sum + Number(i.amount || 0), 0);

  // 保存
  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      const payload = {
        ...values,
        order_date: values.order_date ? values.order_date.format('YYYY-MM-DD') : null,
        total_amount: totalAmount,
        items: items.map(i => ({
          ...i,
          delivery_date: i.delivery_date || null
        }))
      };

      if (editId) {
        await api.put(`/api/purchase_order/${editId}`, payload);
        message.success('保存成功');
      } else {
        await api.post('/api/purchase_order', payload);
        message.success('新增成功');
      }
      if (autoSaveTimer.current) clearTimeout(autoSaveTimer.current);
      setSaveStatus('saved');
      setLastSavedTime(new Date().toLocaleTimeString('zh-CN', {hour:'2-digit', minute:'2-digit', second:'2-digit'}));
      setModalOpen(false);
      loadData();
    } catch (e) {
      if (e.errorFields) return;
      message.error(e.response?.data?.detail || '保存失败');
    }
  };

  // 删除
  const handleDelete = async (id) => {
    if (!window.confirm('确定删除这个采购单？')) return;
    try {
      await api.delete(`/api/purchase_order/${id}`);
      message.success('删除成功');
      loadData();
    } catch (e) {
      message.error(e.response?.data?.detail || '删除失败');
    }
  };

  // 打开到货确认
  const openArrive = async (record) => {
    try {
      const res = await api.get(`/api/purchase_order/${record.id}`);
      setCurrentOrder(res.data);
      setArriveItems(res.data.items.map(i => ({
        ...i,
        checked: false,
        arrive_quantity: 0,
        roll_count: 1,
        rolls: [],
        showRolls: false
      })));
      setArriveModalOpen(true);
    } catch (e) {
      message.error('加载详情失败');
    }
  };

  // 更新到货明细
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
  };

  // 确认到货
  const confirmArrive = async () => {
    const checkedItems = arriveItems.filter(i => i.checked && i.arrive_quantity > 0);
    if (checkedItems.length === 0) {
      message.warning('请勾选到货的明细并输入到货数量');
      return;
    }
    try {
      const payload = {
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
      };
      const res = await api.post(`/api/purchase_order/${currentOrder.id}/arrive`, payload);
      message.success(`到货成功，生成${res.data.count}支卷筒，已自动入库卷料仓`);
      setArriveModalOpen(false);
      loadData();
    } catch (e) {
      message.error(e.response?.data?.detail || '到货确认失败');
    }
  };

  const columns = [
    { title: '采购单号', dataIndex: 'order_no', width: 180 },
    { title: '供应商', dataIndex: 'supplier', width: 200 },
    { title: '交货地址', dataIndex: 'delivery_address', width: 150 },
    { title: '日期', dataIndex: 'order_date', width: 120 },
    {
      title: '状态', dataIndex: 'status', width: 100,
      render: v => {
        const s = STATUS_MAP[v] || { label: v, color: 'default' };
        return <span style={{ color: s.color === 'green' ? '#52c41a' : s.color === 'orange' ? '#fa8c16' : s.color === 'blue' ? '#1890ff' : '#999', fontWeight: 600 }}>{s.label}</span>;
      }
    },
    { title: '总金额(元)', dataIndex: 'total_amount', width: 120, render: v => `¥${Number(v || 0).toFixed(2)}` },
    { title: '制单', dataIndex: 'maker', width: 100 },
    {
      title: '操作', key: 'action', width: 250,
      render: (_, record) => (
        <Space>
          <Button size="small" type="primary" onClick={() => openArrive(record)}>到货确认</Button>
          <Button size="small" onClick={() => openEdit(record)}>编辑</Button>
          <Button size="small" danger onClick={() => handleDelete(record.id)}>删除</Button>
        </Space>
      )
    }
  ];

  return (
    <div style={{ padding: 16 }}>
      <div style={{ marginBottom: 16, display: 'flex', gap: 10 }}>
        <Button type="primary" onClick={openAdd}>新建采购单</Button>
      </div>

      <Table
        rowKey="id"
        columns={columns}
        dataSource={list}
        loading={loading}
        pagination={{ pageSize: 20 }}
      />

      {/* 新增/编辑弹窗 */}
      <Modal
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
        <Form form={form} layout="vertical" onValuesChange={() => triggerAutoSave()}>
          <div style={{ display: 'flex', gap: 16, marginBottom: 8 }}>
            <div style={{ flex: 1 }}>
              <Form.Item label="供应商" name="supplier" rules={[{ required: true, message: '请选择供应商' }]}>
                <Select
                  placeholder="从供应商档案选择"
                  showSearch
                  optionFilterProp="children"
                  onChange={(value, option) => {
                    // 选择供应商后自动带入地址
                    const sup = supplierList.find(s => s.name === value);
                    if (sup && sup.address) {
                      form.setFieldsValue({ delivery_address: sup.address });
                    }
                  }}
                >
                  {supplierList.map(s => (
                    <Select.Option key={s.id} value={s.name}>{s.name}</Select.Option>
                  ))}
                </Select>
              </Form.Item>
            </div>
            <div style={{ flex: 1 }}>
              <Form.Item label="交货地址" name="delivery_address">
                <Input placeholder="如：自提" />
              </Form.Item>
            </div>
            <div style={{ width: 200 }}>
              <Form.Item label="日期" name="order_date">
                <DatePicker style={{ width: '100%' }} format="YYYY-MM-DD" />
              </Form.Item>
            </div>
          </div>

          <div style={{ display: 'flex', gap: 16, marginBottom: 8 }}>
            <div style={{ flex: 1 }}>
              <Form.Item label="制单" name="maker"><Input placeholder="制单人" /></Form.Item>
            </div>
            <div style={{ flex: 1 }}>
              <Form.Item label="审核" name="checker"><Input placeholder="审核人" /></Form.Item>
            </div>
          </div>

          {/* 明细表格 */}
          <div style={{ marginBottom: 8, fontWeight: 600 }}>采购明细</div>
          <div style={{ border: '1px solid #d9d9d9', borderRadius: 4, marginBottom: 16 }}>
            <div style={{ display: 'flex', background: '#fafafa', borderBottom: '1px solid #d9d9d9', fontWeight: 600, fontSize: 13 }}>
              <div style={{ width: 40, padding: '8px 4px', textAlign: 'center' }}>序号</div>
              <div style={{ flex: 1.5, padding: '8px 4px' }}>品牌(物理分类)</div>
              <div style={{ width: 80, padding: '8px 4px' }}>克重</div>
              <div style={{ width: 80, padding: '8px 4px' }}>规格/MM</div>
              <div style={{ width: 60, padding: '8px 4px' }}>单位</div>
              <div style={{ width: 90, padding: '8px 4px' }}>数量(吨)</div>
              <div style={{ width: 100, padding: '8px 4px' }}>单价(元/吨)</div>
              <div style={{ width: 100, padding: '8px 4px' }}>金额(元)</div>
              <div style={{ width: 110, padding: '8px 4px' }}>交货日期</div>
              <div style={{ flex: 1, padding: '8px 4px' }}>备注</div>
              <div style={{ width: 50, padding: '8px 4px', textAlign: 'center' }}>操作</div>
            </div>
            {items.map((item, idx) => (
              <div key={idx} style={{ display: 'flex', borderBottom: idx < items.length - 1 ? '1px solid #f0f0f0' : 'none', alignItems: 'center' }}>
                <div style={{ width: 40, padding: '4px', textAlign: 'center' }}>{idx + 1}</div>
                <div style={{ flex: 1.5, padding: '4px' }}>
                  <Cascader
                    placeholder="一级一级选择品牌"
                    value={getCategoryPathValue(item.category_id)}
                    onChange={(_, selectedOptions) => {
                      if (selectedOptions && selectedOptions.length > 0) {
                        const last = selectedOptions[selectedOptions.length - 1];
                        const newItems = [...items];
                        newItems[idx] = { ...newItems[idx], category_id: last.value };

                        // 第3级是克重（如"400G"），提取数字自动填入
                        if (selectedOptions.length >= 3) {
                          const gramName = selectedOptions[2].label || '';
                          const gramMatch = String(gramName).match(/[\d.]+/);
                          if (gramMatch) {
                            newItems[idx].gram = Number(gramMatch[0]);
                          }
                        }
                        // 第4级是幅宽（如"635"），提取数字自动填入
                        if (selectedOptions.length >= 4) {
                          const widthName = selectedOptions[3].label || '';
                          const widthMatch = String(widthName).match(/[\d.]+/);
                          if (widthMatch) {
                            newItems[idx].width = Number(widthMatch[0]);
                          }
                        }
                        setItems(newItems);
                        triggerAutoSave();
                      } else {
                        updateItemRow(idx, 'category_id', null);
                      }
                    }}
                    options={categoryTree}
                    style={{ width: '100%' }}
                    changeOnSelect
                  />
                </div>
                <div style={{ width: 80, padding: '4px' }}>
                  <InputNumber value={item.gram} onChange={v => updateItemRow(idx, 'gram', v)} style={{ width: '100%' }} placeholder="克重" />
                </div>
                <div style={{ width: 80, padding: '4px' }}>
                  <InputNumber value={item.width} onChange={v => updateItemRow(idx, 'width', v)} style={{ width: '100%' }} placeholder="幅宽" />
                </div>
                <div style={{ width: 60, padding: '4px' }}>
                  <Input value={item.unit} onChange={e => updateItemRow(idx, 'unit', e.target.value)} style={{ width: '100%' }} placeholder="单位" />
                </div>
                <div style={{ width: 90, padding: '4px' }}>
                  <InputNumber value={item.quantity} onChange={v => updateItemRow(idx, 'quantity', v)} style={{ width: '100%' }} placeholder="数量" step="0.001" />
                </div>
                <div style={{ width: 100, padding: '4px' }}>
                  <InputNumber value={item.unit_price} onChange={v => updateItemRow(idx, 'unit_price', v)} style={{ width: '100%' }} placeholder="吨价" />
                </div>
                <div style={{ width: 100, padding: '4px', color: '#1890ff', fontWeight: 600 }}>¥{Number(item.amount || 0).toFixed(2)}</div>
                <div style={{ width: 110, padding: '4px' }}>
                  <DatePicker value={item.delivery_date ? dayjs(item.delivery_date) : null} onChange={(_, dateStr) => updateItemRow(idx, 'delivery_date', dateStr)} style={{ width: '100%' }} format="YYYY-MM-DD" />
                </div>
                <div style={{ flex: 1, padding: '4px' }}>
                  <Input value={item.remark} onChange={e => updateItemRow(idx, 'remark', e.target.value)} placeholder="备注" />
                </div>
                <div style={{ width: 50, padding: '4px', textAlign: 'center' }}>
                  <Button type="link" danger size="small" onClick={() => removeItemRow(idx)}>删</Button>
                </div>
              </div>
            ))}
          </div>

          <div style={{ textAlign: 'right', marginBottom: 16 }}>
            <Button onClick={addItemRow} style={{ marginRight: 16 }}>+ 添加一行</Button>
            <span style={{ fontWeight: 600, fontSize: 15, marginRight: 24 }}>合计吨重：{items.reduce((sum, i) => sum + Number(i.quantity || 0), 0).toFixed(3)} 吨</span>
            <span style={{ fontWeight: 600, fontSize: 15 }}>合计金额：¥{totalAmount.toFixed(2)}</span>
          </div>

          <Form.Item label="备注" name="remark">
            <Input.TextArea rows={2} placeholder="备注信息" />
          </Form.Item>

          <div style={{ textAlign: 'right' }}>
            <Button onClick={() => setModalOpen(false)} style={{ marginRight: 8 }}>取消</Button>
            <Button type="primary" onClick={handleSave}>保存</Button>
          </div>
        </Form>
      </Modal>

      {/* 到货确认弹窗 */}
      <Modal
        open={arriveModalOpen}
        title="采购到货确认"
        onCancel={() => setArriveModalOpen(false)}
        footer={null}
        width={1000}
      >
        {currentOrder && (
          <div>
            <div style={{ marginBottom: 16, padding: 12, background: '#f5f5f5', borderRadius: 4 }}>
              <p><b>采购单号：</b>{currentOrder.order_no} &nbsp;&nbsp; <b>供应商：</b>{currentOrder.supplier}</p>
              <p style={{ color: '#fa8c16' }}>勾选到货明细，逐支录入卷筒编号和实际重量（每支重量可不同），确认后自动入库卷料仓</p>
            </div>

            <div style={{ border: '1px solid #d9d9d9', borderRadius: 4, marginBottom: 16 }}>
              <div style={{ display: 'flex', background: '#fafafa', borderBottom: '1px solid #d9d9d9', fontWeight: 600, fontSize: 13 }}>
                <div style={{ width: 40, padding: '8px 4px', textAlign: 'center' }}>选</div>
                <div style={{ flex: 1.5, padding: '8px 4px' }}>品牌</div>
                <div style={{ width: 70, padding: '8px 4px' }}>克重</div>
                <div style={{ width: 70, padding: '8px 4px' }}>规格</div>
                <div style={{ width: 90, padding: '8px 4px' }}>采购数量</div>
                <div style={{ width: 90, padding: '8px 4px' }}>已到货</div>
                <div style={{ width: 100, padding: '8px 4px' }}>本次到货(吨)</div>
                <div style={{ width: 80, padding: '8px 4px' }}>到货支数</div>
              </div>
              {arriveItems.map((item, idx) => (
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
              ))}
            </div>

            <div style={{ textAlign: 'right' }}>
              <Button onClick={() => setArriveModalOpen(false)} style={{ marginRight: 8 }}>取消</Button>
              <Button type="primary" onClick={confirmArrive}>确认到货并入库</Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
