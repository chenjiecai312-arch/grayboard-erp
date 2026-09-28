with open('src/App.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 删除旧的生产工单state
content = content.replace('''  //----------生产工单state----------
  const [produceForm] = Form.useForm();
  const [produceList, setProduceList] = useState([]);
  const [produceSearch, setProduceSearch] = useState("");
  const [produceModalOpen, setProduceModalOpen] = useState(false);

  //----------财务结算state----------''', '''  //----------财务结算state----------''')

# 删除loadProduce函数
content = content.replace('''  //加载生产工单
  const loadProduce = async () => {
    try {
      const res = await api.get("/api/produce-order");
      setProduceList(res.data)
    } catch (e) { message.error("生产工单加载失败") }
  }
  //加载财务''', '''  //加载财务''')

# 删除useEffect里的loadProduce调用
content = content.replace('''  useEffect(() => {
    if(activeKey === "produce") loadProduce();
    if(activeKey === "finance") loadFinance();
  }, [activeKey])''', '''  useEffect(() => {
    if(activeKey === "finance") loadFinance();
  }, [activeKey])''')

# 删除produceFilter
content = content.replace('''  //生产工单过滤
  const produceFilter = produceList.filter(item =>
    item.order_no?.includes(produceSearch) || item.sale_order_no?.includes(produceSearch)
  )
  //财务过滤''', '''  //财务过滤''')

with open('src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('旧生产工单代码清理完成')
