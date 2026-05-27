import { createBrowserRouter, RouterProvider, Outlet, Link } from 'react-router';
import { Layout, Menu } from 'antd';
import { SettingOutlined } from '@ant-design/icons';
import HomePage from './pages/HomePage';
import StockDetailPage from './pages/StockDetailPage';
import IndustryDetailPage from './pages/IndustryDetailPage';
import WatchlistPage from './pages/WatchlistPage';
import SettingsPage from './pages/SettingsPage';

const { Header, Content, Footer } = Layout;

function AppLayout() {
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <Link to="/" style={{ color: '#fff', fontSize: 18, fontWeight: 'bold', marginRight: 40, textDecoration: 'none' }}>
            Finance Analysis
          </Link>
          <Menu
            theme="dark"
            mode="horizontal"
            items={[
              { key: 'home', label: <Link to="/">首页</Link> },
              { key: 'watchlist', label: <Link to="/watchlist">关注列表</Link> },
            ]}
          />
        </div>
        <Link to="/settings" style={{ color: 'rgba(255,255,255,0.85)', fontSize: 14, textDecoration: 'none' }}>
          <SettingOutlined style={{ marginRight: 6 }} />AI 设置
        </Link>
      </Header>
      <Content>
        <Outlet />
      </Content>
      <Footer style={{ textAlign: 'center' }}>A 股长期投资看板 2026</Footer>
    </Layout>
  );
}

const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    children: [
      { index: true, element: <HomePage /> },
      { path: 'stock/:code', element: <StockDetailPage /> },
      { path: 'industry/:id', element: <IndustryDetailPage /> },
      { path: 'watchlist', element: <WatchlistPage /> },
      { path: 'settings', element: <SettingsPage /> },
    ],
  },
]);

export default function App() {
  return <RouterProvider router={router} />;
}
