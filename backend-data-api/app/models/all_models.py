from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric, Date, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.database import Base

class State(Base):
    __tablename__ = "states"
    state_id = Column(Integer, primary_key=True, index=True) # CONFIRMED_PUBLIC
    state_name = Column(Text, nullable=False, unique=True)
    districts = relationship("District", back_populates="state")

class District(Base):
    __tablename__ = "districts"
    district_id = Column(Integer, primary_key=True, index=True) # CONFIRMED_PUBLIC
    district_name = Column(Text, nullable=False)
    state_id = Column(Integer, ForeignKey("states.state_id", ondelete="CASCADE"), nullable=False)
    state = relationship("State", back_populates="districts")
    constituencies = relationship("Constituency", back_populates="district")

class Constituency(Base):
    __tablename__ = "constituencies"
    constituency_id = Column(Integer, primary_key=True, index=True) # CONFIRMED_PUBLIC
    constituency_name = Column(Text, nullable=False)
    district_id = Column(Integer, ForeignKey("districts.district_id", ondelete="CASCADE"), nullable=False)
    district = relationship("District", back_populates="constituencies")
    mps = relationship("MP", back_populates="constituency")

class MP(Base):
    __tablename__ = "mps"
    mp_id = Column(Integer, primary_key=True, index=True) # CONFIRMED_PUBLIC
    name = Column(Text, nullable=False)
    constituency_id = Column(Integer, ForeignKey("constituencies.constituency_id"))
    state_id = Column(Integer, ForeignKey("states.state_id"))
    parliamentary_house = Column(Text)
    active_period = Column(Text)
    constituency = relationship("Constituency", back_populates="mps")

class Agency(Base):
    __tablename__ = "agencies"
    agency_id = Column(Integer, primary_key=True, index=True) # PROPOSED_OPERATIONAL
    agency_name = Column(Text, nullable=False)
    agency_type = Column(Text)
    district_id = Column(Integer, ForeignKey("districts.district_id"))
    status = Column(Text, default="ACTIVE")

class Project(Base):
    __tablename__ = "projects"
    project_id = Column(Text, primary_key=True) # CONFIRMED_PUBLIC
    project_title = Column(Text, nullable=False) # CONFIRMED_PUBLIC
    description = Column(Text) # CONFIRMED_PUBLIC
    mp_id = Column(Integer, ForeignKey("mps.mp_id")) # CONFIRMED_PUBLIC
    constituency_id = Column(Integer, ForeignKey("constituencies.constituency_id"))
    state_id = Column(Integer, ForeignKey("states.state_id"))
    district_id = Column(Integer, ForeignKey("districts.district_id"))
    agency_id = Column(Integer, ForeignKey("agencies.agency_id"))
    category = Column(Text) # CONFIRMED_PUBLIC - 11 permitted sectors
    sanctioned_amount = Column(Numeric(14,2), default=0) # CONFIRMED_PUBLIC
    cost_estimate = Column(Numeric(14,2), default=0) # CONFIRMED_PUBLIC
    released_amount = Column(Numeric(14,2), default=0) # PROPOSED_OPERATIONAL
    expenditure = Column(Numeric(14,2), default=0) # CONFIRMED_PUBLIC
    project_status = Column(Text, nullable=False) # CONFIRMED_PUBLIC
    recommendation_date = Column(Date) # CONFIRMED_PUBLIC - to check 75 day rule
    sanction_date = Column(Date) # CONFIRMED_PUBLIC
    start_date = Column(Date) # PROPOSED_OPERATIONAL
    expected_completion_date = Column(Date) # PROPOSED_OPERATIONAL
    actual_completion_date = Column(Date) # CONFIRMED_PUBLIC
    progress_percentage = Column(Numeric(5,2), default=0) # PROPOSED_OPERATIONAL
    latitude = Column(Float) # PROPOSED_OPERATIONAL
    longitude = Column(Float) # PROPOSED_OPERATIONAL
    sc_st_area_flag = Column(Boolean, default=False) # CONFIRMED_PUBLIC - statutory quotas
    data_source = Column(Text, default='PROTOTYPE') # SYNTHETIC_DEMO
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Expenditure(Base):
    __tablename__ = "expenditures"
    expenditure_id = Column(Integer, primary_key=True, index=True) # PROPOSED_OPERATIONAL
    project_id = Column(Text, ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False)
    amount = Column(Numeric(14,2), nullable=False) # PROPOSED_OPERATIONAL
    status = Column(String, default='payment_authorization') # PROPOSED_OPERATIONAL - payment_authorization, payment_concurrence, payment_executed
    maker_id = Column(Integer, ForeignKey("users.id")) # PROPOSED_OPERATIONAL
    checker_id = Column(Integer, ForeignKey("users.id")) # PROPOSED_OPERATIONAL
    verifier_id = Column(Integer, ForeignKey("users.id")) # PROPOSED_OPERATIONAL
    date = Column(DateTime(timezone=True), server_default=func.now()) # PROPOSED_OPERATIONAL

