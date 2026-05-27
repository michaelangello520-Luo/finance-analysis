import { useEffect, useState } from 'react';
import { Card, Radio, Flex, Typography, message, Spin } from 'antd';
import { SettingOutlined } from '@ant-design/icons';
import { getLLMSettings, updateLLMSettings } from '../services/api';
import type { LLMSettings } from '../services/api';

const { Title, Text } = Typography;

export default function SettingsPage() {
  const [settings, setSettings] = useState<LLMSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [switching, setSwitching] = useState(false);

  const fetchSettings = async () => {
    try {
      const data = await getLLMSettings();
      setSettings(data);
    } catch {
      message.error('获取设置失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchSettings(); }, []);

  const handleSwitch = async (provider: string) => {
    setSwitching(true);
    try {
      await updateLLMSettings(provider);
      const data = await getLLMSettings();
      setSettings(data);
      message.success('切换成功');
    } catch {
      message.error('切换失败');
    } finally {
      setSwitching(false);
    }
  };

  if (loading) return <Spin style={{ display: 'block', margin: '100px auto' }} />;

  return (
    <div style={{ maxWidth: 600, margin: '40px auto', padding: '0 24px' }}>
      <Card>
        <Title level={4}><SettingOutlined /> AI 模型设置</Title>
        <Text type="secondary" style={{ display: 'block', marginBottom: 24 }}>
          选择用于研报分析和投资建议的大语言模型
        </Text>

        <Radio.Group
          value={settings?.provider}
          onChange={(e) => handleSwitch(e.target.value)}
          disabled={switching}
        >
          <Flex vertical style={{ width: '100%' }}>
            {settings?.available_providers.map((p) => (
              <Radio key={p.name} value={p.name} style={{ fontSize: 16 }}>
                <Flex>
                  <Text strong>{p.name === 'deepseek' ? 'DeepSeek' : '智谱 GLM'}</Text>
                  <Text type="secondary">({p.model})</Text>
                  {settings.provider === p.name && (
                    <Text type="success">- 当前使用</Text>
                  )}
                </Flex>
              </Radio>
            ))}
          </Flex>
        </Radio.Group>

        {settings && (
          <div style={{ marginTop: 24, padding: '12px 16px', background: '#f6f8fa', borderRadius: 8 }}>
            <Text type="secondary">
              当前模型: <Text strong>{settings.model}</Text>
            </Text>
          </div>
        )}
      </Card>
    </div>
  );
}
