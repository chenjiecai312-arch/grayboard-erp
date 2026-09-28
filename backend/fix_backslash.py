with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 修复反斜杠转义错误
content = content.replace(
    'cat_path = " " + "\\".join(path) if path else ""',
    'cat_path = " " + "\\\\".join(path) if path else ""'
)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('反斜杠转义错误修复完成')
