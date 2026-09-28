import React, { useState, useEffect, useMemo } from 'react';
import { Form, Input, Button, Table, message, Modal, Select, Space, Cascader, Tree, Tag, Popover, Checkbox, Divider } from 'antd';
import { api } from './api';

const SEARCH_FIELDS = [
  { label: '全部字段', value: 'all' },
  { label: '卷筒编号', value: 'raw_no' },
  { label: '品名', value: 'product_name' },
  { label: '物理分类', value: 'category' },
  { label: '幅宽(mm)', value: 'width' },
  { label: '克重(g)', value: 'gram' },
  { label: '备注', value: 'remark' },
]

const ALL_COLUMNS = [
  { key: 'raw_no', label: '卷筒编号' },
  { key: 'product_name', label: '品名' },
  { key: 'category', label: '物理分类' },
  { key: 'width', label: '幅宽(mm)' },
  { key: 'gram', label: '克重(g)' },
  { key: 'weight', label: '本支卷筒重量(吨)' },
  { key: 'stock_weight', label: '剩余库存(吨)' },
  { key: 'remark', label: '备注' },
  { key: 'action', label: '操作' },
]
const DEFAULT_VISIBLE_COLS = ['raw_no','product_name','category','width','gram','stock_weight','action']

export default function RollWarehouse({ onNavigate }) {
  const [form] = Form.useForm();
  const [modalOpen, setModalOpen] = useState(false);
  const [rollList, setRollList] = useState([]);
  const [pcList, setPcList] = useState([]);
  const [pnList, setPnList] = useState([]);
  const [searchText, setSearchText] = useState("");
  const [searchField, setSearchField] = useState("all");
  const [filterCategoryPath, setFilterCategoryPath] = useState(null);

  const [visibleCols, setVisibleCols] = useState(() => {
    try {
      const saved = localStorage.getItem('roll_visible_cols');
      if (saved) return JSON.parse(saved);
    } catch (e) {}
    return DEFAULT_VISIBLE_COLS;
  })

  const [pnModal, setPnModal] = useState(false);
  const [pnForm] = Form.useForm();
  const [pcModal, setPcModal] = useState(false);
  const [pcForm] = Form.useForm();

  const [delModalOpen, setDelModalOpen] = useState(false);
  const [delRollId, setDelRollId] = useState(null);

  // 分类管理弹窗（编辑+删除）
  const [catMgrOpen, setCatMgrOpen] = useState(false);
  const [mgrSelectedId, setMgrSelectedId] = useState(null);
  const [mgrEditName, setMgrEditName] = useState("");
  const [mgrEditThreshold, setMgrEditThreshold] = useState("");
  const [mgrDelConfirm, setMgrDelConfirm] = useState("");

  const [reduceModalOpen, setReduceModalOpen] = useState(false);
  const [currentRoll, setCurrentRoll] = useState(null);
  const [reduceVal, setReduceVal] = useState("");


  const loadData = async () => {
    try {
      const [rollRes, pcRes, pnRes] = await Promise.all([
        api.get("/api/rawroll"),
        api.get("/api/physical_category"),
        api.get("/api/product_name")
      ])
      setRollList(rollRes.data);
      setPcList(pcRes.data);
      setPnList(pnRes.data);
    } catch (e) {
      message.error("加载失败：" + e.message)
    }
  }

  useEffect(() => { loadData() }, [])

  useEffect(() => {
    try { localStorage.setItem('roll_visible_cols', JSON.stringify(visibleCols)); } catch (e) {}
  }, [visibleCols])

  // ================= 分类树工具 =================
  function getChildren(parentId) {
    return pcList.filter(x => x.parent_id === parentId)
  }
  function buildTree(parentId, depth) {
    if (depth >= 4) return undefined;
    const children = getChildren(parentId);
    if (children.length === 0) return undefined;
    return children.map(c => ({
      value: c.id, label: c.name, children: buildTree(c.id, depth + 1)
    }));
  }
  const categoryTree = useMemo(() => {
    return getChildren(null).map(l1 => ({
      value: l1.id, label: l1.name, children: buildTree(l1.id, 1)
    }));
  }, [pcList])

  function buildParentTree(parentId, depth) {
    if (depth >= 3) return undefined;
    const children = getChildren(parentId);
    if (children.length === 0) return undefined;
    return children.map(c => ({
      value: c.id, label: c.name, children: buildParentTree(c.id, depth + 1)
    }));
  }
  const parentCategoryTree = useMemo(() => {
    return getChildren(null).map(l1 => ({
      value: l1.id, label: l1.name, children: buildParentTree(l1.id, 1)
    }));
  }, [pcList])

  // 分类管理弹窗的树形数据（显示预警值）
  const mgrTreeData = useMemo(() => {
    function build(parentId) {
      return getChildren(parentId).map(c => ({
        key: c.id,
        title: c.name + (c.warn_threshold != null ? ` (预警:${c.warn_threshold}吨)` : ''),
        children: build(c.id)
      }));
    }
    return build(null);
  }, [pcList])

  function getPathIds(id) {
    if (!id) return null;
    const path = [];
    let current = pcList.find(x => x.id === id);
    while (current) {
      path.unshift(current.id);
      current = current.parent_id ? pcList.find(x => x.id === current.parent_id) : null;
    }
    return path.length ? path : null;
  }
  function getPathName(id) {
    if (!id) return "";
    const names = [];
    let current = pcList.find(x => x.id === id);
    while (current) {
      names.unshift(current.name);
      current = current.parent_id ? pcList.find(x => x.id === current.parent_id) : null;
    }
    return names.join(" / ");
  }
  function getDescendantIds(parentId) {
    const ids = [parentId];
    getChildren(parentId).forEach(c => ids.push(...getDescendantIds(c.id)));
    return ids;
  }
  function extractNumber(text) {
    if (!text) return null;
    const match = String(text).match(/\d+(\.\d+)?/);
    return match ? Number(match[0]) : null;
  }
  // 向上查找最近的有预警阈值的分类
  function getWarnThreshold(categoryId) {
    let current = pcList.find(x => x.id === categoryId);
    while (current) {
      if (current.warn_threshold != null && current.warn_threshold > 0) {
        return current.warn_threshold;
      }
      current = current.parent_id ? pcList.find(x => x.id === current.parent_id) : null;
    }
    return null;
  }

  const pcParentId = Form.useWatch('parent_id', pcForm);
  const pcParentPath = useMemo(() => getPathIds(pcParentId) || [], [pcParentId, pcList]);
  const newCatLevel = pcParentPath.length + 1;

  // 分类管理弹窗选中分类的信息
  const mgrSelectedCat = mgrSelectedId ? pcList.find(x => x.id === mgrSelectedId) : null;
  const mgrSelectedPath = mgrSelectedId ? getPathName(mgrSelectedId) : "";
  const mgrDescendantCount = mgrSelectedId ? getDescendantIds(mgrSelectedId).length : 0;
  const mgrUsedRollCount = mgrSelectedId
    ? rollList.filter(r => getDescendantIds(mgrSelectedId).includes(r.category_id)).length
    : 0;

  // ================= 删除卷筒 =================
  const handleDelete = async () => {
    if (!delRollId) return;
    try {
      await api.delete(`/api/rawroll/${delRollId}`)
      message.success("删除成功")
      setDelModalOpen(false); setDelRollId(null); loadData();
    } catch (err) {
      message.error(err.response?.data?.detail || "删除失败")
    }
  }

  // ================= 分类管理：保存修改 =================
  const handleSaveCatEdit = async () => {
    if (!mgrSelectedId) return;
    if (!mgrEditName.trim()) {
      message.warning("分类名称不能为空");
      return;
    }
    try {
      await api.put(`/api/physical_category/${mgrSelectedId}`, {
        name: mgrEditName.trim(),
        parent_id: mgrSelectedCat?.parent_id || null,
        warn_threshold: mgrEditThreshold !== "" ? Number(mgrEditThreshold) : null
      });
      message.success("分类修改成功");
      loadData();
    } catch (err) {
      message.error(err.response?.data?.detail || "修改失败")
    }
  }

  // ================= 分类管理：删除 =================
  const handleDeleteCategory = async () => {
    if (!mgrSelectedId) return;
    if (mgrDelConfirm !== mgrSelectedCat?.name) {
      message.error("防呆校验失败：输入的分类名称与选中分类不一致");
      return;
    }
    try {
      await api.delete(`/api/physical_category/${mgrSelectedId}`);
      message.success(`删除成功，共删除 ${mgrDescendantCount} 个分类`);
      setCatMgrOpen(false);
      setMgrSelectedId(null);
      setMgrDelConfirm("");
      loadData();
    } catch (err) {
      message.error(err.response?.data?.detail || "删除分类失败")
    }
  }

  // 打开分类管理弹窗
  const openCatMgr = () => {
    setMgrSelectedId(null);
    setMgrEditName("");
    setMgrEditThreshold("");
    setMgrDelConfirm("");
    setCatMgrOpen(true);
  }

  // 选中分类时填充编辑表单
  const handleMgrSelect = (keys) => {
    const id = keys[0] || null;
    setMgrSelectedId(id);
    setMgrDelConfirm("");
    if (id) {
      const cat = pcList.find(x => x.id === id);
      if (cat) {
        setMgrEditName(cat.name);
        setMgrEditThreshold(cat.warn_threshold != null ? String(cat.warn_threshold) : "");
      }
    } else {
      setMgrEditName("");
      setMgrEditThreshold("");
    }
  }

  // ================= 手动减料 =================
  const openReduceModal = (record) => {
    setCurrentRoll(record); setReduceVal(""); setReduceModalOpen(true);
  }
  const confirmReduce = async () => {
    const num = Number(reduceVal);
    if (!reduceVal || num <= 0) { message.warning("请输入大于0的扣减重量(吨)"); return; }
    try {
      await api.post(`/api/rawroll/${currentRoll.id}/reduce_stock`, { reduce_weight: num });
      message.success("手动减料成功");
      setReduceModalOpen(false); loadData();
    } catch (err) {
      message.error(err.response?.data?.detail || "扣减失败");
    }
  }

  // ================= 保存卷筒 =================
  const handleSubmit = async (values) => {
    try {
      let cid = values.category_id;
      if (cid === undefined || cid === null || cid === "") cid = null;
      const payload = {
        raw_no: values.raw_no,
        product_name_id: Number(values.product_name_id),
        category_id: cid,
        width: Number(values.width),
        gram: Number(values.gram),
        weight: Number(values.weight),
        remark: values.remark || ""
      }
      if (isNaN(payload.width) || isNaN(payload.gram) || isNaN(payload.weight)) {
        return message.error("幅宽、克重、重量必须是数字")
      }
      if (payload.weight <= 0) return message.error("重量必须大于0")
      await api.post("/api/rawroll", payload)
      message.success("新增卷筒成功")
      setModalOpen(false); form.resetFields(); loadData()
    } catch (err) {
      console.error(err.response?.data)
      message.error(err.response?.data?.detail || "新增卷筒失败")
    }
  }

  // ================= 新增品名 =================
  const handleAddPn = async (v) => {
    await api.post("/api/product_name", v);
    message.success("品名新增成功");
    setPnModal(false); pnForm.resetFields(); loadData();
  }

  // ================= 新增物理分类 =================
  const handleAddPc = async (v) => {
    const payload = {
      name: v.name,
      parent_id: v.parent_id || null,
      warn_threshold: v.warn_threshold != null && v.warn_threshold !== "" ? Number(v.warn_threshold) : null
    }
    await api.post("/api/physical_category", payload);
    message.success("分类新增成功");
    setPcModal(false); pcForm.resetFields(); loadData();
  }

  // ================= 分类选择变化：自动填入克重和幅宽 =================
  const handleCategoryChange = (path) => {
    if (!path || path.length < 4) return;
    const l3Id = path[2], l4Id = path[3];
    const l3Name = pcList.find(x => x.id === l3Id)?.name;
    const l4Name = pcList.find(x => x.id === l4Id)?.name;
    const gramVal = extractNumber(l3Name);
    const widthVal = extractNumber(l4Name);
    if (gramVal !== null) form.setFieldsValue({ gram: gramVal });
    if (widthVal !== null) form.setFieldsValue({ width: widthVal });
  }

  // ================= 过滤+汇总 =================
  const filterList = useMemo(() => {
    let allowedCatIds = null;
    if (filterCategoryPath && filterCategoryPath.length > 0) {
      const selectedId = filterCategoryPath[filterCategoryPath.length - 1];
      allowedCatIds = getDescendantIds(selectedId);
    }
    const kw = String(searchText || "").trim().toLowerCase();
    return rollList.filter(item => {
      if (allowedCatIds && !allowedCatIds.includes(item.category_id)) return false;
      if (!kw) return true;
      const productName = pnList.find(x => x.id === item.product_name_id)?.name || "";
      const categoryPath = getPathName(item.category_id);
      let target = "";
      switch (searchField) {
        case 'raw_no': target = String(item.raw_no == null ? "" : item.raw_no); break;
        case 'product_name': target = String(productName); break;
        case 'category': target = String(categoryPath); break;
        case 'width': target = String(item.width == null ? "" : item.width); break;
        case 'gram': target = String(item.gram == null ? "" : item.gram); break;
        case 'remark': target = String(item.remark == null ? "" : item.remark); break;
        case 'all':
        default:
          target = [item.raw_no, item.width, item.gram, item.weight, item.stock_weight, item.remark, productName, categoryPath]
            .map(v => String(v == null ? "" : v)).join(" ");
          break;
      }
      return target.toLowerCase().includes(kw);
    })
  }, [rollList, searchText, searchField, filterCategoryPath, pcList, pnList])

  const stat = useMemo(() => {
    const count = filterList.length;
    const totalStock = filterList.reduce((sum, item) => sum + (Number(item.stock_weight) || 0), 0)
    const warningCount = filterList.filter(item => {
      const threshold = getWarnThreshold(item.category_id);
      return threshold != null && Number(item.stock_weight) < threshold;
    }).length
    return { count, totalStock, warningCount }
  }, [filterList, pcList])

  // ================= 列定义 =================
  const allColumnDefs = {
    raw_no: { title: "卷筒编号", dataIndex: "raw_no", key: "raw_no", width: 160, fixed: 'left' },
    product_name: {
      title: "品名", dataIndex: "product_name_id", key: "product_name", width: 100,
      render: (v) => { const p = pnList.find(x => x.id === v); return p?.name || "" }
    },
    category: {
      title: "物理分类", dataIndex: "category_id", key: "category", width: 200,
      render: (v) => getPathName(v)
    },
    width: { title: "幅宽(mm)", dataIndex: "width", key: "width", width: 100, sorter: (a, b) => Number(a.width) - Number(b.width) },
    gram: { title: "克重(g)", dataIndex: "gram", key: "gram", width: 100, sorter: (a, b) => Number(a.gram) - Number(b.gram) },
    weight: { title: "本支卷筒重量(吨)", dataIndex: "weight", key: "weight", width: 140 },
    ton_price: { title: "吨价(元/吨)", dataIndex: "ton_price", key: "ton_price", width: 110, render: v => v ? Number(v).toFixed(2) : '-' },
    stock_weight: {
      title: "剩余库存(吨)", dataIndex: "stock_weight", key: "stock_weight", width: 130,
      render: (val, record) => {
        const threshold = getWarnThreshold(record.category_id);
        const isLow = threshold != null && Number(val) < threshold;
        return (
          <span style={{ color: isLow ? '#cf1322' : undefined, fontWeight: isLow ? 600 : undefined }}>
            {Number(val).toFixed(3)}
            {isLow && <Tag color="red" style={{ marginLeft: 4 }}>低库存</Tag>}
          </span>
        )
      }
    },
    remark: { title: "备注", dataIndex: "remark", key: "remark", width: 150 },
    action: {
      title: "操作", key: "action", width: 160, fixed: 'right',
      render: (_, record) => (
        <Space>
          <Button size="small" onClick={() => openReduceModal(record)}>手动减料</Button>
          <Button danger size="small" onClick={() => { setDelRollId(record.id); setDelModalOpen(true) }}>删除</Button>
        </Space>
      )
    },
  }
  const columns = useMemo(() => visibleCols.map(key => allColumnDefs[key]).filter(Boolean), [visibleCols, pcList, pnList])

  const colSettingContent = (
    <div style={{ width: 180 }}>
      <div style={{ marginBottom: 8, display: 'flex', justifyContent: 'space-between' }}>
        <Button type="link" size="small" onClick={() => setVisibleCols(ALL_COLUMNS.map(c => c.key))}>全选</Button>
        <Button type="link" size="small" onClick={() => setVisibleCols(DEFAULT_VISIBLE_COLS)}>恢复默认</Button>
      </div>
      <Checkbox.Group value={visibleCols} onChange={(vals) => setVisibleCols(vals)}
        style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        {ALL_COLUMNS.map(col => <Checkbox key={col.key} value={col.key}>{col.label}</Checkbox>)}
      </Checkbox.Group>
    </div>
  )

  return (
    <div style={{ padding: 20 }}>
      <div style={{ marginBottom: 12, display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
        <Button type="primary" onClick={() => setModalOpen(true)}>新增卷筒</Button>
        <Button onClick={() => setPnModal(true)}>新建品名</Button>
        <Button onClick={() => onNavigate && onNavigate('purchase')}>采购单列表</Button>
        <Button onClick={() => setPcModal(true)}>新建物理分类</Button>
        <Select value={searchField} onChange={val => setSearchField(val)} style={{ width: 130 }}>
          {SEARCH_FIELDS.map(f => <Select.Option key={f.value} value={f.value}>{f.label}</Select.Option>)}
        </Select>
        <Input placeholder={`输入${SEARCH_FIELDS.find(f => f.value === searchField)?.label || '关键词'}搜索`}
          value={searchText} onChange={e => setSearchText(e.target.value)}
          style={{ width: 240 }} allowClear />
        <Popover content={colSettingContent} title="列显示设置" trigger="click" placement="bottomRight">
          <Button>列设置</Button>
        </Popover>
      </div>

      <div style={{ marginBottom: 16, display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
        <span>物理分类筛选：</span>
        <Button type={filterCategoryPath === null ? "primary" : "default"} onClick={() => setFilterCategoryPath(null)}>全部</Button>
        <Cascader style={{ width: 400 }} options={categoryTree} changeOnSelect allowClear
          placeholder="选择分类筛选（可选任意级别，自动包含子级）"
          value={filterCategoryPath || undefined}
          onChange={(val) => setFilterCategoryPath(val || null)} />
        <span style={{ fontSize: 12, color: '#888', marginLeft: 8 }}>
          提示：库存预警阈值在「分类管理」中设置，子级分类继承父级阈值
        </span>
      </div>

      <Table dataSource={filterList} rowKey="id" columns={columns} scroll={{ x: 'max-content' }}
        pagination={{
          pageSize: 20, showSizeChanger: true,
          pageSizeOptions: ['10', '20', '50', '100'],
          showTotal: (total) => `共 ${total} 条`,
        }}
        onRow={(record) => {
          const threshold = getWarnThreshold(record.category_id);
          if (threshold != null && Number(record.stock_weight) < threshold) {
            return { style: { background: '#fff2f0' } };
          }
          return {};
        }}
        footer={() => (
          <div style={{ fontWeight: 600, textAlign: "center", padding: "8px 0" }}>
            汇总：卷筒总数量 {stat.count} 个 &nbsp;&nbsp;｜&nbsp;&nbsp;
            库存总重量 {stat.totalStock.toFixed(3)} 吨
            {stat.warningCount > 0 && (
              <span style={{ color: '#cf1322', marginLeft: 16 }}>⚠ 低库存预警 {stat.warningCount} 个</span>
            )}
          </div>
        )}
      />


      {/* 删除卷筒确认 */}
      <Modal open={delModalOpen} title="确认删除卷筒" onCancel={() => { setDelModalOpen(false); setDelRollId(null) }}
        footer={<>
          <Button onClick={() => { setDelModalOpen(false); setDelRollId(null) }}>取消</Button>
          <Button danger type="primary" onClick={handleDelete}>确认删除</Button>
        </>}>
        <div>确定要删除这条卷筒原料记录？删除后不可恢复，请确认！</div>
      </Modal>

      {/* 手动减料 */}
      <Modal title="手动减料（扣减卷筒库存）" open={reduceModalOpen}
        onCancel={() => setReduceModalOpen(false)} onOk={confirmReduce}>
        {currentRoll && (
          <div>
            <p>卷筒编号：{currentRoll.raw_no}</p>
            <p>当前剩余库存：{Number(currentRoll.stock_weight).toFixed(3)} 吨</p>
            <Input type="number" step="0.001" min="0.001" placeholder="输入扣减重量，单位：吨"
              value={reduceVal} onChange={e => setReduceVal(e.target.value)} />
          </div>
        )}
      </Modal>

      {/* 新增卷筒 */}
      <Modal open={modalOpen} title="新增单支卷筒原料" footer={null}
        onCancel={() => setModalOpen(false)} maskClosable={false}>
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item label="品名" name="product_name_id" rules={[{ required: true, message: "请选择品名" }]}>
            <Select placeholder="请选择品名" style={{ width: '100%' }}>
              {pnList.map(i => <Select.Option key={i.id} value={i.id}>{i.name}</Select.Option>)}
            </Select>
          </Form.Item>
          <Form.Item label="物理分类（第1级大类 → 第2级纸名 → 第3级克重 → 第4级幅宽）"
            name="category_id" rules={[{ required: true, message: "请选择到第4级幅宽" }]}
            getValueFromEvent={(val) => Array.isArray(val) ? val[val.length - 1] : val}
            getValueProps={(val) => ({ value: getPathIds(val) })}>
            <Cascader options={categoryTree} placeholder="请依次选择，选完自动填入克重和幅宽"
              style={{ width: '100%' }} onChange={handleCategoryChange} />
          </Form.Item>
          <Form.Item label="卷筒编号" name="raw_no" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item label="幅宽(mm)" name="width" rules={[{ required: true }]}>
            <Input placeholder="选择分类后自动填入" />
          </Form.Item>
          <Form.Item label="克重(g)" name="gram" rules={[{ required: true }]}>
            <Input placeholder="选择分类后自动填入" />
          </Form.Item>
          <Form.Item label="本支卷筒实际重量(吨)" name="weight" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item label="吨价(元/吨)" name="ton_price"><Input placeholder="例如：2270" /></Form.Item>
          <Form.Item label="备注" name="remark"><Input.TextArea /></Form.Item>
          <div style={{ textAlign: "right" }}>
            <Button onClick={() => setModalOpen(false)} style={{ marginRight: 8 }}>取消</Button>
            <Button type="primary" htmlType="submit">保存</Button>
          </div>
        </Form>
      </Modal>

      {/* 新建品名 */}
      <Modal open={pnModal} title="新增品名" footer={null} onCancel={() => setPnModal(false)} zIndex={2000}>
        <Form form={pnForm} layout="vertical" onFinish={handleAddPn}>
          <Form.Item label="品名名称" name="name" rules={[{ required: true }]}>
            <Input placeholder="例如：金田金盾" />
          </Form.Item>
          <div style={{ textAlign: 'right' }}>
            <Button onClick={() => setPnModal(false)}>取消</Button>
            <Button htmlType="submit" type="primary">保存</Button>
          </div>
        </Form>
      </Modal>

      {/* 新建物理分类 */}
      <Modal open={pcModal} title="物理分类管理" footer={null}
        onCancel={() => { setPcModal(false); pcForm.resetFields(); }} width={560}>
        <div style={{ marginBottom: 12, padding: 10, background: '#fafafa', border: '1px solid #f0f0f0', borderRadius: 4, fontSize: 13, lineHeight: 1.8 }}>
          <div style={{ fontWeight: 600, marginBottom: 4 }}>分类层级说明（共4级）：</div>
          <div>第1级：大类（如：灰纸卷）</div>
          <div>第2级：纸名（如：金盾）</div>
          <div>第3级：克重（如：350G）</div>
          <div>第4级：幅宽（如：635）</div>
          <div style={{ marginTop: 6, color: '#1677ff' }}>
            库存预警阈值：可在任意一级设置，子级分类自动继承父级阈值；子级单独设置了则覆盖父级。
          </div>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
          <span style={{ fontWeight: 600 }}>新增分类</span>
          <Button onClick={openCatMgr}>分类管理（编辑/删除）</Button>
        </div>
        <Form form={pcForm} layout="vertical" onFinish={handleAddPc}>
          <Form.Item label="上级分类（决定新建分类的层级）" name="parent_id"
            extra={<span style={{ color: '#1677ff' }}>
              {pcParentPath.length === 0
                ? '未选上级 → 将创建【第1级：大类】'
                : `已选：${pcParentPath.map(id => pcList.find(x => x.id === id)?.name).filter(Boolean).join(' / ')} → 将创建【第${newCatLevel}级】`}
            </span>}
            getValueFromEvent={(val) => Array.isArray(val) ? val[val.length - 1] : (val || null)}
            getValueProps={(val) => ({ value: getPathIds(val) })}>
            <Cascader options={parentCategoryTree} changeOnSelect allowClear
              placeholder="不选=第1级；选1级=建第2级；选2级=建第3级；选3级=建第4级"
              style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item label="分类名称" name="name" rules={[{ required: true, message: "请输入分类名称" }]}>
            <Input placeholder={`请输入第${newCatLevel}级分类名称`} />
          </Form.Item>
          <Form.Item label="库存预警阈值(吨)" name="warn_threshold">
            <Input type="number" step="0.001" min="0"
              placeholder="留空=不单独设置（继承上级），低于此值整行标红" />
          </Form.Item>
          <div style={{ textAlign: 'right' }}>
            <Button onClick={() => { setPcModal(false); pcForm.resetFields(); }}>取消</Button>
            <Button htmlType="submit" type="primary" style={{ marginLeft: 8 }}>保存新增</Button>
          </div>
        </Form>
      </Modal>

      {/* 分类管理弹窗（编辑+删除） */}
      <Modal open={catMgrOpen} title="分类管理（编辑预警阈值 / 删除分类）"
        onCancel={() => { setCatMgrOpen(false); setMgrSelectedId(null); setMgrDelConfirm(""); }}
        width={680}
        footer={<>
          <Button onClick={() => { setCatMgrOpen(false); setMgrSelectedId(null); setMgrDelConfirm(""); }}>关闭</Button>
        </>}>
        <div style={{ display: 'flex', gap: 16 }}>
          <div style={{ flex: 1, border: '1px solid #f0f0f0', borderRadius: 4, padding: 8, maxHeight: 420, overflow: 'auto' }}>
            <div style={{ fontSize: 13, color: '#888', marginBottom: 8 }}>点击选择要编辑或删除的分类：</div>
            {mgrTreeData.length > 0 ? (
              <Tree treeData={mgrTreeData}
                selectedKeys={mgrSelectedId ? [mgrSelectedId] : []}
                onSelect={handleMgrSelect}
                defaultExpandAll blockNode />
            ) : (
              <div style={{ color: '#999', textAlign: 'center', padding: 20 }}>暂无分类数据</div>
            )}
          </div>

          <div style={{ flex: 1.2 }}>
            {mgrSelectedCat ? (
              <>
                <div style={{ marginBottom: 12 }}>
                  <div style={{ fontSize: 13, color: '#888', marginBottom: 4 }}>已选分类完整路径：</div>
                  <div style={{ fontWeight: 600, fontSize: 15 }}>{mgrSelectedPath}</div>
                </div>

                <Divider orientation="left" style={{ fontSize: 13 }}>编辑分类</Divider>

                <div style={{ marginBottom: 12 }}>
                  <div style={{ fontSize: 13, marginBottom: 4 }}>分类名称：</div>
                  <Input value={mgrEditName} onChange={e => setMgrEditName(e.target.value)} />
                </div>

                <div style={{ marginBottom: 12 }}>
                  <div style={{ fontSize: 13, marginBottom: 4 }}>
                    库存预警阈值(吨)：
                    <span style={{ color: '#888', fontSize: 12, marginLeft: 4 }}>留空=不单独设置（继承上级）</span>
                  </div>
                  <Input type="number" step="0.001" min="0"
                    value={mgrEditThreshold}
                    onChange={e => setMgrEditThreshold(e.target.value)}
                    placeholder="低于此值的卷筒整行标红" />
                </div>

                <Button type="primary" onClick={handleSaveCatEdit} style={{ marginBottom: 16 }}>保存修改</Button>

                <Divider orientation="left" style={{ fontSize: 13, color: '#cf1322' }}>删除分类</Divider>

                <div style={{ background: '#fff2f0', border: '1px solid #ffccc7', borderRadius: 4, padding: 10, marginBottom: 12, fontSize: 13, lineHeight: 1.8 }}>
                  <div>将级联删除 <Tag color="red">{mgrDescendantCount}</Tag> 个分类（含当前及所有子级）</div>
                  <div>当前有 <Tag color="orange">{mgrUsedRollCount}</Tag> 条卷筒记录使用这些分类</div>
                  <div style={{ marginTop: 4 }}>删除后不可恢复，使用该分类的卷筒将变为未分类状态。</div>
                </div>

                <div style={{ marginBottom: 8 }}>
                  <div style={{ fontSize: 13, marginBottom: 4 }}>
                    为防止误删，请输入分类名称 <b style={{ color: '#cf1322' }}>"{mgrSelectedCat.name}"</b>：
                  </div>
                  <Input placeholder={`请输入：${mgrSelectedCat.name}`}
                    value={mgrDelConfirm} onChange={e => setMgrDelConfirm(e.target.value)} />
                </div>
                {mgrDelConfirm && mgrDelConfirm !== mgrSelectedCat.name && (
                  <div style={{ color: '#cf1322', fontSize: 12, marginBottom: 8 }}>输入名称与选中分类不一致，无法删除</div>
                )}
                <Button danger type="primary"
                  disabled={mgrDelConfirm !== mgrSelectedCat.name}
                  onClick={handleDeleteCategory}>确认删除此分类</Button>
              </>
            ) : (
              <div style={{ color: '#999', textAlign: 'center', padding: '80px 0' }}>
                请在左侧树形列表中<br />选择要编辑或删除的分类
              </div>
            )}
          </div>
        </div>
      </Modal>

    </div>
  )
}
