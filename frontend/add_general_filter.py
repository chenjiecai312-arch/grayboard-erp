with open('src/SalesOrder.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 加筛选字段和筛选值的状态
content = content.replace(
    '  const [searchCustomerId, setSearchCustomerId] = useState(null); // 按客户筛选',
    '  const [searchCustomerId, setSearchCustomerId] = useState(null); // 按客户筛选\n  const [searchField, setSearchField] = useState(""); // 通用筛选字段\n  const [searchValue, setSearchValue] = useState(""); // 通用筛选值'
)

# 2. 加通用筛选的UI（在搜索按钮前面）
old = '''        <DatePicker.RangePicker
          value={searchDateRange}
          onChange={val => setSearchDateRange(val)}
          placeholder={['开始日期', '结束日期']}
        />
        <Button onClick={loadData}>搜索</Button>'''

new = '''        <DatePicker.RangePicker
          value={searchDateRange}
          onChange={val => setSearchDateRange(val)}
          placeholder={['开始日期', '结束日期']}
        />
        <Select
          placeholder="筛选字段"
          value={searchField || undefined}
          onChange={val => setSearchField(val)}
          style={{ width: 120 }}
          allowClear
        >
          <Select.Option value="order_no">订单编号</Select.Option>
          <Select.Option value="customer_name">客户名称</Select.Option>
          <Select.Option value="salesman">业务员</Select.Option>
          <Select.Option value="receiver">收货人</Select.Option>
          <Select.Option value="delivery_date">送货日期</Select.Option>
        </Select>
        <Input
          placeholder="输入筛选值"
          value={searchValue}
          onChange={e => setSearchValue(e.target.value)}
          style={{ width: 160 }}
          allowClear
          onPressEnter={loadData}
        />
        <Button onClick={loadData}>搜索</Button>'''

content = content.replace(old, new)

# 3. loadData 里传筛选参数
old = '''      if (searchCustomerId) params.customer_id = searchCustomerId;'''
new = '''      if (searchCustomerId) params.customer_id = searchCustomerId;
      if (searchField && searchValue) {
        params.search_field = searchField;
        params.search_value = searchValue;
      }'''
content = content.replace(old, new)

with open('src/SalesOrder.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('通用筛选前端完成')
