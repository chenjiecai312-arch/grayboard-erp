import React, { useState, useEffect } from 'react';
import { Form, Input, Button, Layout, Menu, ConfigProvider } from 'antd'
import CustomerManage from './CustomerManage';
// ==========新增3个仓库页面导入==========
import ProductWarehouse from './ProductWarehouse';
import RollWarehouse from './RollWarehouse';
import MaterialWarehouse from './MaterialWarehouse';
// ==========销售订单页面导入==========
import SalesOrder from './SalesOrder';
import OperationLog from './OperationLog';
import ProduceOrder from './ProduceOrder';
import ScheduleList from './ScheduleList';
import PendingProduction from './PendingProduction';
import PurchaseOrder from './PurchaseOrder';
import SupplierManage from './SupplierManage';
import FinanceManage from './FinanceManage';
import StaffManage from './StaffManage';
import CatalogManage from './CatalogManage';
import { api, login, logout } from './api';

const { Sider, Content } = Layout;

const KEY_PERM = {
  customer: 'customer',
  supplier: 'supplier',
  catalog: 'catalog',
  ware_product: 'ware_product',
  ware_roll: 'ware_roll',
  ware_material: 'ware_material',
  purchase: 'purchase',
  sale: 'sales',
  produce: 'produce',
  schedule: 'produce',
  pending: 'produce',
  finance: 'finance',
  log: 'log',
  staff: 'staff',
};

function canSee(permissions, key) {
  return (permissions || []).includes(KEY_PERM[key]);
}

function firstPage(permissions) {
  return Object.keys(KEY_PERM).find((key) => canSee(permissions, key)) || 'customer';
}

