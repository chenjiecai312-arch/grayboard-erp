with open('src/ProduceOrder.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 加销售订单状态映射（在 STATUS_MAP 后面）
content = content.replace(
    '''const STATUS_MAP = {
  draft: { label: '草稿', color: 'default' },
  scheduled: { label: '已排单', color: 'cyan' },
  pending: { label: '待生产', color: 'orange' },
  picking: { label: '领料中', color: 'orange' },
  producing: { label: '生产中', color: 'blue' },
  finished: { label: '已完成', color: 'green' }
};''',
    '''const STATUS_MAP = {
  draft: { label: '草稿', color: 'default' },
  scheduled: { label: '已排单', color: 'cyan' },
  pending: { label: '待生产', color: 'orange' },
  picking: { label: '领料中', color: 'orange' },
  producing: { label: '生产中', color: 'blue' },
  finished: { label: '已完成', color: 'green' }
};

// 销售订单状态映射
const SALES_STATUS_MAP = {
  draft: '草稿',
  pending: '待出库',
  confirmed: '已出库',
  delivered: '已送出',
  completed: '已完成',
  cancelled: '已取消'
};'''
)

# 2. 销售单选择弹窗的状态列改成中文
content = content.replace(
    "            { title: '状态', dataIndex: 'status', width: 100 },",
    "            { title: '状态', dataIndex: 'status', width: 100, render: v => SALES_STATUS_MAP[v] || v },"
)

with open('src/ProduceOrder.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('销售单状态中文显示完成')
