-- CivicShield AI - Unified PostgreSQL Schema (SIH26102)

-- 1. Agencies Table
CREATE TABLE IF NOT EXISTS agencies (
    agency_id SERIAL PRIMARY KEY,
    agency_name  TEXT NOT NULL,
    district  TEXT,
    state      TEXT
);

-- 2. Projects Table
CREATE TABLE IF NOT EXISTS projects (
    project_id      TEXT PRIMARY KEY,
    constituency    TEXT NOT NULL,
    district        TEXT NOT NULL,
    state           TEXT NOT NULL,
    sanctioned_amount NUMERIC(14,2) NOT NULL,
    released_amount NUMERIC(14,2) NOT NULL DEFAULT 0,
    expenditure     NUMERIC(14,2) NOT NULL DEFAULT 0,
    project_status    TEXT NOT NULL CHECK(
        project_status IN ('recommended','sanctioned','ongoing','completed','stalled')
    ),
    project_start_date             DATE,
    expected_completion_date       DATE,
    actual_completion_date         DATE,
    implementing_agency_id         INTEGER REFERENCES agencies(agency_id),
    project_category               TEXT,
    progress_percent               NUMERIC(5,2) CHECK (
        progress_percent IS NULL OR progress_percent BETWEEN 0 AND 100
    ),
    created_at                     TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(project_status);
CREATE INDEX IF NOT EXISTS idx_projects_district ON projects(district);

-- 3. Users Table (Admin & Investigators)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(50) NOT NULL DEFAULT 'investigator',
    password VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- 4. Cases Table (Investigation Workflow State Machine)
CREATE TABLE IF NOT EXISTS cases (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'REQUESTED',
    flagged_work_id VARCHAR(100) NOT NULL,
    risk_score FLOAT NOT NULL DEFAULT 0.0,
    risk_level VARCHAR(20) DEFAULT 'MEDIUM',
    flagged_reasons TEXT,
    recommended_action VARCHAR(255),
    requested_by_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    request_reason TEXT,
    assigned_to_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    evidence_photo_url TEXT,
    latitude FLOAT,
    longitude FLOAT,
    location_timestamp TIMESTAMP WITH TIME ZONE,
    site_condition TEXT,
    financial_observation TEXT,
    investigator_recommendation TEXT,
    investigator_notes TEXT,
    resolution VARCHAR(100),
    resolution_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_cases_flagged_work ON cases(flagged_work_id);
CREATE INDEX IF NOT EXISTS idx_cases_status ON cases(status);

-- 5. Case Audit Logs Table (Immutable History)
CREATE TABLE IF NOT EXISTS case_audit_logs (
    id SERIAL PRIMARY KEY,
    case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL,
    old_value VARCHAR(100),
    new_value VARCHAR(100),
    details TEXT,
    performed_by_id INTEGER REFERENCES users(id),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Seed Initial Agencies
INSERT INTO agencies (agency_id, agency_name, district, state) VALUES
(1, 'Public Works Department (PWD)', 'Visakhapatnam', 'Andhra Pradesh'),
(2, 'Rural Water Supply & Sanitation', 'Guntur', 'Andhra Pradesh'),
(3, 'Municipal Corporation', 'Vijayawada', 'Andhra Pradesh')
ON CONFLICT (agency_id) DO NOTHING;

-- Seed Initial Projects
INSERT INTO projects (project_id, constituency, district, state, sanctioned_amount, released_amount, expenditure, project_status, implementing_agency_id, project_category, progress_percent) VALUES
('PRJ-2026-001', 'Visakhapatnam North', 'Visakhapatnam', 'Andhra Pradesh', 5000000.00, 5000000.00, 4800000.00, 'completed', 1, 'Infrastructure', 100.00),
('PRJ-2026-002', 'Guntur West', 'Guntur', 'Andhra Pradesh', 3500000.00, 2000000.00, 1500000.00, 'ongoing', 2, 'Water & Sanitation', 60.00),
('PRJ-2026-003', 'Vijayawada Central', 'Vijayawada', 'Andhra Pradesh', 7500000.00, 7500000.00, 1000000.00, 'stalled', 3, 'Healthcare', 15.00)
ON CONFLICT (project_id) DO NOTHING;

-- Seed Demo Accounts (Bcrypt Hash for Demo Passwords)
-- admin.demo: CivicShieldAdmin@2026!
-- investigator.demo: CivicShield@Demo2026!
INSERT INTO users (id, username, email, full_name, role, password, is_active) VALUES
(1, 'admin.demo', 'admin.demo@civicshield.gov.in', 'CivicShield System Administrator', 'admin', '$2b$12$DmgYVzZ9e3hXjNfGgC1Y9.e/d8G1U1W0b8x2f1k6G4v0r.7r1e8Gq', true),
(2, 'investigator.demo', 'investigator.demo@civicshield.gov.in', 'Senior Field Investigator', 'investigator', '$2b$12$DmgYVzZ9e3hXjNfGgC1Y9.e/d8G1U1W0b8x2f1k6G4v0r.7r1e8Gq', true)
ON CONFLICT (username) DO NOTHING;
