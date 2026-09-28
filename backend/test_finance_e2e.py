import urllib.request
import urllib.error
import json

BASE = "http://127.0.0.1:8000"

def call(method, url, data=None):
    body = json.dumps(data).encode('utf-8') if data is not None else None
    req = urllib.request.Request(f"{BASE}{url}", data=body,
                                 headers={'Content-Type': 'application/json'}, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code}: {e.read().decode('utf-8')}")
        raise

P, F = 0, 0
def check(name, cond):
    global P, F
    if cond:
        P += 1
        print(f"  ✓ {name}")
    else:
        F += 1
        print(f"  ✗ {name}")

print("=" * 66)
print("财务板块第一期 端到端测试")
print("=" * 66)

# 记录测试前总资金（用于增量验证，支持重复运行）
baseline_cash = call("GET", "/api/finance/summary")['total_cash']

# ---------- 准备：资金账户 ----------
print("\n【1】创建资金账户")
cash = call("POST", "/api/finance/account", {"name":"现金","account_type":"cash","balance":10000})
bank = call("POST", "/api/finance/account", {"name":"工商银行","account_type":"bank","balance":100000})
check("现金账户期初10000", abs(cash['balance']-10000)<0.01)
check("银行账户期初100000", abs(bank['balance']-100000)<0.01)

# 手工记一笔其他收入
call("POST", "/api/finance/transaction", {
    "trans_date":"2026-09-26","direction":"income","category":"其他收入",
    "counterparty":"利息","account_id":bank['id'],"amount":50})
bank_after = call("GET", f"/api/finance/account")
bank_b = [a for a in bank_after if a['id']==bank['id']][0]
check("手工其他收入50入账，银行余额100050", abs(bank_b['balance']-100050)<0.01)

# ---------- 采购线：到货→应付→付款 ----------
print("\n【2】采购单到货，自动生成应付")
pc = call("GET", "/api/physical_category")
leaf = [c for c in pc if c['parent_id'] is not None and not any(x['parent_id']==c['id'] for x in pc)]
cat_id = leaf[0]['id'] if leaf else None

po = call("POST", "/api/purchase_order", {
    "supplier":"鼎立纸业","delivery_address":"东莞","order_date":"2026-09-26","maker":"测试",
    "total_amount":20000,
    "items":[{"category_id":cat_id,"gram":350,"width":787,"unit":"吨","quantity":10,"unit_price":2000,"amount":20000}]
})
po = call("GET", f"/api/purchase_order/{po['id']}")
po_item = po['items'][0]

rolls = [
    {"roll_no":"E2E-001","weight":3.521,"remark":""},
    {"roll_no":"E2E-002","weight":3.487,"remark":""},
    {"roll_no":"E2E-003","weight":2.990,"remark":""}
]
total_w = sum(r['weight'] for r in rolls)  # 9.998
call("POST", f"/api/purchase_order/{po['id']}/arrive", {
    "items":[{"item_id":po_item['id'],"arrive_quantity":total_w,"roll_count":3,"rolls":rolls}]
})

payables = call("GET", "/api/finance/payable")
my_pay = [p for p in payables if p['purchase_order_id']==po['id']]
check("生成1笔应付", len(my_pay)==1)
my_pay = my_pay[0]
expect_pay = round(total_w*2000, 2)  # 19996
check(f"应付金额=到货吨数×单价={expect_pay}", abs(my_pay['amount']-expect_pay)<0.01)
check("应付状态unpaid（未付）", my_pay['status']=="unpaid")
check("供应商名称带入", my_pay['supplier_name']=="鼎立纸业")

print("\n【3】付款核销（工商银行全额付款）")
paid = call("POST", f"/api/finance/payable/{my_pay['id']}/pay", {
    "amount":expect_pay,"account_id":bank['id'],"trans_date":"2026-09-26","operator":"出纳"})
check("付款后应付状态paid", paid['status']=="paid")
check("付款后未付余额=0", abs(paid['balance'])<0.01)
accs = call("GET", "/api/finance/account")
bank_b = [a for a in accs if a['id']==bank['id']][0]
expect_bank = 100050 - expect_pay
check(f"银行余额扣减后={expect_bank:.2f}", abs(bank_b['balance']-expect_bank)<0.01)

