from pydantic import BaseModel


class IndustryBase(BaseModel):
    name: str
    sector: str | None = None


class IndustryListItem(IndustryBase):
    id: int

    model_config = {"from_attributes": True}
