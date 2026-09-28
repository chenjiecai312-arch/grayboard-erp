import React, { useEffect, useState } from 'react';
import { Button, Form, Input, InputNumber, Modal, Space, Table, Tabs, Tag, message } from 'antd';
import { api } from './api';

function childrenOf(list, parentId) {
  return list.filter((item) => (item.parent_id || null) === (parentId || null));
}

function flatten(list, parentId = null, level = 1, rows = []) {
  childrenOf(list, parentId).forEach((item) => {
    rows.push({ ...item, level });
    flatten(list, item.id, level + 1, rows);
  });
  return rows;
}

function CategoryPanel({ title, list, onReload, apiPath, maxLevel = 4 }) {
  const [form] = Form.useForm();
  const [open, setOpen] = useState(false);
  const [editId, setEditId] = useState(null);
  const [parentId, setParentId] = useState(null);

  const rows = flatten(list);

  const openAdd = (parent) => {
    setEditId(null);
    setParentId(parent);
    form.resetFields();
    setOpen(true);
  };

  const openEdit = (record) => {
    setEditId(record.id);
    setParentId(record.parent_id || null);
    form.setFieldsValue({ name: record.name, warn_threshold: record.warn_threshold });
    setOpen(true);
  };

  const save = async () => {
    try {
      const values = await form.validateFields();
      const payload = {
        name: values.name.trim(),
        parent_id: parentId,
        warn_threshold: values.warn_threshold ?? null,
      };
      if (editId) await api.put(`${apiPath}/${editId}`, payload);
      else await api.post(apiPath, payload);
      message.success('保存成功');
      setOpen(false);
      onReload();
    } catch (e) {
      if (e.errorFields) return;
      message.error(e.response?.data?.detail || '保存失败');
    }
  };

  const remove = async (record) => {
    if (!window.confirm(`确定删除「${record.name}」及其子分类？`)) return;
    try {
      await api.delete(`${apiPath}/${record.id}`);
      message.success('已删除');
      onReload();
    } catch (e) {
      message.error(e.response?.data?.detail || '删除失败');
    }
  };

  return (
    <div>
      <Button type="primary" style={{ marginBottom: 12 }} onClick={() => openAdd(null)}>新增一级{title}</Button>
      <Table
        rowKey="id"
        pagination={false}
        dataSource={rows}
        columns={[
          {
            title: '名称', dataIndex: 'name',
            render: (name, record) => <span style={{ paddingLeft: (record.level - 1) * 20 }}>{name}</span>,
          },
          { title: '层级', dataIndex: 'level', width: 80, render: (level) => <Tag>第{level}级</Tag> },
          { title: '预警', dataIndex: 'warn_threshold', width: 120, render: (value) => value ?? '-' },
          {
            title: '操作', width: 220,
            render: (_, record) => (
              <Space>
                {record.level < maxLevel && <Button size="small" type="link" onClick={() => openAdd(record.id)}>子分类</Button>}
                <Button size="small" type="link" onClick={() => openEdit(record)}>编辑</Button>
                <Button size="small" type="link" danger onClick={() => remove(record)}>删除</Button>
              </Space>
            ),
          },
        ]}
      />
      <Modal title={editId ? `编辑${title}` : `新增${title}`} open={open} onCancel={() => setOpen(false)} onOk={save}>
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="名称" rules={[{ required: true, message: '请填写名称' }]}>
            <Input />
          </Form.Item>
          <Form.Item name="warn_threshold" label="预警阈值">
            <InputNumber style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

function NamePanel({ title, list, apiPath, onReload, canDelete = true }) {
  const [name, setName] = useState('');

  const add = async () => {
    if (!name.trim()) {
      message.warning('请填写名称');
      return;
    }
    try {
      await api.post(apiPath, { name: name.trim() });
      setName('');
      message.success('新增成功');
      onReload();
    } catch (e) {
      message.error(e.response?.data?.detail || '新增失败');
    }
  };

  const remove = async (record) => {
    if (!window.confirm(`确定删除「${record.name}」？`)) return;
    try {
      await api.delete(`${apiPath}/${record.id}`);
      message.success('已删除');
      onReload();
    } catch (e) {
      message.error(e.response?.data?.detail || '删除失败');
    }
  };

  return (
    <div>
      <Space style={{ marginBottom: 12 }}>
        <Input placeholder={`新${title}`} value={name} onChange={(e) => setName(e.target.value)} onPressEnter={add} />
        <Button type="primary" onClick={add}>新增</Button>
      </Space>
      <Table
        rowKey="id"
        dataSource={list}
        columns={[
          { title: '名称', dataIndex: 'name' },
          ...(canDelete ? [{ title: '操作', width: 100, render: (_, record) => <Button size="small" danger onClick={() => remove(record)}>删除</Button> }] : []),
        ]}
      />
    </div>
  );
}

export default function CatalogManage() {
  const [productCategories, setProductCategories] = useState([]);
  const [finishedNames, setFinishedNames] = useState([]);
  const [rollCategories, setRollCategories] = useState([]);
  const [rollNames, setRollNames] = useState([]);
  const [auxCategories, setAuxCategories] = useState([]);

  const load = async () => {
    try {
      const [pc, pn, rc, rn, ac] = await Promise.all([
        api.get('/api/product_category'),
        api.get('/api/product_name_finished'),
        api.get('/api/physical_category'),
        api.get('/api/product_name'),
        api.get('/api/aux_category'),
      ]);
      setProductCategories(pc.data);
      setFinishedNames(pn.data);
      setRollCategories(rc.data);
      setRollNames(rn.data);
      setAuxCategories(ac.data);
    } catch (e) {
      message.error(e.response?.data?.detail || '加载失败');
    }
  };

  useEffect(() => { load(); }, []);

  return (
    <div style={{ padding: 16 }}>
      <h2 style={{ marginTop: 0 }}>目录管理</h2>
      <Tabs
        items={[
          {
            key: 'product_category',
            label: '成品分类',
            children: <CategoryPanel title="分类" list={productCategories} apiPath="/api/product_category" onReload={load} />,
          },
          {
            key: 'finished_name',
            label: '成品品名',
            children: <NamePanel title="品名" list={finishedNames} apiPath="/api/product_name_finished" onReload={load} />,
          },
          {
            key: 'roll_category',
            label: '卷料分类',
            children: <CategoryPanel title="分类" list={rollCategories} apiPath="/api/physical_category" onReload={load} />,
          },
          {
            key: 'roll_name',
            label: '卷料品名',
            children: <NamePanel title="品名" list={rollNames} apiPath="/api/product_name" onReload={load} canDelete={false} />,
          },
          {
            key: 'aux_category',
            label: '辅料分类',
            children: <NamePanel title="分类" list={auxCategories} apiPath="/api/aux_category" onReload={load} />,
          },
        ]}
      />
    </div>
  );
}
