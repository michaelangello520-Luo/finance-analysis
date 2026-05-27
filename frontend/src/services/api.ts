import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
});

export interface StockItem {
  id: number;
  code: string;
  name: string;
  industry_id: number | null;
}

export interface IndustryItem {
  id: number;
  name: string;
  sector: string | null;
}

export interface SearchResult {
  stocks: StockItem[];
  industries: IndustryItem[];
}

export async function searchStock(query: string): Promise<SearchResult> {
  const { data } = await api.get<SearchResult>('/search', { params: { q: query } });
  return data;
}
