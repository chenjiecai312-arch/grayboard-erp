with open('src/RollWarehouse.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 加采购单相关 state（在 delRollId 后面）
content = content.replace(
    '  const [delRollId,setDelRollId] = useState(null);',
    '''  const [delRollId,setDelRollId] = useState(null);
  // 从采购单录入
  const [purchaseList, setPurchaseList] = useState([]);
  const [purchaseSelectModal, setPurchaseSelectModal] = useState(false);
  const [purchaseItems, setPurchaseItems] = useState([]);
  const [selectedPurchase, setSelectedPurchase] = useState(null);'''
)

# 2. loadData 里加采购单加载
content = content.replace(
    '''      const [rollRes,pcRes,pnRes] = await Promise.all([
        api.get("/api/rawroll"),
        api.get("/api/physical_category"),
        api.get("/api/product_name")
      ])
      setRollList(rollRes.data);
      setPcList(pcRes.data);
      setPnList(pnRes.data);''',
    '''      const [rollRes,pcRes,pnRes,purchaseRes] = await Promise.all([
        api.get("/api/rawroll"),
        api.get("/api/physical_category"),
        api.get("/api/product_name"),
        api.get("/api/purchase_order")
      ])
      setRollList(rollRes.data);
      setPcList(pcRes.data);
      setPnList(pnRes.data);
      setPurchaseList(purchaseRes.data);'''
)

# 3. 加获取分类路径函数（在 getChildren 后面）
content = content.replace(
    '''  function getChildren(parentId){
    return pcList.filter(x=>x.parent_id===parentId)
  }''',
    '''  function getChildren(parentId){
    return pcList.filter(x=>x.parent_id===parentId)
  }

  // 获取物理分类完整路径
  function getCategoryFullPath(catId){
    if(!catId) return "";
    const cat = pcList.find(x=>x.id===catId);
    if(!cat) return "";
    if(!cat.parent_id) return cat.name;
    const parent = pcList.find(x=>x.id===cat.parent_id);
    if(!parent) return cat.name;
    if(!parent.parent_id) return parent.name + "/" + cat.name;
    const grand = pcList.find(x=>x.id===parent.parent_id);
    if(!grand) return parent.name + "/" + cat.name;
    if(!grand.parent_id) return grand.name + "/" + parent.name + "/" + cat.name;
    const greatGrand = pcList.find(x=>x.id===grand.parent_id);
    if(!greatGrand) return grand.name + "/" + parent.name + "/" + cat.name;
    return greatGrand.name + "/" + grand.name + "/" + parent.name + "/" + cat.name;
  }

  // 打开采购单选择
  const openPurchaseSelect = () => {
    setSelectedPurchase(null);
    setPurchaseItems([]);
    setPurchaseSelectModal(true);
  };

  // 查看采购单明细
  const viewPurchaseItems = async (order) => {
    try {
      const res = await api.get(`/api/purchase_order/${order.id}`);
      setPurchaseItems(res.data.items || []);
      setSelectedPurchase(order);
    } catch(e) {
      message.error("加载采购单明细失败");
    }
  };

  // 从采购单明细选择录入
  const selectFromPurchase = (item) => {
    // 自动带入已有字段
    form.setFieldsValue({
      category_id: item.category_id,
      gram: item.gram,
      width: item.width,
      ton_price: item.unit_price,
      remark: item.remark ? `采购单${selectedPurchase?.order_no || ''}：${item.remark}` : `来自采购单${selectedPurchase?.order_no || ''}`
    });
    setPurchaseSelectModal(false);
    message.success("已从采购单带入规格/克重/分类/吨价，请补齐卷筒编号和重量");
  };'''
)

# 4. 在新增卷筒弹窗顶部加"从采购单选择录入"按钮
content = content.replace(
    '''      <Modal open={modalOpen} title="新增单支卷筒原料" footer={null} onCancel={()=>setModalOpen(false)} maskClosable={false}>
        <Form form={form} layout="vertical" onFinish={handleSubmit}>''',
    '''      <Modal open={modalOpen} title="新增单支卷筒原料" footer={null} onCancel={()=>setModalOpen(false)} maskClosable={false} width={700}>
        <div style={{marginBottom:12,padding:'8px 12px',background:'#e6f7ff',borderRadius:4,display:'flex',justifyContent:'space-between',alignItems:'center'}}>
          <span style={{color:'#1890ff',fontSize:13}}>可从采购单快速带入规格/克重/分类/吨价，缺失字段手动补齐</span>
          <Button size="small" type="primary" onClick={openPurchaseSelect}>从采购单选择录入</Button>
        </div>
        <Form form={form} layout="vertical" onFinish={handleSubmit}>'''
)

# 5. 在删除确认弹窗后面加采购单选择弹窗（找一个合适的位置插入）
content = content.replace(
    '''      {/* =========快速新增品名弹窗========= */}''',
    '''      {/* =========从采购单选择录入弹窗========= */}
      <Modal
        open={purchaseSelectModal}
        title={selectedPurchase ? `选择采购单明细 - ${selectedPurchase.order_no}` : "选择采购单"}
        onCancel={()=>setPurchaseSelectModal(false)}
        footer={null}
        width={900}
      >
        {!selectedPurchase ? (
          <div>
            <div style={{marginBottom:12,color:'#666'}}>选择一个采购单，查看明细后选择要录入的料</div>
            <Table
              rowKey="id"
              dataSource={purchaseList}
              size="small"
              pagination={{pageSize:8}}
              columns={[
                {title:'采购单号',dataIndex:'order_no',width:180},
                {title:'供应商',dataIndex:'supplier',width:200},
                {title:'日期',dataIndex:'order_date',width:120},
                {title:'状态',dataIndex:'status',width:100,render:v=>({pending:'待到货',partial:'部分到货',completed:'已完成',draft:'草稿'}[v]||v)},
                {title:'总金额',dataIndex:'total_amount',width:120,render:v=>`¥${Number(v||0).toFixed(2)}`},
                {title:'操作',width:120,render:(_,record)=>(
                  <Button size="small" type="primary" onClick={()=>viewPurchaseItems(record)}>查看明细</Button>
                )}
              ]}
            />
          </div>
        ) : (
          <div>
            <div style={{marginBottom:12,display:'flex',justifyContent:'space-between',alignItems:'center'}}>
              <span>供应商：<b>{selectedPurchase.supplier}</b> &nbsp;&nbsp; 交货日期：{selectedPurchase.order_date}</span>
              <Button size="small" onClick={()=>{setSelectedPurchase(null);setPurchaseItems([]);}}>返回采购单列表</Button>
            </div>
            <Table
              rowKey="id"
              dataSource={purchaseItems}
              size="small"
              pagination={false}
              columns={[
                {title:'品牌(分类)',width:200,render:(_,r)=>getCategoryFullPath(r.category_id)},
                {title:'克重',dataIndex:'gram',width:80},
                {title:'幅宽',dataIndex:'width',width:80},
                {title:'单位',dataIndex:'unit',width:60},
                {title:'采购数量',dataIndex:'quantity',width:100,render:v=>`${v}吨`},
                {title:'吨价',dataIndex:'unit_price',width:100,render:v=>`¥${Number(v||0).toFixed(0)}`},
                {title:'已到货',dataIndex:'arrived_quantity',width:100,render:v=>`${v||0}吨`},
                {title:'备注',dataIndex:'remark',width:150,ellipsis:true},
                {title:'操作',width:100,render:(_,record)=>(
                  <Button size="small" type="primary" onClick={()=>selectFromPurchase(record)}>选择录入</Button>
                )}
              ]}
            />
          </div>
        )}
      </Modal>

      {/* =========快速新增品名弹窗========= */}'''
)

with open('src/RollWarehouse.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('卷料仓从采购单录入功能加完成')
