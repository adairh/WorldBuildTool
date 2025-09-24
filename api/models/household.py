from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from ..db import Base


class Household(Base):
    __tablename__ = "households"

    id = Column(String, primary_key=True)
    parcelId = Column(String)
    houseType = Column(String)
    status = Column(String, default="occupied")

    members = relationship("Person", back_populates="household")
