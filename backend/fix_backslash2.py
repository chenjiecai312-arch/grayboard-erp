# 直接读取文件，找到错误行，用正确的内容替换
with open('main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'cat_path = " " + "\\"' in line or 'cat_path = " " + "\\".join' in line:
        # 用正确的反斜杠连接
        lines[i] = '                    cat_path = " " + chr(92).join(path) if path else ""\n'
        print(f'修复第 {i+1} 行')
        break

with open('main.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('修复完成')
