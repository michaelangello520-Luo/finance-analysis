# A 股长期投资看板 - 设计文档

> 日期：2026-05-27
> 状态：已确认

---

## 1. 项目概述

一个面向 A 股市场的长期投资分析看板，支持个股和行业两个维度。用户输入股票或行业后，系统自动获取公开研报数据，通过 LLM 进行深度分析，以可视化看板形式展示关键财务数据和产业链信息，辅助投资决策。

### 核心价值

- 不是简单的财务数据展示，而是产业链深度分析（细分领域、上下游、成本结构、技术替代周期）
- 研报观点汇总与一致性判断
- 产业链联动：从上游跳到下游，形成完整分析链路

### 使用模式

- **按需查询**：输入股票/行业，当场获取分析结果
- **持续跟踪**：维护关注列表，定期自动更新数据和分析

---

## 2. 架构设计

### 方案：经典前后端分离 + 定时任务

```
React前端 <-> FastAPI后端 <-> SQLite
                  |
          APScheduler 定时任务
                  |
     数据采集模块(东方财富妙想/AKShare) + LLM分析模块(国内大模型)
```

### 项目结构

```
finance-analysis/
├── frontend/                # React + TypeScript
│   ├── src/
│   │   ├── pages/           # 页面：首页、个股详情、行业详情、关注列表
│   │   ├── components/      # 通用组件：图表、表格、搜索框
│   │   ├── services/        # API 调用层
│   │   └── App.tsx
│   └── package.json
│
├── backend/                 # FastAPI
│   ├── app/
│   │   ├── api/             # API 路由
│   │   ├── models/          # 数据库模型
│   │   ├── schemas/         # Pydantic 数据校验
│   │   ├── services/        # 业务逻辑
│   │   │   ├── collector/   # 数据采集（东方财富妙想/AKShare）
│   │   │   ├── analyzer/    # LLM 研报分析
│   │   │   └── scheduler/   # 定时任务
│   │   └── main.py
│   ├── requirements.txt
│   └── .env                 # API keys 等
│
├── data/                    # SQLite 数据库文件、原始数据缓存
├── docs/                    # 设计文档
└── docker-compose.yml       # 后续部署用
```

---

## 3. 数据流

```
用户输入"机器人行业"
       |
       v
+-- collector 采集模块 ------------------+
|  1. AKShare 获取行业成分股列表          |
|  2. AKShare 获取各股财务数据(季报/年报) |
|  3. 东方财富妙想 API 搜索研报全文       |
|  4. 原始数据存入 SQLite                |
+----------------------------------------+
       |
       v
+-- analyzer 分析模块 -------------------+
|  1. 研报文本切分 -> 送入国内大模型 API  |
|  2. 结构化提取：                       |
|     - 细分领域及分析                   |
|     - 上游行业 + 产业链关系            |
|     - 产品价格/生产成本                |
|     - 技术替代周期                     |
|     - 多空观点 + 一致性判断            |
|  3. 分析结果存入 SQLite                |
+----------------------------------------+
       |
       v
+-- API 展示层 --------------------------+
|  FastAPI 提供接口，前端按需查询展示     |
|  - 个股/行业概览                       |
|  - 产业链关系图                        |
|  - 行业内个股对比                      |
|  - 上游行业可点击跳转                  |
+----------------------------------------+
```

---

## 4. 数据源策略

| 数据源 | 职责 | 费用 |
|--------|------|------|
| 东方财富妙想 API（主） | 研报搜索与全文获取，支持自然语言查询 | 免费（有 API key） |
| AKShare（辅） | 行情数据、财务数据、行业成分股、研报摘要/评级 | 免费 |
| Tushare（备选） | 补充研报数据（需注册） | 免费额度够用 |
| 后续付费接口 | 研报全文深度数据（产品化阶段接入） | 待定 |

### 东方财富妙想 API（研报主数据源）

- 端点：`POST https://ai-saas.eastmoney.com/proxy/b/mcp/tool/searchNews`
- 认证：Header `em_api_key`
- 查询方式：自然语言，如"机器人行业研报"
- 返回字段：标题、日期、机构、评级、实体名称、研报全文内容
- 优势：研报内容完整（非摘要）、券商覆盖广、实时性好（当天研报可获取）
- API key 存储在 `.env` 中，不入 Git

### AKShare（财务/行情数据源）

- `stock_analyst_detail_em()` — 个股研报列表（标题、日期、评级、目标价）
- `stock_profit_forecast_em()` — 盈利预测数据
- `stock_rating_em()` — 机构评级数据
- `stock_financial_analysis_indicator()` — 财务分析指标
- `stock_board_industry_cons_em()` — 行业成分股

---

## 5. 数据库设计

SQLite，7 张核心表：

