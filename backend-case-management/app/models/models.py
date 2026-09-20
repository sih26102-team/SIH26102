from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base

class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    role = Column(String)
    district_id = Column(Integer, nullable=True)

class Project(Base):
    __tablename__ = 'projects'
    __table_args__ = {'extend_existing': True}
    project_id = Column(String, primary_key=True, index=True)
    district_id = Column(Integer)

class Case(Base):
    __tablename__ = 'cases'
    __table_args__ = {'extend_existing': True}
    case_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(String, ForeignKey('projects.project_id'))
    created_by = Column(Integer, ForeignKey('users.id'))
    assigned_officer = Column(Integer, ForeignKey('users.id'), nullable=True)
    status = Column(String, default='REQUESTED')
    resolution = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    project = relationship('Project')
    inspections = relationship('Inspection', back_populates='case')

class Inspection(Base):
    __tablename__ = 'inspections'
    __table_args__ = {'extend_existing': True}
    inspection_id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey('cases.case_id'))
    officer_id = Column(Integer, ForeignKey('users.id'))
    status = Column(String, default='ASSIGNED')
    gps_lat = Column(Float, nullable=True)
    gps_lon = Column(Float, nullable=True)
    physical_progress_pct = Column(Float, nullable=True)
    officer_observations = Column(Text, nullable=True)
    checklist_results = Column(JSON, nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    
    case = relationship('Case', back_populates='inspections')
    evidence = relationship('Evidence', back_populates='inspection')

class Evidence(Base):
    __tablename__ = 'evidence'
    __table_args__ = {'extend_existing': True}
    evidence_id = Column(Integer, primary_key=True, autoincrement=True)
    inspection_id = Column(Integer, ForeignKey('inspections.inspection_id'))
    file_path = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    inspection = relationship('Inspection', back_populates='evidence')

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    __table_args__ = {'extend_existing': True}
    log_id = Column(Integer, primary_key=True, autoincrement=True)
    actor_user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    action = Column(String)
    entity_type = Column(String)
    entity_id = Column(String)
    metadata_json = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
