from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class FlaggedAnomaly(Base):
    
    __tablename__ = "flagged_anomaly"

    anomaly_id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transaction.transaction_id"), nullable=False)

    anomaly_type = Column(String(100), nullable=False)  
    score = Column(Float, nullable=False)  
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed = Column(String(20), nullable=False, default="unreviewed")  
    reviewed_by = Column(String(100), nullable=True)

    transaction = relationship("Transaction", back_populates="anomalies")
