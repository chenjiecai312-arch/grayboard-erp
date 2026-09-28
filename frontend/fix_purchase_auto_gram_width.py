with open('src/PurchaseOrder.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 修改 Cascader 的 onChange，自动提取克重和幅宽
old_onchange = '''                    onChange={(_, selectedOptions) => {
                      if (selectedOptions && selectedOptions.length > 0) {
                        const last = selectedOptions[selectedOptions.length - 1];
                        updateItemRow(idx, 'category_id', last.value);
                      } else {
                        updateItemRow(idx, 'category_id', null);
                      }
                    }}'''

new_onchange = '''                    onChange={(_, selectedOptions) => {
                      if (selectedOptions && selectedOptions.length > 0) {
                        const last = selectedOptions[selectedOptions.length - 1];
                        const newItems = [...items];
                        newItems[idx] = { ...newItems[idx], category_id: last.value };

                        // 第3级是克重（如"400G"），提取数字自动填入
                        if (selectedOptions.length >= 3) {
                          const gramName = selectedOptions[2].label || '';
                          const gramMatch = String(gramName).match(/[\\d.]+/);
                          if (gramMatch) {
                            newItems[idx].gram = Number(gramMatch[0]);
                          }
                        }
                        // 第4级是幅宽（如"635"），提取数字自动填入
                        if (selectedOptions.length >= 4) {
                          const widthName = selectedOptions[3].label || '';
                          const widthMatch = String(widthName).match(/[\\d.]+/);
                          if (widthMatch) {
                            newItems[idx].width = Number(widthMatch[0]);
                          }
                        }
                        setItems(newItems);
                        triggerAutoSave();
                      } else {
                        updateItemRow(idx, 'category_id', null);
                      }
                    }}'''

content = content.replace(old_onchange, new_onchange)

with open('src/PurchaseOrder.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('选分类自动填入克重幅宽完成')
