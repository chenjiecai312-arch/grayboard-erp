with open('src/ProduceOrder.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 加获取二级分类名称的函数（在 getCategoryPath 后面）
content = content.replace(
    '  const filteredRollList = rollList.filter(r => {',
    '''  // 获取二级分类名称（纸名）
  const getSecondCategoryName = (categoryId) => {
    if (!categoryId) return '';
    const path = [];
    let current = pcList.find(c => c.id === categoryId);
    while (current) {
      path.unshift(current);
      current = pcList.find(c => c.id === current.parent_id);
    }
    return path.length >= 2 ? path[1].name : (path.length === 1 ? path[0].name : '');
  };

  // 自动计算生产工艺
  const calcCraft = (itemsList) => {
    return itemsList.map(item => {
      const roll = rollList.find(r => r.id === item.roll_id);
      if (!roll) return '';
      const name = getSecondCategoryName(roll.category_id);
      return `${name}${roll.gram}`;
    }).filter(s => s).join('+');
  };

  const filteredRollList = rollList.filter(r => {'''
)

# 2. updateItem 里自动填入生产工艺
content = content.replace(
    '''    newItems[index].amount = (newItems[index].quantity || 0) * (newItems[index].unit_price || 0);
    setItems(newItems);
    const totalGram = newItems.reduce((s, i) => {''',
    '''    newItems[index].amount = (newItems[index].quantity || 0) * (newItems[index].unit_price || 0);
    setItems(newItems);
    // 自动计算生产工艺
    const craft = calcCraft(newItems);
    if (craft) {
      form.setFieldsValue({ craft: craft });
    }
    const totalGram = newItems.reduce((s, i) => {'''
)

# 3. addLayer 里也重新计算生产工艺
content = content.replace(
    '''  const addLayer = () => {
    const maxLayer = Math.max(...items.map(i => i.layer_no), 0);
    setItems([...items, { layer_no: maxLayer + 1, roll_id: null, roll_name: '', quantity: 0, unit_price: 0, amount: 0, remark: '' }]);
  };''',
    '''  const addLayer = () => {
    const maxLayer = Math.max(...items.map(i => i.layer_no), 0);
    const newItems = [...items, { layer_no: maxLayer + 1, roll_id: null, roll_name: '', quantity: 0, unit_price: 0, amount: 0, remark: '' }];
    setItems(newItems);
    const craft = calcCraft(newItems);
    if (craft) form.setFieldsValue({ craft });
  };'''
)

# 4. removeLayer 里也重新计算生产工艺
content = content.replace(
    '''  const removeLayer = (index) => {
    if (items.length <= 1) return;
    const newItems = items.filter((_, i) => i !== index);
    setItems(newItems.map((item, i) => ({ ...item, layer_no: i + 1 })));
  };''',
    '''  const removeLayer = (index) => {
    if (items.length <= 1) return;
    const newItems = items.filter((_, i) => i !== index).map((item, i) => ({ ...item, layer_no: i + 1 }));
    setItems(newItems);
    const craft = calcCraft(newItems);
    if (craft) form.setFieldsValue({ craft });
  };'''
)

# 5. 打印模板里的 craft 用表单里的，而不是重新算
content = content.replace(
    "    const craft = record.items.map(i => i.roll_name?.match(/(\\d+)g/)?.[1] || '0').join('+');",
    "    const craft = record.craft || record.items.map(i => i.roll_name?.match(/(\\d+)g/)?.[1] || '0').join('+');"
)

with open('src/ProduceOrder.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('生产工艺自动生成功能完成')
