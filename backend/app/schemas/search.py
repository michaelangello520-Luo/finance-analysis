from pydantic import BaseModel

from app.schemas.stock import StockListItem
from app.schemas.industry import IndustryListItem


class SearchResult(BaseModel):
    stocks: list[StockListItem] = []
    industries: list[IndustryListItem] = []
