import { useState } from 'react';
import { Typography, Card, Row, Col, Tag, message } from 'antd';
import { Link, useNavigate } from 'react-router';
import SearchBar from '../components/SearchBar';
import { collectIndustryData } from '../services/api';

const { Title, Paragraph, Text } = Typography;

const HOT_INDUSTRIES = [
  { name: '银行', tag: '金融' },
  { name: '半导体', tag: '科技' },
  { name: '新能源', tag: '制造' },
  { name: '白酒', tag: '消费' },
  { name: '医药', tag: '医疗' },
  { name: '人工智能', tag: '科技' },
];

const DEMO_STOCKS = [
  { code: '600036', name: '招商银行' },
  { code: '000858', name: '五粮液' },
  { code: '300750', name: '宁德时代' },
];

export default function HomePage() {
  const navigate = useNavigate();
  const [collectingIndustry, setCollectingIndustry] = useState<string | null>(null);

  const handleIndustryClick = async (name: string) => {
    setCollectingIndustry(name);
    try {
      const res = await collectIndustryData(name);
      message.success(res.message);
      const industryId = (res as Record<string, unknown>).id;
      if (industryId) {
        navigate(`/industry/${industryId}`);
      }
    } catch {
      message.error('行业数据采集失败');
    } finally {
      setCollectingIndustry(null);
    }
  };

  return (
    <div style={{ padding: '60px 24px 40px', maxWidth: 900, margin: '0 auto' }}>
      <Title level={2} style={{ textAlign: 'center', marginBottom: 8 }}>
        A 股长期投资看板
      </Title>
      <Paragraph style={{ textAlign: 'center', color: '#666', marginBottom: 40 }}>
        输入股票代码或行业名称，获取 AI 研报分析与投资洞察
      </Paragraph>

      <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 48 }}>
        <SearchBar />
      </div>

      <Row gutter={[16, 16]}>
        <Col xs={24} md={12}>
          <Card title="热门行业" size="small">
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
              {HOT_INDUSTRIES.map(ind => (
                <Tag
                  key={ind.name}
                  color="blue"
                  style={{ fontSize: 14, padding: '4px 12px', cursor: collectingIndustry ? 'not-allowed' : 'pointer' }}
                  onClick={() => handleIndustryClick(ind.name)}
                >
                  {collectingIndustry === ind.name ? '采集中...' : ind.name}
                </Tag>
              ))}
            </div>
            <Text type="secondary" style={{ display: 'block', marginTop: 12, fontSize: 12 }}>
              点击行业标签可采集行业数据并查看详情
            </Text>
          </Card>
        </Col>

        <Col xs={24} md={12}>
          <Card title="快速查看" size="small">
            {DEMO_STOCKS.map(s => (
              <Link key={s.code} to={`/stock/${s.code}`} style={{ display: 'block', padding: '6px 0' }}>
                <Text>{s.name}</Text>
                <Text type="secondary" style={{ marginLeft: 8 }}>{s.code}</Text>
              </Link>
            ))}
            <Text type="secondary" style={{ display: 'block', marginTop: 12, fontSize: 12 }}>
              点击个股可查看详情和 AI 分析
            </Text>
          </Card>
        </Col>
      </Row>

      <Paragraph type="secondary" style={{ textAlign: 'center', marginTop: 40, fontSize: 12 }}>
        ⚠️ 免责声明：本平台数据和AI分析仅供参考，不构成投资建议。投资有风险，入市需谨慎。
      </Paragraph>
    </div>
  );
}
