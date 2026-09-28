with open('src/App.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 给 RollWarehouse 传 onNavigate
content = content.replace(
    '{activeKey === "ware_roll" && <RollWarehouse />}',
    '{activeKey === "ware_roll" && <RollWarehouse onNavigate={setActiveKey} />}'
)

with open('src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('RollWarehouse 导航回调加完成')
