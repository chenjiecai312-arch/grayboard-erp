import React from 'react';

// 金额大写转换
function amountToChinese(num) {
  if (!num || num === 0) return '零元整';
  const digits = ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖'];
  const units = ['', '拾', '佰', '仟', '万', '拾', '佰', '仟', '亿'];
  const intPart = Math.floor(num);
  const decPart = Math.round((num - intPart) * 100);
  let result = '';
  const intStr = String(intPart);
  for (let i = 0; i < intStr.length; i++) {
    const d = parseInt(intStr[i]);
    const u = intStr.length - 1 - i;
    if (d !== 0) {
      result += digits[d] + units[u];
    } else if (result && !result.endsWith('零') && u !== 4) {
      result += '零';
    }
    if (u === 4 && !result.endsWith('万')) result += '万';
  }
  result = result.replace(/零+$/, '').replace(/零万/, '万') + '元';
  if (decPart === 0) {
    result += '整';
  } else {
    const jiao = Math.floor(decPart / 10);
    const fen = decPart % 10;
    if (jiao > 0) result += digits[jiao] + '角';
    if (fen > 0) result += digits[fen] + '分';
  }
  return result;
}

// 公司信息（固定，可修改）
const COMPANY_INFO = {
  name: '东莞市捷鼎包装材料有限公司',
  address: 'Add:东莞市大岭山镇下虎山工业区创富路5号102室',
  tel: 'TEL：0755-27661505',
  fax: 'FAX：0755-27865245',
};

