from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..db import Base


class Person(Base):
    __tablename__ = "persons"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    birthYear = Column(Integer)
    deathYear = Column(Integer, nullable=True)
    sex = Column(String)
    profession = Column(String, nullable=True)
    householdId = Column(String, ForeignKey("households.id"))
    homePoiId = Column(String, ForeignKey("pois.id"))

    household = relationship("Household", back_populates="members")
