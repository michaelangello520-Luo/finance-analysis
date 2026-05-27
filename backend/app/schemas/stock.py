from pydantic import BaseModel


class StockBase(BaseModel):
    code: str
    name: str


class StockListItem(StockBase):
    id: int
    industry_id: int | None = None

    model_config = {"from_attributes": True}
