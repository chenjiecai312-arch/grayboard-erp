with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 入库加日志
old = '''    obj.quantity += data.quantity
    db.commit()
    db.refresh(obj)
    return obj

# 移入待出库'''
new = '''    obj.quantity += data.quantity
    # 记录日志
    log = DBOperationLog(module="成品仓", action="入库", target_type="成品", target_id=obj.id, detail=f"入库：{obj.spec}，入库{data.quantity}，现库存{obj.quantity}")
    db.add(log)
    db.commit()
    db.refresh(obj)
    return obj

# 移入待出库'''
content = content.replace(old, new)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('入库日志加完成')