| 表 | 核心字段 | 说明 |
|---|---|---|
| `stocks` | code, name, industry_id | 个股基础信息，关联行业 |
| `industries` | name, sector, description | 行业信息 |
| `watchlist` | target_type, target_id, created_at | 关注列表，个股和行业都放这里 |
| `stock_industry` | stock_id, industry_id | 多对多，一个股可属多个细分行业 |
| `financial_data` | stock_id, period, revenue, profit, roe, pe, pb... | 按季度存储财务指标 |
| `research_reports` | target_type, target_id, source, content, analysis_result, analyzed_at | 研报原文 + LLM 分析结果（JSON） |
| `industry_relations` | from_industry_id, to_industry_id, relation_type(upstream/downstream), detail | 产业链关系，支持上下游跳转 |

### analysis_result JSON 结构

```json
{
  "sub_sectors": [
    {"name": "工业机器人", "analysis": "...", "key_players": ["埃斯顿", "汇川技术"]}
  ],
  "upstream": [
    {"industry": "减速器", "relation": "上游", "detail": "..."}
  ],
  "cost_structure": {"原材料": "40%", "人工": "20%"},
  "tech_substitution": {"cycle": "5-8年", "risk": "中等", "detail": "..."},
  "price_trend": "...",
  "bull_bear_consensus": {"bull": 7, "bear": 2, "neutral": 1}
}
```

---

## 6. API 设计

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/search` | 搜索股票/行业，返回候选列表 |
| GET | `/api/stocks/{code}` | 个股详情：基础信息 + 财务数据 + 研报分析 |
| GET | `/api/industries/{id}` | 行业详情：细分领域 + 产业链 + 研报分析 |
| GET | `/api/industries/{id}/comparison` | 行业内个股对比数据 |
| GET | `/api/watchlist` | 获取关注列表 |
| POST | `/api/watchlist` | 添加到关注列表 |
| DELETE | `/api/watchlist/{id}` | 从关注列表移除 |
| POST | `/api/analysis/trigger` | 手动触发一次采集+分析任务 |
| GET | `/api/analysis/status/{task_id}` | 查询分析任务进度 |

---

## 7. 前端页面设计

### 首页（搜索入口）

- 搜索框：输入股票名称/代码/行业名称，模糊匹配
- 关注列表卡片（快捷入口）
- 最近分析记录

### 个股详情页 (/stock/:code)

- 基础信息 + 核心财务指标卡片
- 财务数据趋势图（营收/利润/ROE 多季度折线图）
- 研报观点汇总（多空比例 + 关键观点列表）
- 所属行业链接（可跳转）

### 行业详情页 (/industry/:id)

- 行业概览
- 细分领域分析（卡片列表，每个领域独立展示）
- 产业链图谱（上游 <- 当前 -> 下游，可点击跳转）
- 成本结构图（饼图）
- 技术替代风险评估
- 产品价格趋势
- 行业内个股对比表格
- 研报观点汇总

### 关注列表页 (/watchlist)

- 关注的股票/行业卡片列表
- 每张卡片显示：最新分析时间、核心指标摘要
- 一键刷新：重新触发分析

---

## 8. 技术栈

| 层 | 技术 | 说明 |
|---|---|---|
| 前端 | React 18 + TypeScript + Vite | 构建工具用 Vite |
| UI 组件库 | Ant Design 5 | 数据看板场景契合 |
| 图表 | ECharts (echarts-for-react) | K线图、饼图、折线图、产业链关系图 |
| 后端 | FastAPI + Python 3.11+ | 异步高性能，自动生成 API 文档 |
| ORM | SQLAlchemy 2.0 | 异步支持好，类型安全 |
| 数据库 | SQLite + aiosqlite | 轻量异步访问 |
| 定时任务 | APScheduler | 简单够用，后续可换 Celery |
| 数据采集 | 东方财富妙想 API + AKShare | 妙想获取研报全文，AKShare 获取行情/财务数据 |
| LLM | 国内大模型 API（先接 DeepSeek） | 性价比高，中文能力强 |
| 部署 | 本地优先 + Docker 可部署架构 | 代码结构按可部署标准写 |

---

## 9. 开发阶段

### Phase 1 -- 基础骨架
- 前后端项目初始化
- 数据库建表
- 基础 API + 前端页面框架
- 搜索功能

### Phase 2 -- 数据采集
- AKShare 接入：获取个股财务数据、行业成分股
- 东方财富妙想 API 接入：研报搜索与全文获取
- 数据存入 SQLite

### Phase 3 -- AI 分析
- 接入国内大模型 API（DeepSeek）
- 研报分析 Prompt 设计与调优
- 结构化提取产业链、成本、技术替代等
- 分析结果存储

### Phase 4 -- 看板展示
- 个股详情页：财务图表 + 研报观点
- 行业详情页：细分领域 + 产业链图谱
- 行业对比表格
- 上下游跳转联动

### Phase 5 -- 关注列表与持续跟踪
- 关注列表增删改
- APScheduler 定时采集和分析
- 关注列表卡片展示

### Phase 6 -- 打磨与产品化
- 加载状态、错误处理
- Docker 部署配置
- 性能优化
