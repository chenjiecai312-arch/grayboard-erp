import React, { useState, useEffect } from 'react';
import { Table, Button, Input, Modal, Form, message, Space } from 'antd';
import { api } from './api';

export default function SupplierManage() {
  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editId, setEditId] = useState(null);
  const [form] = Form.useForm();

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await api.get('/api/supplier');
      setList(res.data);
    } catch (e) {
      message.error('加载失败：' + (e.response?.data?.detail || e.message));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const filteredList = list.filter(item =>
    !searchText ||
    String(item.name).toLowerCase().includes(searchText.toLowerCase()) ||
    String(item.contact || '').toLowerCase().includes(searchText.toLowerCase()) ||
    String(item.phone || '').toLowerCase().includes(searchText.toLowerCase())
  );

  const openAdd = () => {
    setEditId(null);
    form.resetFields();
    setModalOpen(true);
  };

  const openEdit = (record) => {
    setEditId(record.id);
    form.setFieldsValue(record);
    setModalOpen(true);
  };

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      if (editId) {
        await api.put(`/api/supplier/${editId}`, values);
        message.success('修改成功');
      } else {
        await api.post('/api/supplier', values);
        message.success('新增成功');
      }
      setModalOpen(false);
      loadData();
    } catch (e) {
      if (e.errorFields) return;
      message.error(e.response?.data?.detail || '保存失败');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('确定删除这个供应商？')) return;
    try {
      await api.delete(`/api/supplier/${id}`);
      message.success('删除成功');
      loadData();
    } catch (e) {
      message.error(e.response?.data?.detail || '删除失败');
    }
  };

  const columns = [
    { title: '供应商名称', dataIndex: 'name', width: 200 },
    { title: '联系人', dataIndex: 'contact', width: 120 },
    { title: '电话', dataIndex: 'phone', width: 150 },
    { title: '地址', dataIndex: 'address', width: 250, ellipsis: true },
    { title: '账期', dataIndex: 'payment_term', width: 120 },
    { title: '业务员', dataIndex: 'salesman', width: 100 },
    { title: '税号', dataIndex: 'tax_no', width: 180, ellipsis: true },
    { title: '评级', dataIndex: 'level', width: 100 },
    { title: '备注', dataIndex: 'remark', width: 200, ellipsis: true },
    {
      title: '操作', key: 'action', width: 150, fixed: 'right',
      render: (_, record) => (
        <Space>
          <Button size="small" onClick={() => openEdit(record)}>编辑</Button>
          <Button size="small" danger onClick={() => handleDelete(record.id)}>删除</Button>
        </Space>
      )
    }
  ];

  return (
    <div style={{ padding: 16 }}>
      <div style={{ marginBottom: 16, display: 'flex', gap: 10, alignItems: 'center' }}>
        <Button type="primary" onClick={openAdd}>新增供应商</Button>
        <Input
          placeholder="搜索供应商名称/联系人/电话"
          value={searchText}
          onChange={e => setSearchText(e.target.value)}
          style={{ width: 300 }}
          allowClear
        />
      </div>

      <Table
        rowKey="id"
        columns={columns}
        dataSource={filteredList}
        loading={loading}
        pagination={{ pageSize: 20 }}
        scroll={{ x: 1600 }}
      />

      <Modal
        open={modalOpen}
        title={editId ? '编辑供应商' : '新增供应商'}
        onCancel={() => setModalOpen(false)}
        footer={null}
        width={700}
      >
        <Form form={form} layout="vertical">
          <div style={{ display: 'flex', gap: 16 }}>
            <div style={{ flex: 1 }}>
              <Form.Item label="供应商名称" name="name" rules={[{ required: true, message: '请输入供应商名称' }]}>
                <Input placeholder="如：东莞市金田纸业有限公司" />
              </Form.Item>
            </div>
            <div style={{ flex: 1 }}>
              <Form.Item label="联系人" name="contact">
                <Input placeholder="联系人姓名" />
              </Form.Item>
            </div>
          </div>
          <div style={{ display: 'flex', gap: 16 }}>
            <div style={{ flex: 1 }}>
              <Form.Item label="电话" name="phone">
                <Input placeholder="联系电话" />
              </Form.Item>
            </div>
            <div style={{ flex: 1 }}>
              <Form.Item label="账期" name="payment_term">
                <Input placeholder="如：月结30天" />
              </Form.Item>
            </div>
          </div>
          <div style={{ display: 'flex', gap: 16 }}>
            <div style={{ flex: 1 }}>
              <Form.Item label="业务员" name="salesman">
                <Input placeholder="负责业务员" />
              </Form.Item>
            </div>
            <div style={{ flex: 1 }}>
              <Form.Item label="评级" name="level">
                <Input placeholder="如：A级/B级" />
              </Form.Item>
            </div>
          </div>
          <Form.Item label="税号" name="tax_no">
            <Input placeholder="纳税人识别号" />
          </Form.Item>
          <Form.Item label="地址" name="address">
            <Input placeholder="供应商地址" />
          </Form.Item>
          <Form.Item label="备注" name="remark">
            <Input.TextArea rows={2} placeholder="备注信息" />
          </Form.Item>
          <div style={{ textAlign: 'right' }}>
            <Button onClick={() => setModalOpen(false)} style={{ marginRight: 8 }}>取消</Button>
            <Button type="primary" onClick={handleSave}>保存</Button>
          </div>
        </Form>
      </Modal>
    </div>
  );
}
