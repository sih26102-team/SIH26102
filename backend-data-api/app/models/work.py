from sqlalchemy import Column, DECIMAL, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.database import Base


class Work(Base):
    
    __tablename__ = "work"

    work_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=True)  
    recommended_amount = Column(DECIMAL(14, 2), nullable=False)
    financial_year = Column(String(9), nullable=False)  
    status = Column(String(30), nullable=False, default="recommended")
    

    constituency_id = Column(Integer, ForeignKey("constituency.constituency_id"), nullable=False)
    recommended_date = Column(Date, nullable=True)

    constituency = relationship("Constituency", back_populates="works")
    transactions = relationship("Transaction", back_populates="work")
