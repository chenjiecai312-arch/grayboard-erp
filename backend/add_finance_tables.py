with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 在 create_all 之前插入4张财务表
old_anchor = '''#建表
Base.metadata.create_all(bind=engine)'''

finance_tables = '''# =================财务板块表（第一期）=================
# 资金账户（现金/银行/微信等）
class DBFinanceAccount(Base):
    __tablename__ = "finance_account"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)              # 账户名称
    account_type = Column(String(20), default="bank")       # cash现金/bank银行/other其他
    balance = Column(Float, default=0)                      # 当前余额
    remark = Column(String, default="")
    created_at = Column(String, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


# 资金流水（出入账日记账）
class DBFinanceTransaction(Base):
    __tablename__ = "finance_transaction"
    id = Column(Integer, primary_key=True, index=True)
    trans_date = Column(String(20), index=True)             # 日期
    direction = Column(String(10), index=True)             # income收入/expense支出
    category = Column(String(30), default="其他")           # 客户收款/供应商付款/费用报销/其他收入/其他支出
    counterparty = Column(String(200), default="")         # 往来单位
    account_id = Column(Integer, index=True)               # 资金账户
    amount = Column(Float, default=0)                      # 金额
    ref_type = Column(String(20), default="")              # 关联类型 receivable/payable/manual
    ref_id = Column(Integer, nullable=True)
    ref_no = Column(String(50), default="")               # 关联单据号
    operator = Column(String(50), default="")             # 经手人
    remark = Column(String, default="")
    created_at = Column(String, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


# 应收账款（客户欠我的）
class DBFinanceReceivable(Base):
    __tablename__ = "finance_receivable"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, nullable=True)
    customer_name = Column(String(200))
    sales_order_id = Column(Integer, nullable=True, index=True)
    order_no = Column(String(50))                          # 销售单号
    amount = Column(Float, default=0)                      # 应收金额
    received_amount = Column(Float, default=0)             # 已收金额
    balance = Column(Float, default=0)                     # 未收余额
    ship_date = Column(String(20), nullable=True)          # 送出日期
    due_date = Column(String(20), nullable=True)           # 应收日期（账期到期）
    status = Column(String(20), default="unpaid")          # unpaid未收/partial部分收/paid已收
    remark = Column(String, default="")
    created_at = Column(String, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


# 应付账款（我欠供应商的）
class DBFinancePayable(Base):
    __tablename__ = "finance_payable"
    id = Column(Integer, primary_key=True, index=True)
    supplier_name = Column(String(200))
    purchase_order_id = Column(Integer, nullable=True, index=True)
    order_no = Column(String(50))                          # 采购单号
    amount = Column(Float, default=0)                      # 应付金额（随到货累加）
    paid_amount = Column(Float, default=0)                 # 已付金额
    balance = Column(Float, default=0)                     # 未付余额
    arrive_date = Column(String(20), nullable=True)        # 最近到货日期
    due_date = Column(String(20), nullable=True)
    status = Column(String(20), default="unpaid")          # unpaid/partial/paid
    remark = Column(String, default="")
    created_at = Column(String, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


#建表
Base.metadata.create_all(bind=engine)'''

content = content.replace(old_anchor, finance_tables)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('4张财务表定义插入完成')
