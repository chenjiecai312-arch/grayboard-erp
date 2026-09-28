import urllib.request
import json

req = urllib.request.Request('http://localhost:8000/api/produce_order', method='GET')
res = urllib.request.urlopen(req)
data = json.loads(res.read())
print('工单数量:', len(data))
for o in data:
    print(f'  id={o["id"]}, no={o["order_no"]}, status={o["status"]}, schedule={o.get("schedule_date")}')
