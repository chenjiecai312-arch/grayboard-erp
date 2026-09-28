import React, { useState, useEffect } from 'react';
import { Table, Tag, Space, Input, Select, Card } from 'antd';
import { api } from './api';

export default function OperationLog() {
  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [searchModule, setSearchModule] = useState('');

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await api.get('/api/operation_log?limit=500');
      setList(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const moduleColors = {
    '成品仓': 'blue',
    '卷筒仓': 'green',
    '辅料仓': 'orange',
    '销售订单': 'red',
    '客户档案': 'purple'
  };

  const actionColors = {
    '新增': 'green',
    '修改': 'blue',
    '删除': 'red',
    '入库': 'cyan',
    '出库': 'magenta',
    '移入待出库': 'orange',
    '取消待出库': 'gold',
    '确认出库': 'volcano'
  };

  const filteredList = list.filter(item => {
    const matchSearch = !searchText || 
      String(item.detail || '').includes(searchText) ||
      String(item.action || '').includes(searchText);
    const matchModule = !searchModule || item.module === searchModule;
    return matchSearch && matchModule;
  });

  const columns = [
    { title: '时间', dataIndex: 'created_at', width: 160 },
    { title: '模块', dataIndex: 'module', width: 100, render: v => <Tag color={moduleColors[v] || 'default'}>{v}</Tag> },
    { title: '操作', dataIndex: 'action', width: 100, render: v => <Tag color={actionColors[v] || 'default'}>{v}</Tag> },
    { title: '操作对象', dataIndex: 'target_type', width: 120 },
    { title: '详情', dataIndex: 'detail', ellipsis: true }
  ];

  const modules = [...new Set(list.map(l => l.module))];

  return (
    <div style={{ padding: 20 }}>
      <Card title="操作日志（所有增删改操作记录）" extra={
        <Space>
          <Select
            placeholder="按模块筛选"
            allowClear
            value={searchModule || undefined}
            onChange={val => setSearchModule(val)}
            style={{ width: 150 }}
          >
            {modules.map(m => <Select.Option key={m} value={m}>{m}</Select.Option>)}
          </Select>
          <Input
            placeholder="搜索操作详情"
            value={searchText}
            onChange={e => setSearchText(e.target.value)}
            style={{ width: 200 }}
            allowClear
          />
        </Space>
      }>
        <Table
          rowKey="id"
          dataSource={filteredList}
          columns={columns}
          loading={loading}
          pagination={{ pageSize: 50, showSizeChanger: true }}
          size="small"
        />
      </Card>
    </div>
  );
}
