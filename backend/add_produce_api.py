with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 在文件末尾加生产工单接口
produce_api = '''


# ----------------生产工单接口----------------
class ProduceOrderItemCreate(BaseModel):
    layer_no: int
    roll_id: int
    roll_name: str = ""
    quantity: float = 0
    unit_price: float = 0
    amount: float = 0
    remark: Optional[str] = None

class ProduceOrderCreate(BaseModel):
    order_no: Optional[str] = None
    customer_id: Optional[int] = None
    customer_name: Optional[str] = None
    produce_date: Optional[str] = None
    layers: int = 1
    total_amount: float = 0
    status: str = "draft"
    remark: Optional[str] = None
    items: List[ProduceOrderItemCreate] = []

class ProduceOrderItemOut(BaseModel):
    id: int
    order_id: int
    layer_no: int
    roll_id: Optional[int] = None
    roll_name: Optional[str] = None
    quantity: float
    unit_price: float
    amount: float
    remark: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class ProduceOrderOut(BaseModel):
    id: int
    order_no: Optional[str] = None
    customer_id: Optional[int] = None
    customer_name: Optional[str] = None
    produce_date: Optional[str] = None
    layers: int
    total_amount: float
    status: str
    remark: Optional[str] = None
    created_at: Optional[str] = None
    items: List[ProduceOrderItemOut] = []
    model_config = ConfigDict(from_attributes=True)

def generate_produce_order_no(db):
    prefix = "GD" + datetime.now().strftime("%Y%m%d")
    count = db.query(DBProduceOrder).filter(DBProduceOrder.order_no.like(f"{prefix}%")).count()
    return f"{prefix}-{count+1:03d}"

@app.get("/api/produce_order", response_model=List[ProduceOrderOut])
def list_produce_order(db: Session = Depends(get_db)):
    orders = db.query(DBProduceOrder).order_by(DBProduceOrder.id.desc()).all()
    for order in orders:
        order.items = db.query(DBProduceOrderItem).filter(DBProduceOrderItem.order_id == order.id).order_by(DBProduceOrderItem.layer_no).all()
    return orders

@app.post("/api/produce_order", response_model=ProduceOrderOut)
def create_produce_order(item: ProduceOrderCreate, db: Session = Depends(get_db)):
    order_no = item.order_no or generate_produce_order_no(db)
    total_amount = sum((i.quantity or 0) * (i.unit_price or 0) for i in item.items)
    order = DBProduceOrder(
        order_no=order_no,
        customer_id=item.customer_id,
        customer_name=item.customer_name,
        produce_date=item.produce_date or datetime.now().strftime("%Y-%m-%d"),
        layers=item.layers,
        total_amount=total_amount,
        status=item.status,
        remark=item.remark
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    for i in item.items:
        db_item = DBProduceOrderItem(
            order_id=order.id,
            layer_no=i.layer_no,
            roll_id=i.roll_id,
            roll_name=i.roll_name,
            quantity=i.quantity,
            unit_price=i.unit_price,
            amount=i.quantity * i.unit_price,
            remark=i.remark
        )
        db.add(db_item)
    db.commit()
    order.items = db.query(DBProduceOrderItem).filter(DBProduceOrderItem.order_id == order.id).order_by(DBProduceOrderItem.layer_no).all()
    return order

@app.put("/api/produce_order/{order_id}", response_model=ProduceOrderOut)
def update_produce_order(order_id: int, item: ProduceOrderCreate, db: Session = Depends(get_db)):
    order = db.query(DBProduceOrder).filter(DBProduceOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="工单不存在")
    total_amount = sum((i.quantity or 0) * (i.unit_price or 0) for i in item.items)
    order.customer_id = item.customer_id
    order.customer_name = item.customer_name
    order.produce_date = item.produce_date
    order.layers = item.layers
    order.total_amount = total_amount
    order.status = item.status
    order.remark = item.remark
    # 删除旧明细
    db.query(DBProduceOrderItem).filter(DBProduceOrderItem.order_id == order_id).delete()
    # 加新明细
    for i in item.items:
        db_item = DBProduceOrderItem(
            order_id=order.id,
            layer_no=i.layer_no,
            roll_id=i.roll_id,
            roll_name=i.roll_name,
            quantity=i.quantity,
            unit_price=i.unit_price,
            amount=i.quantity * i.unit_price,
            remark=i.remark
        )
        db.add(db_item)
    db.commit()
    db.refresh(order)
    order.items = db.query(DBProduceOrderItem).filter(DBProduceOrderItem.order_id == order.id).order_by(DBProduceOrderItem.layer_no).all()
    return order

@app.delete("/api/produce_order/{order_id}")
def delete_produce_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(DBProduceOrder).filter(DBProduceOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="工单不存在")
    db.query(DBProduceOrderItem).filter(DBProduceOrderItem.order_id == order_id).delete()
    db.delete(order)
    db.commit()
    return {"ok": True}

# 确认领料：锁定卷料库存（stock_weight减少，记录领料日志）
@app.post("/api/produce_order/{order_id}/pick_material")
def pick_material(order_id: int, db: Session = Depends(get_db)):
    order = db.query(DBProduceOrder).filter(DBProduceOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="工单不存在")
    items = db.query(DBProduceOrderItem).filter(DBProduceOrderItem.order_id == order_id).all()
    for item in items:
        roll = db.query(DBRawRoll).filter(DBRawRoll.id == item.roll_id).first()
        if roll:
            if roll.stock_weight < item.quantity:
                raise HTTPException(status_code=400, detail=f"卷料[{roll.raw_no}]库存不足，当前剩余{roll.stock_weight:.3f}吨")
            roll.stock_weight -= item.quantity
            # 记录领料日志
            log = DBProduceMaterialLog(
                order_id=order_id,
                item_id=item.id,
                type="pick",
                material_type="roll",
                material_id=item.roll_id,
                quantity=item.quantity
            )
            db.add(log)
    order.status = "picking"
    db.commit()
    return {"ok": True, "message": "领料成功，卷料库存已锁定"}

# 退料：把没用完的卷料退回卷料仓
@app.post("/api/produce_order/{order_id}/return_material")
def return_material(order_id: int, db: Session = Depends(get_db), return_items: List[dict] = Body(...)):
    order = db.query(DBProduceOrder).filter(DBProduceOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="工单不存在")
    for ri in return_items:
        item_id = ri.get("item_id")
        quantity = ri.get("quantity", 0)
        if quantity <= 0:
            continue
        item = db.query(DBProduceOrderItem).filter(DBProduceOrderItem.id == item_id).first()
        if item:
            roll = db.query(DBRawRoll).filter(DBRawRoll.id == item.roll_id).first()
            if roll:
                roll.stock_weight += quantity
                log = DBProduceMaterialLog(
                    order_id=order_id,
                    item_id=item_id,
                    type="return",
                    material_type="roll",
                    material_id=item.roll_id,
                    quantity=quantity
                )
                db.add(log)
    order.status = "finished"
    db.commit()
    return {"ok": True, "message": "退料成功"}
'''

content += produce_api

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('生产工单接口加完成')
