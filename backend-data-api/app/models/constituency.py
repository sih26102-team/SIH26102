from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.database import Base


class Constituency(Base):
    __tablename__ = "constituency"

    constituency_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    state = Column(String(100), nullable=False)
    mp_id = Column(Integer, ForeignKey("mp.mp_id"), nullable=True)

    mp = relationship("MP", back_populates="constituencies")
    works = relationship("Work", back_populates="constituency")
