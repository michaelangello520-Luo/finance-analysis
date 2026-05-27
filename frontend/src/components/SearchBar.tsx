import { useState } from 'react';
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

  const handleSearch = async (query: string) => {
    if (!query.trim()) {
      setOptions([]);
      return;
    }
    try {
      const result = await searchStock(query);
      const stockOpts: SearchOption[] = result.stocks.map((s: StockItem) => ({
        value: `${s.name} (${s.code})`,
        label: (
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span>{s.name}</span>
            <span style={{ color: '#999' }}>{s.code} · 个股</span>
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
      setOptions([...stockOpts, ...industryOpts]);
    } catch {
      setOptions([]);
    }
  };

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
        placeholder="输入股票名称/代码 或 行业名称"
        prefix={<SearchOutlined />}
        enterButton="搜索"
      />
    </AutoComplete>
  );
}