# 付款超额应被拒绝
try:
    call("POST", f"/api/finance/payable/{my_pay['id']}/pay", {
        "amount":100,"account_id":bank['id']})
    check("重复/超额付款被拒", False)
except Exception:
    check("重复/超额付款被拒", True)

# ---------- 销售线：ship→应收→收款 ----------
print("\n【4】销售订单送出，自动生成应收")
customers = call("GET", "/api/customer")
cus = customers[0]
so = call("POST", "/api/sales_order", {
    "customer_id":cus['id'],"customer_name":cus['customer_name'],
    "delivery_date":"2026-09-26","status":"pending","salesman":"业务员",
    "total_amount":30000,
    "items":[{"line_no":1,"product_name":"灰板","spec":"787x1092","quantity":1000,"unit_price":30,"amount":30000}]
})
call("POST", f"/api/sales_order/{so['id']}/ship")
recs = call("GET", "/api/finance/receivable")
my_rec = [r for r in recs if r['sales_order_id']==so['id']]
check("生成1笔应收", len(my_rec)==1)
my_rec = my_rec[0]
check("应收金额30000", abs(my_rec['amount']-30000)<0.01)
check("应收状态unpaid", my_rec['status']=="unpaid")
# 到期日 = 送货日 + 账期
terms = int(cus.get('payment_terms') or 0)
import datetime as _dt
expect_due = (_dt.datetime(2026,9,26)+_dt.timedelta(days=terms)).strftime("%Y-%m-%d")
check(f"到期日=送货日+账期({terms}天)={expect_due}", my_rec['due_date']==expect_due)

print("\n【5】收款核销（先部分20000，再尾款10000）")
r1 = call("POST", f"/api/finance/receivable/{my_rec['id']}/receive", {
    "amount":20000,"account_id":bank['id'],"trans_date":"2026-09-26"})
check("部分收款后状态partial", r1['status']=="partial")
check("部分收款后未收余额=10000", abs(r1['balance']-10000)<0.01)
r2 = call("POST", f"/api/finance/receivable/{my_rec['id']}/receive", {
    "amount":10000,"account_id":bank['id'],"trans_date":"2026-09-26"})
check("尾款收齐后状态paid", r2['status']=="paid")
check("尾款收齐后余额=0", abs(r2['balance'])<0.01)
accs = call("GET", "/api/finance/account")
bank_b = [a for a in accs if a['id']==bank['id']][0]
expect_bank2 = expect_bank + 30000
check(f"收款30000后银行余额={expect_bank2:.2f}", abs(bank_b['balance']-expect_bank2)<0.01)

# 收款超额被拒
try:
    call("POST", f"/api/finance/receivable/{my_rec['id']}/receive", {
        "amount":1,"account_id":bank['id']})
    check("超额收款被拒", False)
except Exception:
    check("超额收款被拒", True)

# ---------- 流水核对 ----------
print("\n【6】资金流水核对")
txs = call("GET", "/api/finance/transaction")
income = [t for t in txs if t['direction']=='income']
expense = [t for t in txs if t['direction']=='expense']
check("有客户收款流水（本次2笔）", len([t for t in income if t['category']=='客户收款' and t['ref_id']==my_rec['id']])==2)
check("有供应商付款流水（本次1笔）", len([t for t in expense if t['category']=='供应商付款' and t['ref_id']==my_pay['id']])==1)
check("收款流水关联应收单号", all(t['ref_no'] for t in income if t['category']=='客户收款'))

# ---------- 汇总看板 ----------
print("\n【7】财务汇总看板")
summ = call("GET", "/api/finance/summary")
# 净增量=新建账户110000+其他收入50-采购付款19996+销售收款30000=120054
check("账上总资金净增120054（新建账户+收付款）", abs(summ['total_cash']-baseline_cash-120054)<0.01)
check("未结清应收余额=0（测试单已收清）", abs(summ['receivable_balance'])<0.01)
check("未结清应付余额=0（测试单已付清）", abs(summ['payable_balance'])<0.01)

print("\n" + "=" * 66)
print(f"测试结果：通过 {P} 项，失败 {F} 项")
if F == 0:
    print("✅ 财务板块后端+业务联动全部通过")
else:
    print("❌ 有失败项需修复")
print("=" * 66)
