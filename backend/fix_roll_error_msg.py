with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换 start_production 里的报错信息，加完整分类路径
old_error = '''            if roll.stock_weight < item.quantity:
                raise HTTPException(status_code=400, detail=f"卷料 {roll.raw_no} 库存不足，当前剩余 {roll.stock_weight:.3f} 吨")'''

new_error = '''            if roll.stock_weight < item.quantity:
                # 拼接完整分类路径
                cat_path = ""
                if roll.category_id:
                    path = []
                    cur = db.query(DBPhysicalCategory).filter(DBPhysicalCategory.id == roll.category_id).first()
                    while cur:
                        path.insert(0, cur.name)
                        cur = db.query(DBPhysicalCategory).filter(DBPhysicalCategory.id == cur.parent_id).first()
                    cat_path = " " + "\\".join(path) if path else ""
                raise HTTPException(status_code=400, detail=f"卷料 {roll.raw_no}{cat_path} 库存不足，当前剩余 {roll.stock_weight:.3f} 吨")'''

content = content.replace(old_error, new_error)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('后端报错信息显示完整分类路径完成')
