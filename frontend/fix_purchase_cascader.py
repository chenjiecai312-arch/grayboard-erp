with open('src/PurchaseOrder.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. import 加 Cascader
content = content.replace(
    "import { Table, Button, Input, Modal, Form, Select, message, DatePicker, Space, InputNumber } from 'antd';",
    "import { Table, Button, Input, Modal, Form, Select, message, DatePicker, Space, InputNumber, Cascader } from 'antd';"
)

# 2. 加构建分类树的函数（在 getCategoryPath 后面）
content = content.replace(
    '''  // 一级分类列表
  const level1List = pcList.filter(c => c.parent_id === null);''',
    '''  // 构建物理分类树形结构（用于级联选择）
  const buildCategoryTree = (parentId = null) => {
    return pcList
      .filter(c => c.parent_id === parentId)
      .map(c => ({
        value: c.id,
        label: c.name,
        children: buildCategoryTree(c.id)
      }));
  };
  const categoryTree = buildCategoryTree();

  // 根据 category_id 反查级联选择路径
  const getCategoryPathValue = (catId) => {
    if (!catId) return undefined;
    const path = [];
    let current = pcList.find(c => c.id === catId);
    while (current) {
      path.unshift(current.id);
      current = current.parent_id ? pcList.find(c => c.id === current.parent_id) : null;
    }
    return path.length > 0 ? path : undefined;
  };

  // 一级分类列表
  const level1List = pcList.filter(c => c.parent_id === null);'''
)

# 3. 把明细行里的品牌 Select 改成 Cascader
content = content.replace(
    '''                <div style={{ flex: 1.5, padding: '4px' }}>
                  <Select
                    placeholder="选择品牌"
                    value={item.category_id || undefined}
                    onChange={v => updateItemRow(idx, 'category_id', v)}
                    style={{ width: '100%' }}
                    showSearch
                    optionFilterProp="children"
                  >
                    {pcList.map(c => (
                      <Select.Option key={c.id} value={c.id}>{getCategoryPath(c.id)}</Select.Option>
                    ))}
                  </Select>
                </div>''',
    '''                <div style={{ flex: 1.5, padding: '4px' }}>
                  <Cascader
                    placeholder="一级一级选择品牌"
                    value={getCategoryPathValue(item.category_id)}
                    onChange={(_, selectedOptions) => {
                      if (selectedOptions && selectedOptions.length > 0) {
                        const last = selectedOptions[selectedOptions.length - 1];
                        updateItemRow(idx, 'category_id', last.value);
                      } else {
                        updateItemRow(idx, 'category_id', null);
                      }
                    }}
                    options={categoryTree}
                    style={{ width: '100%' }}
                    changeOnSelect
                  />
                </div>'''
)

with open('src/PurchaseOrder.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('采购单品牌选择改级联完成')
