import { useEffect, useState } from 'react';
import { Typography, Card, Row, Col, Button, Tag, Empty, Spin, message } from 'antd';
import { useNavigate } from 'react-router';
import { StarFilled, DeleteOutlined } from '@ant-design/icons';
import { getWatchlist, removeFromWatchlist } from '../services/api';
import type { WatchlistItem } from '../services/api';

const { Title, Text } = Typography;

export default function WatchlistPage() {
  const navigate = useNavigate();
  const [items, setItems] = useState<WatchlistItem[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchList = async () => {
    try {
      const data = await getWatchlist();
      setItems(data);
    } catch {
      message.error('获取关注列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchList(); }, []);

  const handleRemove = async (id: number) => {
    try {
      await removeFromWatchlist(id);
      message.success('已移除');
      fetchList();
    } catch {
      message.error('移除失败');
    }
  };

  if (loading) return <Spin style={{ display: 'block', margin: '100px auto' }} />;

  return (
    <div style={{ padding: 24, maxWidth: 900, margin: '0 auto' }}>
      <Title level={3}>关注列表</Title>

      {items.length === 0 ? (
        <Empty description="暂无关注，请先浏览个股或行业并添加关注" />
      ) : (
        <Row gutter={[16, 16]}>
          {items.map(item => (
            <Col xs={24} sm={12} md={8} key={item.id}>
              <Card
                size="small"
                hoverable
                onClick={() => {
                  if (item.target_type === 'stock' && item.code) {
                    navigate(`/stock/${item.code}`);
                  } else if (item.target_type === 'industry') {
                    navigate(`/industry/${item.target_id}`);
                  }
                }}
                extra={
                  <Button
                    type="text"
                    danger
                    size="small"
                    icon={<DeleteOutlined />}
                    onClick={(e) => { e.stopPropagation(); handleRemove(item.id); }}
                  />
                }
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <StarFilled style={{ color: '#faad14' }} />
                  <Text strong>{item.name}</Text>
                  {item.code && <Text type="secondary">{item.code}</Text>}
                </div>
                <div style={{ marginTop: 8 }}>
                  <Tag color={item.target_type === 'stock' ? 'blue' : 'green'}>
                    {item.target_type === 'stock' ? '个股' : '行业'}
                  </Tag>
                </div>
              </Card>
            </Col>
          ))}
        </Row>
      )}
    </div>
  );
}
