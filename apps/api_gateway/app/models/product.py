from datetime import datetime
from sqlalchemy import String, JSON, DateTime, Numeric, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from apps.api_gateway.app.db.base import Base

class ProductMaster(Base):
    __tablename__ = "products_master"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sku: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    title_master: Mapped[str] = mapped_column(String(255))
    description_master: Mapped[str] = mapped_column(Text)
    specs_json: Mapped[dict] = mapped_column(JSON, default=dict)
    features_json: Mapped[dict] = mapped_column(JSON, default=dict)
    price_base: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ProductChannelVersion(Base):
    __tablename__ = "product_channel_versions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_master_id: Mapped[int] = mapped_column(ForeignKey("products_master.id"), index=True)
    channel: Mapped[str] = mapped_column(String(50), index=True)
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    tags_json: Mapped[dict] = mapped_column(JSON, default=dict)
    seo_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    seo_description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
