from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Stock(Base):
    __tablename__ = "stocks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    industry_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("industries.id"), nullable=True)

    industry = relationship("Industry", back_populates="stocks")
    financial_data = relationship("FinancialData", back_populates="stock", lazy="selectin")
    reports = relationship("ResearchReport", back_populates="stock", lazy="selectin")
