with open('src/App.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 加 import
content = content.replace(
    "import PendingProduction from './PendingProduction';",
    "import PendingProduction from './PendingProduction';\nimport PurchaseOrder from './PurchaseOrder';"
)

# 2. 加菜单项
content = content.replace(
    '            <Menu.Item key="ware_material">辅料仓</Menu.Item>\n          </Menu.SubMenu>',
    '            <Menu.Item key="ware_material">辅料仓</Menu.Item>\n            <Menu.Item key="purchase">采购单</Menu.Item>\n          </Menu.SubMenu>'
)

# 3. 加路由渲染
content = content.replace(
    '        {activeKey === "ware_material" && <MaterialWarehouse />}',
    '        {activeKey === "ware_material" && <MaterialWarehouse />}\n        {activeKey === "purchase" && <PurchaseOrder />}'
)

with open('src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('App.jsx 采购单菜单和路由加完成')
