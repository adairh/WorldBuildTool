from sqlalchemy import Column, JSON, String

from ..db import Base


class POI(Base):
    __tablename__ = "pois"

    id = Column(String, primary_key=True)
    name = Column(String)
    geometry = Column(JSON)
    layers = Column(JSON)
    tags = Column(JSON)
    description = Column(String)
