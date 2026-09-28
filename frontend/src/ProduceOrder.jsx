import React, { useState, useEffect, useRef } from 'react';
import dayjs from 'dayjs';
import { Table, Button, Input, Modal, Form, Select, message, Space, DatePicker, Popconfirm, Tag, Row, Col } from 'antd';
import { api } from './api';

const STATUS_MAP = {
  draft: { label: '草稿', color: 'default' },
  scheduled: { label: '已排单', color: 'cyan' },
  pending: { label: '待生产', color: 'orange' },
  picking: { label: '领料中', color: 'orange' },
  producing: { label: '生产中', color: 'blue' },
  finished: { label: '已完成', color: 'green' }
};

// 销售订单状态映射
const SALES_STATUS_MAP = {
  draft: '草稿',
  pending: '待出库',
  confirmed: '已出库',
  delivered: '已送出',
  completed: '已完成',
  cancelled: '已取消'
};

export default function ProduceOrder() {
  const [list, setList] = useState([]);
  const [rollList, setRollList] = useState([]);
  const [pnList, setPnList] = useState([]);
  const [pcList, setPcList] = useState([]);
  const [customerList, setCustomerList] = useState([]);
  const [loading, setLoading] = useState(false);

  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [form] = Form.useForm();
  const [items, setItems] = useState([{ layer_no: 1, roll_id: null, roll_name: '', quantity: 0, unit_price: 0, amount: 0, remark: '' }]);

  const [rollSelectModalOpen, setRollSelectModalOpen] = useState(false);
  const [currentLayerIndex, setCurrentLayerIndex] = useState(null);
  const [rollSearchField, setRollSearchField] = useState('all');
  const [rollSearchText, setRollSearchText] = useState('');

  const [returnModalOpen, setReturnModalOpen] = useState(false);
  const [currentOrder, setCurrentOrder] = useState(null);
  const [returnItems, setReturnItems] = useState([]);
  // 排单相关
  const [selectedRowKeys, setSelectedRowKeys] = useState([]);
  const [scheduleModalOpen, setScheduleModalOpen] = useState(false);
  const [scheduleDate, setScheduleDate] = useState(null);
  // 销售单关联
  const [salesOrderList, setSalesOrderList] = useState([]);
  const [salesSelectModalOpen, setSalesSelectModalOpen] = useState(false);
  const [salesSearchText, setSalesSearchText] = useState("");
  const [salesDetailModalOpen, setSalesDetailModalOpen] = useState(false);
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
  };

  const loadData = async () => {
    setLoading(true);
    try {
      const [orderRes, rollRes, pnRes, pcRes, cusRes, salesRes] = await Promise.all([
        api.get('/api/produce_order'),
        api.get('/api/rawroll'),
        api.get('/api/product_name'),
        api.get('/api/physical_category'),
        api.get('/api/customer'),
        api.get('/api/sales_order')
      ]);
      setList(orderRes.data);
      setRollList(rollRes.data);
      setPnList(pnRes.data);
      setPcList(pcRes.data);
      setCustomerList(cusRes.data);
      setSalesOrderList(salesRes.data);
    } catch (e) {
      message.error('加载失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // 获取完整分类路径
  const getCategoryPath = (categoryId) => {
    if (!categoryId) return '-';
    const path = [];
    let current = pcList.find(c => c.id === categoryId);
    while (current) {
      path.unshift(current.name);
      current = pcList.find(c => c.id === current.parent_id);
    }
    return path.join(' / ');
  };

  // 获取二级分类名称（纸名）
  const getSecondCategoryName = (categoryId) => {
    if (!categoryId) return '';
    const path = [];
    let current = pcList.find(c => c.id === categoryId);
    while (current) {
      path.unshift(current);
      current = pcList.find(c => c.id === current.parent_id);
    }
    return path.length >= 2 ? path[1].name : (path.length === 1 ? path[0].name : '');
  };

  // 自动计算生产工艺
  const calcCraft = (itemsList) => {
    return itemsList.map(item => {
      const roll = rollList.find(r => r.id === item.roll_id);
      if (!roll) return '';
      const name = getSecondCategoryName(roll.category_id);
      return `${name}${roll.gram}`;
    }).filter(s => s).join('+');
  };

  const filteredRollList = rollList.filter(r => {
    if (!rollSearchText) return true;
    const kw = rollSearchText.toLowerCase();
    const pn = pnList.find(p => p.id === r.product_name_id);
    switch (rollSearchField) {
      case 'name': return getCategoryPath(r.category_id).toLowerCase().includes(kw);
      case 'gram': return String(r.gram).includes(kw);
      case 'width': return String(r.width).includes(kw);
      case 'raw_no': return String(r.raw_no).toLowerCase().includes(kw);
      default:
        return getCategoryPath(r.category_id).toLowerCase().includes(kw)
          || String(r.gram).includes(kw)
          || String(r.width).includes(kw)
          || String(r.raw_no).toLowerCase().includes(kw);
    }
  });

  const openAdd = () => {
    setEditingId(null);
    form.resetFields();
    form.setFieldsValue({ diagonal_error: '2MM内', loss_limit: '2%' });
    setItems([{ layer_no: 1, roll_id: null, roll_name: '', quantity: 0, unit_price: 0, amount: 0, remark: '' }]);
    setSaveStatus('idle');
    setLastSavedTime(null);
    setModalOpen(true);
    setTimeout(() => { isInitialLoad.current = false; }, 500);
  };

  const openEdit = (record) => {
    setEditingId(record.id);
    form.setFieldsValue({
      customer_id: record.customer_id,
      po_no: record.po_no,
      product_name: record.product_name,
      quantity: record.quantity,
      spec_width: record.spec_width,
      spec_length: record.spec_length,
      total_gram: record.total_gram,
      customer_order_no: record.customer_order_no,
      thickness: record.thickness,
      humidity: record.humidity,
      brand: record.brand,
      size_error: record.size_error,
      diagonal_error: record.diagonal_error || '2MM内',
      package_method: record.package_method,
      loss_limit: record.loss_limit || '2%',
      maker: record.maker,
      checker: record.checker,
      produce_date: record.produce_date ? dayjs(record.produce_date) : null,
      remark: record.remark,
      sales_order_id: record.sales_order_id
    });
    setItems(record.items.map(i => ({ ...i })));
    setSaveStatus('idle');
    setLastSavedTime(null);
    setModalOpen(true);
    setTimeout(() => { isInitialLoad.current = false; }, 500);
  };

  const addLayer = () => {
    const maxLayer = Math.max(...items.map(i => i.layer_no), 0);
    const newItems = [...items, { layer_no: maxLayer + 1, roll_id: null, roll_name: '', quantity: 0, unit_price: 0, amount: 0, remark: '' }];
    setItems(newItems);
    const craft = calcCraft(newItems);
    if (craft) form.setFieldsValue({ craft });
  };

  const removeLayer = (index) => {
    if (items.length <= 1) return;
    const newItems = items.filter((_, i) => i !== index).map((item, i) => ({ ...item, layer_no: i + 1 }));
    setItems(newItems);
    const craft = calcCraft(newItems);
    if (craft) form.setFieldsValue({ craft });
  };

  const updateItem = (index, field, value) => {
    const newItems = [...items];
    newItems[index][field] = value;
    if (field === 'roll_id') {
      const roll = rollList.find(r => r.id === value);
      if (roll) {
        const pn = pnList.find(p => p.id === roll.product_name_id);
        newItems[index].roll_name = getCategoryPath(roll.category_id);
        newItems[index].unit_price = roll.ton_price || 0;
      }
    }
    newItems[index].amount = (newItems[index].quantity || 0) * (newItems[index].unit_price || 0);
    setItems(newItems);
    // 自动计算生产工艺
    const craft = calcCraft(newItems);
    if (craft) {
      form.setFieldsValue({ craft: craft });
    }
    const totalGram = newItems.reduce((s, i) => {
      const roll = rollList.find(r => r.id === i.roll_id);
      return s + (roll?.gram || 0);
    }, 0);
    if (totalGram > 0) {
      form.setFieldsValue({ total_gram: totalGram });
    }
  };

  const openRollSelect = (layerIndex) => {
    setCurrentLayerIndex(layerIndex);
    setRollSearchField('all');
    setRollSearchText('');
    setRollSelectModalOpen(true);
  };

  const selectRoll = (roll) => {
    if (currentLayerIndex !== null) {
      updateItem(currentLayerIndex, 'roll_id', roll.id);
    }
    setRollSelectModalOpen(false);
  };

  // 自动计算每层用量
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

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      const customer = customerList.find(c => c.id === values.customer_id);
      const payload = {
        ...values,
        produce_date: values.produce_date ? values.produce_date.format('YYYY-MM-DD') : null,
        customer_name: customer?.customer_name || values.customer_name,
        layers: items.length,
        items: items
      };
      if (editingId) {
        await api.put(`/api/produce_order/${editingId}`, payload);
        message.success('修改成功');
      } else {
        await api.post('/api/produce_order', payload);
        message.success('新增成功');
      }
      if (autoSaveTimer.current) clearTimeout(autoSaveTimer.current);
      setSaveStatus('saved');
      setLastSavedTime(new Date().toLocaleTimeString('zh-CN', {hour:'2-digit', minute:'2-digit', second:'2-digit'}));
      setModalOpen(false);
      loadData();
    } catch (e) {
      message.error(e.response?.data?.detail || '保存失败');
    }
  };

  const handlePick = async (record) => {
    try {
      await api.post(`/api/produce_order/${record.id}/pick_material`);
      message.success('领料成功，卷料库存已锁定');
      loadData();
    } catch (e) {
      message.error(e.response?.data?.detail || '领料失败');
    }
  };

  const openReturn = (record) => {
    setCurrentOrder(record);
    setReturnItems(record.items.map(i => ({ ...i, return_quantity: 0 })));
    setReturnModalOpen(true);
  };

  const handleReturn = async () => {
    try {
      const payload = returnItems
        .filter(i => i.return_quantity > 0)
        .map(i => ({ item_id: i.id, quantity: i.return_quantity }));
      await api.post(`/api/produce_order/${currentOrder.id}/return_material`, payload);
      message.success('退料成功');
      setReturnModalOpen(false);
      loadData();
    } catch (e) {
      message.error(e.response?.data?.detail || '退料失败');
    }
  };

  // 批量排单
  const handleSchedule = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请先勾选要排单的工单');
      return;
    }
    if (!scheduleDate) {
      message.warning('请选择排单日期');
      return;
    }
    try {
      await api.post('/api/produce_order/schedule', {
        ids: selectedRowKeys,
        schedule_date: scheduleDate.format('YYYY-MM-DD')
      });
      message.success(`已将 ${selectedRowKeys.length} 张工单排单到 ${scheduleDate.format('YYYY-MM-DD')}`);
      setScheduleModalOpen(false);
      setSelectedRowKeys([]);
      setScheduleDate(null);
      loadData();
    } catch (e) {
      message.error(e.response?.data?.detail || '排单失败');
    }
  };

  // 打开销售单选择弹窗
  const openSalesSelect = () => {
    setSalesSearchText("");
    setSalesSelectModalOpen(true);
  };

  // 选择销售单
  const selectSalesOrder = (order) => {
    form.setFieldsValue({ sales_order_id: order.id });
    // 自动填充客户、产品名称、数量、规格等
    if (order.customer_id) form.setFieldsValue({ customer_id: order.customer_id });
    if (order.customer_name) form.setFieldsValue({ customer_name: order.customer_name });
    if (order.items && order.items.length > 0) {
      const item = order.items[0];
      if (item.product_name) form.setFieldsValue({ product_name: item.product_name });
      if (item.quantity) form.setFieldsValue({ quantity: item.quantity });
      if (item.width) form.setFieldsValue({ spec_width: item.width });
      if (item.length) form.setFieldsValue({ spec_length: item.length });
      if (item.actual_gram) form.setFieldsValue({ total_gram: item.actual_gram });
    }
    setSalesSelectModalOpen(false);
    message.success(`已匹配销售单 ${order.order_no}`);
  };

  // 查看关联的销售单详情
  const viewLinkedSales = () => {
    const salesId = form.getFieldValue('sales_order_id');
    if (!salesId) return;
    const order = salesOrderList.find(o => o.id === salesId);
    if (order) {
      setCurrentSalesOrder(order);
      setSalesDetailModalOpen(true);
    }
  };

  // 过滤销售单
  const filteredSalesList = salesOrderList.filter(o => {
    if (!salesSearchText) return true;
    const kw = salesSearchText.toLowerCase();
    return String(o.order_no).toLowerCase().includes(kw)
      || String(o.customer_name || '').toLowerCase().includes(kw);
  });

  const handleDelete = async (id) => {
    try {
      await api.delete(`/api/produce_order/${id}`);
      message.success('删除成功');
      loadData();
    } catch (e) {
      message.error('删除失败');
    }
  };

  const handlePrint = (record) => {
    const printWindow = window.open('', '_blank');
    const itemsHtml = record.items.map((item) => `
      <tr>
        <td>${item.roll_name || '-'}</td>
        <td>${item.roll_name?.match(/(\d+)g/)?.[1] || '-'}</td>
        <td>${item.roll_name?.match(/(\d+)mm/)?.[1] || '-'}</td>
        <td>${item.remark || '-'}</td>
        <td>${item.quantity || 0}</td>
      </tr>
    `).join('');

    const craft = record.craft || record.items.map(i => i.roll_name?.match(/(\d+)g/)?.[1] || '0').join('+');

    printWindow.document.write(`
      <html>
      <head>
        <title>生产工程单 - ${record.order_no}</title>
        <style>
          body { font-family: 'Microsoft YaHei', 'SimSun', sans-serif; padding: 20px; font-size: 14px; }
          .header { text-align: center; margin-bottom: 10px; }
          .header .company { font-size: 20px; font-weight: bold; margin-right: 40px; }
          .header .loss { font-size: 16px; color: red; }
          h2 { text-align: center; font-size: 24px; letter-spacing: 8px; margin: 10px 0; }
          table { width: 100%; border-collapse: collapse; margin-top: 10px; }
          th, td { border: 1px solid #333; padding: 6px 8px; text-align: center; }
          th { background: #f5f5f5; font-weight: bold; }
          .label { background: #f5f5f5; font-weight: bold; width: 80px; }
          .配料-title { writing-mode: vertical-rl; text-align: center; font-weight: bold; background: #f5f5f5; width: 40px; }
          .footer { margin-top: 20px; }
          .sign-row { margin-top: 30px; display: flex; justify-content: space-between; }
        </style>
      </head>
      <body>
        <div class="header">
          <span class="company">东莞市鼎亿包装材料有限公司</span>
          <span class="loss">损耗不能超百分之${record.loss_limit?.replace('%','') || '2'}</span>
        </div>
        <h2>生 产 工 程 单</h2>

        <table>
          <tr>
            <td class="label">工程单号</td>
            <td>${record.order_no || '-'}</td>
            <td class="label">Po号</td>
            <td>${record.po_no || '-'}</td>
            <td class="label">宽</td>
            <td>${record.spec_width || '-'}</td>
            <td class="label">长</td>
            <td>${record.spec_length || '-'}</td>
          </tr>
          <tr>
            <td class="label">客 户</td>
            <td>${record.customer_name || '-'}</td>
            <td class="label">产品名称</td>
            <td>${record.product_name || '-'}</td>
            <td class="label">数 量</td>
            <td>${record.quantity || '-'}</td>
            <td class="label">规 格</td>
            <td>${record.spec_width || ''}×${record.spec_length || ''}</td>
          </tr>
          <tr>
            <td class="label">客户制令</td>
            <td>${record.customer_order_no || '-'}</td>
            <td class="label">厚 度</td>
            <td>${record.thickness || '-'}</td>
            <td class="label">湿 度</td>
            <td>${record.humidity || '-'}</td>
            <td class="label">交 期</td>
            <td>${record.produce_date || '-'}</td>
          </tr>
          <tr>
            <td class="label">克 重</td>
            <td>${record.total_gram || '-'}</td>
            <td class="label">使用品牌</td>
            <td>${record.brand || '-'}</td>
            <td class="label">尺寸误差</td>
            <td>${record.size_error || '-'}</td>
            <td class="label">对角线误差</td>
            <td>${record.diagonal_error || '2MM内'}</td>
          </tr>
          <tr>
            <td class="label">生产工艺</td>
            <td colspan="3">${craft || '-'}</td>
            <td class="label">包装方式</td>
            <td colspan="3">${record.package_method || '-'}</td>
          </tr>
        </table>

        <table>
          <tr>
            <th rowspan="${record.items.length + 1}" class="配料-title">配 料</th>
            <th>原料名称</th>
            <th>克重/G</th>
            <th>规格/R</th>
            <th>实发原料（备注）</th>
            <th>实发重量/T</th>
          </tr>
          ${itemsHtml}
        </table>

        <table class="footer">
          <tr>
            <td class="label">备 注</td>
            <td colspan="5">${record.remark || '-'}</td>
          </tr>
        </table>

        <div class="sign-row">
          <span>制表人：${record.maker || '-'}</span>
          <span>审核：${record.checker || '-'}</span>
          <span>制表日期：${record.produce_date || '-'}</span>
        </div>
      </body>
      </html>
    `);
    printWindow.document.close();
    printWindow.print();
  };

  const columns = [
    { title: '工程单号', dataIndex: 'order_no', width: 140 },
    { title: 'PO号', dataIndex: 'po_no', width: 120 },
    { title: '客户', dataIndex: 'customer_name', width: 150 },
    { title: '产品名称', dataIndex: 'product_name', width: 120 },
    { title: '规格', width: 120, render: (_, r) => `${r.spec_width || ''}×${r.spec_length || ''}` },
    { title: '数量', dataIndex: 'quantity', width: 80 },
    { title: '总克重', dataIndex: 'total_gram', width: 80 },
    { title: '层数', dataIndex: 'layers', width: 70, render: v => `${v}层` },
    { title: '领料金额', dataIndex: 'total_amount', width: 100, render: v => `¥${Number(v).toFixed(2)}` },
    { title: '状态', dataIndex: 'status', width: 90, render: v => <Tag color={STATUS_MAP[v]?.color}>{STATUS_MAP[v]?.label || v}</Tag> },
    { title: '生产日期', dataIndex: 'produce_date', width: 100 },
    { title: '排单日期', dataIndex: 'schedule_date', width: 100 },
    {
      title: '操作', key: 'action', width: 280, fixed: 'right',
      render: (_, record) => (
        <Space wrap size={4}>
          <Button size="small" onClick={() => handlePrint(record)}>打印</Button>
          {record.status === 'draft' && (
            <Button size="small" type="primary" onClick={() => handlePick(record)}>确认领料</Button>
          )}
          {record.status === 'picking' && (
            <Button size="small" type="primary" onClick={() => openReturn(record)}>退料完成</Button>
          )}
          <Button size="small" onClick={() => openEdit(record)}>编辑</Button>
          <Popconfirm title="确定删除？" onConfirm={() => handleDelete(record.id)}>
            <Button size="small" danger>删除</Button>
          </Popconfirm>
        </Space>
      )
    }
  ];

  return (
    <div style={{ padding: 20 }}>
      <h2 style={{ marginBottom: 16 }}>生产工单</h2>

      <div style={{ marginBottom: 16, display: 'flex', gap: 8 }}>
        <Button type="primary" onClick={openAdd}>新增工单</Button>
        <Button onClick={() => setScheduleModalOpen(true)} disabled={selectedRowKeys.length === 0}>
          添加到排单 ({selectedRowKeys.length})
        </Button>
        <span style={{ color: '#999', fontSize: 12, alignSelf: 'center' }}>勾选工单后可批量排单</span>
      </div>

      <Table
        rowKey="id"
        dataSource={list}
        columns={columns}
        loading={loading}
        pagination={{ pageSize: 20 }}
        rowSelection={{
          selectedRowKeys,
          onChange: (keys) => setSelectedRowKeys(keys),
          getCheckboxProps: (record) => ({
            disabled: record.status === 'scheduled' || record.status === 'pending' || record.status === 'finished'
          })
        }}
      />

      <Modal
        open={modalOpen}
        title={editingId ? '编辑生产工程单' : '新增生产工程单'}
        onCancel={() => setModalOpen(false)}
        onOk={handleSave}
        width={1000}
        maskClosable={false}
      >
        <Form form={form} layout="vertical">
          <Row gutter={16}>
            <Col span={6}>
              <Form.Item label="工程单号" name="order_no"><Input placeholder="自动生成" /></Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item label="PO号" name="po_no"><Input placeholder="客户PO号" /></Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item label="客户" name="customer_id" rules={[{ required: true, message: '请选择客户' }]}>
                <Select placeholder="请选择客户" showSearch optionFilterProp="children">
                  {customerList.map(c => <Select.Option key={c.id} value={c.id}>{c.customer_name}</Select.Option>)}
                </Select>
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item label="产品名称" name="product_name"><Input placeholder="如：双面白" /></Form.Item>
            </Col>
          </Row>

          {/* 匹配销售单 */}
          <Row gutter={16}>
            <Col span={24}>
              <Form.Item label="关联销售单" name="sales_order_id">
                <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                  <Button onClick={openSalesSelect}>选择销售单匹配</Button>
                  {form.getFieldValue('sales_order_id') && (
                    <Button type="link" onClick={viewLinkedSales}>
                      查看已匹配的销售单
                    </Button>
                  )}
                  <span style={{ color: '#999', fontSize: 12 }}>匹配后自动带入客户、产品、数量、规格等信息</span>
                </div>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={6}>
              <Form.Item label="数量" name="quantity"><Input type="number" placeholder="数量" /></Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item label="规格宽(mm)" name="spec_width"><Input type="number" placeholder="如：889" /></Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item label="规格长(mm)" name="spec_length"><Input type="number" placeholder="如：565" /></Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item label="总克重" name="total_gram"><Input type="number" placeholder="自动计算" /></Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={6}>
              <Form.Item label="客户制令" name="customer_order_no"><Input /></Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item label="厚度" name="thickness"><Input /></Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item label="湿度" name="humidity"><Input /></Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item label="交期" name="produce_date"><DatePicker style={{ width: '100%' }} /></Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={6}>
              <Form.Item label="使用品牌" name="brand"><Input /></Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item label="尺寸误差" name="size_error"><Input /></Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item label="对角线误差" name="diagonal_error"><Input placeholder="默认：2MM内" /></Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item label="损耗上限" name="loss_limit"><Input placeholder="默认：2%" /></Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="生产工艺" name="craft"><Input placeholder="自动生成，如：98+450+400+90" disabled /></Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="包装方式" name="package_method"><Input placeholder="如：1100*1" /></Form.Item>
            </Col>
          </Row>

          <div style={{ marginBottom: 8, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <b>配料明细（共 {items.length} 层）</b>
            <Space>
              <Button size="small" type="primary" onClick={autoCalcQuantity}>自动计算用量</Button>
              <Button size="small" type="dashed" onClick={addLayer}>+ 加一层</Button>
            </Space>
          </div>

          <div style={{ marginBottom: 8, fontSize: 12, color: '#999' }}>
            提示：填好数量、规格宽长、损耗上限，选好每层原料后，点"自动计算用量"自动算出每层卷筒用量（含损耗）
          </div>
          <div style={{ border: '1px solid #d9d9d9', borderRadius: 4, padding: 8, marginBottom: 16, maxHeight: 300, overflowY: 'auto' }}>
            {items.map((item, index) => (
              <div key={index} style={{ display: 'flex', gap: 8, marginBottom: 8, alignItems: 'center' }}>
                <span style={{ width: 50, fontWeight: 'bold' }}>第{index + 1}层</span>
                <Button onClick={() => openRollSelect(index)} style={{ width: 220, textAlign: 'left' }}>
                  {item.roll_name || '点击选择原料'}
                </Button>
                <Input
                  placeholder="实发重量(吨)"
                  type="number"
                  step="0.001"
                  value={item.quantity}
                  onChange={e => updateItem(index, 'quantity', Number(e.target.value))}
                  style={{ width: 120 }}
                />
                <Input
                  placeholder="备注"
                  value={item.remark}
                  onChange={e => updateItem(index, 'remark', e.target.value)}
                  style={{ width: 150 }}
                />
                <span style={{ width: 80, color: '#666' }}>¥{item.amount?.toFixed(2)}</span>
                <Button size="small" danger onClick={() => removeLayer(index)} disabled={items.length <= 1}>删</Button>
              </div>
            ))}
          </div>

          <div style={{ textAlign: 'right', marginBottom: 16, fontWeight: 600, fontSize: 16 }}>
            合计领料金额：¥{items.reduce((s, i) => s + (i.amount || 0), 0).toFixed(2)}
          </div>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item label="制表人" name="maker"><Input /></Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item label="审核" name="checker"><Input /></Form.Item>
            </Col>
            <Col span={24}>
              <Form.Item label="备注" name="remark"><Input.TextArea rows={2} /></Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>

      <Modal
        open={rollSelectModalOpen}
        title="选择原料"
        onCancel={() => setRollSelectModalOpen(false)}
        footer={null}
        width={1000}
      >
        <div style={{ marginBottom: 12, display: 'flex', gap: 8 }}>
          <Select
            value={rollSearchField}
            onChange={val => setRollSearchField(val)}
            style={{ width: 120 }}
          >
            <Select.Option value="all">全部字段</Select.Option>
            <Select.Option value="name">物理分类</Select.Option>
            <Select.Option value="gram">克重</Select.Option>
            <Select.Option value="width">幅宽</Select.Option>
            <Select.Option value="raw_no">卷筒编号</Select.Option>
          </Select>
          <Input
            placeholder="输入搜索值"
            value={rollSearchText}
            onChange={e => setRollSearchText(e.target.value)}
            style={{ width: 300 }}
            allowClear
          />
        </div>
        <Table
          rowKey="id"
          dataSource={filteredRollList}
          size="small"
          pagination={{ pageSize: 8 }}
          columns={[
            { title: '物理分类', dataIndex: 'category_id', width: 280, render: (v, record) => getCategoryPath(v) },
            { title: '克重(g)', dataIndex: 'gram', width: 80 },
            { title: '幅宽(mm)', dataIndex: 'width', width: 90 },
            { title: '卷筒编号', dataIndex: 'raw_no', width: 160 },
            { title: '剩余库存(吨)', dataIndex: 'stock_weight', width: 100, render: v => Number(v).toFixed(3) },
            { title: '吨价(元/吨)', dataIndex: 'ton_price', width: 100, render: v => v ? Number(v).toFixed(2) : '-' },
            {
              title: '操作', width: 70, fixed: 'right',
              render: (_, record) => <Button size="small" type="primary" onClick={() => selectRoll(record)}>选择</Button>
            }
          ]}
        />
      </Modal>

      <Modal
        open={returnModalOpen}
        title="退料完成"
        onCancel={() => setReturnModalOpen(false)}
        onOk={handleReturn}
        width={600}
      >
        <p style={{ color: '#666', marginBottom: 16 }}>根据成品实际重量，填写每层退回的卷料数量（吨）</p>
        {returnItems.map((item, index) => (
          <div key={index} style={{ display: 'flex', gap: 8, marginBottom: 8, alignItems: 'center' }}>
            <span style={{ width: 80 }}>第{item.layer_no}层</span>
            <span style={{ width: 180 }}>{item.roll_name}</span>
            <span style={{ width: 100, color: '#666' }}>领用：{item.quantity}吨</span>
            <Input
              placeholder="退回数量"
              type="number"
              step="0.001"
              value={item.return_quantity}
              onChange={e => {
                const newItems = [...returnItems];
                newItems[index].return_quantity = Number(e.target.value);
                setReturnItems(newItems);
              }}
              style={{ width: 120 }}
            />
            <span>吨</span>
          </div>
        ))}
      </Modal>

      {/* 排单日期选择弹窗 */}
      <Modal
        open={scheduleModalOpen}
        title="选择排单日期"
        onCancel={() => setScheduleModalOpen(false)}
        onOk={handleSchedule}
        width={400}
      >
        <p style={{ marginBottom: 16 }}>已选择 {selectedRowKeys.length} 张工单，请指派生产日期：</p>
        <DatePicker
          style={{ width: '100%' }}
          value={scheduleDate}
          onChange={setScheduleDate}
          placeholder="选择排单日期"
        />
      </Modal>

      {/* 销售单选择弹窗 */}
      <Modal
        open={salesSelectModalOpen}
        title="选择销售单匹配"
        onCancel={() => setSalesSelectModalOpen(false)}
        footer={null}
        width={900}
      >
        <Input
          placeholder="搜索订单号/客户名称"
          value={salesSearchText}
          onChange={e => setSalesSearchText(e.target.value)}
          style={{ marginBottom: 12, width: 300 }}
          allowClear
        />
        <Table
          rowKey="id"
          dataSource={filteredSalesList}
          size="small"
          pagination={{ pageSize: 8 }}
          columns={[
            { title: '订单号', dataIndex: 'order_no', width: 180 },
            { title: '客户', dataIndex: 'customer_name', width: 180 },
            { title: '状态', dataIndex: 'status', width: 100, render: v => SALES_STATUS_MAP[v] || v },
            { title: '交期', dataIndex: 'delivery_date', width: 120 },
            {
              title: '操作', width: 100,
              render: (_, record) => <Button size="small" type="primary" onClick={() => selectSalesOrder(record)}>匹配</Button>
            }
          ]}
        />
      </Modal>

      {/* 销售单详情弹窗 */}
      <Modal
        open={salesDetailModalOpen}
        title="销售单详情"
        onCancel={() => setSalesDetailModalOpen(false)}
        footer={null}
        width={800}
      >
        {currentSalesOrder && (
          <div>
            <div style={{ marginBottom: 16, lineHeight: 2 }}>
              <p><b>订单号：</b>{currentSalesOrder.order_no}</p>
              <p><b>客户：</b>{currentSalesOrder.customer_name}</p>
              <p><b>状态：</b>{currentSalesOrder.status}</p>
              <p><b>交期：</b>{currentSalesOrder.delivery_date || '-'}</p>
              <p><b>备注：</b>{currentSalesOrder.remark || '-'}</p>
            </div>
            <Table
              rowKey="id"
              dataSource={currentSalesOrder.items || []}
              size="small"
              pagination={false}
              columns={[
                { title: '产品名称', dataIndex: 'product_name' },
                { title: '规格', width: 120, render: (_, r) => `${r.width || ''}×${r.length || ''}` },
                { title: '数量', dataIndex: 'quantity', width: 80 },
                { title: '实克', dataIndex: 'actual_gram', width: 80 },
                { title: '虚克', dataIndex: 'nominal_gram', width: 80 },
                { title: '吨价', dataIndex: 'ton_price', width: 100, render: v => v ? `¥${Number(v).toFixed(2)}` : '-' }
              ]}
            />
          </div>
        )}
      </Modal>
    </div>
  );
}
