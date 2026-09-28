import urllib.request
import json

# 测试工单列表
try:
    req = urllib.request.Request('http://localhost:8000/api/produce_order', method='GET')
    res = urllib.request.urlopen(req)
    data = json.loads(res.read())
    print('✅ 工单列表接口正常，数量:', len(data))
    for o in data[:3]:
        print(f'   id={o["id"]}, no={o["order_no"]}, status={o["status"]}')
except Exception as e:
    print('❌ 工单列表接口失败:', e)

# 测试排单接口（空ids）
try:
    data = json.dumps({"ids": [], "schedule_date": "2026-09-25"}).encode()
    req = urllib.request.Request('http://localhost:8000/api/produce_order/schedule', data=data, headers={'Content-Type': 'application/json'}, method='POST')
    res = urllib.request.urlopen(req)
    result = json.loads(res.read())
    print('✅ 排单接口正常:', result)
except Exception as e:
    print('❌ 排单接口失败:', e)

print('\n测试完成')
