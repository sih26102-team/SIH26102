from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database.database import Base


class MP(Base):
    __tablename__ = "mp"

    mp_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    party = Column(String(100), nullable=True)
    house = Column(String(20), nullable=True) 
    state = Column(String(100), nullable=True)

    constituencies = relationship("Constituency", back_populates="mp")
