with open('src/ProduceOrder.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 卷料选择弹窗的列，加品名、分类，把编号放后面
old_columns = '''          columns={[
            { title: '卷筒编号', dataIndex: 'raw_no', width: 180 },
            { title: '幅宽(mm)', dataIndex: 'width', width: 90 },
            { title: '克重(g)', dataIndex: 'gram', width: 90 },
            { title: '剩余库存(吨)', dataIndex: 'stock_weight', width: 110, render: v => Number(v).toFixed(3) },
            { title: '吨价(元/吨)', dataIndex: 'ton_price', width: 110, render: v => v ? Number(v).toFixed(2) : '-' },
            {
              title: '操作', width: 80,
              render: (_, record) => <Button size="small" type="primary" onClick={() => selectRoll(record)}>选择</Button>
            }
          ]}'''

new_columns = '''          columns={[
            { title: '原料名称', dataIndex: 'product_name_id', width: 120, render: v => {
              const pn = pnList.find(p => p.id === v);
              return pn?.name || '-';
            }},
            { title: '克重(g)', dataIndex: 'gram', width: 80 },
            { title: '幅宽(mm)', dataIndex: 'width', width: 90 },
            { title: '卷筒编号', dataIndex: 'raw_no', width: 160 },
            { title: '剩余库存(吨)', dataIndex: 'stock_weight', width: 100, render: v => Number(v).toFixed(3) },
            { title: '吨价(元/吨)', dataIndex: 'ton_price', width: 100, render: v => v ? Number(v).toFixed(2) : '-' },
            {
              title: '操作', width: 70, fixed: 'right',
              render: (_, record) => <Button size="small" type="primary" onClick={() => selectRoll(record)}>选择</Button>
            }
          ]}'''

content = content.replace(old_columns, new_columns)

# 加pnList的加载（卷料的品名）
content = content.replace(
    '  const [rollList, setRollList] = useState([]);\n  const [customerList, setCustomerList] = useState([]);',
    '  const [rollList, setRollList] = useState([]);\n  const [pnList, setPnList] = useState([]);\n  const [customerList, setCustomerList] = useState([]);'
)

# loadData里加品名加载
content = content.replace(
    '''      const [orderRes, rollRes, cusRes] = await Promise.all([
        api.get('/api/produce_order'),
        api.get('/api/rawroll'),
        api.get('/api/customer')
      ]);
      setList(orderRes.data);
      setRollList(rollRes.data);
      setCustomerList(cusRes.data);''',
    '''      const [orderRes, rollRes, pnRes, cusRes] = await Promise.all([
        api.get('/api/produce_order'),
        api.get('/api/rawroll'),
        api.get('/api/product_name'),
        api.get('/api/customer')
      ]);
      setList(orderRes.data);
      setRollList(rollRes.data);
      setPnList(pnRes.data);
      setCustomerList(cusRes.data);'''
)

# 选择卷料后，roll_name用 品名+克重+幅宽 格式
content = content.replace(
    '''      const roll = rollList.find(r => r.id === value);
      if (roll) {
        newItems[index].roll_name = roll.raw_no;
        newItems[index].unit_price = roll.ton_price || 0;
      }''',
    '''      const roll = rollList.find(r => r.id === value);
      if (roll) {
        const pn = pnList.find(p => p.id === roll.product_name_id);
        newItems[index].roll_name = `${pn?.name || ''} ${roll.gram}g ${roll.width}mm`;
        newItems[index].unit_price = roll.ton_price || 0;
      }'''
)

with open('src/ProduceOrder.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('卷料选择显示完整信息完成')
