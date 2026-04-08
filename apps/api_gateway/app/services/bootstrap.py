from apps.api_gateway.app.db.base import Base
from apps.api_gateway.app.db.session import engine
from apps.api_gateway.app import models  # noqa: F401

def init_db() -> None:
    Base.metadata.create_all(bind=engine)
