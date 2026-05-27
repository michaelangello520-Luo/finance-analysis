import { useParams } from 'react-router';
import { Typography } from 'antd';

const { Title, Paragraph } = Typography;

export default function StockDetailPage() {
  const { code } = useParams<{ code: string }>();
  return (
    <div style={{ padding: 24 }}>
      <Title level={3}>个股详情: {code}</Title>
      <Paragraph>Phase 4 实现</Paragraph>
    </div>
  );
}
