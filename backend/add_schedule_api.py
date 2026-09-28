with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. DBProduceOrder 加 schedule_date
content = content.replace(
    '    checker = Column(String(50))\n    produce_date = Column(String(20))',
    '    checker = Column(String(50))\n    schedule_date = Column(String(20))\n    produce_date = Column(String(20))'
)

# 2. ProduceOrderCreate 加 schedule_date
content = content.replace(
    '    checker: Optional[str] = None\n    produce_date: Optional[str] = None',
    '    checker: Optional[str] = None\n    schedule_date: Optional[str] = None\n    produce_date: Optional[str] = None'
)

# 3. ProduceOrderOut 加 schedule_date
content = content.replace(
    '    checker: Optional[str] = None\n    produce_date: Optional[str] = None',
    '    checker: Optional[str] = None\n    schedule_date: Optional[str] = None\n    produce_date: Optional[str] = None'
)

# 4. create 接口里赋值 schedule_date
content = content.replace(
    '        checker=item.checker,\n        produce_date=item.produce_date or datetime.now().strftime("%Y-%m-%d"),',
    '        checker=item.checker,\n        schedule_date=item.schedule_date,\n        produce_date=item.produce_date or datetime.now().strftime("%Y-%m-%d"),'
)

# 5. update 接口里赋值 schedule_date
content = content.replace(
    '    order.checker = item.checker\n    order.produce_date = item.produce_date',
    '    order.checker = item.checker\n    order.schedule_date = item.schedule_date\n    order.produce_date = item.produce_date'
)

# 6. 在删除接口后面加三个新接口（排单、移入待生产、完成生产）
old_delete_end = '''@app.delete("/api/produce_order/{order_id}")
def delete_produce_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(DBProduceOrder).filter(DBProduceOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="工单不存在")
    db.delete(order)
    db.commit()
    return {"ok": True}'''

new_delete_end = '''@app.delete("/api/produce_order/{order_id}")
def delete_produce_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(DBProduceOrder).filter(DBProduceOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="工单不存在")
    db.delete(order)
    db.commit()
    return {"ok": True}


# ----------------排单相关接口----------------

class ScheduleRequest(BaseModel):
    ids: List[int]
    schedule_date: str

@app.post("/api/produce_order/schedule", response_model=List[ProduceOrderOut])
def schedule_orders(req: ScheduleRequest, db: Session = Depends(get_db)):
    """批量排单：把选中的工单指派到指定日期"""
    orders = db.query(DBProduceOrder).filter(DBProduceOrder.id.in_(req.ids)).all()
    for order in orders:
        order.schedule_date = req.schedule_date
        order.status = "scheduled"
    db.commit()
    for order in orders:
        db.refresh(order)
    return orders


@app.post("/api/produce_order/{order_id}/start_production", response_model=ProduceOrderOut)
def start_production(order_id: int, db: Session = Depends(get_db)):
    """移入待生产：锁定卷料库存"""
    order = db.query(DBProduceOrder).filter(DBProduceOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="工单不存在")

    # 扣减每层卷料库存
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
    return order


@app.post("/api/produce_order/{order_id}/finish_production", response_model=ProduceOrderOut)
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
    return order'''

content = content.replace(old_delete_end, new_delete_end)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('排单相关后端接口加完成')
