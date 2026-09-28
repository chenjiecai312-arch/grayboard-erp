with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

finance_code = '''
# =================财务板块接口（第一期）=================
# ----------Pydantic模型----------
class FinanceAccountCreate(BaseModel):
    name: str
    account_type: str = "bank"
    balance: float = 0
    remark: Optional[str] = ""

class FinanceAccountOut(BaseModel):
    id: int
    name: str
    account_type: str
    balance: float
    remark: Optional[str] = ""
    model_config = ConfigDict(from_attributes=True)

class FinanceTransactionCreate(BaseModel):
    trans_date: str
    direction: str                                   # income/expense
    category: str = "其他"
    counterparty: Optional[str] = ""
    account_id: int
    amount: float
    ref_type: Optional[str] = "manual"
    ref_no: Optional[str] = ""
    operator: Optional[str] = ""
    remark: Optional[str] = ""

class FinanceTransactionOut(BaseModel):
    id: int
    trans_date: Optional[str] = None
    direction: Optional[str] = None
    category: Optional[str] = None
    counterparty: Optional[str] = None
    account_id: Optional[int] = None
    amount: float
    ref_type: Optional[str] = None
    ref_no: Optional[str] = None
    operator: Optional[str] = None
    remark: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class FinanceReceivableOut(BaseModel):
    id: int
    customer_id: Optional[int] = None
    customer_name: Optional[str] = None
    sales_order_id: Optional[int] = None
    order_no: Optional[str] = None
    amount: float
    received_amount: float
    balance: float
    ship_date: Optional[str] = None
    due_date: Optional[str] = None
    status: str
    remark: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class FinancePayableOut(BaseModel):
    id: int
    supplier_name: Optional[str] = None
    purchase_order_id: Optional[int] = None
    order_no: Optional[str] = None
    amount: float
    paid_amount: float
    balance: float
    arrive_date: Optional[str] = None
    due_date: Optional[str] = None
    status: str
    remark: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class SettleRequest(BaseModel):
    amount: float
    account_id: int
    trans_date: Optional[str] = None
    operator: Optional[str] = ""
    remark: Optional[str] = ""

# ----------资金账户接口----------
@app.get("/api/finance/account", response_model=List[FinanceAccountOut])
def list_finance_account(db: Session = Depends(get_db)):
    return db.query(DBFinanceAccount).order_by(DBFinanceAccount.id).all()

@app.post("/api/finance/account", response_model=FinanceAccountOut)
def create_finance_account(item: FinanceAccountCreate, db: Session = Depends(get_db)):
    obj = DBFinanceAccount(**item.model_dump())
    db.add(obj)
    log = DBOperationLog(module="财务", action="新增账户", target_type="资金账户", detail=f"新增账户：{obj.name}，期初余额{obj.balance}")
    db.add(log)
    db.commit()
    db.refresh(obj)
    return obj

@app.put("/api/finance/account/{account_id}", response_model=FinanceAccountOut)
def update_finance_account(account_id: int, item: FinanceAccountCreate, db: Session = Depends(get_db)):
    obj = db.query(DBFinanceAccount).filter(DBFinanceAccount.id == account_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="账户不存在")
    # 余额由流水驱动，不允许直接改，只改名称/类型/备注
    obj.name = item.name
    obj.account_type = item.account_type
    obj.remark = item.remark
    db.commit()
    db.refresh(obj)
    return obj

@app.delete("/api/finance/account/{account_id}")
def delete_finance_account(account_id: int, db: Session = Depends(get_db)):
    obj = db.query(DBFinanceAccount).filter(DBFinanceAccount.id == account_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="账户不存在")
    tx_count = db.query(DBFinanceTransaction).filter(DBFinanceTransaction.account_id == account_id).count()
    if tx_count > 0:
        raise HTTPException(status_code=400, detail=f"该账户有{tx_count}笔流水记录，不能删除")
    db.delete(obj)
    db.commit()
    return {"ok": True}

# ----------资金流水接口----------
@app.get("/api/finance/transaction", response_model=List[FinanceTransactionOut])
def list_finance_transaction(direction: Optional[str] = None, category: Optional[str] = None,
                             account_id: Optional[int] = None, keyword: Optional[str] = None,
                             start_date: Optional[str] = None, end_date: Optional[str] = None,
                             db: Session = Depends(get_db)):
    q = db.query(DBFinanceTransaction)
    if direction:
        q = q.filter(DBFinanceTransaction.direction == direction)
    if category:
        q = q.filter(DBFinanceTransaction.category == category)
    if account_id:
        q = q.filter(DBFinanceTransaction.account_id == account_id)
    if keyword:
        q = q.filter(DBFinanceTransaction.counterparty.like(f"%{keyword}%"))
    if start_date:
        q = q.filter(DBFinanceTransaction.trans_date >= start_date)
    if end_date:
        q = q.filter(DBFinanceTransaction.trans_date <= end_date)
    return q.order_by(DBFinanceTransaction.trans_date.desc(), DBFinanceTransaction.id.desc()).all()

@app.post("/api/finance/transaction", response_model=FinanceTransactionOut)
def create_finance_transaction(item: FinanceTransactionCreate, db: Session = Depends(get_db)):
    if item.amount <= 0:
        raise HTTPException(status_code=400, detail="金额必须大于0")
    account = db.query(DBFinanceAccount).filter(DBFinanceAccount.id == item.account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="资金账户不存在")
    if item.direction == "expense" and account.balance < item.amount:
        raise HTTPException(status_code=400, detail=f"账户余额不足，当前余额{account.balance:.2f}")
    # 更新账户余额
    account.balance += item.amount if item.direction == "income" else -item.amount
    tx = DBFinanceTransaction(**item.model_dump())
    db.add(tx)
    log = DBOperationLog(module="财务", action="手工记账", target_type="资金流水",
                        detail=f"{'收入' if item.direction=='income' else '支出'}{item.amount}（{item.category}，{item.counterparty}）")
    db.add(log)
    db.commit()
    db.refresh(tx)
    return tx

# ----------应收账款接口----------
@app.get("/api/finance/receivable", response_model=List[FinanceReceivableOut])
def list_finance_receivable(status: Optional[str] = None, keyword: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(DBFinanceReceivable)
    if status:
        q = q.filter(DBFinanceReceivable.status == status)
    if keyword:
        q = q.filter(DBFinanceReceivable.customer_name.like(f"%{keyword}%"))
    return q.order_by(DBFinanceReceivable.id.desc()).all()

@app.post("/api/finance/receivable/{rid}/receive", response_model=FinanceReceivableOut)
def receive_finance(rid: int, data: SettleRequest, db: Session = Depends(get_db)):
    rec = db.query(DBFinanceReceivable).filter(DBFinanceReceivable.id == rid).first()
    if not rec:
        raise HTTPException(status_code=404, detail="应收记录不存在")
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="收款金额必须大于0")
    if data.amount > rec.balance + 1e-6:
        raise HTTPException(status_code=400, detail=f"收款金额不能超过未收余额{rec.balance:.2f}")
    account = db.query(DBFinanceAccount).filter(DBFinanceAccount.id == data.account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="资金账户不存在")
    trans_date = data.trans_date or datetime.now().strftime("%Y-%m-%d")
    # 更新应收
    rec.received_amount += data.amount
    rec.balance -= data.amount
    rec.status = "paid" if rec.balance <= 1e-6 else "partial"
    if rec.balance <= 1e-6:
        rec.balance = 0
    # 更新账户
    account.balance += data.amount
    # 生成流水
    tx = DBFinanceTransaction(trans_date=trans_date, direction="income", category="客户收款",
                              counterparty=rec.customer_name, account_id=account.id, amount=data.amount,
                              ref_type="receivable", ref_id=rec.id, ref_no=rec.order_no,
                              operator=data.operator or "", remark=data.remark or "")
    db.add(tx)
    log = DBOperationLog(module="财务", action="收款", target_type="应收账款", target_id=rec.id,
                        detail=f"收到{rec.customer_name}货款{data.amount}（{rec.order_no}），入{account.name}")
    db.add(log)
    db.commit()
    db.refresh(rec)
    return rec

# ----------应付账款接口----------
@app.get("/api/finance/payable", response_model=List[FinancePayableOut])
def list_finance_payable(status: Optional[str] = None, keyword: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(DBFinancePayable)
    if status:
        q = q.filter(DBFinancePayable.status == status)
    if keyword:
        q = q.filter(DBFinancePayable.supplier_name.like(f"%{keyword}%"))
    return q.order_by(DBFinancePayable.id.desc()).all()

@app.post("/api/finance/payable/{pid}/pay", response_model=FinancePayableOut)
def pay_finance(pid: int, data: SettleRequest, db: Session = Depends(get_db)):
    pay = db.query(DBFinancePayable).filter(DBFinancePayable.id == pid).first()
    if not pay:
        raise HTTPException(status_code=404, detail="应付记录不存在")
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="付款金额必须大于0")
    if data.amount > pay.balance + 1e-6:
        raise HTTPException(status_code=400, detail=f"付款金额不能超过未付余额{pay.balance:.2f}")
    account = db.query(DBFinanceAccount).filter(DBFinanceAccount.id == data.account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="资金账户不存在")
    if account.balance < data.amount:
        raise HTTPException(status_code=400, detail=f"账户余额不足，{account.name}当前余额{account.balance:.2f}")
    trans_date = data.trans_date or datetime.now().strftime("%Y-%m-%d")
    pay.paid_amount += data.amount
    pay.balance -= data.amount
    pay.status = "paid" if pay.balance <= 1e-6 else "partial"
    if pay.balance <= 1e-6:
        pay.balance = 0
    account.balance -= data.amount
    tx = DBFinanceTransaction(trans_date=trans_date, direction="expense", category="供应商付款",
                              counterparty=pay.supplier_name, account_id=account.id, amount=data.amount,
                              ref_type="payable", ref_id=pay.id, ref_no=pay.order_no,
                              operator=data.operator or "", remark=data.remark or "")
    db.add(tx)
    log = DBOperationLog(module="财务", action="付款", target_type="应付账款", target_id=pay.id,
                        detail=f"付给{pay.supplier_name}{data.amount}（{pay.order_no}），出{account.name}")
    db.add(log)
    db.commit()
    db.refresh(pay)
    return pay

# ----------财务汇总看板----------
@app.get("/api/finance/summary")
def finance_summary(db: Session = Depends(get_db)):
    accounts = db.query(DBFinanceAccount).all()
    total_cash = sum(a.balance for a in accounts)
    rec_total = db.query(DBFinanceReceivable).filter(DBFinanceReceivable.status != "paid")
    rec_balance = sum(r.balance for r in rec_total.all())
    pay_balance = sum(p.balance for p in db.query(DBFinancePayable).filter(DBFinancePayable.status != "paid").all())
    today = datetime.now().strftime("%Y-%m-%d")
    overdue_rec = db.query(DBFinanceReceivable).filter(
        DBFinanceReceivable.status != "paid",
        DBFinanceReceivable.due_date < today
    ).all()
    return {
        "total_cash": round(total_cash, 2),
        "receivable_balance": round(rec_balance, 2),
        "payable_balance": round(pay_balance, 2),
        "overdue_count": len(overdue_rec),
        "overdue_amount": round(sum(r.balance for r in overdue_rec), 2),
        "accounts": [{"id": a.id, "name": a.name, "balance": a.balance} for a in accounts]
    }


if __name__ == "__main__":'''

content = content.replace(
    '\nif __name__ == "__main__":',
    finance_code
)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('财务Pydantic模型和接口插入完成')
