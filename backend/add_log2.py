with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# ========== 成品仓：修改成品 加日志 ==========
old1 = '''    for key, value in item.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj

@app.delete("/api/product/{product_id}")'''
new1 = '''    for key, value in item.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
    # 记录日志
    log = DBOperationLog(module="成品仓", action="修改", target_type="成品", target_id=obj.id, detail=f"修改成品：{obj.spec}，修改了{list(item.model_dump(exclude_unset=True).keys())}")
    db.add(log)
    db.commit()
    db.refresh(obj)
    return obj

@app.delete("/api/product/{product_id}")'''
content = content.replace(old1, new1)

# ========== 成品仓：移入待出库 加日志 ==========
old2 = '''    # 总库存不变，待出库数量增加
    obj.pending_out_qty += data.quantity
    record = DBPendingOut(
        product_id=obj.id,
        quantity=data.quantity,
        reason=data.reason or "",
        status="pending"
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record'''
new2 = '''    # 总库存不变，待出库数量增加
    obj.pending_out_qty += data.quantity
    record = DBPendingOut(
        product_id=obj.id,
        quantity=data.quantity,
        reason=data.reason or "",
        status="pending"
    )
    db.add(record)
    # 记录日志
    log = DBOperationLog(module="成品仓", action="移入待出库", target_type="成品", target_id=obj.id, detail=f"移入待出库：{obj.spec}，数量{data.quantity}，原因：{data.reason}")
    db.add(log)
    db.commit()
    db.refresh(record)
    return record'''
content = content.replace(old2, new2)

# ========== 成品仓：取消待出库 加日志 ==========
old3 = '''    record.status = "cancelled"
    db.commit()
    db.refresh(record)
    return record

# 确认出库（真正扣减总库存，待出库数量减少）'''
new3 = '''    record.status = "cancelled"
    # 记录日志
    log = DBOperationLog(module="成品仓", action="取消待出库", target_type="待出库", target_id=record.id, detail=f"取消待出库：产品ID{record.product_id}，数量{record.quantity}，原因：{record.reason}")
    db.add(log)
    db.commit()
    db.refresh(record)
    return record

# 确认出库（真正扣减总库存，待出库数量减少）'''
content = content.replace(old3, new3)

# ========== 成品仓：确认出库 加日志 ==========
old4 = '''    product.pending_out_qty -= record.quantity
    record.status = "confirmed"
    db.commit()
    db.refresh(record)
    return record

# ----------------成品品名接口（独立）----------------'''
new4 = '''    product.pending_out_qty -= record.quantity
    record.status = "confirmed"
    # 记录日志
    log = DBOperationLog(module="成品仓", action="确认出库", target_type="待出库", target_id=record.id, detail=f"确认出库：产品ID{record.product_id}，数量{record.quantity}，原因：{record.reason}")
    db.add(log)
    db.commit()
    db.refresh(record)
    return record

# ----------------成品品名接口（独立）----------------'''
content = content.replace(old4, new4)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('成品仓所有操作日志加完成')
