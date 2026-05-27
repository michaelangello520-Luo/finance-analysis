import { Typography, Layout } from 'antd';
import SearchBar from '../components/SearchBar';

const { Title, Paragraph } = Typography;
const { Content } = Layout;

export default function HomePage() {
  return (
    <Content style={{ padding: '80px 24px', maxWidth: 800, margin: '0 auto' }}>
      <Title level={2} style={{ textAlign: 'center', marginBottom: 8 }}>
        A 股长期投资看板
      </Title>
      <Paragraph style={{ textAlign: 'center', color: '#666', marginBottom: 40 }}>
        输入股票或行业，获取 AI 研报分析与产业链洞察
      </Paragraph>
      <div style={{ display: 'flex', justifyContent: 'center' }}>
        <SearchBar />
      </div>
    </Content>
  );
}
