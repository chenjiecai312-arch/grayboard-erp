with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# ========== 1. 销售订单 ship 生成应收账款 ==========
old_ship = '''    # 修改订单状态为已送出
    order.status = "shipped"
    db.commit()
    db.refresh(order)
    order.items = db.query(DBSalesOrderItem).filter(DBSalesOrderItem.order_id == order_id).order_by(DBSalesOrderItem.line_no).all()
    return order'''

new_ship = '''    # 修改订单状态为已送出
    order.status = "shipped"

    # ===财务联动：生成应收账款（一张销售单一笔，防重复）===
    from datetime import timedelta as _td
    exist_rec = db.query(DBFinanceReceivable).filter(DBFinanceReceivable.sales_order_id == order.id).first()
    if not exist_rec:
        terms = 0
        if order.customer_id:
            _cust = db.query(DBCustomer).filter(DBCustomer.id == order.customer_id).first()
            if _cust:
                terms = int(_cust.payment_terms or 0)
        _due = None
        try:
            _base = datetime.strptime(order.delivery_date, "%Y-%m-%d")
            _due = (_base + _td(days=terms)).strftime("%Y-%m-%d")
        except Exception:
            _due = None
        _rec = DBFinanceReceivable(
            customer_id=order.customer_id,
            customer_name=order.customer_name,
            sales_order_id=order.id,
            order_no=order.order_no,
            amount=order.total_amount or 0,
            received_amount=0,
            balance=order.total_amount or 0,
            ship_date=datetime.now().strftime("%Y-%m-%d"),
            due_date=_due,
            status="unpaid"
        )
        db.add(_rec)

    db.commit()
    db.refresh(order)
    order.items = db.query(DBSalesOrderItem).filter(DBSalesOrderItem.order_id == order_id).order_by(DBSalesOrderItem.line_no).all()
    return order'''

content = content.replace(old_ship, new_ship)

# ========== 2. 采购到货：初始化本次到货金额 ==========
content = content.replace(
    '''    created_rolls = []
    all_arrived = True

    for arrive_item in req.items:
        item = db.query(DBPurchaseOrderItem).filter(DBPurchaseOrderItem.id == arrive_item.item_id).first()
        if not item:
            continue
        if arrive_item.arrive_quantity <= 0:
            continue

        # 更新明细已到货数量
        item.arrived_quantity = (item.arrived_quantity or 0) + arrive_item.arrive_quantity''',
    '''    created_rolls = []
    all_arrived = True
    arrive_amount_total = 0

    for arrive_item in req.items:
        item = db.query(DBPurchaseOrderItem).filter(DBPurchaseOrderItem.id == arrive_item.item_id).first()
        if not item:
            continue
        if arrive_item.arrive_quantity <= 0:
            continue

        # 更新明细已到货数量
        item.arrived_quantity = (item.arrived_quantity or 0) + arrive_item.arrive_quantity
        # 累计本次到货金额（到货吨数 × 采购单价）
        arrive_amount_total += arrive_item.arrive_quantity * (item.unit_price or 0)'''
)

# ========== 3. 采购到货：循环后生成应付账款 ==========
old_po_status = '''    # 更新采购单状态
    if all_arrived:
        order.status = "completed"
    else:
        order.status = "partial"

    # 操作日志
    log = DBOperationLog(module="卷料仓", action="采购到货", target_type="采购单", target_id=order.id, detail=f"采购单到货：{order.order_no}，生成{len(created_rolls)}支卷筒，总重量{sum(r['weight'] for r in created_rolls):.3f}吨")
    db.add(log)'''

new_po_status = '''    # ===财务联动：生成应付账款（一张采购单一笔，随到货累加）===
    if arrive_amount_total > 0:
        _today = datetime.now().strftime("%Y-%m-%d")
        exist_pay = db.query(DBFinancePayable).filter(DBFinancePayable.purchase_order_id == order.id).first()
        if exist_pay:
            exist_pay.amount += arrive_amount_total
            exist_pay.balance += arrive_amount_total
            exist_pay.arrive_date = _today
            exist_pay.status = "partial" if (exist_pay.paid_amount or 0) > 0 else "unpaid"
        else:
            _pay = DBFinancePayable(
                supplier_name=order.supplier,
                purchase_order_id=order.id,
                order_no=order.order_no,
                amount=arrive_amount_total,
                paid_amount=0,
                balance=arrive_amount_total,
                arrive_date=_today,
                status="unpaid"
            )
            db.add(_pay)

    # 更新采购单状态
    if all_arrived:
        order.status = "completed"
    else:
        order.status = "partial"

    # 操作日志
    log = DBOperationLog(module="卷料仓", action="采购到货", target_type="采购单", target_id=order.id, detail=f"采购单到货：{order.order_no}，生成{len(created_rolls)}支卷筒，总重量{sum(r['weight'] for r in created_rolls):.3f}吨，应付{arrive_amount_total:.2f}元")
    db.add(log)'''

content = content.replace(old_po_status, new_po_status)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('业务联动（销售生成应收/采购生成应付）完成')
