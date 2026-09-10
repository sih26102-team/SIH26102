from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(String(50), default="investigator", nullable=False)  # "admin" or "investigator"
    password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    assigned_cases = relationship("Case", foreign_keys="Case.assigned_to_id", back_populates="assigned_officer")
    requested_cases = relationship("Case", foreign_keys="Case.requested_by_id", back_populates="requester")


class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # State Machine Status:
    # REQUESTED, APPROVED, ASSIGNED, UNDER_INVESTIGATION, EVIDENCE_SUBMITTED, UNDER_REVIEW, RESOLVED, ESCALATED, REJECTED, ARCHIVED
    status = Column(String(50), default="REQUESTED", nullable=False)

    flagged_work_id = Column(String(100), nullable=False, index=True)
    risk_score = Column(Float, default=0.0, nullable=False)
    risk_level = Column(String(20), default="MEDIUM")
    flagged_reasons = Column(Text, nullable=True)
    recommended_action = Column(String(255), nullable=True)

    # Request & Assignment
    requested_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    request_reason = Column(Text, nullable=True)
    assigned_to_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Field Inspection & Geolocation Evidence
    evidence_photo_url = Column(Text, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    location_timestamp = Column(DateTime(timezone=True), nullable=True)
    site_condition = Column(Text, nullable=True)
    financial_observation = Column(Text, nullable=True)
    investigator_recommendation = Column(Text, nullable=True)
    investigator_notes = Column(Text, nullable=True)

    # Resolution & Closure
    resolution = Column(String(100), nullable=True)
    resolution_notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    assigned_officer = relationship("User", foreign_keys=[assigned_to_id], back_populates="assigned_cases")
    requester = relationship("User", foreign_keys=[requested_by_id], back_populates="requested_cases")
    audit_logs = relationship("CaseAuditLog", back_populates="case", cascade="all, delete-orphan")


class CaseAuditLog(Base):
    __tablename__ = "case_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    action = Column(String(50), nullable=False)  # REQUESTED, APPROVED, ASSIGNED, EVIDENCE_UPLOADED, STATUS_CHANGED, RESOLVED, REJECTED
    old_value = Column(String(100), nullable=True)
    new_value = Column(String(100), nullable=True)
    details = Column(Text, nullable=True)
    performed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    case = relationship("Case", back_populates="audit_logs")
    performer = relationship("User")