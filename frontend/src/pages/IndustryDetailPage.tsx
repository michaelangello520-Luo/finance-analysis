import { useParams } from 'react-router';
import { Typography } from 'antd';

const { Title, Paragraph } = Typography;

export default function IndustryDetailPage() {
  const { id } = useParams<{ id: string }>();
  return (
    <div style={{ padding: 24 }}>
      <Title level={3}>行业详情: {id}</Title>
      <Paragraph>Phase 4 实现</Paragraph>
    </div>
  );
}
