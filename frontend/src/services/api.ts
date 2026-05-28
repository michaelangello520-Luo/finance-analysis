import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 120000,
});

// --- Types ---

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

export interface FinancialData {
  period: string;
  roe: number | null;
  gross_margin: number | null;
  net_margin: number | null;
  eps: number | null;
}

export interface ReportItem {
  id: number;
  title: string | null;
  institution: string | null;
  rating: string | null;
  report_date: string | null;
  content?: string | null;
}

export interface StockDetail {
  id: number;
  code: string;
  name: string;
  industry_id: number | null;
  financial_data: FinancialData[];
  reports: ReportItem[];
}

export interface StockBrief {
  id: number;
  code: string;
  name: string;
}

export interface IndustryDetail {
  id: number;
  name: string;
  sector: string | null;
  description: string | null;
  stocks: StockBrief[];
  reports: ReportItem[];
}

export interface LLMSettings {
  provider: string;
  model: string;
  available_providers: { name: string; model: string }[];
}

export interface AIAnalysis {
  stock_code?: string;
  stock_name?: string;
  report_id?: number;
  report_title?: string;
  analysis: string;
}

export interface WatchlistItem {
  id: number;
  target_type: string;
  target_id: number;
  name: string;
  code: string | null;
}

export interface WatchlistCheck {
  watched: boolean;
  id: number | null;
}

// --- API Functions ---

export async function searchStock(query: string): Promise<SearchResult> {
  const { data } = await api.get<SearchResult>('/search', { params: { q: query } });
  return data;
}

export async function getStockDetail(code: string): Promise<StockDetail> {
  const { data } = await api.get<StockDetail>(`/stocks/${code}`);
  return data;
}

export async function getIndustryDetail(id: number): Promise<IndustryDetail> {
  const { data } = await api.get<IndustryDetail>(`/industries/${id}`);
  return data;
}

export async function collectStockData(code: string): Promise<{ message: string }> {
  const { data } = await api.post('/data/stock', null, { params: { code }, timeout: 30000 });
  return data;
}

export async function collectIndustryData(name: string, sector?: string): Promise<{ message: string }> {
  const { data } = await api.post('/data/industry', null, { params: { name, sector: sector || '' }, timeout: 60000 });
  return data;
}

export async function collectReports(q: string): Promise<{ message: string }> {
  const { data } = await api.post('/data/report', null, { params: { q }, timeout: 30000 });
  return data;
}

export async function analyzeStock(stockCode: string): Promise<AIAnalysis> {
  const { data } = await api.post<AIAnalysis>('/ai/analyze-stock', { stock_code: stockCode });
  return data;
}

export async function analyzeReport(reportId: number): Promise<AIAnalysis> {
  const { data } = await api.post<AIAnalysis>('/ai/analyze-report', { report_id: reportId });
  return data;
}

export async function getLLMSettings(): Promise<LLMSettings> {
  const { data } = await api.get<LLMSettings>('/settings/llm');
  return data;
}

export async function updateLLMSettings(provider: string): Promise<LLMSettings & { message: string }> {
  const { data } = await api.put<LLMSettings & { message: string }>('/settings/llm', { provider });
  return data;
}

export async function getWatchlist(): Promise<WatchlistItem[]> {
  const { data } = await api.get<WatchlistItem[]>('/watchlist');
  return data;
}

export async function addToWatchlist(targetType: string, targetId: number): Promise<{ id: number; message: string }> {
  const { data } = await api.post('/watchlist', { target_type: targetType, target_id: targetId });
  return data;
}

export async function removeFromWatchlist(id: number): Promise<{ message: string }> {
  const { data } = await api.delete(`/watchlist/${id}`);
  return data;
}

export async function checkWatchlist(targetType: string, targetId: number): Promise<WatchlistCheck> {
  const { data } = await api.get<WatchlistCheck>('/watchlist/check', { params: { target_type: targetType, target_id: targetId } });
  return data;
}
