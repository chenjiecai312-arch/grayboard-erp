with open('src/ProduceOrder.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 加卷料选择弹窗的state
content = content.replace(
    '  const [returnItems, setReturnItems] = useState([]);',
    '  const [returnItems, setReturnItems] = useState([]);\n  // 卷料选择弹窗\n  const [rollSelectModalOpen, setRollSelectModalOpen] = useState(false);\n  const [currentLayerIndex, setCurrentLayerIndex] = useState(null);\n  const [rollSearchText, setRollSearchText] = useState("");'
)

# 2. 打开卷料选择弹窗
content = content.replace(
    '  // 新增\n  const openAdd = () => {',
    '''  // 打开卷料选择弹窗
  const openRollSelect = (layerIndex) => {
    setCurrentLayerIndex(layerIndex);
    setRollSearchText("");
    setRollSelectModalOpen(true);
  };

  // 选择卷料
  const selectRoll = (roll) => {
    if (currentLayerIndex !== null) {
      updateItem(currentLayerIndex, 'roll_id', roll.id);
    }
    setRollSelectModalOpen(false);
  };

  // 过滤卷料列表
  const filteredRollList = rollList.filter(r => {
    const kw = rollSearchText.toLowerCase();
    return !kw || String(r.raw_no).toLowerCase().includes(kw) || String(r.gram).includes(kw) || String(r.width).includes(kw);
  });

  // 新增
  const openAdd = () => {'''
)

# 3. 把下拉框改成选择按钮
content = content.replace(
    '''              <Select
                placeholder="选择卷料"
                value={item.roll_id || undefined}
                onChange={val => updateItem(index, 'roll_id', val)}
                style={{ width: 200 }}
                showSearch optionFilterProp="children"
              >
                {rollList.filter(r => (r.stock_weight || 0) > 0).map(r => (
                  <Select.Option key={r.id} value={r.id}>{r.raw_no} (剩{r.stock_weight?.toFixed(3)}吨)</Select.Option>
                ))}
              </Select>''',
    '''              <Button onClick={() => openRollSelect(index)} style={{ width: 200, textAlign: 'left' }}>
                {item.roll_name ? item.roll_name : '点击选择卷料'}
              </Button>'''
)

# 4. 在退料弹窗后面加卷料选择弹窗
content = content.replace(
    '    </div>\n  );\n}',
    '''      {/* 卷料选择弹窗 */}
      <Modal
        open={rollSelectModalOpen}
        title="选择卷料"
        onCancel={() => setRollSelectModalOpen(false)}
        footer={null}
        width={900}
      >
        <Input
          placeholder="搜索编号/克重/幅宽"
          value={rollSearchText}
          onChange={e => setRollSearchText(e.target.value)}
          style={{ marginBottom: 12, width: 300 }}
          allowClear
        />
        <Table
          rowKey="id"
          dataSource={filteredRollList}
          size="small"
          pagination={{ pageSize: 8 }}
          columns={[
            { title: '卷筒编号', dataIndex: 'raw_no', width: 180 },
            { title: '幅宽(mm)', dataIndex: 'width', width: 90 },
            { title: '克重(g)', dataIndex: 'gram', width: 90 },
            { title: '剩余库存(吨)', dataIndex: 'stock_weight', width: 110, render: v => Number(v).toFixed(3) },
            { title: '吨价(元/吨)', dataIndex: 'ton_price', width: 110, render: v => v ? Number(v).toFixed(2) : '-' },
            {
              title: '操作', width: 80,
              render: (_, record) => <Button size="small" type="primary" onClick={() => selectRoll(record)}>选择</Button>
            }
          ]}
        />
      </Modal>
    </div>
  );
}'''
)

with open('src/ProduceOrder.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('卷料选择弹窗改完成')
