import React, { useState, useEffect } from 'react';
import { Tabs, Table, Button, Modal, Form, Input, InputNumber, Select, DatePicker, Tag, Space, message, Row, Col, Card, Statistic } from 'antd';
import { api } from './api';
import dayjs from 'dayjs';

const REC_STATUS = { unpaid: { label: '未收', color: 'red' }, partial: { label: '部分收', color: 'orange' }, paid: { label: '已收清', color: 'green' } };
const PAY_STATUS = { unpaid: { label: '未付', color: 'red' }, partial: { label: '部分付', color: 'orange' }, paid: { label: '已付清', color: 'green' } };
const ACCOUNT_TYPE = { cash: '现金', bank: '银行', other: '其他' };

const money = v => Number(v || 0).toFixed(2);

export default function FinanceManage() {
  const [summary, setSummary] = useState({});
  const [accounts, setAccounts] = useState([]);
  const [receivables, setReceivables] = useState([]);
  const [payables, setPayables] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [txFilter, setTxFilter] = useState({ direction: undefined, account_id: undefined, keyword: '' });

  // 收款 / 付款弹窗
  const [receiveOpen, setReceiveOpen] = useState(false);
  const [payOpen, setPayOpen] = useState(false);
  const [currentRec, setCurrentRec] = useState(null);
  const [currentPay, setCurrentPay] = useState(null);
  const [receiveForm] = Form.useForm();
  const [payForm] = Form.useForm();

  // 账户弹窗
  const [accountOpen, setAccountOpen] = useState(false);
  const [editingAccount, setEditingAccount] = useState(null);
  const [accountForm] = Form.useForm();

  // 手工记账弹窗
  const [txOpen, setTxOpen] = useState(false);
  const [txDirection, setTxDirection] = useState('income');
  const [txForm] = Form.useForm();

  const loadAll = async () => {
    try {
      const [s, a, r, p] = await Promise.all([
        api.get('/api/finance/summary'),
        api.get('/api/finance/account'),
        api.get('/api/finance/receivable'),
        api.get('/api/finance/payable')
      ]);
      setSummary(s.data); setAccounts(a.data); setReceivables(r.data); setPayables(p.data);
    } catch (e) { message.error('财务数据加载失败'); }
  };

  const loadTransactions = async () => {
    const params = {};
    if (txFilter.direction) params.direction = txFilter.direction;
    if (txFilter.account_id) params.account_id = txFilter.account_id;
    if (txFilter.keyword) params.keyword = txFilter.keyword;
    const res = await api.get('/api/finance/transaction', { params });
    setTransactions(res.data);
  };

  useEffect(() => { loadAll(); }, []);
  useEffect(() => { loadTransactions(); }, [txFilter]);

  // ========== 收款 ==========
  const openReceive = (rec) => {
    setCurrentRec(rec);
    receiveForm.resetFields();
    receiveForm.setFieldsValue({ amount: rec.balance, trans_date: dayjs() });
    setReceiveOpen(true);
  };
  const confirmReceive = async () => {
    try {
      const v = await receiveForm.validateFields();
      await api.post(`/api/finance/receivable/${currentRec.id}/receive`, {
        amount: Number(v.amount), account_id: v.account_id,
        trans_date: v.trans_date.format('YYYY-MM-DD'),
        operator: v.operator || '', remark: v.remark || ''
      });
      message.success('收款成功，已登记流水');
      setReceiveOpen(false);
      loadAll(); loadTransactions();
    } catch (e) {
      if (e.errorFields) return;
      message.error(e.response?.data?.detail || '收款失败');
    }
  };

  // ========== 付款 ==========
  const openPay = (p) => {
    setCurrentPay(p);
    payForm.resetFields();
    payForm.setFieldsValue({ amount: p.balance, trans_date: dayjs() });
    setPayOpen(true);
  };
  const confirmPay = async () => {
    try {
      const v = await payForm.validateFields();
      await api.post(`/api/finance/payable/${currentPay.id}/pay`, {
        amount: Number(v.amount), account_id: v.account_id,
        trans_date: v.trans_date.format('YYYY-MM-DD'),
        operator: v.operator || '', remark: v.remark || ''
      });
      message.success('付款成功，已登记流水');
      setPayOpen(false);
      loadAll(); loadTransactions();
    } catch (e) {
      if (e.errorFields) return;
      message.error(e.response?.data?.detail || '付款失败');
    }
  };

  // ========== 账户 ==========
  const openAddAccount = () => {
    setEditingAccount(null);
    accountForm.resetFields();
    accountForm.setFieldsValue({ account_type: 'bank' });
    setAccountOpen(true);
  };
  const openEditAccount = (a) => {
    setEditingAccount(a);
    accountForm.setFieldsValue({ name: a.name, account_type: a.account_type, balance: a.balance, remark: a.remark });
    setAccountOpen(true);
  };
  const saveAccount = async () => {
    try {
      const v = await accountForm.validateFields();
      if (editingAccount) {
        await api.put(`/api/finance/account/${editingAccount.id}`, v);
        message.success('账户已更新');
      } else {
        await api.post('/api/finance/account', v);
        message.success('账户已创建');
      }
      setAccountOpen(false);
      loadAll();
    } catch (e) {
      if (e.errorFields) return;
      message.error(e.response?.data?.detail || '保存失败');
    }
  };
  const deleteAccount = async (a) => {
    try {
      await api.delete(`/api/finance/account/${a.id}`);
      message.success('账户已删除');
      loadAll();
    } catch (e) { message.error(e.response?.data?.detail || '删除失败'); }
  };

  // ========== 手工记账 ==========
  const openAddTx = () => {
    txForm.resetFields();
    setTxDirection('income');
    txForm.setFieldsValue({ trans_date: dayjs(), direction: 'income', category: '其他收入' });
    setTxOpen(true);
  };
  const saveTx = async () => {
    try {
      const v = await txForm.validateFields();
      await api.post('/api/finance/transaction', {
        trans_date: v.trans_date.format('YYYY-MM-DD'),
        direction: v.direction, category: v.category,
        counterparty: v.counterparty || '', account_id: v.account_id,
        amount: Number(v.amount), ref_type: 'manual', ref_no: '',
        operator: v.operator || '', remark: v.remark || ''
      });
      message.success('记账成功');
      setTxOpen(false);
      loadAll(); loadTransactions();
    } catch (e) {
      if (e.errorFields) return;
      message.error(e.response?.data?.detail || '记账失败');
    }
  };

  const accountName = id => accounts.find(a => a.id === id)?.name || '';
  const today = dayjs().format('YYYY-MM-DD');

  // ========== 列定义 ==========
  const receivableColumns = [
    { title: '销售单号', dataIndex: 'order_no', width: 160 },
    { title: '客户', dataIndex: 'customer_name' },
    { title: '应收金额', dataIndex: 'amount', align: 'right', render: v => `¥${money(v)}` },
    { title: '已收', dataIndex: 'received_amount', align: 'right', render: v => `¥${money(v)}` },
    { title: '未收余额', dataIndex: 'balance', align: 'right', render: v => <b style={{ color: v > 0 ? '#cf1322' : '#3f8600' }}>{money(v)}</b> },
    { title: '送出日期', dataIndex: 'ship_date', width: 110 },
    {
      title: '到期日', dataIndex: 'due_date', width: 120,
      render: (v, r) => v && r.status !== 'paid' && v < today
        ? <Tag color="red">{v} 已超期</Tag>
        : <span>{v || '-'}</span>
    },
    { title: '状态', dataIndex: 'status', width: 90, render: v => <Tag color={REC_STATUS[v]?.color}>{REC_STATUS[v]?.label || v}</Tag> },
    {
      title: '操作', width: 100,
      render: (_, r) => <Button size="small" type="primary" disabled={r.status === 'paid'} onClick={() => openReceive(r)}>收款</Button>
    }
  ];

  const payableColumns = [
    { title: '采购单号', dataIndex: 'order_no', width: 160 },
    { title: '供应商', dataIndex: 'supplier_name' },
    { title: '应付金额', dataIndex: 'amount', align: 'right', render: v => `¥${money(v)}` },
    { title: '已付', dataIndex: 'paid_amount', align: 'right', render: v => `¥${money(v)}` },
    { title: '未付余额', dataIndex: 'balance', align: 'right', render: v => <b style={{ color: v > 0 ? '#cf1322' : '#3f8600' }}>{money(v)}</b> },
    { title: '到货日期', dataIndex: 'arrive_date', width: 110 },
    { title: '到期日', dataIndex: 'due_date', width: 120, render: v => v || '-' },
    { title: '状态', dataIndex: 'status', width: 90, render: v => <Tag color={PAY_STATUS[v]?.color}>{PAY_STATUS[v]?.label || v}</Tag> },
    {
      title: '操作', width: 100,
      render: (_, r) => <Button size="small" type="primary" danger disabled={r.status === 'paid'} onClick={() => openPay(r)}>付款</Button>
    }
  ];

  const transactionColumns = [
    { title: '日期', dataIndex: 'trans_date', width: 110 },
    {
      title: '方向', dataIndex: 'direction', width: 80,
      render: v => <Tag color={v === 'income' ? 'green' : 'red'}>{v === 'income' ? '收入' : '支出'}</Tag>
    },
    { title: '类别', dataIndex: 'category', width: 110 },
    { title: '往来单位', dataIndex: 'counterparty' },
    { title: '资金账户', dataIndex: 'account_id', width: 120, render: v => accountName(v) },
    {
      title: '金额', dataIndex: 'amount', align: 'right', width: 130,
      render: (v, r) => <b style={{ color: r.direction === 'income' ? '#3f8600' : '#cf1322' }}>
        {r.direction === 'income' ? '+' : '-'}{money(v)}
      </b>
    },
    { title: '关联单据', dataIndex: 'ref_no', width: 160, render: v => v || '-' },
    { title: '经手人', dataIndex: 'operator', width: 90 },
    { title: '备注', dataIndex: 'remark' }
  ];

  const accountColumns = [
    { title: '账户名称', dataIndex: 'name' },
    { title: '类型', dataIndex: 'account_type', width: 100, render: v => ACCOUNT_TYPE[v] || v },
    { title: '当前余额', dataIndex: 'balance', align: 'right', render: v => <b style={{ color: v < 0 ? '#cf1322' : '#3f8600' }}>¥{money(v)}</b> },
    { title: '备注', dataIndex: 'remark' },
    {
      title: '操作', width: 140,
      render: (_, a) => (
        <Space>
          <Button size="small" onClick={() => openEditAccount(a)}>编辑</Button>
          <Button size="small" danger onClick={() => deleteAccount(a)}>删除</Button>
        </Space>
      )
    }
  ];

  const accountOptions = accounts.map(a => ({ value: a.id, label: `${a.name}（¥${money(a.balance)}）` }));

  return (
    <div style={{ padding: 20 }}>
      {/* 汇总看板 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}><Card><Statistic title="账上总资金" value={summary.total_cash || 0} precision={2} prefix="¥" /></Card></Col>
        <Col span={6}><Card><Statistic title="应收余额（客户欠我）" value={summary.receivable_balance || 0} precision={2} prefix="¥" valueStyle={{ color: '#fa8c16' }} /></Card></Col>
        <Col span={6}><Card><Statistic title="应付余额（我欠供应商）" value={summary.payable_balance || 0} precision={2} prefix="¥" valueStyle={{ color: '#cf1322' }} /></Card></Col>
        <Col span={6}><Card><Statistic title={`超期应收（${summary.overdue_count || 0}笔）`} value={summary.overdue_amount || 0} precision={2} prefix="¥" valueStyle={{ color: '#cf1322' }} /></Card></Col>
      </Row>

      <Tabs
        defaultActiveKey="receivable"
        items={[
          {
            key: 'receivable',
            label: `应收账款`,
            children: <Table rowKey="id" columns={receivableColumns} dataSource={receivables} pagination={false} size="middle" scroll={{ x: 1100 }} />
          },
          {
            key: 'payable',
            label: `应付账款`,
            children: <Table rowKey="id" columns={payableColumns} dataSource={payables} pagination={false} size="middle" scroll={{ x: 1100 }} />
          },
          {
            key: 'transaction',
            label: '资金流水',
            children: (
              <div>
                <Space style={{ marginBottom: 12 }} wrap>
                  <Select
                    placeholder="全部方向" allowClear style={{ width: 120 }}
                    value={txFilter.direction}
                    onChange={v => setTxFilter({ ...txFilter, direction: v })}
                    options={[{ value: 'income', label: '收入' }, { value: 'expense', label: '支出' }]}
                  />
                  <Select
                    placeholder="全部账户" allowClear style={{ width: 200 }}
                    value={txFilter.account_id}
                    onChange={v => setTxFilter({ ...txFilter, account_id: v })}
                    options={accounts.map(a => ({ value: a.id, label: a.name }))}
                  />
                  <Input
                    placeholder="搜索往来单位" style={{ width: 180 }}
                    value={txFilter.keyword}
                    onChange={e => setTxFilter({ ...txFilter, keyword: e.target.value })}
                  />
                  <Button type="primary" onClick={openAddTx}>+ 手工记账</Button>
                </Space>
                <Table rowKey="id" columns={transactionColumns} dataSource={transactions} pagination={false} size="middle" scroll={{ x: 1100 }} />
              </div>
            )
          },
          {
            key: 'account',
            label: '资金账户',
            children: (
              <div>
                <Button type="primary" onClick={openAddAccount} style={{ marginBottom: 12 }}>+ 新增账户</Button>
                <Table rowKey="id" columns={accountColumns} dataSource={accounts} pagination={false} size="middle" />
              </div>
            )
          }
        ]}
      />

      {/* 收款弹窗 */}
      <Modal open={receiveOpen} title={`收款登记 - ${currentRec?.customer_name || ''}`} onCancel={() => setReceiveOpen(false)} onOk={confirmReceive} okText="确认收款">
        <p style={{ color: '#666' }}>销售单号：{currentRec?.order_no} ｜ 未收余额：¥{money(currentRec?.balance)}</p>
        <Form form={receiveForm} layout="vertical">
          <Form.Item label="收款金额(元)" name="amount" rules={[{ required: true, message: '请输入收款金额' }]}>
            <InputNumber style={{ width: '100%' }} min={0.01} step="0.01" precision={2} />
          </Form.Item>
          <Form.Item label="收款入哪个账户" name="account_id" rules={[{ required: true, message: '请选择账户' }]}>
            <Select placeholder="选择资金账户" options={accountOptions} />
          </Form.Item>
          <Form.Item label="收款日期" name="trans_date" rules={[{ required: true }]}>
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item label="经手人" name="operator"><Input placeholder="收款人" /></Form.Item>
          <Form.Item label="备注" name="remark"><Input.TextArea rows={2} /></Form.Item>
        </Form>
      </Modal>

      {/* 付款弹窗 */}
      <Modal open={payOpen} title={`付款登记 - ${currentPay?.supplier_name || ''}`} onCancel={() => setPayOpen(false)} onOk={confirmPay} okText="确认付款">
        <p style={{ color: '#666' }}>采购单号：{currentPay?.order_no} ｜ 未付余额：¥{money(currentPay?.balance)}</p>
        <Form form={payForm} layout="vertical">
          <Form.Item label="付款金额(元)" name="amount" rules={[{ required: true, message: '请输入付款金额' }]}>
            <InputNumber style={{ width: '100%' }} min={0.01} step="0.01" precision={2} />
          </Form.Item>
          <Form.Item label="从哪个账户付出" name="account_id" rules={[{ required: true, message: '请选择账户' }]}>
            <Select placeholder="选择资金账户" options={accountOptions} />
          </Form.Item>
          <Form.Item label="付款日期" name="trans_date" rules={[{ required: true }]}>
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item label="经手人" name="operator"><Input placeholder="付款人" /></Form.Item>
          <Form.Item label="备注" name="remark"><Input.TextArea rows={2} /></Form.Item>
        </Form>
      </Modal>

      {/* 账户弹窗 */}
      <Modal open={accountOpen} title={editingAccount ? '编辑资金账户' : '新增资金账户'} onCancel={() => setAccountOpen(false)} onOk={saveAccount}>
        <Form form={accountForm} layout="vertical">
          <Form.Item label="账户名称" name="name" rules={[{ required: true, message: '请输入账户名称' }]}>
            <Input placeholder="如 现金、工商银行、微信" />
          </Form.Item>
          <Form.Item label="账户类型" name="account_type" rules={[{ required: true }]}>
            <Select options={[{ value: 'cash', label: '现金' }, { value: 'bank', label: '银行' }, { value: 'other', label: '其他' }]} />
          </Form.Item>
          <Form.Item label={editingAccount ? '当前余额（由流水驱动，不可直接改）' : '期初余额'} name="balance">
            <InputNumber style={{ width: '100%' }} step="0.01" precision={2} disabled={!!editingAccount} />
          </Form.Item>
          <Form.Item label="备注" name="remark"><Input /></Form.Item>
        </Form>
      </Modal>

      {/* 手工记账弹窗 */}
      <Modal open={txOpen} title="手工记账（其他收支）" onCancel={() => setTxOpen(false)} onOk={saveTx} okText="保存">
        <Form form={txForm} layout="vertical">
          <Form.Item label="日期" name="trans_date" rules={[{ required: true }]}>
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item label="方向" name="direction" rules={[{ required: true }]}>
            <Select onChange={v => {
              setTxDirection(v);
              txForm.setFieldsValue({ category: v === 'income' ? '其他收入' : '其他支出' });
            }} options={[{ value: 'income', label: '收入' }, { value: 'expense', label: '支出' }]} />
          </Form.Item>
          <Form.Item label="类别" name="category" rules={[{ required: true }]}>
            <Select options={txDirection === 'income'
              ? [{ value: '客户收款', label: '客户收款' }, { value: '其他收入', label: '其他收入' }]
              : [{ value: '供应商付款', label: '供应商付款' }, { value: '费用报销', label: '费用报销' }, { value: '其他支出', label: '其他支出' }]} />
          </Form.Item>
          <Form.Item label="往来单位" name="counterparty"><Input placeholder="客户/供应商/其他" /></Form.Item>
          <Form.Item label="资金账户" name="account_id" rules={[{ required: true, message: '请选择账户' }]}>
            <Select placeholder="选择账户" options={accountOptions} />
          </Form.Item>
          <Form.Item label="金额(元)" name="amount" rules={[{ required: true, message: '请输入金额' }]}>
            <InputNumber style={{ width: '100%' }} min={0.01} step="0.01" precision={2} />
          </Form.Item>
          <Form.Item label="经手人" name="operator"><Input /></Form.Item>
          <Form.Item label="备注" name="remark"><Input.TextArea rows={2} /></Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
