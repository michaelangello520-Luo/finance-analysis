from sqlalchemy import String, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Industry(Base):
    __tablename__ = "industries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    sector: Mapped[str | None] = mapped_column(String(50), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    stocks = relationship("Stock", back_populates="industry")
    reports = relationship("ResearchReport", back_populates="industry", lazy="selectin")
    upstream_relations = relationship(
        "IndustryRelation", foreign_keys="IndustryRelation.from_industry_id",
        back_populates="from_industry", lazy="selectin",
    )
    downstream_relations = relationship(
        "IndustryRelation", foreign_keys="IndustryRelation.to_industry_id",
        back_populates="to_industry", lazy="selectin",
    )


class IndustryRelation(Base):
    __tablename__ = "industry_relations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    from_industry_id: Mapped[int] = mapped_column(Integer, ForeignKey("industries.id"), nullable=False)
    to_industry_id: Mapped[int] = mapped_column(Integer, ForeignKey("industries.id"), nullable=False)
    relation_type: Mapped[str] = mapped_column(String(20), nullable=False)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)

    from_industry = relationship("Industry", foreign_keys=[from_industry_id], back_populates="upstream_relations")
    to_industry = relationship("Industry", foreign_keys=[to_industry_id], back_populates="downstream_relations")


class StockIndustry(Base):
    __tablename__ = "stock_industry"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    stock_id: Mapped[int] = mapped_column(Integer, ForeignKey("stocks.id"), nullable=False)
    industry_id: Mapped[int] = mapped_column(Integer, ForeignKey("industries.id"), nullable=False)
