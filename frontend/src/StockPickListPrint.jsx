import React from 'react';
import { Modal, Button } from 'antd';

// 备货单打印模板（仓库用，支持多订单一起打印）
export default function StockPickListPrint({ orders, open, onCancel }) {
  if (!orders || orders.length === 0) return null;

  // 汇总所有明细
  const allItems = [];
  orders.forEach(order => {
    (order.items || []).forEach(it => {
      allItems.push({
        ...it,
        order_no: order.order_no,
        customer_name: order.customer_name,
        delivery_date: order.delivery_date
      });
    });
  });

  const totalQty = allItems.reduce((sum, it) => sum + (Number(it.quantity) || 0), 0);

  return (
    <Modal
      open={open}
      title="备货单打印预览（仓库专用）"
      onCancel={onCancel}
      zIndex={3000}
      width={900}
      footer={
        <div style={{ textAlign: 'right' }}>
          <Button onClick={onCancel} style={{ marginRight: 8 }}>关闭</Button>
          <Button type="primary" onClick={() => window.print()}>打印</Button>
        </div>
      }
    >
      <div id="pick-list-print-area" style={{ padding: '20px', fontFamily: 'Microsoft YaHei, sans-serif' }}>
        {/* 表头 */}
        <div style={{ textAlign: 'center', marginBottom: 20 }}>
          <h2 style={{ margin: 0, fontSize: 22, fontWeight: 'bold' }}>备货单</h2>
          <div style={{ fontSize: 12, marginTop: 4, color: '#666' }}>仓库备货专用 · 共 {orders.length} 个订单</div>
        </div>

        {/* 订单信息汇总 */}
        <div style={{ marginBottom: 16, fontSize: 13, backgroundColor: '#f9f9f9', padding: 10, borderRadius: 4 }}>
          {orders.map(o => (
            <div key={o.id} style={{ marginBottom: 4 }}>
              <b>{o.order_no}</b> · {o.customer_name} · 送货日期：{o.delivery_date}
            </div>
          ))}
        </div>

        {/* 明细表格 */}
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
          <thead>
            <tr style={{ backgroundColor: '#f5f5f5' }}>
              <th style={{ border: '1px solid #ddd', padding: '8px', textAlign: 'center' }}>序号</th>
              <th style={{ border: '1px solid #ddd', padding: '8px', textAlign: 'center' }}>订单号</th>
              <th style={{ border: '1px solid #ddd', padding: '8px', textAlign: 'center' }}>客户</th>
              <th style={{ border: '1px solid #ddd', padding: '8px', textAlign: 'center' }}>品名</th>
              <th style={{ border: '1px solid #ddd', padding: '8px', textAlign: 'center' }}>规格</th>
              <th style={{ border: '1px solid #ddd', padding: '8px', textAlign: 'center' }}>数量</th>
              <th style={{ border: '1px solid #ddd', padding: '8px', textAlign: 'center' }}>备货打勾</th>
            </tr>
          </thead>
          <tbody>
            {allItems.map((it, idx) => (
              <tr key={idx}>
                <td style={{ border: '1px solid #ddd', padding: '8px', textAlign: 'center' }}>{idx + 1}</td>
                <td style={{ border: '1px solid #ddd', padding: '8px', fontSize: 12 }}>{it.order_no}</td>
                <td style={{ border: '1px solid #ddd', padding: '8px', fontSize: 12 }}>{it.customer_name}</td>
                <td style={{ border: '1px solid #ddd', padding: '8px' }}>{it.product_name}</td>
                <td style={{ border: '1px solid #ddd', padding: '8px', textAlign: 'center' }}>{it.spec}</td>
                <td style={{ border: '1px solid #ddd', padding: '8px', textAlign: 'center', fontWeight: 'bold', fontSize: 16 }}>
                  {Number(it.quantity).toFixed(0)} {it.unit}
                </td>
                <td style={{ border: '1px solid #ddd', padding: '8px', textAlign: 'center', height: 30 }}></td>
              </tr>
            ))}
          </tbody>
        </table>

        {/* 合计 */}
        <div style={{ marginTop: 16, fontSize: 13 }}>
          <b>合计：</b>共 {allItems.length} 项，总数量 {totalQty.toFixed(0)} 张
        </div>

        {/* 签字栏 */}
        <div style={{ marginTop: 40, display: 'flex', justifyContent: 'space-between', fontSize: 13 }}>
          <div>备货人：__________</div>
          <div>仓管：__________</div>
          <div>复核：__________</div>
        </div>

        {/* 底部提示 */}
        <div style={{ marginTop: 30, fontSize: 11, color: '#999', textAlign: 'center' }}>
          请按备货单备货，备货完成后打勾签字，确认出库后库存自动扣减
        </div>
      </div>

      {/* 打印样式 */}
      <style>{`
        @media print {
          body * { visibility: hidden; }
          #pick-list-print-area, #pick-list-print-area * { visibility: visible; }
          #pick-list-print-area { position: absolute; left: 0; top: 0; width: 100%; }
        }
      `}</style>
    </Modal>
  );
}
