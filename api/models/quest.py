from sqlalchemy import Column, JSON, String

from ..db import Base


class Quest(Base):
    __tablename__ = "quests"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    dialogueTree = Column(JSON)
    relatedEventIds = Column(JSON)