export default function App() {
  const [activeKey, setActiveKey] = useState("customer");
  const [authed, setAuthed] = useState(!!localStorage.getItem('access_token'));
  const [loggingIn, setLoggingIn] = useState(false);
  const [loginError, setLoginError] = useState('');
  const [me, setMe] = useState(null);

  useEffect(() => {
    const onLost = () => { setAuthed(false); setMe(null); };
    window.addEventListener('auth-lost', onLost);
    return () => window.removeEventListener('auth-lost', onLost);
  }, []);

  useEffect(() => {
    if (!authed) return;
    api.get('/api/auth/me').then((res) => {
      setMe(res.data);
      setActiveKey((current) => canSee(res.data.permissions, current) ? current : firstPage(res.data.permissions));
    }).catch(() => {
      logout();
      setAuthed(false);
      setMe(null);
    });
  }, [authed]);

  if (!authed) {
    return (
      <ConfigProvider theme={{ token: { colorPrimary: '#24312c', borderRadius: 10, controlHeightLG: 46, fontFamily: "system-ui, 'PingFang SC', 'Microsoft YaHei', sans-serif" } }}>
        <div className="login-page">
          <aside className="login-aside">
            <div>
              <div className="login-kicker">GRAYBOARD</div>
              <h1>灰板产销系统</h1>
              <p className="login-lead">采购、排产、仓储和结算放在同一套账里。</p>
            </div>
            <ul className="login-points">
              <li><span>01</span>客户档案与销售订单</li>
              <li><span>02</span>卷料、成品、辅料仓库</li>
              <li><span>03</span>生产排单与财务结算</li>
            </ul>
            <div className="login-sheets" aria-hidden="true">
              <span /><span /><span />
            </div>
          </aside>
          <main className="login-main">
            <Form
              className="login-card"
              layout="vertical"
              size="large"
              requiredMark={false}
              onFinish={async (values) => {
                setLoggingIn(true);
                setLoginError('');
                try {
                  await login(values.username, values.password);
                  setAuthed(true);
                } catch (err) {
                  setLoginError(err.response?.data?.error_description || '登录失败');
                } finally {
                  setLoggingIn(false);
                }
              }}
            >
              <div className="login-card-kicker">内部系统</div>
              <h2>登录</h2>
              <p className="login-card-sub">使用分配的账号进入系统</p>
              <Form.Item name="username" label="账号" rules={[{ required: true, message: '请输入账号' }]}>
                <Input autoFocus placeholder="请输入账号" />
              </Form.Item>
              <Form.Item name="password" label="密码" rules={[{ required: true, message: '请输入密码' }]}>
                <Input.Password placeholder="请输入密码" />
              </Form.Item>
              {loginError && <div className="login-error">{loginError}</div>}
              <Button type="primary" htmlType="submit" block loading={loggingIn}>登录</Button>
            </Form>
          </main>
        </div>
      </ConfigProvider>
    );
  }

  return (
    <Layout style={{ height: "100vh", width: "100vw", overflow: "hidden", flexDirection: "row" }}>
      <Sider theme="dark" width={220} style={{ height: "100vh", flexShrink: 0 }}>
        <div style={{ color:"#fff",padding:16,fontSize:16,fontWeight:"bold" }}>灰板产销系统</div>
        <div style={{ color:"#aaa", padding:"0 16px 8px", fontSize:12 }}>
          {me?.real_name || me?.username}
          <Button type="link" size="small" onClick={() => { logout(); setAuthed(false); setMe(null); }}>退出</Button>
        </div>
                <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[activeKey]}
          onClick={({ key }) => setActiveKey(key)}
          style={{ height: "calc(100vh - 60px)", overflowY: "auto" }}
        >
          {canSee(me?.permissions, 'customer') && <Menu.Item key="customer">客户档案</Menu.Item>}
          {canSee(me?.permissions, 'supplier') && <Menu.Item key="supplier">供应商管理</Menu.Item>}
          {canSee(me?.permissions, 'catalog') && <Menu.Item key="catalog">目录管理</Menu.Item>}

          {(canSee(me?.permissions, 'ware_product') || canSee(me?.permissions, 'ware_roll') || canSee(me?.permissions, 'ware_material') || canSee(me?.permissions, 'purchase')) && (
            <Menu.SubMenu key="warehouse" title="仓库管理">
              {canSee(me?.permissions, 'ware_product') && <Menu.Item key="ware_product">成品仓</Menu.Item>}
              {canSee(me?.permissions, 'ware_roll') && <Menu.Item key="ware_roll">卷料仓</Menu.Item>}
              {canSee(me?.permissions, 'ware_material') && <Menu.Item key="ware_material">辅料仓</Menu.Item>}
              {canSee(me?.permissions, 'purchase') && <Menu.Item key="purchase">采购单</Menu.Item>}
            </Menu.SubMenu>
          )}

          {canSee(me?.permissions, 'sale') && <Menu.Item key="sale">销售订单</Menu.Item>}
          {canSee(me?.permissions, 'produce') && (
            <Menu.SubMenu key="produce_group" title="生产管理">
              <Menu.Item key="produce">生产工单</Menu.Item>
              <Menu.Item key="schedule">已排单</Menu.Item>
              <Menu.Item key="pending">待生产</Menu.Item>
            </Menu.SubMenu>
          )}
          {canSee(me?.permissions, 'finance') && <Menu.Item key="finance">财务结算</Menu.Item>}
          {canSee(me?.permissions, 'log') && <Menu.Item key="log">操作日志</Menu.Item>}
          {canSee(me?.permissions, 'staff') && <Menu.Item key="staff">人员权限</Menu.Item>}
        </Menu>

      </Sider>

      <Content style={{ background:"#f0f2f5", overflow: "auto", height: "100vh", flex: 1, padding: 0, minWidth: 0 }}>
        {!me ? <div style={{ padding: 24 }}>加载中...</div> : (
          <>
            {activeKey === "customer" && canSee(me.permissions, "customer") && <CustomerManage />}
            {activeKey === "supplier" && canSee(me.permissions, "supplier") && <SupplierManage />}
            {activeKey === "catalog" && canSee(me.permissions, "catalog") && <CatalogManage />}
            {activeKey === "ware_product" && canSee(me.permissions, "ware_product") && <ProductWarehouse />}
            {activeKey === "ware_roll" && canSee(me.permissions, "ware_roll") && <RollWarehouse onNavigate={setActiveKey} />}
            {activeKey === "ware_material" && canSee(me.permissions, "ware_material") && <MaterialWarehouse />}
            {activeKey === "purchase" && canSee(me.permissions, "purchase") && <PurchaseOrder />}
            {activeKey === "sale" && canSee(me.permissions, "sale") && <SalesOrder />}
            {activeKey === "produce" && canSee(me.permissions, "produce") && <ProduceOrder />}
            {activeKey === "schedule" && canSee(me.permissions, "schedule") && <ScheduleList />}
            {activeKey === "pending" && canSee(me.permissions, "pending") && <PendingProduction />}
            {activeKey === "log" && canSee(me.permissions, "log") && <OperationLog />}
            {activeKey === "finance" && canSee(me.permissions, "finance") && <FinanceManage />}
            {activeKey === "staff" && canSee(me.permissions, "staff") && <StaffManage />}
          </>
        )}
      </Content>
    </Layout>
  )
}
