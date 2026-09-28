import React, { useState, useEffect, useMemo, useRef } from 'react';
import { Form, Input, Button, Table, message, Modal, Select, Space, Popover, Checkbox, Tag, InputNumber, Cascader, Badge } from 'antd';
import { api } from './api';

const SEARCH_FIELDS = [
  { label: '全部字段', value: 'all' },
  { label: '品名', value: 'name' },
  { label: '客户', value: 'customer' },
  { label: '工单号', value: 'work_order' },
  { label: '规格', value: 'spec' },
  { label: '备注', value: 'remark' },
]

const ALL_COLUMNS = [
  { key: 'name', label: '品名' },
  { key: 'customer', label: '客户' },
  { key: 'category', label: '分类' },
  { key: 'work_order_no', label: '工单号' },
  { key: 'spec', label: '规格' },
  { key: 'actual_gram', label: '实克' },
  { key: 'nominal_gram', label: '虚克' },
  { key: 'quantity', label: '可用库存' },
  { key: 'pending_out_qty', label: '待出库' },
  { key: 'unit', label: '单位' },
  { key: 'remark', label: '备注' },
  { key: 'action', label: '操作' },
]
const DEFAULT_VISIBLE_COLS = ['name', 'customer', 'category', 'work_order_no', 'spec', 'actual_gram', 'nominal_gram', 'quantity', 'pending_out_qty', 'unit', 'action']

const UNIT_PRESETS = ['令', '张', '吨', '包', '箱', '个', '卷']

