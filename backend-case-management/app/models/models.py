from sqlalchemy import Column, Integer,Float, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.database import Base 


class User(Base):
    __tablename__ = "users"


    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(String(50), default="user", nullable=False)
    password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    cases = relationship("Case",back_populates = "assigned_officer")

class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer,primary_key=True,index=True)
    title = Column(String(200),nullable=False)
    description = Column(Text, nullable = True)
    status = Column(String(50),default = "OPEN",nullable=False)

    flagged_work_id = Column(String(100),nullable = False,index = True)
    risk_score = Column(Float,default = 0.0,nullable = False) 
    risk_level = Column(String(20), default="MEDIUM")     
    flagged_reasons = Column(Text, nullable=True)   
    recommended_action = Column(String(255), nullable = True)       

    investigator_notes = Column(Text, nullable=True)       
    resolution = Column(String(100), nullable=True)        

    assigned_to_id = Column(Integer,ForeignKey("users.id", ondelete = "SET NULL"),nullable = True)
    created_at = Column(DateTime(timezone = True), server_default = func.now(),nullable = False)

    assigned_officer = relationship("User", back_populates = "cases")


class CaseAuditLog(Base):
    __tablename__ = "case_audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    action = Column(String(50), nullable=False)       # CREATED, STATUS_CHANGED, ARCHIVED, UPDATED
    old_value = Column(String(100), nullable=True)
    new_value = Column(String(100), nullable=True)
    performed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    