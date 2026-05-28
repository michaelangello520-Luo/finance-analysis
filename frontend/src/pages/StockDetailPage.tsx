import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router';
import { Typography, Card, Table, Button, Spin, Tag, message, Row, Col, Empty, Divider } from 'antd';
import { ArrowLeftOutlined, RobotOutlined, FileTextOutlined, StarOutlined, StarFilled } from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import { getStockDetail, analyzeStock, analyzeReport, collectStockData, collectReports, checkWatchlist, addToWatchlist, removeFromWatchlist } from '../services/api';
import type { StockDetail as StockDetailType, ReportItem } from '../services/api';

const { Title, Text, Paragraph } = Typography;

export default function StockDetailPage() {
  const { code } = useParams<{ code: string }>();
  const [stock, setStock] = useState<StockDetailType | null>(null);
  const [loading, setLoading] = useState(true);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiAnalysis, setAiAnalysis] = useState<string | null>(null);
  const [collecting, setCollecting] = useState(false);
  const [watched, setWatched] = useState<{ watched: boolean; id: number | null }>({ watched: false, id: null });

  const fetchStock = async () => {
    if (!code) return;
    try {
      const data = await getStockDetail(code);
      setStock(data);
      const wc = await checkWatchlist('stock', data.id);
      setWatched(wc);
    } catch {
      message.error('股票数据不存在，请先采集');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchStock(); }, [code]);

  const handleToggleWatch = async () => {
    if (!stock) return;
    try {
      if (watched.watched && watched.id) {
        await removeFromWatchlist(watched.id);
        setWatched({ watched: false, id: null });
        message.success('已取消关注');
      } else {
        const res = await addToWatchlist('stock', stock.id);
        setWatched({ watched: true, id: res.id });
        message.success('已添加关注');
      }
    } catch {
      message.error('操作失败');
    }
  };

  const handleCollect = async () => {
    if (!code) return;
    setCollecting(true);
    try {
      const res = await collectStockData(code);
      message.success(res.message);
      await collectReports(code);
      fetchStock();
    } catch {
      message.error('采集失败');
    } finally {
      setCollecting(false);
    }
  };

  const handleAI = async () => {
    if (!code) return;
    setAiLoading(true);
    try {
      const res = await analyzeStock(code);
      setAiAnalysis(res.analysis);
    } catch {
      message.error('AI 分析失败，请检查模型设置');
    } finally {
      setAiLoading(false);
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

  if (!stock) {
    return (
      <div style={{ padding: 40, textAlign: 'center' }}>
        <Empty description={`未找到 ${code} 的数据`}>
          <Button type="primary" loading={collecting} onClick={handleCollect}>
            采集数据
          </Button>
        </Empty>
      </div>
    );
  }

  const chartOption = {
    title: { text: '财务指标趋势', left: 'center', textStyle: { fontSize: 14 } },
    tooltip: { trigger: 'axis' },
    legend: { bottom: 0, data: ['ROE', '毛利率', '净利率'] },
    grid: { left: 50, right: 20, top: 40, bottom: 40 },
    xAxis: {
      type: 'category' as const,
      data: stock.financial_data.slice(-10).map(d => d.period?.substring(0, 10) || ''),
    },
    yAxis: { type: 'value' as const, axisLabel: { formatter: '{value}%' } },
    series: [
      {
        name: 'ROE', type: 'line', data: stock.financial_data.slice(-10).map(d => d.roe),
        smooth: true, itemStyle: { color: '#1890ff' },
      },
      {
        name: '毛利率', type: 'line', data: stock.financial_data.slice(-10).map(d => d.gross_margin),
        smooth: true, itemStyle: { color: '#52c41a' },
      },
      {
        name: '净利率', type: 'line', data: stock.financial_data.slice(-10).map(d => d.net_margin),
        smooth: true, itemStyle: { color: '#faad14' },
      },
    ],
  };

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
    <div style={{ padding: '24px', maxWidth: 1100, margin: '0 auto' }}>
      <div style={{ marginBottom: 16 }}>
        <Link to="/"><ArrowLeftOutlined /> 返回首页</Link>
      </div>

      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Card>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <Title level={3} style={{ margin: 0 }}>{stock.name || stock.code}</Title>
                <Text type="secondary">{stock.code}</Text>
              </div>
              <div style={{ display: 'flex', gap: 8 }}>
                <Button
                  icon={watched.watched ? <StarFilled /> : <StarOutlined />}
                  onClick={handleToggleWatch}
                  style={{ color: watched.watched ? '#faad14' : undefined }}
                >
                  {watched.watched ? '已关注' : '关注'}
                </Button>
                <Button type="primary" icon={<RobotOutlined />} loading={aiLoading} onClick={handleAI}>
                  AI 投资分析
                </Button>
              </div>
            </div>
          </Card>
        </Col>

        {stock.financial_data.length > 0 && (
          <Col span={24}>
            <Card title="财务数据">
              <ReactECharts option={chartOption} style={{ height: 300 }} />
            </Card>
          </Col>
        )}

        <Col span={24}>
          <Card
            title={<><FileTextOutlined /> 研究报告</>}
            extra={<Button size="small" loading={collecting} onClick={handleCollect}>刷新数据</Button>}
          >
            {stock.reports.length > 0 ? (
              <Table dataSource={stock.reports} columns={reportColumns} rowKey="id" size="small" pagination={{ pageSize: 5 }} />
            ) : (
              <Empty description="暂无研报，点击刷新数据采集" />
            )}
          </Card>
        </Col>

        {aiAnalysis && (
          <Col span={24}>
            <Card title={<><RobotOutlined /> AI 分析结果</>}>
              <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.8 }}>
                {aiAnalysis.split('\n').map((line, i) => {
                  if (line.startsWith('### ')) return <Title key={i} level={5} style={{ marginTop: 16 }}>{line.replace('### ', '')}</Title>;
                  if (line.startsWith('**') && line.endsWith('**')) return <Text key={i} strong style={{ display: 'block', marginTop: 8 }}>{line.replace(/\*\*/g, '')}</Text>;
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