export default function ProductWarehouse() {
  const [list, setList] = useState([]);
  const [pcList, setPcList] = useState([]);          // 成品分类（独立）
  const [pnList, setPnList] = useState([]);          // 成品品名（独立）
  const [customerList, setCustomerList] = useState([]); // 客户档案
  const [pendingList, setPendingList] = useState([]);

  const [searchText, setSearchText] = useState("");
  const [searchField, setSearchField] = useState("all");
  const [selectedCategoryId, setSelectedCategoryId] = useState(null);
  const [selectedCustomerId, setSelectedCustomerId] = useState(null); // 客户筛选

  const [visibleCols, setVisibleCols] = useState(() => {
    try {
      const saved = localStorage.getItem('product_visible_cols');
      if (saved) return JSON.parse(saved);
    } catch (e) {}
    return DEFAULT_VISIBLE_COLS;
  })
  useEffect(() => {
    try { localStorage.setItem('product_visible_cols', JSON.stringify(visibleCols)); } catch (e) {}
  }, [visibleCols])

  // 新增/编辑成品
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [editForm] = Form.useForm();

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

  // 入库
  const [stockInOpen, setStockInOpen] = useState(false);
  const [stockInItem, setStockInItem] = useState(null);
  const [stockInQty, setStockInQty] = useState("");
  const [stockInReason, setStockInReason] = useState("");

  // 移入待出库
  const [pendingOutOpen, setPendingOutOpen] = useState(false);
  const [pendingOutItem, setPendingOutItem] = useState(null);
  const [pendingOutQty, setPendingOutQty] = useState("");
  const [pendingOutReason, setPendingOutReason] = useState("");

  // 待出库管理
  const [pendingMgrOpen, setPendingMgrOpen] = useState(false);
  const [selectedPending, setSelectedPending] = useState([]); // 选中的待出库记录

  // 删除成品
  const [delModalOpen, setDelModalOpen] = useState(false);
  const [delId, setDelId] = useState(null);

  // 成品分类管理
  const [catMgrOpen, setCatMgrOpen] = useState(false);
  const [catEditOpen, setCatEditOpen] = useState(false);
  const [editingCatId, setEditingCatId] = useState(null);
  const [catParentId, setCatParentId] = useState(null);
  const [catForm] = Form.useForm();
  const [delCatOpen, setDelCatOpen] = useState(false);
  const [delCatId, setDelCatId] = useState(null);
  const [delCatConfirm, setDelCatConfirm] = useState("");

  // 成品品名管理
  const [pnMgrOpen, setPnMgrOpen] = useState(false);
  const [pnInput, setPnInput] = useState("");


  const loadData = async () => {
    try {
      const [pRes, pcRes, pnRes, cRes, poRes] = await Promise.all([
        api.get("/api/product"),
        api.get("/api/product_category"),
        api.get("/api/product_name_finished"),
        api.get("/api/customer"),
        api.get("/api/pending_out", { params: { status: 'pending' } })
      ])
      setList(pRes.data);
      setPcList(pcRes.data);
      setPnList(pnRes.data);
      setCustomerList(cRes.data);
      setPendingList(poRes.data);
    } catch (e) {
      message.error("加载失败：" + (e.response?.data?.detail || e.message))
    }
  }

  useEffect(() => { loadData() }, [])

  // ========== 工具 ==========
  function getPnName(id) {
    const p = pnList.find(x => x.id === id);
    return p?.name || "";
  }
  function getCustomerName(id) {
    const c = customerList.find(x => x.id === id);
    return c?.customer_name || "";
  }
  function getCatName(id) {
    const c = pcList.find(x => x.id === id);
    return c?.name || "";
  }
  function getCategoryPath(catId) {
    if (!catId) return "";
    const path = [];
    let cur = pcList.find(x => x.id === catId);
    while (cur) {
      path.unshift(cur.name);
      cur = cur.parent_id ? pcList.find(x => x.id === cur.parent_id) : null;
    }
    return path.join(" / ");
  }
  function getCatLevel(catId) {
    let level = 1;
    let cur = pcList.find(x => x.id === catId);
    while (cur?.parent_id) {
      level++;
      cur = pcList.find(x => x.id === cur.parent_id);
    }
    return level;
  }

  const level1List = useMemo(() => pcList.filter(x => x.parent_id === null), [pcList])
  function getChildren(pid) { return pcList.filter(x => x.parent_id === pid) }

  const cascaderOptions = useMemo(() => {
    function build(pid) {
      return pcList.filter(c => c.parent_id === pid).map(c => ({
        value: c.id, label: c.name, children: build(c.id)
      }))
    }
    return build(null)
  }, [pcList])

  function catIdToCascaderValue(catId) {
    if (!catId) return undefined;
    const path = [];
    let cur = pcList.find(x => x.id === catId);
    while (cur) {
      path.unshift(cur.id);
      cur = cur.parent_id ? pcList.find(x => x.id === cur.parent_id) : null;
    }
    return path;
  }

  // ========== 新增/编辑成品 ==========
  const openAdd = () => {
    setEditingId(null);
    setSaveStatus('idle');
    setLastSavedTime(null);
    editForm.resetFields();
    editForm.setFieldsValue({ quantity: 0, unit: "令", actual_gram: 0, nominal_gram: 0, customer_id: undefined });
    setEditModalOpen(true);
  }
  const openEdit = (record) => {
    setEditingId(record.id);
    setSaveStatus('idle');
    setLastSavedTime(null);
    editForm.setFieldsValue({
      product_name_id: record.product_name_id,
      customer_id: record.customer_id || undefined,
      category_path: catIdToCascaderValue(record.category_id),
      work_order_no: record.work_order_no || "",
      spec: record.spec || "",
      actual_gram: record.actual_gram,
      nominal_gram: record.nominal_gram,
      quantity: record.quantity,
      unit: record.unit,
      remark: record.remark || ""
    })
    setEditModalOpen(true);
  }
  const handleSave = async () => {
    try {
      const values = await editForm.validateFields();
      const catPath = values.category_path;
      const category_id = catPath && catPath.length > 0 ? catPath[catPath.length - 1] : null;
      const payload = {
        product_name_id: Number(values.product_name_id),
        customer_id: values.customer_id ? Number(values.customer_id) : null,
        category_id,
        work_order_no: values.work_order_no || null,
        spec: values.spec || "",
        actual_gram: Number(values.actual_gram) || 0,
        nominal_gram: Number(values.nominal_gram) || 0,
        quantity: Number(values.quantity) || 0,
        unit: values.unit || "令",
        remark: values.remark || ""
      }
      if (editingId) {
        await api.put(`/api/product/${editingId}`, payload);
        message.success("修改成功");
      } else {
        await api.post("/api/product", payload);
        message.success("新增成功");
      }
      setEditModalOpen(false);
      loadData();
    } catch (err) {
      if (err.errorFields) return;
      message.error(err.response?.data?.detail || "保存失败")
    }
  }

  // ========== 入库 ==========
  const openStockIn = (record) => {
    setStockInItem(record);
    setStockInQty("");
    setStockInReason("");
    setStockInOpen(true);
  }
  const handleStockIn = async () => {
    const num = Number(stockInQty);
    if (!stockInQty || isNaN(num) || num <= 0) {
      message.warning("请输入大于0的入库数量");
      return;
    }
    try {
      await api.post(`/api/product/${stockInItem.id}/stock_in`, { quantity: num, reason: stockInReason || "" });
      message.success(`入库 ${num} ${stockInItem.unit} 成功`);
      setStockInOpen(false);
      loadData();
    } catch (err) {
      message.error(err.response?.data?.detail || "入库失败")
    }
  }

  // ========== 移入待出库 ==========
  const openPendingOut = (record) => {
    setPendingOutItem(record);
    setPendingOutQty("");
    setPendingOutReason("");
    setPendingOutOpen(true);
  }
  const handlePendingOut = async () => {
    const num = Number(pendingOutQty);
    if (!pendingOutQty || isNaN(num) || num <= 0) {
      message.warning("请输入大于0的出库数量");
      return;
    }
    const available = Number(pendingOutItem.quantity) - Number(pendingOutItem.pending_out_qty || 0);
    if (num > available) {
      message.error(`可用库存不足！可用只有 ${available.toFixed(2)} ${pendingOutItem.unit}，你要移入 ${num} ${pendingOutItem.unit}`);
      return;
    }
    try {
      await api.post(`/api/product/${pendingOutItem.id}/pending_out`, { quantity: num, reason: pendingOutReason || "" });
      message.success(`已移入待出库 ${num} ${pendingOutItem.unit}，库存已扣减`);
      setPendingOutOpen(false);
      loadData();
    } catch (err) {
      message.error(err.response?.data?.detail || "操作失败")
    }
  }

  // ========== 待出库管理 ==========
  const cancelPending = async (record) => {
    if (!window.confirm(`确定取消这笔待出库？数量将加回可用库存。`)) return;
    try {
      await api.post(`/api/pending_out/${record.id}/cancel`);
      message.success("已取消，库存已加回");
      loadData();
    } catch (err) {
      message.error(err.response?.data?.detail || "取消失败")
    }
  }
  const confirmPending = async (record) => {
    if (!window.confirm(`确认出库？确认后将从待出库移除，不可撤销。`)) return;
    try {
      await api.post(`/api/pending_out/${record.id}/confirm`);
      message.success("已确认出库");
      loadData();
    } catch (err) {
      message.error(err.response?.data?.detail || "确认失败")
    }
  }

  // ========== 删除成品 ==========
  const handleDelete = async () => {
    if (!delId) return;
    try {
      await api.delete(`/api/product/${delId}`);
      message.success("删除成功");
      setDelModalOpen(false);
      setDelId(null);
      loadData();
    } catch (err) {
      message.error(err.response?.data?.detail || "删除失败")
    }
  }

  // ========== 成品分类管理 ==========
  const openAddCat = (parentId = null) => {
    setEditingCatId(null);
    setCatParentId(parentId);
    catForm.resetFields();
    catForm.setFieldsValue({ warn_threshold: null });
    setCatEditOpen(true);
  }
  const openEditCat = (record) => {
    setEditingCatId(record.id);
    setCatParentId(record.parent_id);
    catForm.setFieldsValue({ name: record.name, warn_threshold: record.warn_threshold })
    setCatEditOpen(true);
  }
  const handleSaveCat = async () => {
    try {
      const values = await catForm.validateFields();
      const payload = {
        name: values.name,
        parent_id: catParentId,
        warn_threshold: values.warn_threshold != null ? Number(values.warn_threshold) : null
      }
      if (editingCatId) {
        await api.put(`/api/product_category/${editingCatId}`, payload);
        message.success("分类修改成功");
      } else {
        await api.post("/api/product_category", payload);
        message.success("分类新增成功");
      }
      setCatEditOpen(false);
      loadData();
    } catch (err) {
      if (err.errorFields) return;
      message.error(err.response?.data?.detail || "保存失败")
    }
  }
  const openDelCat = (id) => {
    setDelCatId(id);
    setDelCatConfirm("");
    setDelCatOpen(true);
  }
  const handleDelCat = async () => {
    const cat = pcList.find(x => x.id === delCatId);
    if (delCatConfirm !== cat?.name) {
      message.warning("请输入分类名称确认删除");
      return;
    }
    try {
      await api.delete(`/api/product_category/${delCatId}`);
      message.success("分类已删除（含子分类）");
      setDelCatOpen(false);
      setDelCatId(null);
      loadData();
    } catch (err) {
      message.error(err.response?.data?.detail || "删除失败")
    }
  }

  const renderCatTree = (parentId, level) => {
    const children = getChildren(parentId);
    return children.map(c => (
      <div key={c.id}>
        <div style={{
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          padding: '6px 12px', paddingLeft: 12 + level * 24,
          borderBottom: '1px solid #f0f0f0', background: level % 2 ? '#fafafa' : '#fff'
        }}>
          <span>
            <b>{c.name}</b>
            <Tag color="blue" style={{ marginLeft: 8 }}>第{level}级</Tag>
            {c.warn_threshold != null && <Tag color="orange" style={{ marginLeft: 4 }}>预警 {c.warn_threshold}</Tag>}
          </span>
          <Space>
            {level < 4 && <Button size="small" type="link" onClick={() => openAddCat(c.id)}>+ 子分类</Button>}
            <Button size="small" type="link" onClick={() => openEditCat(c)}>编辑</Button>
            <Button size="small" type="link" danger onClick={() => openDelCat(c.id)}>删除</Button>
          </Space>
        </div>
        {renderCatTree(c.id, level + 1)}
      </div>
    ))
  }

  // ========== 成品品名管理 ==========
  const handleAddPn = async () => {
    if (!pnInput.trim()) {
      message.warning("请输入品名");
      return;
    }
    try {
      await api.post("/api/product_name_finished", { name: pnInput.trim() });
      message.success("品名新增成功");
      setPnInput("");
      loadData();
    } catch (err) {
      message.error(err.response?.data?.detail || "新增失败")
    }
  }
  const handleDeletePn = async (id) => {
    const name = getPnName(id);
    const used = list.filter(x => x.product_name_id === id).length;
    if (used > 0) {
      message.warning(`该品名下还有 ${used} 条成品，无法删除`);
      return;
    }
    if (!window.confirm(`确定删除品名「${name}」？`)) return;
    try {
      await api.delete(`/api/product_name_finished/${id}`);
      message.success("品名已删除");
      loadData();
    } catch (err) {
      message.error(err.response?.data?.detail || "删除失败")
    }
  }

  // ========== 过滤 ==========
  const filterList = useMemo(() => {
    const kw = String(searchText || "").trim().toLowerCase();
    return list.filter(item => {
      if (selectedCategoryId !== null) {
        function getDescendants(pid) {
          const kids = pcList.filter(c => c.parent_id === pid).map(i => i.id);
          let all = [...kids];
          kids.forEach(k => all = all.concat(getDescendants(k)));
          return all;
        }
        if (![selectedCategoryId, ...getDescendants(selectedCategoryId)].includes(item.category_id)) return false;
      }
      // 客户筛选
      if (selectedCustomerId !== null && selectedCustomerId !== undefined) {
        if (item.customer_id !== selectedCustomerId) return false;
      }
      if (!kw) return true;
      let target = "";
      switch (searchField) {
        case 'name': target = getPnName(item.product_name_id); break;
        case 'customer': target = getCustomerName(item.customer_id); break;
        case 'work_order': target = String(item.work_order_no || ""); break;
        case 'spec': target = String(item.spec || ""); break;
        case 'remark': target = String(item.remark || ""); break;
        case 'all':
        default:
          target = [getPnName(item.product_name_id), getCustomerName(item.customer_id), getCategoryPath(item.category_id), item.work_order_no, item.spec, item.remark]
            .map(v => String(v || "")).join(" ");
          break;
      }
      return target.toLowerCase().includes(kw);
    })
  }, [list, searchText, searchField, selectedCategoryId, selectedCustomerId, pcList, pnList, customerList])

  const stat = useMemo(() => {
    const totalKinds = filterList.length;
    const totalQty = filterList.reduce((s, i) => s + (Number(i.quantity) || 0), 0);
    const totalPending = filterList.reduce((s, i) => s + (Number(i.pending_out_qty) || 0), 0);
    
    // 计算总吨数：长×宽×克重×张数 / 1e12
    const totalTons = filterList.reduce((s, i) => {
      const spec = String(i.spec || "");
      const m = spec.match(/(\d+)\s*[*xX×]\s*(\d+)/);
      if (!m) return s;
      const width = Number(m[1]);
      const length = Number(m[2]);
      const gram = Number(i.actual_gram || 0);
      const qty = Number(i.quantity || 0);
      return s + (width * length * gram * qty / 1e12);
    }, 0);
    const groups = {};
    filterList.forEach(item => {
      const catName = getCatName(item.category_id) || "未分类";
      const unit = item.unit || "令";
      const key = `${catName}__${unit}`;
      if (!groups[key]) groups[key] = { category: catName, unit, quantity: 0 };
      groups[key].quantity += Number(item.quantity) || 0;
    })
    return { totalKinds, totalQty, totalPending, totalTons, groups: Object.values(groups) };
  }, [filterList, pcList])

  // ========== 列 ==========
  const allColumnDefs = {
    name: { title: "品名", dataIndex: "product_name_id", key: "name", width: 160, fixed: 'left', render: v => getPnName(v) },
    customer: { title: "客户归属", dataIndex: "customer_id", key: "customer", width: 160, render: v => v ? <Tag color="purple">{getCustomerName(v)}</Tag> : <span style={{color:'#999'}}>未指定</span> },
    category: { title: "分类", dataIndex: "category_id", key: "category", width: 180, render: v => getCategoryPath(v) },
    work_order_no: { title: "工单号", dataIndex: "work_order_no", key: "work_order_no", width: 140 },
    spec: { title: "规格", dataIndex: "spec", key: "spec", width: 120 },
    actual_gram: { title: "实克", dataIndex: "actual_gram", key: "actual_gram", width: 90 },
    nominal_gram: { title: "虚克", dataIndex: "nominal_gram", key: "nominal_gram", width: 90 },
    quantity: { title: "库存情况", dataIndex: "quantity", key: "quantity", width: 160, render: (val, r) => {
      const qty = Number(val) || 0;
      const pending = Number(r.pending_out_qty) || 0;
      const available = qty - pending;
      return (
        <div>
          <div style={{ color: available < 0 ? '#cf1322' : '#389e0d', fontWeight: 600 }}>
            总库存: {qty.toFixed(2)}
          </div>
          {pending > 0 && <div style={{ fontSize: 11, color: '#d46b08' }}>锁定: {pending.toFixed(2)}</div>}
          <div style={{ fontSize: 11, color: available < 0 ? '#cf1322' : '#666' }}>
            可用: {available.toFixed(2)}
          </div>
          {available < 0 && <div style={{ fontSize: 11, color: '#cf1322' }}>⚠️ 不足</div>}
        </div>
      );
    } },
    pending_out_qty: { title: "待出库", dataIndex: "pending_out_qty", key: "pending_out_qty", width: 100, render: val => Number(val) > 0 ? <Tag color="orange">{val.toFixed(2)}</Tag> : "0.00" },
    unit: { title: "单位", dataIndex: "unit", key: "unit", width: 80 },
    remark: { title: "备注", dataIndex: "remark", key: "remark", width: 160 },
    action: {
      title: "操作", key: "action", width: 280, fixed: 'right',
      render: (_, record) => (
        <Space wrap>
          <Button size="small" type="primary" onClick={() => openStockIn(record)}>入库</Button>
          <Button size="small" danger onClick={() => openPendingOut(record)}>移入待出库</Button>
          <Button size="small" onClick={() => openEdit(record)}>编辑</Button>
          <Button size="small" danger type="link" onClick={() => { setDelId(record.id); setDelModalOpen(true) }}>删除</Button>
        </Space>
      )
    },
  }
  const columns = useMemo(() => visibleCols.map(key => allColumnDefs[key]).filter(Boolean), [visibleCols, pcList, pnList, customerList])

  const colSettingContent = (
    <div style={{ width: 180 }}>
      <div style={{ marginBottom: 8, display: 'flex', justifyContent: 'space-between' }}>
        <Button type="link" size="small" onClick={() => setVisibleCols(ALL_COLUMNS.map(c => c.key))}>全选</Button>
        <Button type="link" size="small" onClick={() => setVisibleCols(DEFAULT_VISIBLE_COLS)}>恢复默认</Button>
      </div>
      <Checkbox.Group value={visibleCols} onChange={vals => setVisibleCols(vals)}
        style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        {ALL_COLUMNS.map(col => <Checkbox key={col.key} value={col.key}>{col.label}</Checkbox>)}
      </Checkbox.Group>
    </div>
  )

  const pendingColumns = [
    { title: "成品品名", dataIndex: "product_id", render: v => getPnName(list.find(p => p.id === v)?.product_name_id) },
    { title: "客户", dataIndex: "product_id", render: v => { const p = list.find(x => x.id === v); return p?.customer_id ? getCustomerName(p.customer_id) : ""; } },
    { title: "规格", dataIndex: "product_id", render: v => list.find(p => p.id === v)?.spec || "" },
    { title: "数量", dataIndex: "quantity", render: (v, r) => `${v.toFixed(2)} ${list.find(p => p.id === r.product_id)?.unit || ''}` },
    { title: "原因", dataIndex: "reason" },
    { title: "创建时间", dataIndex: "created_at", width: 160, render: (v) => {
      if (!v) return "-";
      const days = Math.floor((new Date() - new Date(v)) / (1000 * 60 * 60 * 24));
      return <span style={{ color: days > 5 ? "#cf1322" : undefined, fontWeight: days > 5 ? 600 : 400 }}>
        {v}
        {days > 5 && <span style={{ color: "#cf1322" }}>（超{days - 5}天）</span>}
      </span>;
    } },
    {
      title: "操作", width: 180,
      render: (_, record) => (
        <Space>
          <Button size="small" type="primary" onClick={() => confirmPending(record)}>确认出库</Button>
          <Button size="small" onClick={() => cancelPending(record)}>取消(加回)</Button>
        </Space>
      )
    }
  ]

  return (
    <div style={{ padding: 20 }}>
      {/* 顶部按钮 */}
      <div style={{ marginBottom: 12, display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
        <Button type="primary" onClick={openAdd}>新增成品</Button>
        <Button onClick={() => setPnMgrOpen(true)}>品名管理</Button>
        <Button onClick={() => setCatMgrOpen(true)}>分类管理</Button>
        <Badge count={pendingList.length} size="small" offset={[-4, 2]}>
          <Button onClick={() => setPendingMgrOpen(true)}>待出库管理</Button>
        </Badge>

        <Select value={searchField} onChange={val => setSearchField(val)} style={{ width: 120 }}>
          {SEARCH_FIELDS.map(f => <Select.Option key={f.value} value={f.value}>{f.label}</Select.Option>)}
        </Select>
        <Input placeholder={`输入${SEARCH_FIELDS.find(f => f.value === searchField)?.label || '关键词'}搜索`}
          value={searchText} onChange={e => setSearchText(e.target.value)}
          style={{ width: 240 }} allowClear />

        <Popover content={colSettingContent} title="列显示设置" trigger="click" placement="bottomRight">
          <Button>列设置</Button>
        </Popover>
      </div>

      {/* 筛选栏 */}
      <div style={{ marginBottom: 16, display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
        <span>分类筛选：</span>
        <Button type={selectedCategoryId === null ? "primary" : "default"} onClick={() => setSelectedCategoryId(null)}>全部</Button>
        {level1List.map(l1 => {
          const children = getChildren(l1.id)
          return (
            <Select key={l1.id}
              value={selectedCategoryId === l1.id ? l1.id : undefined}
              style={{ width: 'auto', minWidth: 110 }}
              placeholder={l1.name}
              onSelect={(val) => setSelectedCategoryId(Number(val))}
              options={[
                { value: String(l1.id), label: `${l1.name}（全部）` },
                ...children.map(l2 => ({ value: String(l2.id), label: l2.name }))
              ]}
            />
          )
        })}
        <span style={{ marginLeft: 20 }}>客户筛选：</span>
        <Button type={selectedCustomerId === null ? "primary" : "default"} onClick={() => setSelectedCustomerId(null)}>全部</Button>
        <Select
          allowClear
          placeholder="选择客户"
          style={{ width: 200 }}
          value={selectedCustomerId || undefined}
          onChange={val => setSelectedCustomerId(val)}
        >
          {customerList.map(c => <Select.Option key={c.id} value={c.id}>{c.customer_name}</Select.Option>)}
        </Select>
      </div>

      <Table dataSource={filterList} rowKey="id" columns={columns} scroll={{ x: 'max-content' }}
        pagination={{ pageSize: 20, showSizeChanger: true, pageSizeOptions: ['10', '20', '50', '100'], showTotal: t => `共 ${t} 条` }}
        footer={() => (
          <div style={{ fontWeight: 600, textAlign: "center", padding: "8px 0", lineHeight: 2 }}>
            汇总：成品品种 <b>{stat.totalKinds}</b> 种
            &nbsp;｜&nbsp; 可用库存合计 <b style={{ color: '#389e0d' }}>{stat.totalQty.toFixed(2)} 张</b>
            &nbsp;｜&nbsp; 约合 <b style={{ color: '#389e0d' }}>{stat.totalTons.toFixed(3)} 吨</b>
            &nbsp;｜&nbsp; 待出库合计 <b style={{ color: '#d46b08' }}>{stat.totalPending.toFixed(2)}</b> 张
            <br />
            按分类统计：
            {stat.groups.length === 0 && <span style={{ color: '#999', marginLeft: 6 }}>暂无</span>}
            {stat.groups.map((g, i) => (
              <Tag key={i} color="blue" style={{ marginLeft: 6 }}>{g.category} {g.quantity.toFixed(2)} {g.unit}</Tag>
            ))}
          </div>
        )}
      />

      {/* 新增/编辑成品弹窗 */}
      <Modal open={editModalOpen}
        title={
          <div style={{display:'flex', alignItems:'center', gap:12}}>
            <span>{editingId ? "编辑成品" : "新增成品"}</span>
            {saveStatus === 'saving' && <span style={{fontSize:13, color:'#fa8c16'}}>正在保存...</span>}
            {saveStatus === 'saved' && <span style={{fontSize:13, color:'#52c41a'}}>✓ 已保存 {lastSavedTime || ''}</span>}
            {saveStatus === 'error' && <span style={{fontSize:13, color:'#ff4d4f'}}>保存失败，请检查必填项</span>}
          </div>
        }
        onCancel={closeEditModal} onOk={handleSave} width={600}>
        <Form form={editForm} layout="vertical" onValuesChange={() => triggerAutoSave()}>
          <div style={{ display: 'flex', gap: 12 }}>
            <Form.Item label="品名" name="product_name_id" style={{ flex: 1 }} rules={[{ required: true, message: "请选择品名" }]}>
              <Select placeholder="请选择品名" showSearch optionFilterProp="label">
                {pnList.map(p => <Select.Option key={p.id} value={p.id} label={p.name}>{p.name}</Select.Option>)}
              </Select>
            </Form.Item>
            <Form.Item label="客户（从客户档案选择）" name="customer_id" style={{ flex: 1 }}>
              <Select placeholder="可留空" allowClear showSearch optionFilterProp="label">
                {customerList.map(c => (
                  <Select.Option key={c.id} value={c.id} label={c.customer_name}>
                    {c.customer_name}（{c.salesperson || '未分配'}）
                  </Select.Option>
                ))}
              </Select>
            </Form.Item>
          </div>
          <div style={{ display: 'flex', gap: 12 }}>
            <Form.Item label="单位" name="unit" style={{ flex: 1 }} rules={[{ required: true }]}>
              <Select showSearch placeholder="选择或输入单位"
                options={UNIT_PRESETS.map(u => ({ label: u, value: u }))}
                filterOption={(input, option) => (option?.label ?? '').includes(input)} />
            </Form.Item>
            <Form.Item label="成品分类（四级联动）" name="category_path" style={{ flex: 2 }}>
              <Cascader options={cascaderOptions} changeOnSelect placeholder="请选择分类（可只选到任意级）" style={{ width: '100%' }} />
            </Form.Item>
          </div>
          <div style={{ display: 'flex', gap: 12 }}>
            <Form.Item label="客户归属（可选）" name="customer_id" style={{ flex: 1 }}>
              <Select allowClear placeholder="选择客户">
                {customerList.map(c => <Select.Option key={c.id} value={c.id}>{c.customer_name}</Select.Option>)}
              </Select>
            </Form.Item>
            <Form.Item label="工单号（可选）" name="work_order_no" style={{ flex: 1 }}>
              <Input placeholder="例如：WO20260821001" />
            </Form.Item>
            <Form.Item label="规格" name="spec" style={{ flex: 1 }}>
              <Input placeholder="例如：787*1092" />
            </Form.Item>
          </div>
          <div style={{ display: 'flex', gap: 12 }}>
            <Form.Item label="实克" name="actual_gram" style={{ flex: 1 }} rules={[{ required: true }]}>
              <InputNumber min={0} step="1" style={{ width: '100%' }} placeholder="实际克重" />
            </Form.Item>
            <Form.Item label="虚克" name="nominal_gram" style={{ flex: 1 }} rules={[{ required: true }]}>
              <InputNumber min={0} step="1" style={{ width: '100%' }} placeholder="标称克重" />
            </Form.Item>
          </div>
          <Form.Item label="初始库存数量" name="quantity" rules={[{ required: true }]}>
            <InputNumber min={0} step="0.01" style={{ width: '100%' }} placeholder="0" />
          </Form.Item>
          <Form.Item label="备注" name="remark">
            <Input.TextArea rows={2} placeholder="可选" />
          </Form.Item>
        </Form>
      </Modal>

      {/* 入库弹窗 */}
      <Modal open={stockInOpen} title="成品入库" onCancel={() => setStockInOpen(false)} onOk={handleStockIn} width={420}>
        {stockInItem && (
          <div>
            <p>品名：<b>{getPnName(stockInItem.product_name_id)}</b></p>
            {stockInItem.customer_id && <p>客户：<b>{getCustomerName(stockInItem.customer_id)}</b></p>}
            <p>当前可用库存：<b style={{ color: '#389e0d' }}>{Number(stockInItem.quantity).toFixed(2)} {stockInItem.unit}</b></p>
            <div style={{ marginBottom: 12 }}>
              <div style={{ marginBottom: 4 }}>入库数量：</div>
              <InputNumber min={0} step="0.01" style={{ width: '100%' }} placeholder="输入入库数量"
                value={stockInQty} onChange={val => setStockInQty(val)} />
            </div>
            <div>
              <div style={{ marginBottom: 4 }}>入库原因（可选）：</div>
              <Input placeholder="例如：生产完工入库 / 退货入库"
                value={stockInReason} onChange={e => setStockInReason(e.target.value)} />
            </div>
          </div>
        )}
      </Modal>

      {/* 移入待出库弹窗 */}
      <Modal open={pendingOutOpen} title="移入待出库（扣减可用库存）"
        onCancel={() => setPendingOutOpen(false)} onOk={handlePendingOut} width={440}>
        {pendingOutItem && (
          <div>
            <p>品名：<b>{getPnName(pendingOutItem.product_name_id)}</b></p>
            {pendingOutItem.customer_id && <p>客户：<b>{getCustomerName(pendingOutItem.customer_id)}</b></p>}
            <p>总库存：<b>{Number(pendingOutItem.quantity).toFixed(2)} {pendingOutItem.unit}</b></p>
            <p>已锁定：<b style={{ color: '#d46b08' }}>{Number(pendingOutItem.pending_out_qty).toFixed(2)} {pendingOutItem.unit}</b></p>
            <p>可用库存：<b style={{ color: (Number(pendingOutItem.quantity) - Number(pendingOutItem.pending_out_qty)) < 0 ? '#cf1322' : '#389e0d' }}>{(Number(pendingOutItem.quantity) - Number(pendingOutItem.pending_out_qty)).toFixed(2)} {pendingOutItem.unit}</b></p>
            <p style={{ color: '#d46b08', fontSize: 13 }}>移入待出库后，可用库存立即扣减；在「待出库管理」中可取消加回或确认出库。</p>
            <div style={{ marginBottom: 12 }}>
              <div style={{ marginBottom: 4 }}>出库数量：</div>
              <InputNumber min={0} step="0.01" style={{ width: '100%' }} placeholder="输入待出库数量"
                value={pendingOutQty} onChange={val => setPendingOutQty(val)} />
            </div>
            <div>
              <div style={{ marginBottom: 4 }}>出库原因（可选）：</div>
              <Input placeholder="例如：客户订单 / 样品寄出"
                value={pendingOutReason} onChange={e => setPendingOutReason(e.target.value)} />
            </div>
          </div>
        )}
      </Modal>

      {/* 待出库管理弹窗 */}
      <Modal open={pendingMgrOpen} title="待出库管理" onCancel={() => setPendingMgrOpen(false)}
        footer={
          <Space>
            <Button danger disabled={selectedPending.length === 0} onClick={async () => {
              if (!window.confirm(`确定取消选中的 ${selectedPending.length} 条待出库记录吗？库存将加回。`)) return;
              try {
                for (const rec of selectedPending) {
                  await api.post(`/api/pending_out/${rec.id}/cancel`);
                }
                message.success("批量取消成功，库存已加回");
                setSelectedPending([]);
                loadData();
              } catch (e) {
                message.error("批量取消失败：" + (e.response?.data?.detail || e.message));
              }
            }}>
              批量取消加回（{selectedPending.length}）
            </Button>
            <Button type="primary" disabled={selectedPending.length === 0} onClick={async () => {
              if (!window.confirm(`确定对选中的 ${selectedPending.length} 条记录批量确认出库吗？不可撤销！`)) return;
              try {
                for (const rec of selectedPending) {
                  await api.post(`/api/pending_out/${rec.id}/confirm`);
                }
                message.success("批量出库成功");
                setSelectedPending([]);
                loadData();
              } catch (e) {
                message.error("批量出库失败：" + (e.response?.data?.detail || e.message));
              }
            }}>
              批量确认出库（{selectedPending.length}）
            </Button>
            <Button onClick={() => setPendingMgrOpen(false)}>关闭</Button>
          </Space>
        } width={900}>
        {pendingList.length === 0 ? (
          <div style={{ color: '#999', textAlign: 'center', padding: 40 }}>暂无待出库记录</div>
        ) : (
          <Table 
            dataSource={pendingList} 
            rowKey="id" 
            columns={pendingColumns} 
            pagination={false} 
            size="small"
            rowSelection={{
              selectedRowKeys: selectedPending.map(r => r.id),
              onChange: (keys, rows) => setSelectedPending(rows)
            }}
          />
        )}
        <div style={{ fontSize: 12, color: '#888', marginTop: 8 }}>
          「确认出库」：从待出库移除，不可撤销；「取消(加回)」：取消待出库，数量加回可用库存。
        </div>
      </Modal>

      {/* 品名管理弹窗 */}
      <Modal open={pnMgrOpen} title="成品品名管理（独立）" onCancel={() => setPnMgrOpen(false)}
        footer={<Button onClick={() => setPnMgrOpen(false)}>关闭</Button>} width={520}>
        <div style={{ marginBottom: 16, display: 'flex', gap: 8 }}>
          <Input placeholder="输入新品名" value={pnInput} onChange={e => setPnInput(e.target.value)}
            onPressEnter={handleAddPn} />
          <Button type="primary" onClick={handleAddPn}>新增品名</Button>
        </div>
        <div style={{ maxHeight: 360, overflow: 'auto', border: '1px solid #f0f0f0', borderRadius: 4 }}>
          {pnList.length === 0 ? (
            <div style={{ color: '#999', textAlign: 'center', padding: 30 }}>暂无品名，请在上方新增</div>
          ) : (
            pnList.map(p => (
              <div key={p.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 12px', borderBottom: '1px solid #f0f0f0' }}>
                <span>{p.name}</span>
                <Button danger size="small" type="link" onClick={() => handleDeletePn(p.id)}>删除</Button>
              </div>
            ))
          )}
        </div>
        <div style={{ fontSize: 12, color: '#888', marginTop: 8 }}>
          品名下有成品时无法删除，请先将成品移到其他品名。
        </div>
      </Modal>

      {/* 成品分类管理弹窗 */}
      <Modal open={catMgrOpen} title="成品分类管理（四级，独立于卷筒仓）"
        onCancel={() => setCatMgrOpen(false)}
        footer={<Space>
          <Button type="primary" onClick={() => openAddCat(null)}>+ 新增一级分类</Button>
          <Button onClick={() => setCatMgrOpen(false)}>关闭</Button>
        </Space>}
        width={720}>
        <div style={{ marginBottom: 8, fontSize: 13, color: '#666' }}>
          第1级：大类｜第2级：纸名｜第3级：克重｜第4级：幅宽/规格。预警阈值可在任意级设置，子级继承父级。
        </div>
        <div style={{ maxHeight: 480, overflow: 'auto', border: '1px solid #f0f0f0', borderRadius: 4 }}>
          {pcList.length === 0 ? (
            <div style={{ color: '#999', textAlign: 'center', padding: 40 }}>暂无分类，请点右上角「+ 新增一级分类」</div>
          ) : (
            renderCatTree(null, 1)
          )}
        </div>
      </Modal>

      {/* 分类新增/编辑弹窗 */}
      <Modal open={catEditOpen} zIndex={3000}
        title={editingCatId ? "编辑分类" : `新增分类（第${catParentId ? getCatLevel(catParentId) + 1 : 1}级）`}
        onCancel={() => setCatEditOpen(false)} onOk={handleSaveCat} width={440}>
        <Form form={catForm} layout="vertical">
          {catParentId && (
            <div style={{ marginBottom: 12, color: '#666', fontSize: 13 }}>
              父分类：<b>{getCatName(catParentId)}</b>（第{getCatLevel(catParentId)}级）
            </div>
          )}
          <Form.Item label="分类名称" name="name" rules={[{ required: true, message: "请输入分类名称" }]}>
            <Input placeholder="例如：灰板成品 / 金盾 / 350G / 787" />
          </Form.Item>
          <Form.Item label="库存预警阈值（可选）" name="warn_threshold">
            <InputNumber min={0} step="0.01" style={{ width: '100%' }} placeholder="留空=不单独设置（继承上级）" />
          </Form.Item>
        </Form>
      </Modal>

      {/* 删除分类确认弹窗 */}
      <Modal open={delCatOpen} title="确认删除分类" zIndex={3000} onCancel={() => { setDelCatOpen(false); setDelCatId(null) }}
        footer={<>
          <Button onClick={() => { setDelCatOpen(false); setDelCatId(null) }}>取消</Button>
          <Button danger type="primary" onClick={handleDelCat} disabled={delCatConfirm !== pcList.find(x => x.id === delCatId)?.name}>确认删除</Button>
        </>}>
        <div>
          <p>将删除分类「<b>{pcList.find(x => x.id === delCatId)?.name}</b>」及其所有子分类，级联删除不可恢复。</p>
          <p>请输入分类名称确认：</p>
          <Input value={delCatConfirm} onChange={e => setDelCatConfirm(e.target.value)} placeholder="输入分类名称" />
        </div>
      </Modal>

      {/* 删除成品确认 */}
      <Modal open={delModalOpen} title="确认删除成品" onCancel={() => { setDelModalOpen(false); setDelId(null) }}
        footer={<>
          <Button onClick={() => { setDelModalOpen(false); setDelId(null) }}>取消</Button>
          <Button danger type="primary" onClick={handleDelete}>确认删除</Button>
        </>}>
        <div>确定要删除这条成品记录？删除后不可恢复。<br />如有待出库记录需先处理。</div>
      </Modal>

    </div>
  )
}
