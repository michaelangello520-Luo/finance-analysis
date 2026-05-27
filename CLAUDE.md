# A 股长期投资看板 - 项目规则

## 技术栈

- **后端**: Python 3.10 (D:/python310/python.exe) + FastAPI + SQLAlchemy 2.0 (async) + SQLite + aiosqlite
- **前端**: React 18 + TypeScript + Vite + Ant Design 5 + React Router v7 + ECharts
- **LLM**: DeepSeek API (Phase 3 接入)
- **定时任务**: APScheduler
- **数据源**: 东方财富妙想 API (研报主源) + AKShare (财务数据) + Tushare (备用)

## 模块结构 (Phase 1 目标)

```
finance-analysis/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI 入口
│   │   ├── models.py        # SQLAlchemy 模型
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── database.py      # DB 连接配置
│   │   └── routers/         # API 路由
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/           # 页面组件
│   │   ├── components/      # 通用组件
│   │   ├── services/        # API 调用层
│   │   └── App.tsx
│   └── package.json
├── docs/                    # 设计文档
└── prototype.html           # UI 原型 (已完成)
```

## 数据库设计

7 张表: stocks, industries, watchlist, stock_industry, financial_data, research_reports, industry_relations

详细设计见: docs/superpowers/specs/2026-05-27-a-share-investment-dashboard-design.md

## 代码规范

- 后端: async/await 全异步, Pydantic v2 做数据校验, 路由按功能拆分到 routers/
- 前端: 函数组件 + hooks, TypeScript strict, Ant Design 5 组件库, ECharts 图表
- API: RESTful, 统一 Response 格式, 错误码规范
- 命名: 后端 snake_case, 前端 camelCase, 文件 kebab-case

## 设计文档

- 设计规格书: docs/superpowers/specs/2026-05-27-a-share-investment-dashboard-design.md
- Phase 1 实施计划: docs/superpowers/plans/2026-05-27-phase1-scaffold.md

## 高风险规则

- 东方财富 API 调用需要 em_api_key，不可硬编码，走环境变量
- 研报数据仅供分析参考，所有用户可见处必须带免责声明
- 数据库使用 SQLite，注意并发写入限制
