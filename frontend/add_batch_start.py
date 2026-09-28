with open('src/ScheduleList.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 加多选state
content = content.replace(
    '  const [filterDate, setFilterDate] = useState(null);',
    '  const [filterDate, setFilterDate] = useState(null);\n  const [selectedRowKeys, setSelectedRowKeys] = useState([]);'
)

# 2. 加批量移入待生产函数
content = content.replace(
    '  // 移入待生产\n  const handleStartProduction = async (record) => {',
    '''  // 批量移入待生产
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

  // 移入待生产
  const handleStartProduction = async (record) => {'''
)

# 3. 顶部加批量按钮
content = content.replace(
    '''      <div style={{ marginBottom: 16, display: 'flex', gap: 8, alignItems: 'center' }}>
        <span>按日期筛选：</span>
        <DatePicker
          value={filterDate}
          onChange={setFilterDate}
          placeholder="选择日期"
          allowClear
        />
        <Button onClick={() => setFilterDate(null)}>显示全部</Button>
      </div>''',
    '''      <div style={{ marginBottom: 16, display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
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
      </div>'''
)

# 4. Table 加 rowSelection（只对已排单状态的可勾选）
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
            disabled: record.status !== 'scheduled'
          })
        }}
      />'''
)

with open('src/ScheduleList.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('已排单页面多选功能完成')
