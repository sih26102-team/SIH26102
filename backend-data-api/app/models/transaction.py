from sqlalchemy import Column, DECIMAL, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.database import Base


class Transaction(Base):
    
    __tablename__ = "transaction"

    transaction_id = Column(Integer, primary_key=True, index=True)
    work_id = Column(Integer, ForeignKey("work.work_id"), nullable=False)

    amount = Column(DECIMAL(14, 2), nullable=False)
    transaction_date = Column(Date, nullable=False)
    vendor_name = Column(String(255), nullable=True)
    payment_mode = Column(String(50), nullable=True)  
    status = Column(String(30), nullable=False, default="pending")
    
    work = relationship("Work", back_populates="transactions")
    anomalies = relationship("FlaggedAnomaly", back_populates="transaction")
