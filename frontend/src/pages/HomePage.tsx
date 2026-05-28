import { useEffect, useState } from 'react';
import { Typography, Card, Row, Col, Tag, Table, message, Spin, Button, Empty } from 'antd';
import { Link, useNavigate } from 'react-router';
import { ReloadOutlined } from '@ant-design/icons';
import SearchBar from '../components/SearchBar';
import { collectIndustryData, getHotIndustries, getHotStocks, type HotIndustry, type HotStock } from '../services/api';

const { Title, Paragraph, Text } = Typography;

export default function HomePage() {
  const navigate = useNavigate();
  const [hotIndustries, setHotIndustries] = useState<HotIndustry[]>([]);
  const [hotStocks, setHotStocks] = useState<HotStock[]>([]);
  const [loadingHot, setLoadingHot] = useState(false);
  const [collectingIndustry, setCollectingIndustry] = useState<string | null>(null);

  const fetchAll = async () => {
    setLoadingHot(true);
    try {
      const [indRes, stockRes] = await Promise.all([getHotIndustries(12), getHotStocks(10)]);
      setHotIndustries(indRes.industries || []);
      setHotStocks(stockRes.stocks || []);
    } catch {
      message.error('获取热门数据失败');
    } finally {
      setLoadingHot(false);
    }
  };

  useEffect(() => { fetchAll(); }, []);

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

  const stockColumns = [
    {
      title: '名称', dataIndex: 'name', key: 'name',
      render: (name: string, record: HotStock) => <Link to={`/stock/${record.code}`}>{name}</Link>,
    },
    { title: '代码', dataIndex: 'code', key: 'code', width: 80 },
    {
      title: '最新价', dataIndex: 'price', key: 'price', width: 80, align: 'right' as const,
      render: (v: number) => v?.toFixed(2) || '-',
    },
    {
      title: '涨跌幅', dataIndex: 'change', key: 'change', width: 90, align: 'right' as const,
      render: (v: number) => (
        <span style={{ color: v > 0 ? '#f5222d' : v < 0 ? '#52c41a' : '#999', fontWeight: 600 }}>
          {v > 0 ? '+' : ''}{v}%
        </span>
      ),
    },
  ];

  return (
    <div style={{ padding: '60px 24px 40px', maxWidth: 1000, margin: '0 auto' }}>
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
          <Card
            title="热门行业"
            size="small"
            extra={<Button size="small" icon={<ReloadOutlined />} loading={loadingHot} onClick={fetchAll}>刷新</Button>}
          >
            {loadingHot && hotIndustries.length === 0 ? (
              <Spin style={{ display: 'block', margin: '20px auto' }} />
            ) : hotIndustries.length > 0 ? (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                {hotIndustries.map(ind => (
                  <Tag
                    key={ind.name}
                    color={ind.change > 0 ? 'red' : ind.change < 0 ? 'green' : 'default'}
                    style={{ fontSize: 14, padding: '4px 12px', cursor: collectingIndustry ? 'not-allowed' : 'pointer' }}
                    onClick={() => handleIndustryClick(ind.name)}
                  >
                    {collectingIndustry === ind.name ? '采集中...' : ind.name}
                    <span style={{ marginLeft: 4, fontWeight: 600 }}>{ind.change > 0 ? '+' : ''}{ind.change}%</span>
                  </Tag>
                ))}
              </div>
            ) : (
              <Empty description="暂无数据" />
            )}
            <Text type="secondary" style={{ display: 'block', marginTop: 12, fontSize: 12 }}>
              数据来源：同花顺行业板块涨幅排行 · 点击可采集详情
            </Text>
          </Card>
        </Col>

        <Col xs={24} md={12}>
          <Card title="热门股票" size="small">
            {loadingHot && hotStocks.length === 0 ? (
              <Spin style={{ display: 'block', margin: '20px auto' }} />
            ) : hotStocks.length > 0 ? (
              <Table dataSource={hotStocks} columns={stockColumns} rowKey="code" size="small" pagination={false} />
            ) : (
              <Empty description="暂无数据" />
            )}
            <Text type="secondary" style={{ display: 'block', marginTop: 8, fontSize: 12 }}>
              点击股票名称可采集详情和 AI 分析
            </Text>
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col span={24}>
          <Card title="我的关注" size="small">
            <Link to="/watchlist"><Button type="primary">查看关注列表</Button></Link>
            <Text type="secondary" style={{ marginLeft: 12, fontSize: 12 }}>
              在个股或行业详情页点击星标即可添加关注
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
