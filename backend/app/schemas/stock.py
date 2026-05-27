from pydantic import BaseModel


class StockBase(BaseModel):
    code: str
    name: str


class StockListItem(StockBase):
    id: int
    industry_id: int | None = None

    model_config = {"from_attributes": True}


class FinancialDataOut(BaseModel):
    period: str
    roe: float | None = None
    gross_margin: float | None = None
    net_margin: float | None = None
    eps: float | None = None

    model_config = {"from_attributes": True}


class ReportOut(BaseModel):
    id: int
    title: str | None = None
    institution: str | None = None
    rating: str | None = None
    report_date: str | None = None
    content: str | None = None

    model_config = {"from_attributes": True}


class StockDetail(StockBase):
    id: int
    industry_id: int | None = None
    financial_data: list[FinancialDataOut] = []
    reports: list[ReportOut] = []

    model_config = {"from_attributes": True}
