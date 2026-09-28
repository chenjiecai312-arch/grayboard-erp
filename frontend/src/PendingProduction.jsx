import React, { useState, useEffect } from 'react';
import { Table, Button, message, Tag, Space, Popconfirm, Modal } from 'antd';
import { api } from './api';

export default function PendingProduction() {
  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [currentOrder, setCurrentOrder] = useState(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await api.get('/api/produce_order');
      const data = res.data.filter(o => o.status === 'pending');
      setList(data);
    } catch (e) {
      message.error('加载失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // 完成生产
  const handleFinish = async (record) => {
    try {
      await api.post(`/api/produce_order/${record.id}/finish_production`);
      message.success('生产完成，成品已自动入库');
      loadData();
    } catch (e) {
      message.error(e.response?.data?.detail || '操作失败');
    }
  };

  // 打回草稿
  const handleBackToDraft = async (record) => {
    try {
      await api.post(`/api/produce_order/${record.id}/back_to_draft`);
      message.success('已打回草稿，卷料库存已退回');
      loadData();
    } catch (e) {
      message.error(e.response?.data?.detail || '操作失败');
    }
  };

  // 重新排单
  const handleReschedule = async (record) => {
    try {
      await api.post(`/api/produce_order/${record.id}/reschedule`);
      message.success('已移回已排单，可重新选择排单日期');
      loadData();
    } catch (e) {
      message.error(e.response?.data?.detail || '操作失败');
    }
  };

  // 查看配料明细
  const openDetail = (record) => {
    setCurrentOrder(record);
    setDetailModalOpen(true);
  };

  const columns = [
    { title: '排单日期', dataIndex: 'schedule_date', width: 110 },
    { title: '工程单号', dataIndex: 'order_no', width: 140 },
    { title: '客户', dataIndex: 'customer_name', width: 150 },
    { title: '产品名称', dataIndex: 'product_name', width: 120 },
    { title: '规格', width: 120, render: (_, r) => `${r.spec_width || ''}×${r.spec_length || ''}` },
    { title: '数量', dataIndex: 'quantity', width: 80 },
    { title: '总克重', dataIndex: 'total_gram', width: 80 },
    { title: '层数', dataIndex: 'layers', width: 70, render: v => `${v}层` },
    { title: '生产工艺', dataIndex: 'craft', width: 200, ellipsis: true },
    {
      title: '操作', key: 'action', width: 220, fixed: 'right',
      render: (_, record) => (
        <Space wrap size={4}>
          <Button size="small" onClick={() => openDetail(record)}>查看配料</Button>
          <Popconfirm
            title="确认完成生产？"
            description="完成后成品将自动入库到成品仓"
            onConfirm={() => handleFinish(record)}
          >
            <Button size="small" type="primary">完成生产</Button>
          </Popconfirm>
          <Popconfirm
            title="确认重新排单？"
            description="移回已排单状态，可重新选日期，卷料库存保持锁定"
            onConfirm={() => handleReschedule(record)}
          >
            <Button size="small">重新排单</Button>
          </Popconfirm>
          <Popconfirm
            title="确认打回草稿？"
            description="打回后卷料库存将退回，工单回到草稿状态"
            onConfirm={() => handleBackToDraft(record)}
          >
            <Button size="small" danger>打回草稿</Button>
          </Popconfirm>
        </Space>
      )
    }
  ];

  return (
    <div style={{ padding: 20 }}>
      <h2 style={{ marginBottom: 16 }}>待生产</h2>

      <div style={{ marginBottom: 16, color: '#666' }}>
        以下工单已锁定卷料库存，生产完成后点"完成生产"自动入库成品仓
      </div>

      <Table
        rowKey="id"
        dataSource={list}
        columns={columns}
        loading={loading}
        pagination={{ pageSize: 20 }}
      />

      {/* 配料明细弹窗 */}
      <Modal
        open={detailModalOpen}
        title="配料明细"
        onCancel={() => setDetailModalOpen(false)}
        footer={null}
        width={700}
      >
        {currentOrder && (
          <Table
            rowKey="id"
            dataSource={currentOrder.items}
            size="small"
            pagination={false}
            columns={[
              { title: '层级', dataIndex: 'layer_no', width: 70, render: v => `第${v}层` },
              { title: '原料', dataIndex: 'roll_name' },
              { title: '实发重量(吨)', dataIndex: 'quantity', width: 120, render: v => Number(v).toFixed(3) },
              { title: '备注', dataIndex: 'remark' }
            ]}
          />
        )}
      </Modal>
    </div>
  );
}
