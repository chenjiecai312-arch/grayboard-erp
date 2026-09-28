import React, { useState, useEffect, useMemo } from 'react';
import { Form, Input, Button, Table, message, Modal, Select, Space, Popover, Checkbox, Tag, InputNumber, Radio } from 'antd';
import { api } from './api';

// 搜索范围
const SEARCH_FIELDS = [
  { label: '全部字段', value: 'all' },
  { label: '品名', value: 'name' },
  { label: '分类', value: 'category' },
  { label: '单位', value: 'unit' },
  { label: '备注', value: 'remark' },
]

// 可配置显示的列
const ALL_COLUMNS = [
  { key: 'name', label: '品名' },
  { key: 'category', label: '分类' },
  { key: 'quantity', label: '库存数量' },
  { key: 'unit', label: '单位' },
  { key: 'remark', label: '备注' },
  { key: 'action', label: '操作' },
]
const DEFAULT_VISIBLE_COLS = ['name', 'category', 'quantity', 'unit', 'action']

// 常用单位预设
const UNIT_PRESETS = ['个', '包', '卷', 'kg', 'g', '米', '箱', '桶', '瓶', '条', '张', '套']

// 调整原因快捷选项
const ADJUST_REASONS = ['采购入库', '生产领用', '盘点损耗']

