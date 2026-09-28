with open('src/ScheduleList.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 加取消排单函数（在 handleStartProduction 后面）
content = content.replace(
    '  // 移入待生产\n  const handleStartProduction = async (record) => {',
    '''  // 取消排单
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
  const handleStartProduction = async (record) => {'''
)

# 2. 操作列加取消排单按钮
content = content.replace(
    '''          {record.status === 'scheduled' && (
            <Popconfirm
              title="确认移入待生产？"
              description="移入后将锁定对应卷料库存"
              onConfirm={() => handleStartProduction(record)}
            >
              <Button size="small" type="primary">移入待生产</Button>
            </Popconfirm>
          )}''',
    '''          {record.status === 'scheduled' && (
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
          )}'''
)

with open('src/ScheduleList.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('已排单页面取消排单功能完成')