export default function SalesOrderPrint({ order }) {
  if (!order) return null;

  const totalAmount = order.total_amount || 0;
  const items = order.items || [];

  return (
    <div className="print-container" style={{
      fontFamily: '"SimSun", "宋体", serif',
      fontSize: '12px',
      color: '#000',
      padding: '10px',
      lineHeight: 1.6,
    }}>
      <style>{`
        @media print {
          .print-container { padding: 0; }
          .no-print { display: none !important; }
          body { margin: 0; padding: 10mm; }
        }
        .print-table {
          width: 100%;
          border-collapse: collapse;
        }
        .print-table td, .print-table th {
          border: 1px solid #000;
          padding: 4px 6px;
          text-align: center;
        }
        .print-table th {
          background: #f5f5f5;
          font-weight: bold;
        }
      `}</style>

      {/* 公司抬头 */}
      <div style={{ textAlign: 'center', marginBottom: '8px' }}>
        <div style={{ fontSize: '22px', fontWeight: 'bold', letterSpacing: '4px', marginBottom: '4px' }}>
          {COMPANY_INFO.name}
        </div>
        <div style={{ fontSize: '12px', marginBottom: '2px' }}>{COMPANY_INFO.address}</div>
        <div style={{ fontSize: '12px' }}>
          {COMPANY_INFO.tel} &nbsp;&nbsp; {COMPANY_INFO.fax}
        </div>
      </div>

      {/* 单据标题 */}
      <div style={{ textAlign: 'center', fontSize: '20px', fontWeight: 'bold', margin: '10px 0', letterSpacing: '8px' }}>
        送货单
      </div>

      {/* 订单信息 */}
      <table style={{ width: '100%', marginBottom: '0', borderCollapse: 'collapse' }}>
        <tbody>
          <tr>
            <td style={{ padding: '3px 0', whiteSpace: 'nowrap' }}>
              <b>客户名称：</b>{order.customer_name || ''}
            </td>
            <td style={{ padding: '3px 0', whiteSpace: 'nowrap' }}>
              <b>编号：</b>{order.order_no || ''}
            </td>
            <td style={{ padding: '3px 0', whiteSpace: 'nowrap', textAlign: 'right' }}>
              <b>送货日期：</b>{order.delivery_date || ''}
            </td>
          </tr>
          <tr>
            <td style={{ padding: '3px 0', whiteSpace: 'nowrap' }}>
              <b>客户订单号：</b>{order.customer_order_no || ''}
            </td>
            <td style={{ padding: '3px 0', whiteSpace: 'nowrap' }}>
              <b>收货人：</b>{order.receiver || ''}
            </td>
            <td style={{ padding: '3px 0', whiteSpace: 'nowrap' }}>
              <b>收货人电话：</b>{order.receiver_phone || ''}
            </td>
          </tr>
          <tr>
            <td colSpan={3} style={{ padding: '3px 0' }}>
              <b>送货地址：</b>{order.delivery_address || ''}
            </td>
          </tr>
        </tbody>
      </table>

      {/* 明细表格 */}
      <table className="print-table" style={{ marginTop: '0' }}>
        <thead>
          <tr>
            <th style={{ width: '5%' }}>行号</th>
            <th style={{ width: '18%' }}>货品名称</th>
            <th style={{ width: '15%' }}>规格MM</th>
            <th style={{ width: '7%' }}>单位</th>
            <th style={{ width: '10%' }}>数量</th>
            <th style={{ width: '10%' }}>价格</th>
            <th style={{ width: '12%' }}>金额</th>
            <th style={{ width: '13%' }}>备注</th>
          </tr>
        </thead>
        <tbody>
          {items.map((it, idx) => (
            <tr key={idx}>
              <td>{idx + 1}</td>
              <td style={{ textAlign: 'left' }}>{it.product_name}</td>
              <td>{it.spec || ''}</td>
              <td>{it.unit || ''}</td>
              <td>{Number(it.quantity || 0).toFixed(0)}</td>
              <td>{Number(it.price || 0).toFixed(2)}</td>
              <td>{Number(it.amount || 0).toFixed(2)}</td>
              <td>{it.remark || ''}</td>
            </tr>
          ))}
          {/* 空行填充 */}
          {items.length < 5 && Array.from({ length: 5 - items.length }).map((_, i) => (
            <tr key={`empty-${i}`}>
              <td>&nbsp;</td>
              <td>&nbsp;</td>
              <td>&nbsp;</td>
              <td>&nbsp;</td>
              <td>&nbsp;</td>
              <td>&nbsp;</td>
              <td>&nbsp;</td>
              <td>&nbsp;</td>
            </tr>
          ))}
          {/* 合计行 */}
          <tr>
            <td colSpan={6} style={{ textAlign: 'right', fontWeight: 'bold' }}>
              合&nbsp;&nbsp;计：（大写）
            </td>
            <td style={{ fontWeight: 'bold' }}>{totalAmount.toFixed(2)}
              <div style={{ fontSize: 10, fontWeight: 'normal' }}>
                {order.tax_included === false ? '（不含税）' : '（含税）'}
              </div>
            </td>
            <td>&nbsp;</td>
          </tr>
          <tr>
            <td colSpan={8} style={{ textAlign: 'left', padding: '6px' }}>
              人民币大写：<b>{amountToChinese(totalAmount)}</b>
              <span style={{ marginLeft: 20, color: '#666' }}>
                {order.tax_included === false ? '不含税价' : '含税价'}
              </span>
            </td>
          </tr>
        </tbody>
      </table>

      {/* 签字栏 */}
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '8px', fontSize: '12px' }}>
        <span>制单人：{order.maker || ''}</span>
        <span>财务：__________</span>
        <span>仓管：__________</span>
        <span>司机：__________</span>
        <span>业务员：{order.salesman || ''}</span>
      </div>

      {/* 备注条款 */}
      <div style={{ marginTop: '10px', fontSize: '11px', lineHeight: 1.8 }}>
        <div>1.货已发出，概不退换，特殊情况时，无破损前提下按九折退换。</div>
        <div>2.请当面验清货物，客户签收后，如有品种、规格、数量问题我司概不负责。</div>
        <div>3.此单经收货人员签字或盖章后既已确认为有效支付货款凭证，具有法律依据。</div>
      </div>

      {/* 底部签字 */}
      <div style={{ marginTop: '16px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px', fontSize: '12px' }}>
          <span>制单人：{order.maker || ''}</span>
          <span>发货人：__________</span>
          <span>业务员：{order.salesman || ''}</span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
          <span>送货单位盖章签名：____________________</span>
          <span>收货单位盖章签名：____________________</span>
        </div>
      </div>

      {/* 订单备注 */}
      {order.remark && (
        <div style={{ marginTop: '10px', fontSize: '11px', color: '#666' }}>
          备注：{order.remark}
        </div>
      )}
    </div>
  );
}
