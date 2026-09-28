with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 在 if __name__ 前面插入采购单相关代码
purchase_code = '''

# ----------------采购单数据库表----------------
class DBPurchaseOrder(Base):
    __tablename__ = "purchase_order"
    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(50))
    supplier = Column(String(200))
    delivery_address = Column(String(200))
    order_date = Column(String(20))
    remark = Column(Text)
    maker = Column(String(50))
    checker = Column(String(50))
    status = Column(String(20), default="draft")
    total_amount = Column(Float, default=0)
    created_at = Column(String(30))


class DBPurchaseOrderItem(Base):
    __tablename__ = "purchase_order_item"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer)
    category_id = Column(Integer)
    gram = Column(Float)
    width = Column(Float)
    unit = Column(String(20), default="吨")
    quantity = Column(Float, default=0)
    unit_price = Column(Float, default=0)
    amount = Column(Float, default=0)
    delivery_date = Column(String(20))
    remark = Column(String(200))
    arrived_quantity = Column(Float, default=0)
    status = Column(String(20), default="pending")


# ----------------采购单Pydantic模型----------------
class PurchaseOrderItemCreate(BaseModel):
    category_id: Optional[int] = None
    gram: Optional[float] = 0
    width: Optional[float] = 0
    unit: str = "吨"
    quantity: float = 0
    unit_price: float = 0
    amount: float = 0
    delivery_date: Optional[str] = None
    remark: Optional[str] = None


class PurchaseOrderItemOut(BaseModel):
    id: int
    order_id: int
    category_id: Optional[int] = None
    gram: Optional[float] = 0
    width: Optional[float] = 0
    unit: str = "吨"
    quantity: float
    unit_price: float
    amount: float
    delivery_date: Optional[str] = None
    remark: Optional[str] = None
    arrived_quantity: float
    status: str
    model_config = ConfigDict(from_attributes=True)


class PurchaseOrderCreate(BaseModel):
    order_no: Optional[str] = None
    supplier: Optional[str] = None
    delivery_address: Optional[str] = None
    order_date: Optional[str] = None
    remark: Optional[str] = None
    maker: Optional[str] = None
    checker: Optional[str] = None
    total_amount: Optional[float] = 0
    items: List[PurchaseOrderItemCreate] = []


class PurchaseOrderOut(BaseModel):
    id: int
    order_no: Optional[str] = None
    supplier: Optional[str] = None
    delivery_address: Optional[str] = None
    order_date: Optional[str] = None
    remark: Optional[str] = None
    maker: Optional[str] = None
    checker: Optional[str] = None
    status: str
    total_amount: float
    created_at: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


# 到货确认明细
class PurchaseArriveItem(BaseModel):
    item_id: int
    arrive_quantity: float
    roll_count: int = 1  # 到货支数，默认1支


class PurchaseArriveRequest(BaseModel):
    items: List[PurchaseArriveItem]


# ----------------采购单接口----------------
@app.get("/api/purchase_order", response_model=List[PurchaseOrderOut])
def list_purchase_order(db: Session = Depends(get_db)):
    return db.query(DBPurchaseOrder).order_by(DBPurchaseOrder.id.desc()).all()


@app.get("/api/purchase_order/{order_id}")
def get_purchase_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(DBPurchaseOrder).filter(DBPurchaseOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="采购单不存在")
    items = db.query(DBPurchaseOrderItem).filter(DBPurchaseOrderItem.order_id == order_id).all()
    return {**order.__dict__, "items": [i.__dict__ for i in items]}


@app.post("/api/purchase_order", response_model=PurchaseOrderOut)
def create_purchase_order(item: PurchaseOrderCreate, db: Session = Depends(get_db)):
    # 自动生成采购单号
    if not item.order_no:
        prefix = "PO" + datetime.now().strftime("%Y%m%d")
        count = db.query(DBPurchaseOrder).filter(DBPurchaseOrder.order_no.like(f"{prefix}%")).count()
        order_no = f"{prefix}{count + 1:03d}"
    else:
        order_no = item.order_no

    order = DBPurchaseOrder(
        order_no=order_no,
        supplier=item.supplier,
        delivery_address=item.delivery_address,
        order_date=item.order_date or datetime.now().strftime("%Y-%m-%d"),
        remark=item.remark,
        maker=item.maker,
        checker=item.checker,
        status="pending",
        total_amount=item.total_amount or 0,
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    db.add(order)
    db.flush()

    # 保存明细
    for it in item.items:
        db_item = DBPurchaseOrderItem(
            order_id=order.id,
            category_id=it.category_id,
            gram=it.gram,
            width=it.width,
            unit=it.unit,
            quantity=it.quantity,
            unit_price=it.unit_price,
            amount=it.amount,
            delivery_date=it.delivery_date,
            remark=it.remark,
            arrived_quantity=0,
            status="pending"
        )
        db.add(db_item)

    # 操作日志
    log = DBOperationLog(module="卷料仓", action="新增采购单", target_type="采购单", target_id=order.id, detail=f"新增采购单：{order.order_no}，供应商{order.supplier}，金额{order.total_amount}")
    db.add(log)

    db.commit()
    db.refresh(order)
    return order


@app.put("/api/purchase_order/{order_id}", response_model=PurchaseOrderOut)
def update_purchase_order(order_id: int, item: PurchaseOrderCreate, db: Session = Depends(get_db)):
    order = db.query(DBPurchaseOrder).filter(DBPurchaseOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="采购单不存在")

    order.supplier = item.supplier
    order.delivery_address = item.delivery_address
    order.order_date = item.order_date
    order.remark = item.remark
    order.maker = item.maker
    order.checker = item.checker
    order.total_amount = item.total_amount or 0

    # 删除旧明细，重新保存
    db.query(DBPurchaseOrderItem).filter(DBPurchaseOrderItem.order_id == order_id).delete()
    for it in item.items:
        db_item = DBPurchaseOrderItem(
            order_id=order.id,
            category_id=it.category_id,
            gram=it.gram,
            width=it.width,
            unit=it.unit,
            quantity=it.quantity,
            unit_price=it.unit_price,
            amount=it.amount,
            delivery_date=it.delivery_date,
            remark=it.remark,
            arrived_quantity=0,
            status="pending"
        )
        db.add(db_item)

    # 操作日志
    log = DBOperationLog(module="卷料仓", action="修改采购单", target_type="采购单", target_id=order.id, detail=f"修改采购单：{order.order_no}，供应商{order.supplier}")
    db.add(log)

    db.commit()
    db.refresh(order)
    return order


@app.delete("/api/purchase_order/{order_id}")
def delete_purchase_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(DBPurchaseOrder).filter(DBPurchaseOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="采购单不存在")
    db.query(DBPurchaseOrderItem).filter(DBPurchaseOrderItem.order_id == order_id).delete()
    # 操作日志
    log = DBOperationLog(module="卷料仓", action="删除采购单", target_type="采购单", target_id=order_id, detail=f"删除采购单：{order.order_no}，供应商{order.supplier}")
    db.add(log)
    db.delete(order)
    db.commit()
    return {"ok": True}


# 到货确认（自动入库卷料仓）
@app.post("/api/purchase_order/{order_id}/arrive")
def arrive_purchase_order(order_id: int, req: PurchaseArriveRequest, db: Session = Depends(get_db)):
    order = db.query(DBPurchaseOrder).filter(DBPurchaseOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="采购单不存在")

    created_rolls = []
    all_arrived = True

    for arrive_item in req.items:
        item = db.query(DBPurchaseOrderItem).filter(DBPurchaseOrderItem.id == arrive_item.item_id).first()
        if not item:
            continue
        if arrive_item.arrive_quantity <= 0:
            continue

        # 更新明细已到货数量
        item.arrived_quantity = (item.arrived_quantity or 0) + arrive_item.arrive_quantity
        if item.arrived_quantity >= item.quantity:
            item.status = "arrived"
        else:
            item.status = "partial"
            all_arrived = False

        # 自动生成卷筒记录（按支数生成，每支重量=总重量/支数）
        roll_count = max(1, arrive_item.roll_count)
        per_roll_weight = round(arrive_item.arrive_quantity / roll_count, 6)

        for i in range(roll_count):
            # 生成卷筒编号
            prefix = "JD" + datetime.now().strftime("%Y%m%d%H%M%S")
            roll_no = f"{prefix}{i + 1:03d}"

            # 品名：从物理分类的二级分类获取，如果没有就用"未命名"
            product_name_id = None
            if item.category_id:
                cat = db.query(DBPhysicalCategory).filter(DBPhysicalCategory.id == item.category_id).first()
                if cat:
                    # 找二级分类（parent_id不为null的）
                    if cat.parent_id:
                        # 当前就是二级，找对应的品名
                        pn = db.query(DBProductName).filter(DBProductName.name == cat.name).first()
                        if pn:
                            product_name_id = pn.id
                        else:
                            # 自动创建品名
                            new_pn = DBProductName(name=cat.name)
                            db.add(new_pn)
                            db.flush()
                            product_name_id = new_pn.id
                    else:
                        # 当前是一级，找它的子分类（二级）
                        children = db.query(DBPhysicalCategory).filter(DBPhysicalCategory.parent_id == cat.id).all()
                        if children:
                            child = children[0]
                            pn = db.query(DBProductName).filter(DBProductName.name == child.name).first()
                            if pn:
                                product_name_id = pn.id
                            else:
                                new_pn = DBProductName(name=child.name)
                                db.add(new_pn)
                                db.flush()
                                product_name_id = new_pn.id

            roll = DBRawRoll(
                raw_no=roll_no,
                product_name_id=product_name_id,
                category_id=item.category_id,
                width=item.width,
                gram=item.gram,
                weight=per_roll_weight,
                stock_weight=per_roll_weight,
                ton_price=item.unit_price,
                remark=f"采购单{order.order_no}到货，第{i+1}/{roll_count}支"
            )
            db.add(roll)
            db.flush()
            created_rolls.append({"id": roll.id, "raw_no": roll_no, "weight": per_roll_weight})

    # 更新采购单状态
    if all_arrived:
        order.status = "completed"
    else:
        order.status = "partial"

    # 操作日志
    log = DBOperationLog(module="卷料仓", action="采购到货", target_type="采购单", target_id=order.id, detail=f"采购单到货：{order.order_no}，生成{len(created_rolls)}支卷筒，总重量{sum(r['weight'] for r in created_rolls):.3f}吨")
    db.add(log)

    db.commit()
    return {"ok": True, "created_rolls": created_rolls, "count": len(created_rolls)}

'''

# 插入到 if __name__ 前面
content = content.replace(
    '\nif __name__ == "__main__":',
    purchase_code + '\nif __name__ == "__main__":'
)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('采购单后端模型和接口加完成')
