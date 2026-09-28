import React, { useEffect, useState } from 'react';
import { Button, Checkbox, Form, Input, Modal, Select, Space, Switch, Table, Tag, message } from 'antd';
import { api } from './api';

export default function StaffManage() {
  const [list, setList] = useState([]);
  const [meta, setMeta] = useState({ permissions: [], roles: [] });
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [editId, setEditId] = useState(null);
  const [form] = Form.useForm();

  const loadData = async () => {
    setLoading(true);
    try {
      const [staffRes, metaRes] = await Promise.all([api.get('/api/staff'), api.get('/api/staff/meta')]);
      setList(staffRes.data);
      setMeta(metaRes.data);
    } catch (e) {
      message.error(e.response?.data?.detail || '加载失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadData(); }, []);

  const roleName = (code) => meta.roles.find((role) => role.code === code)?.name || code;
  const permName = (code) => meta.permissions.find((item) => item.code === code)?.name || code;

  const openAdd = () => {
    setEditId(null);
    const sales = meta.roles.find((role) => role.code === 'SALES');
    form.resetFields();
    form.setFieldsValue({
      role: 'SALES',
      enabled: true,
      permissions: sales?.permissions || ['customer', 'sales'],
    });
    setModalOpen(true);
  };

  const openEdit = (record) => {
    setEditId(record.id);
    form.setFieldsValue({
      username: record.username,
      real_name: record.real_name,
      phone: record.phone,
      role: record.role,
      permissions: record.permissions,
      enabled: record.enabled,
      password: '',
    });
    setModalOpen(true);
  };

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      const payload = {
        username: values.username,
        real_name: values.real_name,
        phone: values.phone,
        role: values.role,
        permissions: values.permissions,
        enabled: values.enabled,
      };
      if (values.password) payload.password = values.password;
      if (editId) {
        await api.put(`/api/staff/${editId}`, payload);
        message.success('修改成功');
      } else {
        await api.post('/api/staff', payload);
        message.success('新增成功');
      }
      setModalOpen(false);
      loadData();
    } catch (e) {
      if (e.errorFields) return;
      message.error(e.response?.data?.detail || '保存失败');
    }
  };

  const handleDelete = async (record) => {
    if (!window.confirm(`确定删除人员 ${record.username}？`)) return;
    try {
      await api.delete(`/api/staff/${record.id}`);
      message.success('删除成功');
      loadData();
    } catch (e) {
      message.error(e.response?.data?.detail || '删除失败');
    }
  };

  const filtered = list.filter((item) => {
    const text = searchText.trim().toLowerCase();
    if (!text) return true;
    return [item.username, item.real_name, item.phone, roleName(item.role)]
      .some((value) => String(value || '').toLowerCase().includes(text));
  });

  const columns = [
    { title: '账号', dataIndex: 'username', width: 140 },
    { title: '姓名', dataIndex: 'real_name', width: 120 },
    { title: '电话', dataIndex: 'phone', width: 140 },
    { title: '角色', dataIndex: 'role', width: 120, render: (role) => roleName(role) },
    {
      title: '权限', dataIndex: 'permissions',
      render: (permissions) => (permissions || []).map((code) => <Tag key={code}>{permName(code)}</Tag>),
    },
    {
      title: '状态', dataIndex: 'enabled', width: 90,
      render: (enabled) => enabled ? <Tag color="green">启用</Tag> : <Tag>停用</Tag>,
    },
    {
      title: '操作', width: 150, fixed: 'right',
      render: (_, record) => (
        <Space>
          <Button size="small" onClick={() => openEdit(record)}>编辑</Button>
          <Button size="small" danger onClick={() => handleDelete(record)}>删除</Button>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: 16 }}>
      <div style={{ marginBottom: 16, display: 'flex', gap: 10 }}>
        <Button type="primary" onClick={openAdd}>新增人员</Button>
        <Input
          allowClear
          placeholder="搜索账号、姓名、电话"
          style={{ width: 260 }}
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
        />
      </div>
      <Table rowKey="id" loading={loading} columns={columns} dataSource={filtered} scroll={{ x: 1100 }} />
      <Modal
        title={editId ? '编辑人员' : '新增人员'}
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={handleSave}
        destroyOnClose
        width={640}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="username" label="账号" rules={[{ required: true, message: '请填写账号' }]}>
            <Input disabled={!!editId} />
          </Form.Item>
          <Form.Item name="real_name" label="姓名">
            <Input />
          </Form.Item>
          <Form.Item name="phone" label="电话">
            <Input />
          </Form.Item>
          <Form.Item
            name="password"
            label={editId ? '密码（不修改请留空）' : '密码'}
            rules={editId ? [] : [{ required: true, min: 6, message: '密码至少 6 位' }]}
          >
            <Input.Password />
          </Form.Item>
          <Form.Item name="role" label="角色" rules={[{ required: true, message: '请选择角色' }]}>
            <Select
              options={meta.roles.map((role) => ({ value: role.code, label: role.name }))}
              onChange={(code) => {
                const role = meta.roles.find((item) => item.code === code);
                if (role) form.setFieldValue('permissions', role.permissions);
              }}
            />
          </Form.Item>
          <Form.Item name="permissions" label="权限" rules={[{ required: true, message: '请至少选择一项权限' }]}>
            <Checkbox.Group
              options={meta.permissions.map((item) => ({ value: item.code, label: item.name }))}
            />
          </Form.Item>
          <Form.Item name="enabled" label="启用" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
