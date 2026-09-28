with open('src/App.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 导入 ProduceOrder
content = content.replace(
    "import OperationLog from './OperationLog';",
    "import OperationLog from './OperationLog';\nimport ProduceOrder from './ProduceOrder';"
)

# 2. 把原来的生产工单占位页面替换成新的 ProduceOrder
old_produce = '''        {/*生产工单页面*/}
        {activeKey === "produce" && (
          <div style={{ padding:20 }}>
            <h2>生产工单</h2>
            <Input placeholder="搜索工单/关联销售单号" value={produceSearch} onChange={e=>setProduceSearch(e.target.value)} style={{width:340,marginBottom:16}} />
            <Button type="primary" style={{marginLeft:10,marginBottom:16}}>新建工单</Button>
            <Table bordered dataSource={produceFilter} rowKey="id" columns={[
              {title:"工单编号",dataIndex:"order_no"},
              {title:"关联销售单",dataIndex:"sale_order_no"},
              {title:"规格",dataIndex:"spec"},
              {title:"状态",dataIndex:"status"}
            ]}/>
          </div>
        )}'''

new_produce = '''        {/*生产工单页面*/}
        {activeKey === "produce" && <ProduceOrder />}'''

content = content.replace(old_produce, new_produce)

with open('src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('生产工单页面接入完成')