class RiskResult(Base):
    __tablename__ = "risk_results"
    risk_id = Column(Integer, primary_key=True, index=True) # PROPOSED_OPERATIONAL
    project_id = Column(Text, ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False, unique=True)
    risk_score = Column(Float, nullable=False) # PROPOSED_OPERATIONAL
    risk_level = Column(Text, nullable=False) # PROPOSED_OPERATIONAL
    model_version = Column(Text) # PROPOSED_OPERATIONAL
    reasons = Column(Text) # JSON string array # PROPOSED_OPERATIONAL
    recommended_verification = Column(Text) # JSON string array # PROPOSED_OPERATIONAL
    generated_at = Column(DateTime(timezone=True), server_default=func.now())

class RiskSignal(Base):
    __tablename__ = "risk_signals"
    signal_id = Column(Integer, primary_key=True, index=True) # PROPOSED_OPERATIONAL
    risk_id = Column(Integer, ForeignKey("risk_results.risk_id", ondelete="CASCADE"), nullable=False)
    signal_type = Column(Text, nullable=False) # PROPOSED_OPERATIONAL
    signal_value = Column(Text) # PROPOSED_OPERATIONAL
    explanation = Column(Text) # PROPOSED_OPERATIONAL
    severity = Column(Text) # PROPOSED_OPERATIONAL

class SyntheticGroundTruth(Base):
    __tablename__ = "synthetic_ground_truth"
    id = Column(Integer, primary_key=True, index=True) # SYNTHETIC_DEMO
    project_id = Column(Text, ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False) # SYNTHETIC_DEMO
    injected_scenario = Column(Text, nullable=False) # SYNTHETIC_DEMO
    expected_detection = Column(Boolean, default=True) # SYNTHETIC_DEMO

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True) # PROPOSED_OPERATIONAL
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(100))
    role = Column(String(50), nullable=False)
    password = Column(String(255), nullable=False)
    state_id = Column(Integer, ForeignKey("states.state_id"))
    district_id = Column(Integer, ForeignKey("districts.district_id"))
    designation = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)
    is_first_login = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Case(Base):
    __tablename__ = 'cases'
    case_id = Column(Integer, primary_key=True, index=True, autoincrement=True) # PROPOSED_OPERATIONAL
    project_id = Column(String, ForeignKey('projects.project_id'))
    created_by = Column(Integer, ForeignKey('users.id'))
    assigned_officer = Column(Integer, ForeignKey('users.id'), nullable=True)
    status = Column(String, default='REQUESTED')
    resolution = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    project = relationship('Project')
    inspections = relationship('Inspection', back_populates='case')

class Inspection(Base):
    __tablename__ = 'inspections'
    inspection_id = Column(Integer, primary_key=True, autoincrement=True) # PROPOSED_OPERATIONAL
    case_id = Column(Integer, ForeignKey('cases.case_id'))
    officer_id = Column(Integer, ForeignKey('users.id'))
    status = Column(String, default='ASSIGNED')
    gps_lat = Column(Float, nullable=True)
    gps_lon = Column(Float, nullable=True)
    physical_progress_pct = Column(Float, nullable=True)
    officer_observations = Column(Text, nullable=True)
    checklist_results = Column(JSON, nullable=True)
    statutory_quota_flag = Column(String, nullable=True) # PROPOSED_OPERATIONAL - e.g., '10_PERCENT_DISTRICT'
    submitted_at = Column(DateTime, nullable=True)
    case = relationship('Case', back_populates='inspections')
    evidence = relationship('Evidence', back_populates='inspection')

class Evidence(Base):
    __tablename__ = 'evidence'
    evidence_id = Column(Integer, primary_key=True, autoincrement=True) # PROPOSED_OPERATIONAL
    inspection_id = Column(Integer, ForeignKey('inspections.inspection_id'))
    file_path = Column(String)
    uploaded_at = Column(DateTime, default=func.now())
    inspection = relationship('Inspection', back_populates='evidence')

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    log_id = Column(Integer, primary_key=True, autoincrement=True) # PROPOSED_OPERATIONAL
    actor_user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    action = Column(String)
    entity_type = Column(String)
    entity_id = Column(String)
    metadata_json = Column(String, nullable=True)
    timestamp = Column(DateTime, default=func.now())
