with open('src/PendingProduction.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 加打回草稿和重新排单函数（在 handleFinish 后面）
content = content.replace(
    '  // 查看配料明细\n  const openDetail = (record) => {',
    '''  // 打回草稿
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
  const openDetail = (record) => {'''
)

# 2. 操作列加打回草稿和重新排单按钮
content = content.replace(
    '''        <Space>
          <Button size="small" onClick={() => openDetail(record)}>查看配料</Button>
          <Popconfirm
            title="确认完成生产？"
            description="完成后成品将自动入库到成品仓"
            onConfirm={() => handleFinish(record)}
          >
            <Button size="small" type="primary">完成生产</Button>
          </Popconfirm>
        </Space>''',
    '''        <Space wrap size={4}>
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
        </Space>'''
)

with open('src/PendingProduction.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('待生产页面打回草稿和重新排单功能完成')
