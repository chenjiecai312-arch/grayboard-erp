with open('src/SalesOrder.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 修复正则，支持小数
content = content.replace(
    "const m = String(product.spec).match(/(\\d+)\\s*[*xX×]\\s*(\\d+)/);",
    "const m = String(product.spec).match(/(\\d+\\.?\\d*)\\s*[*xX×]\\s*(\\d+\\.?\\d*)/);"
)

with open('src/SalesOrder.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('规格解析正则修复完成，支持小数')
