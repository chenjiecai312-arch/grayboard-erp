with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 新增工单加日志（在 create_produce_order 的 return order 前面）
content = content.replace(
    '''    db.commit()
    db.refresh(order)
    return order


# ----------------生产工单明细接口----------------''',
    '''    db.commit()
    db.refresh(order)
    # 操作日志
    log = DBOperationLog(module="生产管理", action="新增", target_type="生产工单", target_id=order.id, detail=f"新增工单：{order.order_no}，客户{order.customer_name}，{order.layers}层")
    db.add(log)
    db.commit()
    return order


# ----------------生产工单明细接口----------------'''
)

# 2. 修改工单加日志（在 update_produce_order 的 return order 前面）
content = content.replace(
    '''    db.commit()
    db.refresh(order)
    return order


# 删除生产工单''',
    '''    db.commit()
    db.refresh(order)
    # 操作日志
    log = DBOperationLog(module="生产管理", action="修改", target_type="生产工单", target_id=order.id, detail=f"修改工单：{order.order_no}，客户{order.customer_name}")
    db.add(log)
    db.commit()
    return order


# 删除生产工单'''
)

# 3. 删除工单加日志（在 delete_produce_order 的 return 前面）
content = content.replace(
    '''    db.query(DBProduceOrderItem).filter(DBProduceOrderItem.order_id == order_id).delete()
    db.delete(order)
    db.commit()
    return {"ok": True}


# 确认领料''',
    '''    db.query(DBProduceOrderItem).filter(DBProduceOrderItem.order_id == order_id).delete()
    # 操作日志
    log = DBOperationLog(module="生产管理", action="删除", target_type="生产工单", target_id=order_id, detail=f"删除工单：{order.order_no}，客户{order.customer_name}")
    db.add(log)
    db.delete(order)
    db.commit()
    return {"ok": True}


# 确认领料'''
)

# 4. 确认领料加日志（在 pick_material 的 return 前面）
content = content.replace(
    '''    order.status = "picking"
    db.commit()
    return {"ok": True, "message": "领料成功"}''',
    '''    order.status = "picking"
    # 操作日志
    log = DBOperationLog(module="生产管理", action="领料", target_type="生产工单", target_id=order_id, detail=f"确认领料：{order.order_no}，锁定卷料库存")
    db.add(log)
    db.commit()
    return {"ok": True, "message": "领料成功"}'''
)

# 5. 退料加日志（在 return_material 的 return 前面）
content = content.replace(
    '''    order.status = "finished"
    db.commit()
    return {"ok": True, "message": "退料成功"}''',
    '''    order.status = "finished"
    # 操作日志
    log = DBOperationLog(module="生产管理", action="退料", target_type="生产工单", target_id=order_id, detail=f"退料完成：{order.order_no}，退回剩余卷料")
    db.add(log)
    db.commit()
    return {"ok": True, "message": "退料成功"}'''
)

# 6. 批量排单加日志（在 schedule_orders 的 return 前面）
content = content.replace(
    '''    db.commit()
    for order in orders:
        db.refresh(order)
    return {"ok": True, "count": len(orders)}''',
    '''    db.commit()
    for order in orders:
        db.refresh(order)
    # 操作日志
    for order in orders:
        log = DBOperationLog(module="生产管理", action="排单", target_type="生产工单", target_id=order.id, detail=f"排单：{order.order_no}，排单日期{req.schedule_date}")
        db.add(log)
    db.commit()
    return {"ok": True, "count": len(orders)}'''
)

# 7. 移入待生产加日志（在 start_production 的 return 前面）
content = content.replace(
    '''    order.status = "pending"
    db.commit()
    db.refresh(order)
    return {"ok": True, "status": "pending"}


@app.post("/api/produce_order/{order_id}/finish_production")''',
    '''    order.status = "pending"
    # 操作日志
    log = DBOperationLog(module="生产管理", action="移入待生产", target_type="生产工单", target_id=order_id, detail=f"移入待生产：{order.order_no}，锁定卷料库存")
    db.add(log)
    db.commit()
    db.refresh(order)
    return {"ok": True, "status": "pending"}


@app.post("/api/produce_order/{order_id}/finish_production")'''
)

# 8. 完成生产加日志（在 finish_production 的 return 前面）
content = content.replace(
    '''    order.status = "finished"
    db.commit()
    db.refresh(order)
    return {"ok": True, "status": "finished", "product_id": product.id}''',
    '''    order.status = "finished"
    # 操作日志
    log = DBOperationLog(module="生产管理", action="完成生产", target_type="生产工单", target_id=order_id, detail=f"完成生产：{order.order_no}，成品自动入库{order.quantity}令")
    db.add(log)
    db.commit()
    db.refresh(order)
    return {"ok": True, "status": "finished", "product_id": product.id}'''
)

# 9. 取消排单加日志
content = content.replace(
    '''    order.status = "draft"
    order.schedule_date = None
    db.commit()
    db.refresh(order)
    return {"ok": True, "status": "draft"}


@app.post("/api/produce_order/{order_id}/back_to_draft")''',
    '''    order.status = "draft"
    order.schedule_date = None
    # 操作日志
    log = DBOperationLog(module="生产管理", action="取消排单", target_type="生产工单", target_id=order_id, detail=f"取消排单：{order.order_no}，工单回到草稿")
    db.add(log)
    db.commit()
    db.refresh(order)
    return {"ok": True, "status": "draft"}


@app.post("/api/produce_order/{order_id}/back_to_draft")'''
)

# 10. 打回草稿加日志
content = content.replace(
    '''    order.status = "draft"
    order.schedule_date = None
    db.commit()
    db.refresh(order)
    return {"ok": True, "status": "draft"}


@app.post("/api/produce_order/{order_id}/reschedule")''',
    '''    order.status = "draft"
    order.schedule_date = None
    # 操作日志
    log = DBOperationLog(module="生产管理", action="打回草稿", target_type="生产工单", target_id=order_id, detail=f"打回草稿：{order.order_no}，卷料库存已退回")
    db.add(log)
    db.commit()
    db.refresh(order)
    return {"ok": True, "status": "draft"}


@app.post("/api/produce_order/{order_id}/reschedule")'''
)

# 11. 重新排单加日志
content = content.replace(
    '''    order.status = "scheduled"
    db.commit()
    db.refresh(order)
    return {"ok": True, "status": "scheduled"}''',
    '''    order.status = "scheduled"
    # 操作日志
    log = DBOperationLog(module="生产管理", action="重新排单", target_type="生产工单", target_id=order_id, detail=f"重新排单：{order.order_no}，移回已排单可重新选日期")
    db.add(log)
    db.commit()
    db.refresh(order)
    return {"ok": True, "status": "scheduled"}'''
)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('生产管理操作日志全部加完成')
