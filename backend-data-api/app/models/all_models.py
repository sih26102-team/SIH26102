from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.database import Base

class State(Base):
    __tablename__ = "states"
    state_id = Column(Integer, primary_key=True, index=True)
    state_name = Column(Text, nullable=False, unique=True)
    districts = relationship("District", back_populates="state")

class District(Base):
    __tablename__ = "districts"
    district_id = Column(Integer, primary_key=True, index=True)
    district_name = Column(Text, nullable=False)
    state_id = Column(Integer, ForeignKey("states.state_id", ondelete="CASCADE"), nullable=False)
    state = relationship("State", back_populates="districts")
    constituencies = relationship("Constituency", back_populates="district")

class Constituency(Base):
    __tablename__ = "constituencies"
    constituency_id = Column(Integer, primary_key=True, index=True)
    constituency_name = Column(Text, nullable=False)
    district_id = Column(Integer, ForeignKey("districts.district_id", ondelete="CASCADE"), nullable=False)
    district = relationship("District", back_populates="constituencies")
    mps = relationship("MP", back_populates="constituency")

class MP(Base):
    __tablename__ = "mps"
    mp_id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, nullable=False)
    constituency_id = Column(Integer, ForeignKey("constituencies.constituency_id"))
    state_id = Column(Integer, ForeignKey("states.state_id"))
    parliamentary_house = Column(Text)
    active_period = Column(Text)
    constituency = relationship("Constituency", back_populates="mps")

class Agency(Base):
    __tablename__ = "agencies"
    agency_id = Column(Integer, primary_key=True, index=True)
    agency_name = Column(Text, nullable=False)
    agency_type = Column(Text)
    district_id = Column(Integer, ForeignKey("districts.district_id"))
    status = Column(Text, default="ACTIVE")

class Project(Base):
    __tablename__ = "projects"
    project_id = Column(Text, primary_key=True)
    project_title = Column(Text, nullable=False)
    description = Column(Text)
    mp_id = Column(Integer, ForeignKey("mps.mp_id"))
    constituency_id = Column(Integer, ForeignKey("constituencies.constituency_id"))
    state_id = Column(Integer, ForeignKey("states.state_id"))
    district_id = Column(Integer, ForeignKey("districts.district_id"))
    agency_id = Column(Integer, ForeignKey("agencies.agency_id"))
    category = Column(Text)
    sanctioned_amount = Column(Numeric(14,2), default=0)
    cost_estimate = Column(Numeric(14,2), default=0)
    released_amount = Column(Numeric(14,2), default=0)
    expenditure = Column(Numeric(14,2), default=0)
    project_status = Column(Text, nullable=False)
    sanction_date = Column(Date)
    start_date = Column(Date)
    expected_completion_date = Column(Date)
    actual_completion_date = Column(Date)
    progress_percentage = Column(Numeric(5,2), default=0)
    latitude = Column(Float)
    longitude = Column(Float)
    data_source = Column(Text, default='PROTOTYPE')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Expenditure(Base):
    __tablename__ = "expenditures"
    expenditure_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Text, ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False)
class RiskResult(Base):
    __tablename__ = "risk_results"
    risk_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Text, ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False, unique=True)
    risk_score = Column(Float, nullable=False)
    risk_level = Column(Text, nullable=False)
    model_version = Column(Text)
    reasons = Column(Text) # JSON string array
    recommended_verification = Column(Text) # JSON string array
    generated_at = Column(DateTime(timezone=True), server_default=func.now())

class RiskSignal(Base):
    __tablename__ = "risk_signals"
    signal_id = Column(Integer, primary_key=True, index=True)
    risk_id = Column(Integer, ForeignKey("risk_results.risk_id", ondelete="CASCADE"), nullable=False)
    signal_type = Column(Text, nullable=False)
    signal_value = Column(Text)
    explanation = Column(Text)
    severity = Column(Text)


# Auth / Case Management 
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
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


