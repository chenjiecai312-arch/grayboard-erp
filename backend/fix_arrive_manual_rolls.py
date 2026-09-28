with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 修改请求模型，加每支卷筒明细
old_models = '''class PurchaseArriveItem(BaseModel):
    item_id: int
    arrive_quantity: float
    roll_count: int = 1  # 到货支数，默认1支


class PurchaseArriveRequest(BaseModel):
    items: List[PurchaseArriveItem]'''

new_models = '''class PurchaseArriveRoll(BaseModel):
    roll_no: str          # 卷筒编号（手动输入）
    weight: float         # 本支重量（吨，手动输入）
    remark: Optional[str] = None

class PurchaseArriveItem(BaseModel):
    item_id: int
    arrive_quantity: float
    roll_count: int = 1  # 到货支数，默认1支
    rolls: Optional[List[PurchaseArriveRoll]] = None  # 手动录入的每支明细，为空则平均分配


class PurchaseArriveRequest(BaseModel):
    items: List[PurchaseArriveItem]'''

content = content.replace(old_models, new_models)

# 2. 改到货接口，支持按手动明细生成卷筒
old_gen = '''        # 自动生成卷筒记录（按支数生成，每支重量=总重量/支数）
        roll_count = max(1, arrive_item.roll_count)
        per_roll_weight = round(arrive_item.arrive_quantity / roll_count, 6)

        for i in range(roll_count):
            # 生成卷筒编号
            prefix = "JD" + datetime.now().strftime("%Y%m%d%H%M%S")
            roll_no = f"{prefix}{i + 1:03d}"'''

new_gen = '''        # 生成卷筒记录：优先用手动录入的明细，否则按支数平均分配
        if arrive_item.rolls and len(arrive_item.rolls) > 0:
            roll_detail_list = [{"roll_no": r.roll_no, "weight": r.weight, "remark": r.remark} for r in arrive_item.rolls if r.roll_no and r.weight and r.weight > 0]
        else:
            roll_count = max(1, arrive_item.roll_count)
            per_roll_weight = round(arrive_item.arrive_quantity / roll_count, 6)
            prefix = "JD" + datetime.now().strftime("%Y%m%d%H%M%S")
            roll_detail_list = [{"roll_no": f"{prefix}{i + 1:03d}", "weight": per_roll_weight, "remark": None} for i in range(roll_count)]

        for idx, roll_detail in enumerate(roll_detail_list):
            roll_no = roll_detail["roll_no"]
            per_roll_weight = roll_detail["weight"]
            manual_remark = roll_detail.get("remark")'''

content = content.replace(old_gen, new_gen)

# 3. 修改卷筒的 remark，手动明细用手动备注
old_remark = '''                ton_price=item.unit_price,
                remark=f"采购单{order.order_no}到货，第{i+1}/{roll_count}支"
            )'''
new_remark = '''                ton_price=item.unit_price,
                remark=manual_remark if manual_remark else f"采购单{order.order_no}到货，第{idx+1}/{len(roll_detail_list)}支"
            )'''
content = content.replace(old_remark, new_remark)

# 4. 修改 created_rolls 里的索引变量
content = content.replace(
    '''            created_rolls.append({"id": roll.id, "raw_no": roll_no, "weight": per_roll_weight})''',
    '''            created_rolls.append({"id": roll.id, "raw_no": roll_no, "weight": per_roll_weight})
            # 品名查找逻辑在循环内，保持不变'''
)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('后端到货接口支持手动明细完成')
