# 排单相关接口
schedule_code = '''


# ----------------排单相关接口----------------

class ScheduleRequest(BaseModel):
    ids: list
    schedule_date: str

@app.post("/api/produce_order/schedule")
def schedule_orders(req: ScheduleRequest, db: Session = Depends(get_db)):
    """批量排单：把选中的工单指派到指定日期"""
    orders = db.query(DBProduceOrder).filter(DBProduceOrder.id.in_(req.ids)).all()
    for order in orders:
        order.schedule_date = req.schedule_date
        order.status = "scheduled"
    db.commit()
    for order in orders:
        db.refresh(order)
    return {"ok": True, "count": len(orders)}


@app.post("/api/produce_order/{order_id}/start_production")
def start_production(order_id: int, db: Session = Depends(get_db)):
    """移入待生产：锁定卷料库存"""
    order = db.query(DBProduceOrder).filter(DBProduceOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="工单不存在")

    items = db.query(DBProduceOrderItem).filter(DBProduceOrderItem.order_id == order_id).all()
    for item in items:
        roll = db.query(DBRawRoll).filter(DBRawRoll.id == item.roll_id).first()
        if roll:
            if roll.stock_weight < item.quantity:
                raise HTTPException(status_code=400, detail=f"卷料 {roll.raw_no} 库存不足，当前剩余 {roll.stock_weight:.3f} 吨")
            roll.stock_weight -= item.quantity

    order.status = "pending"
    db.commit()
    db.refresh(order)
    return {"ok": True, "status": "pending"}


@app.post("/api/produce_order/{order_id}/finish_production")
def finish_production(order_id: int, db: Session = Depends(get_db)):
    """完成生产：成品自动入库"""
    order = db.query(DBProduceOrder).filter(DBProduceOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="工单不存在")

    # 查找或创建成品品名
    pn = None
    if order.product_name:
        pn = db.query(DBProductNameFinished).filter(DBProductNameFinished.name == order.product_name).first()
        if not pn:
            pn = DBProductNameFinished(name=order.product_name)
            db.add(pn)
            db.commit()
            db.refresh(pn)

    # 创建成品入库记录
    spec = f"{order.spec_width or ''}x{order.spec_length or ''}" if order.spec_width else ""
    product = DBProduct(
        product_name_id=pn.id if pn else None,
        category_id=None,
        work_order_no=order.order_no,
        spec=spec,
        actual_gram=order.total_gram or 0,
        nominal_gram=order.total_gram or 0,
        quantity=order.quantity or 0,
        pending_out_qty=0,
        unit="令",
        remark=f"生产工单 {order.order_no} 自动入库"
    )
    db.add(product)

    order.status = "finished"
    db.commit()
    db.refresh(order)
    return {"ok": True, "status": "finished", "product_id": product.id}
'''

with open('main.py', 'a', encoding='utf-8') as f:
    f.write(schedule_code)

print('排单接口追加完成')
