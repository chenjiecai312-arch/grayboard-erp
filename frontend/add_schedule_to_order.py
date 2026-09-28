with open('src/ProduceOrder.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 加勾选和排单弹窗的state
content = content.replace(
    '  const [returnItems, setReturnItems] = useState([]);',
    '''  const [returnItems, setReturnItems] = useState([]);
  // 排单相关
  const [selectedRowKeys, setSelectedRowKeys] = useState([]);
  const [scheduleModalOpen, setScheduleModalOpen] = useState(false);
  const [scheduleDate, setScheduleDate] = useState(null);'''
)

# 2. 加排单函数（在 handleDelete 后面）
content = content.replace(
    '  const handleDelete = async (id) => {',
    '''  // 批量排单
  const handleSchedule = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请先勾选要排单的工单');
      return;
    }
    if (!scheduleDate) {
      message.warning('请选择排单日期');
      return;
    }
    try {
      await api.post('/api/produce_order/schedule', {
        ids: selectedRowKeys,
        schedule_date: scheduleDate.format('YYYY-MM-DD')
      });
      message.success(`已将 ${selectedRowKeys.length} 张工单排单到 ${scheduleDate.format('YYYY-MM-DD')}`);
      setScheduleModalOpen(false);
      setSelectedRowKeys([]);
      setScheduleDate(null);
      loadData();
    } catch (e) {
      message.error(e.response?.data?.detail || '排单失败');
    }
  };

  const handleDelete = async (id) => {'''
)

# 3. 顶部按钮加"添加到排单"
content = content.replace(
    '''      <div style={{ marginBottom: 16 }}>
        <Button type="primary" onClick={openAdd}>新增工单</Button>
      </div>''',
    '''      <div style={{ marginBottom: 16, display: 'flex', gap: 8 }}>
        <Button type="primary" onClick={openAdd}>新增工单</Button>
        <Button onClick={() => setScheduleModalOpen(true)} disabled={selectedRowKeys.length === 0}>
          添加到排单 ({selectedRowKeys.length})
        </Button>
        <span style={{ color: '#999', fontSize: 12, alignSelf: 'center' }}>勾选工单后可批量排单</span>
      </div>'''
)

# 4. Table 加 rowSelection
content = content.replace(
    '''      <Table
        rowKey="id"
        dataSource={list}
        columns={columns}
        loading={loading}
        pagination={{ pageSize: 20 }}
      />''',
    '''      <Table
        rowKey="id"
        dataSource={list}
        columns={columns}
        loading={loading}
        pagination={{ pageSize: 20 }}
        rowSelection={{
          selectedRowKeys,
          onChange: (keys) => setSelectedRowKeys(keys),
          getCheckboxProps: (record) => ({
            disabled: record.status === 'scheduled' || record.status === 'pending' || record.status === 'finished'
          })
        }}
      />'''
)

# 5. 状态映射加 scheduled 和 pending
content = content.replace(
    '''const STATUS_MAP = {
  draft: { label: '草稿', color: 'default' },
  picking: { label: '领料中', color: 'orange' },
  producing: { label: '生产中', color: 'blue' },
  finished: { label: '已完成', color: 'green' }
};''',
    '''const STATUS_MAP = {
  draft: { label: '草稿', color: 'default' },
  scheduled: { label: '已排单', color: 'cyan' },
  pending: { label: '待生产', color: 'orange' },
  picking: { label: '领料中', color: 'orange' },
  producing: { label: '生产中', color: 'blue' },
  finished: { label: '已完成', color: 'green' }
};'''
)

# 6. 列表加排单日期列
content = content.replace(
    "    { title: '日期', dataIndex: 'produce_date', width: 100 },",
    "    { title: '生产日期', dataIndex: 'produce_date', width: 100 },\n    { title: '排单日期', dataIndex: 'schedule_date', width: 100 },"
)

# 7. 在退料弹窗后面加排单弹窗
content = content.replace(
    '      </Modal>\n    </div>\n  );\n}',
    '''      </Modal>

      {/* 排单日期选择弹窗 */}
      <Modal
        open={scheduleModalOpen}
        title="选择排单日期"
        onCancel={() => setScheduleModalOpen(false)}
        onOk={handleSchedule}
        width={400}
      >
        <p style={{ marginBottom: 16 }}>已选择 {selectedRowKeys.length} 张工单，请指派生产日期：</p>
        <DatePicker
          style={{ width: '100%' }}
          value={scheduleDate}
          onChange={setScheduleDate}
          placeholder="选择排单日期"
        />
      </Modal>
    </div>
  );
}'''
)

with open('src/ProduceOrder.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('工单主页排单功能加完成')
