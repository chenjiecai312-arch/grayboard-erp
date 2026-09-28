with open('src/PurchaseOrder.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 重写 getCategoryPath 函数，支持完整4级路径
old_func = '''  // 获取物理分类完整路径
  const getCategoryPath = (catId) => {
    if (!catId) return '';
    const cat = pcList.find(c => c.id === catId);
    if (!cat) return '';
    if (!cat.parent_id) return cat.name;
    const parent = pcList.find(c => c.id === cat.parent_id);
    if (!parent) return cat.name;
    if (!parent.parent_id) return `${parent.name}/${cat.name}`;
    const grandparent = pcList.find(c => c.id === parent.parent_id);
    if (!grandparent) return `${parent.name}/${cat.name}`;
    return `${grandparent.name}/${parent.name}/${cat.name}`;
  };'''

new_func = '''  // 获取物理分类完整路径（支持任意层级，最多4级）
  const getCategoryPath = (catId) => {
    if (!catId) return '';
    const path = [];
    let current = pcList.find(c => c.id === catId);
    let guard = 0;
    while (current && guard < 10) {
      path.unshift(current.name);
      current = current.parent_id ? pcList.find(c => c.id === current.parent_id) : null;
      guard++;
    }
    return path.join('/');
  };'''

content = content.replace(old_func, new_func)

# 2. 到货确认弹窗品牌列，空时显示灰色提示
content = content.replace(
    '''                  <div style={{ flex: 1.5, padding: '4px' }}>{getCategoryPath(item.category_id)}</div>''',
    '''                  <div style={{ flex: 1.5, padding: '4px' }}>
                    {item.category_id ? getCategoryPath(item.category_id) : <span style={{color:'#999'}}>未选择分类</span>}
                  </div>'''
)

with open('src/PurchaseOrder.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('物理分类路径显示修复完成（支持4级+空提示）')
