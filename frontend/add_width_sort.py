with open('src/RollWarehouse.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 给幅宽、克重、剩余库存加上排序
content = content.replace(
    'width: { title: "幅宽(mm)", dataIndex: "width", key: "width", width: 100 },',
    'width: { title: "幅宽(mm)", dataIndex: "width", key: "width", width: 100, sorter: (a, b) => Number(a.width) - Number(b.width) },'
)
content = content.replace(
    'gram: { title: "克重(g)", dataIndex: "gram", key: "gram", width: 100 },',
    'gram: { title: "克重(g)", dataIndex: "gram", key: "gram", width: 100, sorter: (a, b) => Number(a.gram) - Number(b.gram) },'
)

with open('src/RollWarehouse.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('幅宽排序加完成')
