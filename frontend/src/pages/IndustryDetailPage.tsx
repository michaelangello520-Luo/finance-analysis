import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router';
import { Typography, Card, Table, Button, Spin, Tag, message, Row, Col, Empty, Divider } from 'antd';
import { ArrowLeftOutlined, RobotOutlined, FileTextOutlined } from '@ant-design/icons';
import { getIndustryDetail, analyzeReport, collectIndustryData } from '../services/api';
import type { IndustryDetail as IndustryDetailType, StockBrief, ReportItem } from '../services/api';

const { Title, Text } = Typography;

export default function IndustryDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [industry, setIndustry] = useState<IndustryDetailType | null>(null);
  const [loading, setLoading] = useState(true);
  const [collecting, setCollecting] = useState(false);
  const [aiAnalysis, setAiAnalysis] = useState<string | null>(null);

  const fetchIndustry = async () => {
    if (!id) return;
    try {
      const data = await getIndustryDetail(Number(id));
      setIndustry(data);
    } catch {
      message.error('行业数据不存在');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchIndustry(); }, [id]);

  const handleCollect = async () => {
    if (!industry) return;
    setCollecting(true);
    try {
      const res = await collectIndustryData(industry.name, industry.sector || undefined);
      message.success(res.message);
      fetchIndustry();
    } catch {
      message.error('采集失败');
    } finally {
      setCollecting(false);
    }
  };

  const handleReportAI = async (reportId: number) => {
    try {
      const res = await analyzeReport(reportId);
      setAiAnalysis(res.analysis);
      window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
    } catch {
      message.error('研报分析失败');
    }
  };

  if (loading) return <Spin style={{ display: 'block', margin: '100px auto' }} />;

  if (!industry) {
    return (
      <div style={{ padding: 40, textAlign: 'center' }}>
        <Empty description={`未找到行业 ${id} 的数据`} />
      </div>
    );
  }

  const stockColumns = [
    { title: '代码', dataIndex: 'code', key: 'code', width: 100 },
    { title: '名称', dataIndex: 'name', key: 'name',
      render: (name: string, record: StockBrief) => <Link to={`/stock/${record.code}`}>{name || record.code}</Link>,
    },
  ];

  const reportColumns = [
    { title: '日期', dataIndex: 'report_date', key: 'date', width: 110, render: (v: string) => v?.substring(0, 10) || '-' },
    { title: '标题', dataIndex: 'title', key: 'title', ellipsis: true },
    { title: '机构', dataIndex: 'institution', key: 'inst', width: 120 },
    {
      title: '操作', key: 'action', width: 100,
      render: (_: unknown, record: ReportItem) => (
        <Button size="small" icon={<RobotOutlined />} onClick={() => handleReportAI(record.id)}>AI解读</Button>
      ),
    },
  ];

  return (
    <div style={{ padding: 24, maxWidth: 1100, margin: '0 auto' }}>
      <div style={{ marginBottom: 16 }}>
        <Link to="/"><ArrowLeftOutlined /> 返回首页</Link>
      </div>

      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Card>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <Title level={3} style={{ margin: 0 }}>{industry.name}</Title>
                {industry.sector && <Tag color="blue" style={{ marginLeft: 8 }}>{industry.sector}</Tag>}
              </div>
              <Button loading={collecting} onClick={handleCollect}>刷新数据</Button>
            </div>
            {industry.description && (
              <Text type="secondary" style={{ display: 'block', marginTop: 8 }}>{industry.description}</Text>
            )}
          </Card>
        </Col>

        <Col xs={24} md={12}>
          <Card title="成分股" size="small">
            {industry.stocks.length > 0 ? (
              <Table dataSource={industry.stocks} columns={stockColumns} rowKey="id" size="small" pagination={{ pageSize: 10 }} />
            ) : (
              <Empty description="暂无成分股" />
            )}
          </Card>
        </Col>

        <Col xs={24} md={12}>
          <Card title={<><FileTextOutlined /> 研究报告</>} size="small">
            {industry.reports.length > 0 ? (
              <Table dataSource={industry.reports} columns={reportColumns} rowKey="id" size="small" pagination={{ pageSize: 5 }} />
            ) : (
              <Empty description="暂无研报" />
            )}
          </Card>
        </Col>

        {aiAnalysis && (
          <Col span={24}>
            <Card title={<><RobotOutlined /> AI 研报解读</>}>
              <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.8 }}>
                {aiAnalysis.split('\n').map((line, i) => {
                  if (line.startsWith('### ')) return <Title key={i} level={5} style={{ marginTop: 16 }}>{line.replace('### ', '')}</Title>;
                  if (line.startsWith('- ')) return <div key={i} style={{ paddingLeft: 16 }}>{line}</div>;
                  if (line.startsWith('⚠️')) return <Tag key={i} color="orange" style={{ marginTop: 16 }}>{line}</Tag>;
                  return <span key={i}>{line}<br /></span>;
                })}
              </div>
            </Card>
          </Col>
        )}
      </Row>

      <Divider />
      <Text type="secondary" style={{ fontSize: 12 }}>
        ⚠️ 免责声明：以上数据和AI分析仅供参考，不构成投资建议。投资有风险，入市需谨慎。
      </Text>
    </div>
  );
}
