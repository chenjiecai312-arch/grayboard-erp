with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# ========== 销售订单：新增订单 加日志 ==========
old1 = '''    db.commit()
    
    # 如果状态是待出库，自动在成品仓锁定库存（创建待出库记录）
    if item.status == "pending":'''
new1 = '''    db.commit()
    
    # 记录日志
    log = DBOperationLog(module="销售订单", action="新增", target_type="销售订单", target_id=order.id, detail=f"新增订单：{order.order_no}，客户{order.customer_name}，金额{order.total_amount}，状态{order.status}")
    db.add(log)
    db.commit()
    
    # 如果状态是待出库，自动在成品仓锁定库存（创建待出库记录）
    if item.status == "pending":'''
content = content.replace(old1, new1)

# ========== 销售订单：修改订单 加日志 ==========
old2 = '''    db.commit()
    db.refresh(order)
    order.items = db.query(DBSalesOrderItem).filter(DBSalesOrderItem.order_id == order.id).order_by(DBSalesOrderItem.line_no).all()
    return order



# 销售订单出库（完成待出库记录，扣减总库存，状态改为已送出）'''
new2 = '''    db.commit()
    
    # 记录日志
    log = DBOperationLog(module="销售订单", action="修改", target_type="销售订单", target_id=order.id, detail=f"修改订单：{order.order_no}，客户{order.customer_name}，金额{order.total_amount}，状态{order.status}")
    db.add(log)
    db.commit()
    
    db.refresh(order)
    order.items = db.query(DBSalesOrderItem).filter(DBSalesOrderItem.order_id == order.id).order_by(DBSalesOrderItem.line_no).all()
    return order



# 销售订单出库（完成待出库记录，扣减总库存，状态改为已送出）'''
content = content.replace(old2, new2)

# ========== 销售订单：确认出库 加日志 ==========
old3 = '''    # 扣减总库存，待出库数量减少
    for rec in pending_records:
        product = db.query(DBProduct).filter(DBProduct.id == rec.product_id).first()
        if product:
            product.quantity -= rec.quantity
            product.pending_out_qty -= rec.quantity
        rec.status = "confirmed"
    
    order.status = "shipped"
    db.commit()'''
new3 = '''    # 扣减总库存，待出库数量减少
    for rec in pending_records:
        product = db.query(DBProduct).filter(DBProduct.id == rec.product_id).first()
        if product:
            product.quantity -= rec.quantity
            product.pending_out_qty -= rec.quantity
        rec.status = "confirmed"
    
    order.status = "shipped"
    # 记录日志
    log = DBOperationLog(module="销售订单", action="确认出库", target_type="销售订单", target_id=order.id, detail=f"订单出库：{order.order_no}，客户{order.customer_name}，金额{order.total_amount}")
    db.add(log)
    db.commit()'''
content = content.replace(old3, new3)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('销售订单所有操作日志加完成')
