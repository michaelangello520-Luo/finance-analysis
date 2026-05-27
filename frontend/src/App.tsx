import { createBrowserRouter, RouterProvider, Outlet, Link } from 'react-router';
import { Layout, Menu } from 'antd';
import HomePage from './pages/HomePage';
import StockDetailPage from './pages/StockDetailPage';
import IndustryDetailPage from './pages/IndustryDetailPage';
import WatchlistPage from './pages/WatchlistPage';

const { Header, Content, Footer } = Layout;

function AppLayout() {
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center' }}>
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
    ],
  },
]);

export default function App() {
  return <RouterProvider router={router} />;
}
