with open('src/ProduceOrder.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 加销售单相关state
content = content.replace(
    '  const [scheduleDate, setScheduleDate] = useState(null);',
    '''  const [scheduleDate, setScheduleDate] = useState(null);
  // 销售单关联
  const [salesOrderList, setSalesOrderList] = useState([]);
  const [salesSelectModalOpen, setSalesSelectModalOpen] = useState(false);
  const [salesSearchText, setSalesSearchText] = useState("");
  const [salesDetailModalOpen, setSalesDetailModalOpen] = useState(false);
  const [currentSalesOrder, setCurrentSalesOrder] = useState(null);'''
)

# 2. loadData 里加销售单加载
content = content.replace(
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
      setCustomerList(cusRes.data);''',
    '''      const [orderRes, rollRes, pnRes, pcRes, cusRes, salesRes] = await Promise.all([
        api.get('/api/produce_order'),
        api.get('/api/rawroll'),
        api.get('/api/product_name'),
        api.get('/api/physical_category'),
        api.get('/api/customer'),
        api.get('/api/sales_order')
      ]);
      setList(orderRes.data);
      setRollList(rollRes.data);
      setPnList(pnRes.data);
      setPcList(pcRes.data);
      setCustomerList(cusRes.data);
      setSalesOrderList(salesRes.data);'''
)

# 3. 加销售单相关函数（在 handleSchedule 后面）
content = content.replace(
    '  const handleDelete = async (id) => {',
    '''  // 打开销售单选择弹窗
  const openSalesSelect = () => {
    setSalesSearchText("");
    setSalesSelectModalOpen(true);
  };

  // 选择销售单
  const selectSalesOrder = (order) => {
    form.setFieldsValue({ sales_order_id: order.id });
    // 自动填充客户、产品名称、数量、规格等
    if (order.customer_id) form.setFieldsValue({ customer_id: order.customer_id });
    if (order.customer_name) form.setFieldsValue({ customer_name: order.customer_name });
    if (order.items && order.items.length > 0) {
      const item = order.items[0];
      if (item.product_name) form.setFieldsValue({ product_name: item.product_name });
      if (item.quantity) form.setFieldsValue({ quantity: item.quantity });
      if (item.width) form.setFieldsValue({ spec_width: item.width });
      if (item.length) form.setFieldsValue({ spec_length: item.length });
      if (item.actual_gram) form.setFieldsValue({ total_gram: item.actual_gram });
    }
    setSalesSelectModalOpen(false);
    message.success(`已匹配销售单 ${order.order_no}`);
  };

  // 查看关联的销售单详情
  const viewLinkedSales = () => {
    const salesId = form.getFieldValue('sales_order_id');
    if (!salesId) return;
    const order = salesOrderList.find(o => o.id === salesId);
    if (order) {
      setCurrentSalesOrder(order);
      setSalesDetailModalOpen(true);
    }
  };

  // 过滤销售单
  const filteredSalesList = salesOrderList.filter(o => {
    if (!salesSearchText) return true;
    const kw = salesSearchText.toLowerCase();
    return String(o.order_no).toLowerCase().includes(kw)
      || String(o.customer_name || '').toLowerCase().includes(kw);
  });

  const handleDelete = async (id) => {'''
)

# 4. openEdit 里加 sales_order_id
content = content.replace(
    '      remark: record.remark\n    });',
    '      remark: record.remark,\n      sales_order_id: record.sales_order_id\n    });'
)

# 5. 表单里加匹配销售单按钮（在工程单号那一行后面）
content = content.replace(
    '''          <Row gutter={16}>
            <Col span={6}>
              <Form.Item label="工程单号" name="order_no"><Input placeholder="自动生成" /></Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item label="PO号" name="po_no"><Input placeholder="客户PO号" /></Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item label="客户" name="customer_id" rules={[{ required: true, message: '请选择客户' }]}>
                <Select placeholder="请选择客户" showSearch optionFilterProp="children">
                  {customerList.map(c => <Select.Option key={c.id} value={c.id}>{c.customer_name}</Select.Option>)}
                </Select>
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item label="产品名称" name="product_name"><Input placeholder="如：双面白" /></Form.Item>
            </Col>
          </Row>''',
    '''          <Row gutter={16}>
            <Col span={6}>
              <Form.Item label="工程单号" name="order_no"><Input placeholder="自动生成" /></Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item label="PO号" name="po_no"><Input placeholder="客户PO号" /></Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item label="客户" name="customer_id" rules={[{ required: true, message: '请选择客户' }]}>
                <Select placeholder="请选择客户" showSearch optionFilterProp="children">
                  {customerList.map(c => <Select.Option key={c.id} value={c.id}>{c.customer_name}</Select.Option>)}
                </Select>
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item label="产品名称" name="product_name"><Input placeholder="如：双面白" /></Form.Item>
            </Col>
          </Row>

          {/* 匹配销售单 */}
          <Row gutter={16}>
            <Col span={24}>
              <Form.Item label="关联销售单" name="sales_order_id">
                <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                  <Button onClick={openSalesSelect}>选择销售单匹配</Button>
                  {form.getFieldValue('sales_order_id') && (
                    <Button type="link" onClick={viewLinkedSales}>
                      查看已匹配的销售单
                    </Button>
                  )}
                  <span style={{ color: '#999', fontSize: 12 }}>匹配后自动带入客户、产品、数量、规格等信息</span>
                </div>
              </Form.Item>
            </Col>
          </Row>'''
)

# 6. 在退料弹窗后面加销售单选择弹窗和详情弹窗
content = content.replace(
    '      </Modal>\n    </div>\n  );\n}',
    '''      </Modal>

      {/* 销售单选择弹窗 */}
      <Modal
        open={salesSelectModalOpen}
        title="选择销售单匹配"
        onCancel={() => setSalesSelectModalOpen(false)}
        footer={null}
        width={900}
      >
        <Input
          placeholder="搜索订单号/客户名称"
          value={salesSearchText}
          onChange={e => setSalesSearchText(e.target.value)}
          style={{ marginBottom: 12, width: 300 }}
          allowClear
        />
        <Table
          rowKey="id"
          dataSource={filteredSalesList}
          size="small"
          pagination={{ pageSize: 8 }}
          columns={[
            { title: '订单号', dataIndex: 'order_no', width: 180 },
            { title: '客户', dataIndex: 'customer_name', width: 180 },
            { title: '状态', dataIndex: 'status', width: 100 },
            { title: '交期', dataIndex: 'delivery_date', width: 120 },
            {
              title: '操作', width: 100,
              render: (_, record) => <Button size="small" type="primary" onClick={() => selectSalesOrder(record)}>匹配</Button>
            }
          ]}
        />
      </Modal>

      {/* 销售单详情弹窗 */}
      <Modal
        open={salesDetailModalOpen}
        title="销售单详情"
        onCancel={() => setSalesDetailModalOpen(false)}
        footer={null}
        width={800}
      >
        {currentSalesOrder && (
          <div>
            <div style={{ marginBottom: 16, lineHeight: 2 }}>
              <p><b>订单号：</b>{currentSalesOrder.order_no}</p>
              <p><b>客户：</b>{currentSalesOrder.customer_name}</p>
              <p><b>状态：</b>{currentSalesOrder.status}</p>
              <p><b>交期：</b>{currentSalesOrder.delivery_date || '-'}</p>
              <p><b>备注：</b>{currentSalesOrder.remark || '-'}</p>
            </div>
            <Table
              rowKey="id"
              dataSource={currentSalesOrder.items || []}
              size="small"
              pagination={false}
              columns={[
                { title: '产品名称', dataIndex: 'product_name' },
                { title: '规格', width: 120, render: (_, r) => `${r.width || ''}×${r.length || ''}` },
                { title: '数量', dataIndex: 'quantity', width: 80 },
                { title: '实克', dataIndex: 'actual_gram', width: 80 },
                { title: '虚克', dataIndex: 'nominal_gram', width: 80 },
                { title: '吨价', dataIndex: 'ton_price', width: 100, render: v => v ? `¥${Number(v).toFixed(2)}` : '-' }
              ]}
            />
          </div>
        )}
      </Modal>
    </div>
  );
}'''
)

with open('src/ProduceOrder.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('生产工单匹配销售单功能完成')
