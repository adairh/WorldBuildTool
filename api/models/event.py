from sqlalchemy import Column, Date, String

from ..db import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(String, primary_key=True)
    date = Column(Date)
    title = Column(String)
    description = Column(String)
    linkedPoiIds = Column(String)
    linkedPersonIds = Column(String)
