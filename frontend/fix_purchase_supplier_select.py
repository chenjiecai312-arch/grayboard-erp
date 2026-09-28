with open('src/PurchaseOrder.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 加供应商列表 state
content = content.replace(
    '  const [pcList, setPcList] = useState([]);',
    '  const [pcList, setPcList] = useState([]);\n  const [supplierList, setSupplierList] = useState([]);'
)

# 2. loadData 里加供应商加载
content = content.replace(
    '''      const [res, pcRes] = await Promise.all([
        api.get('/api/purchase_order'),
        api.get('/api/physical_category')
      ]);
      setList(res.data);
      setPcList(pcRes.data);''',
    '''      const [res, pcRes, supplierRes] = await Promise.all([
        api.get('/api/purchase_order'),
        api.get('/api/physical_category'),
        api.get('/api/supplier')
      ]);
      setList(res.data);
      setPcList(pcRes.data);
      setSupplierList(supplierRes.data);'''
)

# 3. 把供应商 Input 改成 Select，选择后自动带入地址
content = content.replace(
    '''            <div style={{ flex: 1 }}>
              <Form.Item label="供应商" name="supplier" rules={[{ required: true, message: '请输入供应商' }]}>
                <Input placeholder="如：东莞市金田纸业有限公司" />
              </Form.Item>
            </div>''',
    '''            <div style={{ flex: 1 }}>
              <Form.Item label="供应商" name="supplier" rules={[{ required: true, message: '请选择供应商' }]}>
                <Select
                  placeholder="从供应商档案选择"
                  showSearch
                  optionFilterProp="children"
                  onChange={(value, option) => {
                    // 选择供应商后自动带入地址
                    const sup = supplierList.find(s => s.name === value);
                    if (sup && sup.address) {
                      form.setFieldsValue({ delivery_address: sup.address });
                    }
                  }}
                >
                  {supplierList.map(s => (
                    <Select.Option key={s.id} value={s.name}>{s.name}</Select.Option>
                  ))}
                </Select>
              </Form.Item>
            </div>'''
)

with open('src/PurchaseOrder.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('采购单供应商改下拉选择完成')
