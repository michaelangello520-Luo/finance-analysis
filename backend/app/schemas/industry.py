from pydantic import BaseModel


class IndustryBase(BaseModel):
    name: str
    sector: str | None = None


class IndustryListItem(IndustryBase):
    id: int

    model_config = {"from_attributes": True}


class StockBrief(BaseModel):
    id: int
    code: str
    name: str

    model_config = {"from_attributes": True}


class IndustryDetail(IndustryBase):
    id: int
    description: str | None = None
    stocks: list[StockBrief] = []
    reports: list["ReportBrief"] = []

    model_config = {"from_attributes": True}


class ReportBrief(BaseModel):
    id: int
    title: str | None = None
    institution: str | None = None
    rating: str | None = None
    report_date: str | None = None

    model_config = {"from_attributes": True}


IndustryDetail.model_rebuild()
