with open('src/RollWarehouse.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 表单加吨价输入
content = content.replace(
    '<Form.Item label="本支卷筒实际重量(吨)" name="weight" rules={[{ required: true }]}><Input /></Form.Item>',
    '<Form.Item label="本支卷筒实际重量(吨)" name="weight" rules={[{ required: true }]}><Input /></Form.Item>\n          <Form.Item label="吨价(元/吨)" name="ton_price"><Input placeholder="例如：2270" /></Form.Item>'
)

# 2. 列定义加吨价列（在剩余库存后面）
content = content.replace(
    "stock_weight: {\n      title: \"剩余库存(吨)\", dataIndex: \"stock_weight\", key: \"stock_weight\", width: 130,",
    "ton_price: { title: \"吨价(元/吨)\", dataIndex: \"ton_price\", key: \"ton_price\", width: 110, render: v => v ? Number(v).toFixed(2) : '-' },\n    stock_weight: {\n      title: \"剩余库存(吨)\", dataIndex: \"stock_weight\", key: \"stock_weight\", width: 130,"
)

# 3. 汇总加总金额
content = content.replace(
    '汇总：卷筒总数量 {stat.count} 个 &nbsp;｜&nbsp; 库存总重量 {stat.totalStock.toFixed(3)} 吨',
    '汇总：卷筒总数量 {stat.count} 个 &nbsp;｜&nbsp; 库存总重量 {stat.totalStock.toFixed(3)} 吨 &nbsp;｜&nbsp; 库存总金额 ¥{stat.totalAmount.toFixed(2)}'
)

# 4. stat 计算加总金额
content = content.replace(
    'const totalStock = filterList.reduce((sum,item)=>sum+(Number(item.stock_weight)||0),0)\n    return {count,totalStock}',
    'const totalStock = filterList.reduce((sum,item)=>sum+(Number(item.stock_weight)||0),0)\n    const totalAmount = filterList.reduce((sum,item)=>sum+(Number(item.stock_weight)||0)*(Number(item.ton_price)||0),0)\n    return {count,totalStock,totalAmount}'
)

with open('src/RollWarehouse.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('前端吨价加完成')
