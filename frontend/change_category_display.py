with open('src/ProduceOrder.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 加 pcList state
content = content.replace(
    '  const [pnList, setPnList] = useState([]);\n  const [customerList, setCustomerList] = useState([]);',
    '  const [pnList, setPnList] = useState([]);\n  const [pcList, setPcList] = useState([]);\n  const [customerList, setCustomerList] = useState([]);'
)

# 2. loadData 里加物理分类加载
content = content.replace(
    '''      const [orderRes, rollRes, pnRes, cusRes] = await Promise.all([
        api.get('/api/produce_order'),
        api.get('/api/rawroll'),
        api.get('/api/product_name'),
        api.get('/api/customer')
      ]);
      setList(orderRes.data);
      setRollList(rollRes.data);
      setPnList(pnRes.data);
      setCustomerList(cusRes.data);''',
    '''      const [orderRes, rollRes, pnRes, pcRes, cusRes] = await Promise.all([
        api.get('/api/produce_order'),
        api.get('/api/rawroll'),
        api.get('/api/product_name'),
        api.get('/api/physical_category'),
        api.get('/api/customer')
      ]);
      setList(orderRes.data);
      setRollList(rollRes.data);
      setPnList(pnRes.data);
      setPcList(pcRes.data);
      setCustomerList(cusRes.data);'''
)

# 3. 加获取分类路径的函数（在 filteredRollList 前面）
content = content.replace(
    '  const filteredRollList = rollList.filter(r => {',
    '''  // 获取完整分类路径
  const getCategoryPath = (categoryId) => {
    if (!categoryId) return '-';
    const path = [];
    let current = pcList.find(c => c.id === categoryId);
    while (current) {
      path.unshift(current.name);
      current = pcList.find(c => c.id === current.parent_id);
    }
    return path.join(' / ');
  };

  const filteredRollList = rollList.filter(r => {'''
)

# 4. 选择原料弹窗的列，把原料名称改成物理分类
content = content.replace(
    '''            { title: '原料名称', dataIndex: 'product_name_id', width: 120, render: v => {
              const pn = pnList.find(p => p.id === v);
              return pn?.name || '-';
            }},
            { title: '克重(g)', dataIndex: 'gram', width: 80 },
            { title: '幅宽(mm)', dataIndex: 'width', width: 90 },''',
    '''            { title: '物理分类', dataIndex: 'category_id', width: 280, render: (v, record) => getCategoryPath(v) },
            { title: '克重(g)', dataIndex: 'gram', width: 80 },
            { title: '幅宽(mm)', dataIndex: 'width', width: 90 },'''
)

# 5. 选料后 roll_name 用分类路径
content = content.replace(
    '''        newItems[index].roll_name = `${pn?.name || ''} ${roll.gram}g ${roll.width}mm`;''',
    '''        newItems[index].roll_name = getCategoryPath(roll.category_id);'''
)

# 6. 搜索字段里把 name 改成 分类
content = content.replace(
    '''            <Select.Option value="name">原料名称</Select.Option>''',
    '''            <Select.Option value="name">物理分类</Select.Option>'''
)

# 7. 搜索逻辑里 name 改成分类路径
content = content.replace(
    '''      case 'name': return (pn?.name || '').toLowerCase().includes(kw);''',
    '''      case 'name': return getCategoryPath(r.category_id).toLowerCase().includes(kw);'''
)

# 8. default 搜索里也加分类路径
content = content.replace(
    '''      default:
        return (pn?.name || '').toLowerCase().includes(kw)
          || String(r.gram).includes(kw)
          || String(r.width).includes(kw)
          || String(r.raw_no).toLowerCase().includes(kw);''',
    '''      default:
        return getCategoryPath(r.category_id).toLowerCase().includes(kw)
          || String(r.gram).includes(kw)
          || String(r.width).includes(kw)
          || String(r.raw_no).toLowerCase().includes(kw);'''
)

with open('src/ProduceOrder.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('原料选择显示完整分类路径完成')