export default function AuxWarehouse() {
  const [list, setList] = useState([]);
  const [categoryList, setCategoryList] = useState([]);
  const [searchText, setSearchText] = useState("");
  const [searchField, setSearchField] = useState("all");
  const [filterCategoryId, setFilterCategoryId] = useState(null);

  const [visibleCols, setVisibleCols] = useState(() => {
    try {
      const saved = localStorage.getItem('aux_visible_cols');
      if (saved) return JSON.parse(saved);
    } catch (e) {}
    return DEFAULT_VISIBLE_COLS;
  })
  useEffect(() => {
    try { localStorage.setItem('aux_visible_cols', JSON.stringify(visibleCols)); } catch (e) {}
  }, [visibleCols])

  // 新增/编辑弹窗
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [editForm] = Form.useForm();

  // 调整库存弹窗
  const [adjustModalOpen, setAdjustModalOpen] = useState(false);
  const [adjustItem, setAdjustItem] = useState(null);
  const [adjustQty, setAdjustQty] = useState("");
  const [adjustReason, setAdjustReason] = useState("");

  // 删除确认
  const [delModalOpen, setDelModalOpen] = useState(false);
  const [delItemId, setDelItemId] = useState(null);

  // 分类管理弹窗
  const [catModalOpen, setCatModalOpen] = useState(false);
  const [catInput, setCatInput] = useState("");


  const loadData = async () => {
    try {
      const [matRes, catRes] = await Promise.all([
        api.get("/api/aux_material"),
        api.get("/api/aux_category")
      ])
      setList(matRes.data);
      setCategoryList(catRes.data);
    } catch (e) {
      message.error("加载失败：" + (e.response?.data?.detail || e.message))
    }
  }

  useEffect(() => { loadData() }, [])

  // ================= 工具 =================
  function getCatName(id) {
    const c = categoryList.find(x => x.id === id);
    return c?.name || "";
  }

  // ================= 新增/编辑 =================
  const openAdd = () => {
    setEditingId(null);
    editForm.resetFields();
    editForm.setFieldsValue({ quantity: 0, unit: "个" });
    setEditModalOpen(true);
  }

  const openEdit = (record) => {
    setEditingId(record.id);
    editForm.setFieldsValue({
      name: record.name,
      category_id: record.category_id,
      quantity: record.quantity,
      unit: record.unit,
      remark: record.remark || ""
    })
    setEditModalOpen(true);
  }

  const handleSave = async () => {
    try {
      const values = await editForm.validateFields();
      const payload = {
        name: values.name,
        category_id: values.category_id || null,
        quantity: Number(values.quantity) || 0,
        unit: values.unit || "个",
        remark: values.remark || ""
      }
      if (editingId) {
        await api.put(`/api/aux_material/${editingId}`, payload);
        message.success("修改成功");
      } else {
        await api.post("/api/aux_material", payload);
        message.success("新增成功");
      }
      setEditModalOpen(false);
      loadData();
    } catch (err) {
      if (err.errorFields) return;
      message.error(err.response?.data?.detail || "保存失败")
    }
  }

  // ================= 调整库存（入库/出库） =================
  const openAdjust = (record) => {
    setAdjustItem(record);
    setAdjustQty("");
    setAdjustReason("");
    setAdjustModalOpen(true);
  }

  const handleAdjust = async () => {
    const num = Number(adjustQty);
    if (!adjustQty || isNaN(num) || num === 0) {
      message.warning("请输入非零的调整数量（正数入库，负数出库）");
      return;
    }
    try {
      await api.post(`/api/aux_material/${adjustItem.id}/adjust`, {
        adjust_quantity: num,
        reason: adjustReason || ""
      });
      message.success(num > 0 ? `入库 ${num} ${adjustItem.unit} 成功` : `出库 ${Math.abs(num)} ${adjustItem.unit} 成功`);
      setAdjustModalOpen(false);
      loadData();
    } catch (err) {
      message.error(err.response?.data?.detail || "调整失败")
    }
  }

  const adjustedPreview = useMemo(() => {
    if (!adjustItem) return null;
    const num = Number(adjustQty);
    if (!adjustQty || isNaN(num)) return null;
    return adjustItem.quantity + num;
  }, [adjustItem, adjustQty])

  // ================= 删除 =================
  const handleDelete = async () => {
    if (!delItemId) return;
    try {
      await api.delete(`/api/aux_material/${delItemId}`);
      message.success("删除成功");
      setDelModalOpen(false);
      setDelItemId(null);
      loadData();
    } catch (err) {
      message.error(err.response?.data?.detail || "删除失败")
    }
  }

  // ================= 分类管理 =================
  const handleAddCategory = async () => {
    if (!catInput.trim()) {
      message.warning("请输入分类名称");
      return;
    }
    try {
      await api.post("/api/aux_category", { name: catInput.trim() });
      message.success("分类新增成功");
      setCatInput("");
      loadData();
    } catch (err) {
      message.error(err.response?.data?.detail || "新增分类失败")
    }
  }

  const handleDeleteCategory = async (id) => {
    const name = getCatName(id);
    const used = list.filter(x => x.category_id === id).length;
    if (used > 0) {
      message.warning(`该分类下还有 ${used} 条辅料，无法删除，请先移到其他分类`);
      return;
    }
    if (!window.confirm(`确定删除分类「${name}」？`)) return;
    try {
      await api.delete(`/api/aux_category/${id}`);
      message.success("分类已删除");
      loadData();
    } catch (err) {
      message.error(err.response?.data?.detail || "删除失败")
    }
  }

  // ================= 过滤+汇总 =================
  const filterList = useMemo(() => {
    const kw = String(searchText || "").trim().toLowerCase();
    return list.filter(item => {
      if (filterCategoryId !== null && item.category_id !== filterCategoryId) return false;
      if (!kw) return true;

      let target = "";
      switch (searchField) {
        case 'name': target = String(item.name || ""); break;
        case 'category': target = getCatName(item.category_id); break;
        case 'unit': target = String(item.unit || ""); break;
        case 'remark': target = String(item.remark || ""); break;
        case 'all':
        default:
          target = [item.name, getCatName(item.category_id), item.unit, item.remark]
            .map(v => String(v || "")).join(" ");
          break;
      }
      return target.toLowerCase().includes(kw);
    })
  }, [list, searchText, searchField, filterCategoryId, categoryList])

  // 汇总：品种数 + 按【分类+单位】分组统计
  const stat = useMemo(() => {
    const totalKinds = filterList.length;
    const groups = {};
    filterList.forEach(item => {
      const catName = getCatName(item.category_id) || "未分类";
      const unit = item.unit || "个";
      const key = `${catName}__${unit}`;
      if (!groups[key]) {
        groups[key] = { category: catName, unit, quantity: 0 };
      }
      groups[key].quantity += Number(item.quantity) || 0;
    })
    return { totalKinds, groups: Object.values(groups) };
  }, [filterList, categoryList])

  // ================= 列定义 =================
  const allColumnDefs = {
    name: { title: "品名", dataIndex: "name", key: "name", width: 200, fixed: 'left' },
    category: {
      title: "分类", dataIndex: "category_id", key: "category", width: 140,
      render: (v) => getCatName(v)
    },
    quantity: {
      title: "库存数量", dataIndex: "quantity", key: "quantity", width: 120,
      render: (val) => <b>{Number(val).toFixed(2)}</b>
    },
    unit: { title: "单位", dataIndex: "unit", key: "unit", width: 100 },
    remark: { title: "备注", dataIndex: "remark", key: "remark", width: 200 },
    action: {
      title: "操作", key: "action", width: 220, fixed: 'right',
      render: (_, record) => (
        <Space>
          <Button size="small" type="primary" onClick={() => openAdjust(record)}>入库/出库</Button>
          <Button size="small" onClick={() => openEdit(record)}>编辑</Button>
          <Button danger size="small" onClick={() => { setDelItemId(record.id); setDelModalOpen(true) }}>删除</Button>
        </Space>
      )
    },
  }
  const columns = useMemo(() => visibleCols.map(key => allColumnDefs[key]).filter(Boolean), [visibleCols, categoryList])

  const colSettingContent = (
    <div style={{ width: 160 }}>
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
      {/* 顶部按钮行 */}
      <div style={{ marginBottom: 12, display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
        <Button type="primary" onClick={openAdd}>新增辅料</Button>
        <Button onClick={() => setCatModalOpen(true)}>分类管理</Button>

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

      {/* 分类筛选 */}
      <div style={{ marginBottom: 16, display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
        <span>分类筛选：</span>
        <Button type={filterCategoryId === null ? "primary" : "default"} onClick={() => setFilterCategoryId(null)}>全部</Button>
        {categoryList.map(c => (
          <Button key={c.id} type={filterCategoryId === c.id ? "primary" : "default"}
            onClick={() => setFilterCategoryId(c.id)}>{c.name}</Button>
        ))}
      </div>

      <Table dataSource={filterList} rowKey="id" columns={columns} scroll={{ x: 'max-content' }}
        pagination={{
          pageSize: 20, showSizeChanger: true,
          pageSizeOptions: ['10', '20', '50', '100'],
          showTotal: (total) => `共 ${total} 条`,
        }}
        footer={() => (
          <div style={{ fontWeight: 600, textAlign: "center", padding: "8px 0", lineHeight: 2 }}>
            汇总：辅料品种 <b>{stat.totalKinds}</b> 种
            &nbsp;&nbsp;｜&nbsp;&nbsp;
            库存按分类统计：
            {stat.groups.length === 0 && <span style={{ color: '#999', marginLeft: 6 }}>暂无</span>}
            {stat.groups.map((g, i) => (
              <Tag key={i} color="blue" style={{ marginLeft: 6 }}>
                {g.category} {g.quantity.toFixed(2)} {g.unit}
              </Tag>
            ))}
          </div>
        )}
      />


      {/* 新增/编辑弹窗 */}
      <Modal open={editModalOpen} title={editingId ? "编辑辅料" : "新增辅料"}
        onCancel={() => setEditModalOpen(false)}
        onOk={handleSave} width={520}>
        <Form form={editForm} layout="vertical">
          <Form.Item label="品名" name="name" rules={[{ required: true, message: "请输入品名" }]}>
            <Input placeholder="例如：封箱胶带、打包带" />
          </Form.Item>
          <Form.Item label="分类" name="category_id">
            <Select allowClear placeholder="请选择分类" style={{ width: '100%' }}>
              {categoryList.map(c => <Select.Option key={c.id} value={c.id}>{c.name}</Select.Option>)}
            </Select>
          </Form.Item>
          <div style={{ display: 'flex', gap: 12 }}>
            <Form.Item label="库存数量" name="quantity" style={{ flex: 1 }} rules={[{ required: true }]}>
              <InputNumber min={0} step="0.01" style={{ width: '100%' }} placeholder="0" />
            </Form.Item>
            <Form.Item label="单位" name="unit" style={{ flex: 1 }} rules={[{ required: true }]}>
              <Select
                showSearch
                placeholder="选择或输入单位"
                style={{ width: '100%' }}
                options={UNIT_PRESETS.map(u => ({ label: u, value: u }))}
                filterOption={(input, option) => (option?.label ?? '').includes(input)}
                onSearch={() => {}}
              />
            </Form.Item>
          </div>
          <div style={{ fontSize: 12, color: '#888', marginTop: -8, marginBottom: 12 }}>
            单位可从预设选择，也可直接键盘输入自定义单位（如"米"、"kg"、"卷"）
          </div>
          <Form.Item label="备注" name="remark">
            <Input.TextArea rows={2} placeholder="可选" />
          </Form.Item>
        </Form>
      </Modal>

      {/* 调整库存弹窗 */}
      <Modal open={adjustModalOpen} title="库存调整（入库/出库）"
        onCancel={() => setAdjustModalOpen(false)}
        onOk={handleAdjust} width={460}>
        {adjustItem && (
          <div>
            <p>品名：<b>{adjustItem.name}</b></p>
            <p>当前库存：<b style={{ color: '#1677ff' }}>{Number(adjustItem.quantity).toFixed(2)} {adjustItem.unit}</b></p>
            <div style={{ marginBottom: 12 }}>
              <div style={{ marginBottom: 4 }}>调整数量（正数=入库，负数=出库）：</div>
              <InputNumber
                step="0.01"
                style={{ width: '100%' }}
                placeholder="例如：10 入库，-5 出库"
                value={adjustQty}
                onChange={val => setAdjustQty(val)}
              />
            </div>
            {adjustedPreview !== null && (
              <p style={{ background: '#f6ffed', border: '1px solid #b7eb8f', padding: '8px 12px', borderRadius: 4 }}>
                调整后库存：<b style={{ color: adjustedPreview < 0 ? '#cf1322' : '#389e0d' }}>
                  {adjustedPreview.toFixed(2)} {adjustItem.unit}
                </b>
                {adjustedPreview < 0 && <span style={{ color: '#cf1322', marginLeft: 8 }}>（库存不足，无法出库）</span>}
              </p>
            )}
            <div style={{ marginBottom: 12 }}>
              <div style={{ marginBottom: 8 }}>调整原因：</div>
              <Radio.Group
                value={adjustReason}
                onChange={e => setAdjustReason(e.target.value)}
                buttonStyle="solid"
              >
                {ADJUST_REASONS.map(r => (
                  <Radio.Button key={r} value={r}>{r}</Radio.Button>
                ))}
              </Radio.Group>
            </div>
          </div>
        )}
      </Modal>

      {/* 删除确认 */}
      <Modal open={delModalOpen} title="确认删除辅料" onCancel={() => { setDelModalOpen(false); setDelItemId(null) }}
        footer={<>
          <Button onClick={() => { setDelModalOpen(false); setDelItemId(null) }}>取消</Button>
          <Button danger type="primary" onClick={handleDelete}>确认删除</Button>
        </>}>
        <div>确定要删除这条辅料记录？删除后不可恢复，请确认！</div>
      </Modal>

      {/* 分类管理弹窗 */}
      <Modal open={catModalOpen} title="辅料分类管理" onCancel={() => setCatModalOpen(false)}
        footer={<Button onClick={() => setCatModalOpen(false)}>关闭</Button>} width={460}>
        <div style={{ marginBottom: 16, display: 'flex', gap: 8 }}>
          <Input placeholder="输入新分类名称" value={catInput} onChange={e => setCatInput(e.target.value)}
            onPressEnter={handleAddCategory} />
          <Button type="primary" onClick={handleAddCategory}>新增分类</Button>
        </div>
        <div style={{ maxHeight: 320, overflow: 'auto' }}>
          {categoryList.length === 0 ? (
            <div style={{ color: '#999', textAlign: 'center', padding: 20 }}>暂无分类，请在上方新增</div>
          ) : (
            categoryList.map(c => (
              <div key={c.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 12px', borderBottom: '1px solid #f0f0f0' }}>
                <span>{c.name}</span>
                <Button danger size="small" type="link" onClick={() => handleDeleteCategory(c.id)}>删除</Button>
              </div>
            ))
          )}
        </div>
        <div style={{ fontSize: 12, color: '#888', marginTop: 8 }}>
          提示：分类下有辅料时无法删除，请先将辅料移到其他分类。
        </div>
      </Modal>

    </div>
  )
}
