from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from apps.api_gateway.app.db.session import get_db
from apps.api_gateway.app.models.product import ProductMaster, ProductChannelVersion

router = APIRouter()

@router.get("/master")
def list_master_products(db: Session = Depends(get_db)):
    items = db.execute(select(ProductMaster)).scalars().all()
    return items

@router.get("/channels")
def list_channel_versions(db: Session = Depends(get_db)):
    items = db.execute(select(ProductChannelVersion)).scalars().all()
    return items
