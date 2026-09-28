with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

supplier_code = '''

# ----------------供应商数据库表----------------
class DBSupplier(Base):
    __tablename__ = "supplier"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    contact = Column(String(100))
    phone = Column(String(50))
    address = Column(String(500))
    payment_term = Column(String(100))
    salesman = Column(String(50))
    tax_no = Column(String(100))
    level = Column(String(50))
    remark = Column(Text)
    created_at = Column(String(30))


# ----------------供应商Pydantic模型----------------
class SupplierCreate(BaseModel):
    name: str
    contact: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    payment_term: Optional[str] = None
    salesman: Optional[str] = None
    tax_no: Optional[str] = None
    level: Optional[str] = None
    remark: Optional[str] = None


class SupplierOut(BaseModel):
    id: int
    name: str
    contact: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    payment_term: Optional[str] = None
    salesman: Optional[str] = None
    tax_no: Optional[str] = None
    level: Optional[str] = None
    remark: Optional[str] = None
    created_at: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


# ----------------供应商接口----------------
@app.get("/api/supplier", response_model=List[SupplierOut])
def list_supplier(db: Session = Depends(get_db)):
    return db.query(DBSupplier).order_by(DBSupplier.id.desc()).all()


@app.post("/api/supplier", response_model=SupplierOut)
def create_supplier(item: SupplierCreate, db: Session = Depends(get_db)):
    obj = DBSupplier(
        name=item.name,
        contact=item.contact,
        phone=item.phone,
        address=item.address,
        payment_term=item.payment_term,
        salesman=item.salesman,
        tax_no=item.tax_no,
        level=item.level,
        remark=item.remark,
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    db.add(obj)
    # 操作日志
    log = DBOperationLog(module="供应商管理", action="新增", target_type="供应商", target_id=obj.id, detail=f"新增供应商：{obj.name}")
    db.add(log)
    db.commit()
    db.refresh(obj)
    return obj


@app.put("/api/supplier/{supplier_id}", response_model=SupplierOut)
def update_supplier(supplier_id: int, item: SupplierCreate, db: Session = Depends(get_db)):
    obj = db.query(DBSupplier).filter(DBSupplier.id == supplier_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="供应商不存在")
    for key, value in item.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
    # 操作日志
    log = DBOperationLog(module="供应商管理", action="修改", target_type="供应商", target_id=obj.id, detail=f"修改供应商：{obj.name}")
    db.add(log)
    db.commit()
    db.refresh(obj)
    return obj


@app.delete("/api/supplier/{supplier_id}")
def delete_supplier(supplier_id: int, db: Session = Depends(get_db)):
    obj = db.query(DBSupplier).filter(DBSupplier.id == supplier_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="供应商不存在")
    # 操作日志
    log = DBOperationLog(module="供应商管理", action="删除", target_type="供应商", target_id=supplier_id, detail=f"删除供应商：{obj.name}")
    db.add(log)
    db.delete(obj)
    db.commit()
    return {"ok": True}

'''

# 插入到 if __name__ 前面
content = content.replace(
    '\nif __name__ == "__main__":',
    supplier_code + '\nif __name__ == "__main__":'
)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('供应商后端模型和接口加完成')
