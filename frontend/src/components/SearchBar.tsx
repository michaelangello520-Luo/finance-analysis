import { useState, useRef, useCallback } from 'react';
import { Input, AutoComplete } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router';
import { searchStock, type StockItem, type IndustryItem } from '../services/api';

interface SearchOption {
  value: string;
  label: React.ReactNode;
  type: 'stock' | 'industry';
  id: number | string;
}

export default function SearchBar() {
  const [options, setOptions] = useState<SearchOption[]>([]);
  const navigate = useNavigate();
  const timerRef = useRef<ReturnType<typeof setTimeout>>();

  const handleSearch = useCallback((query: string) => {
    if (timerRef.current) clearTimeout(timerRef.current);
    if (!query.trim()) {
      setOptions([]);
      return;
    }
    timerRef.current = setTimeout(async () => {
      try {
        const result = await searchStock(query);
        const stockOpts: SearchOption[] = result.stocks.map((s: StockItem) => ({
          value: `${s.name} (${s.code})`,
          label: (
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>{s.name}</span>
              <span style={{ color: '#999' }}>{s.code} · 股票</span>
            </div>
          ),
          type: 'stock',
          id: s.code,
        }));
        const industryOpts: SearchOption[] = result.industries.map((i: IndustryItem) => ({
          value: i.name,
          label: (
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>{i.name}</span>
              <span style={{ color: '#999' }}>{i.sector || ''} · 行业</span>
            </div>
          ),
          type: 'industry',
          id: i.id,
        }));
        const all = [...stockOpts, ...industryOpts];
        if (all.length === 0 && query.trim().length >= 2) {
          setOptions([{
            value: '_hint',
            label: <div style={{ color: '#999', padding: '4px 0' }}>输入6位股票代码即可自动采集数据</div>,
            type: 'stock',
            id: '',
          }]);
        } else {
          setOptions(all);
        }
      } catch {
        setOptions([]);
      }
    }, 300);
  }, []);

  const handleSelect = (_value: string, option: SearchOption) => {
    if (option.type === 'stock') {
      navigate(`/stock/${option.id}`);
    } else {
      navigate(`/industry/${option.id}`);
    }
  };

  return (
    <AutoComplete
      style={{ width: '100%', maxWidth: 600 }}
      options={options}
      onSearch={handleSearch}
      onSelect={handleSelect as any}
    >
      <Input.Search
        size="large"
        placeholder="输入股票代码采集数据（如 600519）或搜索行业"
        prefix={<SearchOutlined />}
        enterButton="采集"
      />
    </AutoComplete>
  );
}
