with open('src/App.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 加 import
content = content.replace(
    "import PurchaseOrder from './PurchaseOrder';",
    "import PurchaseOrder from './PurchaseOrder';\nimport SupplierManage from './SupplierManage';"
)

# 2. 加菜单项（在客户档案后面）
content = content.replace(
    '          <Menu.Item key="customer">客户档案</Menu.Item>',
    '          <Menu.Item key="customer">客户档案</Menu.Item>\n          <Menu.Item key="supplier">供应商管理</Menu.Item>'
)

# 3. 加路由渲染
content = content.replace(
    '        {activeKey === "customer" && <CustomerManage />}',
    '        {activeKey === "customer" && <CustomerManage />}\n        {activeKey === "supplier" && <SupplierManage />}'
)

with open('src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('App.jsx 供应商管理菜单和路由加完成')
