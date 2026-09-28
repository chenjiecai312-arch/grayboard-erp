with open('src/SalesOrder.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 把状态下拉框改成按钮组
old = '''          <Button size="small" type="primary" onClick={() => handlePrint(record)}>打印</Button>
          <Select
            size="small"
            value={record.status}
            style={{ width: 100 }}
            onChange={(val) => handleChangeStatus(record, val)}
            options={[
              { value: "draft", label: "草稿" },
              { value: "pending", label: "待出库" },
              { value: "shipped", label: "已发货" },
              { value: "completed", label: "已完成" },
              { value: "cancelled", label: "已取消" },
            ]}
          />
          <Button size="small" onClick={() => openEdit(record)}>编辑</Button>'''

new = '''          <Button size="small" type="primary" onClick={() => handlePrint(record)}>打印</Button>
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
          <Button size="small" onClick={() => openEdit(record)}>编辑</Button>'''

content = content.replace(old, new)

with open('src/SalesOrder.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('状态按钮化完成')
