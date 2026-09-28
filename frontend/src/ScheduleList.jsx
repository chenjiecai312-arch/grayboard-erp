import React, { useState, useEffect } from 'react';
import { Table, Button, message, Tag, Space, Popconfirm, DatePicker } from 'antd';
import { api } from './api';
import dayjs from 'dayjs';

const STATUS_MAP = {
  scheduled: { label: '已排单', color: 'cyan' },
  pending: { label: '待生产', color: 'orange' },
  finished: { label: '已完成', color: 'green' }
};

export default function ScheduleList() {
  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filterDate, setFilterDate] = useState(null);
  const [selectedRowKeys, setSelectedRowKeys] = useState([]);

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await api.get('/api/produce_order');
      let data = res.data.filter(o => o.status === 'scheduled' || o.status === 'pending');
      if (filterDate) {
        const dateStr = filterDate.format('YYYY-MM-DD');
        data = data.filter(o => o.schedule_date === dateStr);
      }
      // 按排单日期排序
      data.sort((a, b) => (a.schedule_date || '').localeCompare(b.schedule_date || ''));
      setList(data);
    } catch (e) {
      message.error('加载失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [filterDate]);

  // 批量移入待生产
  const handleBatchStart = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请先勾选要移入待生产的工单');
      return;
    }
    let success = 0;
    let failed = 0;
    for (const id of selectedRowKeys) {
      try {
        await api.post(`/api/produce_order/${id}/start_production`);
        success++;
      } catch (e) {
        failed++;
        message.error(`工单 ${id} 移入失败：${e.response?.data?.detail || '未知错误'}`);
      }
    }
    if (success > 0) message.success(`成功移入 ${success} 张工单待生产`);
    if (failed > 0) message.warning(`${failed} 张工单移入失败`);
    setSelectedRowKeys([]);
    loadData();
  };

  // 取消排单
  const handleCancelSchedule = async (record) => {
    try {
      await api.post(`/api/produce_order/${record.id}/cancel_schedule`);
      message.success('已取消排单，工单回到草稿');
      loadData();
    } catch (e) {
      message.error(e.response?.data?.detail || '操作失败');
    }
  };

  // 移入待生产
  const handleStartProduction = async (record) => {
    try {
      await api.post(`/api/produce_order/${record.id}/start_production`);
      message.success('已移入待生产，卷料库存已锁定');
      loadData();
    } catch (e) {
      message.error(e.response?.data?.detail || '操作失败');
    }
  };

  const columns = [
    { title: '排单日期', dataIndex: 'schedule_date', width: 110, render: v => v || '-' },
    { title: '工程单号', dataIndex: 'order_no', width: 140 },
    { title: '客户', dataIndex: 'customer_name', width: 150 },
    { title: '产品名称', dataIndex: 'product_name', width: 120 },
    { title: '规格', width: 120, render: (_, r) => `${r.spec_width || ''}×${r.spec_length || ''}` },
    { title: '数量', dataIndex: 'quantity', width: 80 },
    { title: '总克重', dataIndex: 'total_gram', width: 80 },
    { title: '层数', dataIndex: 'layers', width: 70, render: v => `${v}层` },
    { title: '状态', dataIndex: 'status', width: 90, render: v => <Tag color={STATUS_MAP[v]?.color}>{STATUS_MAP[v]?.label || v}</Tag> },
    {
      title: '操作', key: 'action', width: 200, fixed: 'right',
      render: (_, record) => (
        <Space>
          {record.status === 'scheduled' && (
            <Space>
              <Popconfirm
                title="确认移入待生产？"
                description="移入后将锁定对应卷料库存"
                onConfirm={() => handleStartProduction(record)}
              >
                <Button size="small" type="primary">移入待生产</Button>
              </Popconfirm>
              <Popconfirm
                title="确认取消排单？"
                description="取消后工单回到草稿，可重新排单"
                onConfirm={() => handleCancelSchedule(record)}
              >
                <Button size="small">取消排单</Button>
              </Popconfirm>
            </Space>
          )}
          {record.status === 'pending' && (
            <Tag color="orange">待生产中</Tag>
          )}
        </Space>
      )
    }
  ];

  return (
    <div style={{ padding: 20 }}>
      <h2 style={{ marginBottom: 16 }}>已排单 / 待生产</h2>

      <div style={{ marginBottom: 16, display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
        <span>按日期筛选：</span>
        <DatePicker
          value={filterDate}
          onChange={setFilterDate}
          placeholder="选择日期"
          allowClear
        />
        <Button onClick={() => setFilterDate(null)}>显示全部</Button>
        <span style={{ marginLeft: 20 }}>
          <Button type="primary" onClick={handleBatchStart} disabled={selectedRowKeys.length === 0}>
            批量移入待生产 ({selectedRowKeys.length})
          </Button>
        </span>
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
            disabled: record.status !== 'scheduled'
          })
        }}
      />
    </div>
  );
}
