with open('src/SalesOrder.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 改成所有状态按钮
old = '''      title: "操作", key: "action", width: 220, fixed: 'right',
      render: (_, record) => (
        <Space wrap>
          <Button size="small" type="primary" onClick={() => handlePrint(record)}>打印</Button>
          <Button 
            size="small" 
            type={record.status === "pending" ? "primary" : "default"}
            onClick={() => {
              if (record.status === "pending") return;
              Modal.confirm({
                title: "确认切换为待出库？",
                content: "切换为待出库后，系统会自动在成品仓锁定对应库存。",
                onOk: () => handleChangeStatus(record, "pending")
              });
            }}
          >待出库</Button>
          <Button 
            size="small" 
            danger={record.status === "cancelled"}
            onClick={() => {
              if (record.status === "cancelled") return;
              Modal.confirm({
                title: "确认取消订单？",
                content: "取消订单后，所有待出库库存都会加回。",
                onOk: () => handleChangeStatus(record, "cancelled")
              });
            }}
          >取消</Button>
          <Button size="small" onClick={() => openEdit(record)}>编辑</Button>
          <Popconfirm title="确定删除该订单？" onConfirm={() => handleDelete(record.id)} okText="确认" cancelText="取消">
            <Button size="small" danger>删除</Button>
          </Popconfirm>
        </Space>
      )'''

new = '''      title: "操作", key: "action", width: 360, fixed: 'right',
      render: (_, record) => (
        <Space wrap size={4}>
          <Button size="small" type="primary" onClick={() => handlePrint(record)}>打印</Button>
          <Button 
            size="small" 
            type={record.status === "draft" ? "primary" : "default"}
            onClick={() => {
              if (record.status === "draft") return;
              Modal.confirm({
                title: "确认打回草稿？",
                content: "打回草稿后，所有待出库库存都会加回。",
                onOk: () => handleChangeStatus(record, "draft")
              });
            }}
          >草稿</Button>
          <Button 
            size="small" 
            type={record.status === "pending" ? "primary" : "default"}
            onClick={() => {
              if (record.status === "pending") return;
              Modal.confirm({
                title: "确认切换为待出库？",
                content: "切换为待出库后，系统会自动在成品仓锁定对应库存。",
                onOk: () => handleChangeStatus(record, "pending")
              });
            }}
          >待出库</Button>
          <Button 
            size="small" 
            type={record.status === "shipped" ? "primary" : "default"}
            onClick={() => {
              if (record.status === "shipped") return;
              Modal.confirm({
                title: "确认标记为已出库？",
                content: "确认后将真正扣减成品仓总库存，不可恢复。",
                onOk: () => handleChangeStatus(record, "shipped")
              });
            }}
          >已出库</Button>
          <Button 
            size="small" 
            type={record.status === "completed" ? "primary" : "default"}
            onClick={() => {
              if (record.status === "completed") return;
              Modal.confirm({
                title: "确认标记为已完成？",
                content: "确认表示客户已实际收货。",
                onOk: () => handleChangeStatus(record, "completed")
              });
            }}
          >已完成</Button>
          <Button 
            size="small" 
            danger={record.status === "cancelled"}
            onClick={() => {
              if (record.status === "cancelled") return;
              Modal.confirm({
                title: "确认取消订单？",
                content: "取消订单后，所有待出库库存都会加回。",
                onOk: () => handleChangeStatus(record, "cancelled")
              });
            }}
          >取消</Button>
          <Button size="small" onClick={() => openEdit(record)}>编辑</Button>
          <Popconfirm title="确定删除该订单？" onConfirm={() => handleDelete(record.id)} okText="确认" cancelText="取消">
            <Button size="small" danger>删除</Button>
          </Popconfirm>
        </Space>
      )'''

content = content.replace(old, new)

with open('src/SalesOrder.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('所有状态按钮完成')
