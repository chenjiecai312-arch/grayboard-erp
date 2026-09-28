import React, { useState, useEffect, useMemo } from 'react';
import { Button, Table, Modal, Form, Input, message, Space, Select, InputNumber, Popconfirm, Tag } from 'antd';
import { api } from './api';

// 搜索范围选项
const SEARCH_FIELDS = [
  { label: '全部字段', value: 'all' },
  { label: '客户名称', value: 'customer_name' },
  { label: '联系人', value: 'contact' },
  { label: '电话', value: 'phone' },
  { label: '地址', value: 'address' },
  { label: '账期', value: 'payment_terms' },
  { label: '所属业务员', value: 'salesperson' },
  { label: '税号', value: 'tax_no' },
  { label: '客户评级', value: 'customer_level' },
]

// 客户评级颜色映射
const LEVEL_COLORS = {
  'S': 'red',
  'A': 'orange',
  'B': 'blue',
  'C': 'green',
  'D': 'default',
}

export default function CustomerManage() {
  const [customerList, setCustomerList] = useState([]);
  const [loading, setLoading] = useState(false);

  // 搜索
  const [searchText, setSearchText] = useState("");
  const [searchField, setSearchField] = useState("all");

  // 新增/编辑弹窗
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [editForm] = Form.useForm();

  // 加载客户列表
  const loadCustomer = async () => {
    setLoading(true);
    try {
      const res = await api.get("/api/customer");
      setCustomerList(res.data);
    } catch (err) {
      message.error("加载客户失败：" + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadCustomer();
  }, []);

  // 搜索过滤
  const filteredList = useMemo(() => {
    const kw = String(searchText || "").trim().toLowerCase();
    if (!kw) return customerList;
    return customerList.filter(item => {
      let target = "";
      switch (searchField) {
        case 'customer_name':
          target = String(item.customer_name || "");
          break;
        case 'contact':
          target = String(item.contact || "");
          break;
        case 'phone':
          target = String(item.phone || "");
          break;
        case 'address':
          target = String(item.address || "");
          break;
        case 'payment_terms':
          target = String(item.payment_terms ?? "");
          break;
        case 'salesperson':
          target = String(item.salesperson || "");
          break;
        case 'tax_no':
          target = String(item.tax_no || "");
          break;
        case 'customer_level':
          target = String(item.customer_level || "");
          break;
        case 'all':
        default:
          target = [
            item.customer_name, item.contact, item.phone, item.address,
            item.payment_terms, item.salesperson, item.tax_no, item.customer_level
          ].map(v => String(v ?? "")).join(" ");
          break;
      }
      return target.toLowerCase().includes(kw);
    });
  }, [customerList, searchText, searchField]);

  // 打开新增
  const openAdd = () => {
    setEditingId(null);
    editForm.resetFields();
    editForm.setFieldsValue({ payment_terms: 0 });
    setEditModalOpen(true);
  }

  // 打开编辑
  const openEdit = (record) => {
    setEditingId(record.id);
    editForm.setFieldsValue({
      customer_name: record.customer_name,
      contact: record.contact,
      phone: record.phone,
      address: record.address,
      payment_terms: record.payment_terms ?? 0,
      salesperson: record.salesperson,
      tax_no: record.tax_no || undefined,
      customer_level: record.customer_level || undefined,
    });
    setEditModalOpen(true);
  }

  // 保存
  const handleSave = async () => {
    try {
      const values = await editForm.validateFields();
      const payload = {
        customer_name: values.customer_name.trim(),
        contact: values.contact.trim(),
        phone: values.phone.trim(),
        address: values.address.trim(),
        payment_terms: Number(values.payment_terms) || 0,
        salesperson: values.salesperson.trim(),
        tax_no: values.tax_no ? values.tax_no.trim() : null,
        customer_level: values.customer_level || null,
      };
      if (editingId) {
        await api.put(`/api/customer/${editingId}`, payload);
        message.success("修改成功");
      } else {
        await api.post("/api/customer", payload);
        message.success("新增成功");
      }
      setEditModalOpen(false);
      loadCustomer();
    } catch (err) {
      if (err.errorFields) return;
      message.error(err.response?.data?.detail || "保存失败");
    }
  }

  // 删除
  const handleDelete = async (id) => {
    try {
      await api.delete(`/api/customer/${id}`);
      message.success("删除成功");
      loadCustomer();
    } catch (err) {
      message.error(err.response?.data?.detail || "删除失败");
    }
  }

  // 表格列
  const columns = [
    { title: "ID", dataIndex: "id", key: "id", width: 60 },
    { title: "客户名称", dataIndex: "customer_name", key: "customer_name", width: 180, fixed: 'left', render: v => <b>{v}</b> },
    { title: "联系人", dataIndex: "contact", key: "contact", width: 100 },
    { title: "电话", dataIndex: "phone", key: "phone", width: 130 },
    { title: "地址", dataIndex: "address", key: "address", width: 220, ellipsis: true },
    {
      title: "账期(天)", dataIndex: "payment_terms", key: "payment_terms", width: 90,
      render: v => {
        const days = Number(v) || 0;
        if (days === 0) return <Tag>现款现货</Tag>;
        return <Tag color="blue">{days} 天</Tag>;
      }
    },
    { title: "所属业务员", dataIndex: "salesperson", key: "salesperson", width: 110 },
    {
      title: "税号", dataIndex: "tax_no", key: "tax_no", width: 180,
      render: v => v ? <span style={{ fontFamily: 'monospace', fontSize: 12 }}>{v}</span> : <span style={{ color: '#999' }}>-</span>
    },
    {
      title: "客户评级", dataIndex: "customer_level", key: "customer_level", width: 90,
      render: v => v ? <Tag color={LEVEL_COLORS[v] || 'default'}>{v}级</Tag> : <span style={{ color: '#999' }}>-</span>
    },
    {
      title: "操作", key: "action", width: 150, fixed: 'right',
      render: (_, record) => (
        <Space>
          <Button size="small" onClick={() => openEdit(record)}>编辑</Button>
          <Popconfirm
            title="确认删除该客户？"
            description="删除后不可恢复。若该客户下有成品记录将无法删除。"
            onConfirm={() => handleDelete(record.id)}
            okText="确认删除"
            cancelText="取消"
            okButtonProps={{ danger: true }}
          >
            <Button danger size="small">删除</Button>
          </Popconfirm>
        </Space>
      )
    }
  ];

  return (
    <div style={{ padding: 20 }}>
      <h2 style={{ marginBottom: 16 }}>客户档案库</h2>

      {/* 顶部操作栏 */}
      <div style={{ marginBottom: 16, display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
        <Button type="primary" onClick={openAdd}>新增客户</Button>

        <Select
          value={searchField}
          onChange={val => setSearchField(val)}
          style={{ width: 130 }}
        >
          {SEARCH_FIELDS.map(f => (
            <Select.Option key={f.value} value={f.value}>{f.label}</Select.Option>
          ))}
        </Select>

        <Input
          placeholder={`输入${SEARCH_FIELDS.find(f => f.value === searchField)?.label || '关键词'}搜索`}
          value={searchText}
          onChange={e => setSearchText(e.target.value)}
          style={{ width: 280 }}
          allowClear
        />

        <span style={{ color: '#888', fontSize: 13 }}>
          共 <b>{filteredList.length}</b> 个客户
        </span>
      </div>

      {/* 客户表格 */}
      <Table
        rowKey="id"
        dataSource={filteredList}
        columns={columns}
        loading={loading}
        bordered
        scroll={{ x: 'max-content' }}
        pagination={{
          pageSize: 20,
          showSizeChanger: true,
          pageSizeOptions: ['10', '20', '50', '100'],
          showTotal: t => `共 ${t} 条`
        }}
      />

      {/* 新增/编辑客户弹窗 */}
      <Modal
        open={editModalOpen}
        title={editingId ? "编辑客户" : "新增客户"}
        onCancel={() => setEditModalOpen(false)}
        onOk={handleSave}
        width={560}
        destroyOnClose
      >
        <Form form={editForm} layout="vertical">
          <Form.Item
            label="客户名称"
            name="customer_name"
            rules={[{ required: true, message: "请输入客户名称" }]}
          >
            <Input placeholder="例如：深圳鼎立纸业有限公司" />
          </Form.Item>

          <div style={{ display: 'flex', gap: 12 }}>
            <Form.Item
              label="联系人"
              name="contact"
              style={{ flex: 1 }}
              rules={[{ required: true, message: "请输入联系人" }]}
            >
              <Input placeholder="例如：张经理" />
            </Form.Item>
            <Form.Item
              label="电话"
              name="phone"
              style={{ flex: 1 }}
              rules={[{ required: true, message: "请输入电话" }]}
            >
              <Input placeholder="例如：13800138000" />
            </Form.Item>
          </div>

          <Form.Item
            label="地址"
            name="address"
            rules={[{ required: true, message: "请输入地址" }]}
          >
            <Input placeholder="例如：广东省深圳市宝安区XX街道XX工业园" />
          </Form.Item>

          <div style={{ display: 'flex', gap: 12 }}>
            <Form.Item
              label="账期（天）"
              name="payment_terms"
              style={{ flex: 1 }}
              rules={[{ required: true, message: "请输入账期" }]}
            >
              <InputNumber min={0} step={1} style={{ width: '100%' }} placeholder="0=现款现货" />
            </Form.Item>
            <Form.Item
              label="所属业务员"
              name="salesperson"
              style={{ flex: 1 }}
              rules={[{ required: true, message: "请输入所属业务员" }]}
            >
              <Input placeholder="例如：李四" />
            </Form.Item>
          </div>

          <div style={{ display: 'flex', gap: 12 }}>
            <Form.Item
              label="税号/付款人信息（非必填）"
              name="tax_no"
              style={{ flex: 2 }}
            >
              <Input placeholder="例如：91440300XXXXXXXXXX 或 付款公司全称" />
            </Form.Item>
            <Form.Item
              label="客户评级（非必填）"
              name="customer_level"
              style={{ flex: 1 }}
            >
              <Select placeholder="选择评级" allowClear>
                <Select.Option value="S">S级（核心客户）</Select.Option>
                <Select.Option value="A">A级（重要客户）</Select.Option>
                <Select.Option value="B">B级（普通客户）</Select.Option>
                <Select.Option value="C">C级（小客户）</Select.Option>
                <Select.Option value="D">D级（待观察）</Select.Option>
              </Select>
            </Form.Item>
          </div>

          <div style={{ fontSize: 12, color: '#888', marginTop: -8 }}>
            提示：带 * 为必填项。税号和客户级为非必填。
          </div>
        </Form>
      </Modal>
    </div>
  );
}
