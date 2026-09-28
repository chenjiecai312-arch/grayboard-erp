# 追加移出相关接口
code = '''


# ----------------移出/打回相关接口----------------

@app.post("/api/produce_order/{order_id}/cancel_schedule")
def cancel_schedule(order_id: int, db: Session = Depends(get_db)):
    """取消排单：已排单 → 草稿"""
    order = db.query(DBProduceOrder).filter(DBProduceOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="工单不存在")
    if order.status != "scheduled":
        raise HTTPException(status_code=400, detail="只有已排单状态的工单才能取消排单")
    order.status = "draft"
    order.schedule_date = None
    db.commit()
    db.refresh(order)
    return {"ok": True, "status": "draft"}


@app.post("/api/produce_order/{order_id}/back_to_draft")
def back_to_draft(order_id: int, db: Session = Depends(get_db)):
    """打回草稿：待生产 → 草稿，同时回滚卷料库存"""
    order = db.query(DBProduceOrder).filter(DBProduceOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="工单不存在")
    if order.status != "pending":
        raise HTTPException(status_code=400, detail="只有待生产状态的工单才能打回草稿")

    # 回滚卷料库存
    items = db.query(DBProduceOrderItem).filter(DBProduceOrderItem.order_id == order_id).all()
    for item in items:
        roll = db.query(DBRawRoll).filter(DBRawRoll.id == item.roll_id).first()
        if roll:
            roll.stock_weight += item.quantity

    order.status = "draft"
    order.schedule_date = None
    db.commit()
    db.refresh(order)
    return {"ok": True, "status": "draft"}


@app.post("/api/produce_order/{order_id}/reschedule")
def reschedule_order(order_id: int, db: Session = Depends(get_db)):
    """重新排单：待生产 → 已排单（库存保持锁定，可重新选日期）"""
    order = db.query(DBProduceOrder).filter(DBProduceOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="工单不存在")
    if order.status != "pending":
        raise HTTPException(status_code=400, detail="只有待生产状态的工单才能重新排单")
    order.status = "scheduled"
    db.commit()
    db.refresh(order)
    return {"ok": True, "status": "scheduled"}
'''

with open('main.py', 'a', encoding='utf-8') as f:
    f.write(code)

print('移出/打回接口追加完成')
