-- CivicShield AI - Unified PostgreSQL Schema (SIH26102)

CREATE TABLE IF NOT EXISTS states (
    state_id SERIAL PRIMARY KEY,
    state_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS districts (
    district_id SERIAL PRIMARY KEY,
    district_name TEXT NOT NULL,
    state_id INTEGER NOT NULL REFERENCES states(state_id) ON DELETE CASCADE,
    UNIQUE (district_name, state_id)
);

CREATE TABLE IF NOT EXISTS constituencies (
    constituency_id SERIAL PRIMARY KEY,
    constituency_name TEXT NOT NULL,
    district_id INTEGER NOT NULL REFERENCES districts(district_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS mps (
    mp_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    constituency_id INTEGER REFERENCES constituencies(constituency_id),
    state_id INTEGER REFERENCES states(state_id),
    parliamentary_house TEXT,
    active_period TEXT
);

CREATE TABLE IF NOT EXISTS agencies (
    agency_id SERIAL PRIMARY KEY,
    agency_name TEXT NOT NULL,
    agency_type TEXT,
    district_id INTEGER REFERENCES districts(district_id),
    status TEXT DEFAULT 'ACTIVE'
);

CREATE TABLE IF NOT EXISTS projects (
    project_id TEXT PRIMARY KEY,
    project_title TEXT NOT NULL,
    description TEXT,
    mp_id INTEGER REFERENCES mps(mp_id),
    constituency_id INTEGER REFERENCES constituencies(constituency_id),
    state_id INTEGER REFERENCES states(state_id),
    district_id INTEGER REFERENCES districts(district_id),
    agency_id INTEGER REFERENCES agencies(agency_id),
    category TEXT,
    sanctioned_amount NUMERIC(14,2) NOT NULL DEFAULT 0,
    cost_estimate NUMERIC(14,2) DEFAULT 0,
    released_amount NUMERIC(14,2) NOT NULL DEFAULT 0,
    expenditure NUMERIC(14,2) NOT NULL DEFAULT 0,
    project_status TEXT NOT NULL,
    sanction_date DATE,
    start_date DATE,
    expected_completion_date DATE,
    actual_completion_date DATE,
    progress_percentage NUMERIC(5,2) DEFAULT 0,
    latitude FLOAT,
    longitude FLOAT,
    data_source TEXT DEFAULT 'PROTOTYPE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE IF NOT EXISTS expenditures (
    expenditure_id SERIAL PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
    transaction_ref TEXT,
    amount NUMERIC(14,2) NOT NULL,
    date DATE NOT NULL,
    expenditure_type TEXT,
    status TEXT,
    source TEXT
);

CREATE TABLE IF NOT EXISTS risk_results (
    risk_id SERIAL PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
    risk_score FLOAT NOT NULL,
    risk_level TEXT NOT NULL,
    model_version TEXT,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    UNIQUE(project_id)
);

CREATE TABLE IF NOT EXISTS risk_signals (
    signal_id SERIAL PRIMARY KEY,
    risk_id INTEGER NOT NULL REFERENCES risk_results(risk_id) ON DELETE CASCADE,
    signal_type TEXT NOT NULL,
    signal_value TEXT,
    explanation TEXT,
    severity TEXT
);

-- Users / Authentication
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(50) NOT NULL CHECK(role IN ('MINISTRY', 'STATE_NODAL_AUTHORITY', 'DISTRICT_AUTHORITY', 'INSPECTION_OFFICER')),
    password VARCHAR(255) NOT NULL,
    state_id INTEGER REFERENCES states(state_id),
    district_id INTEGER REFERENCES districts(district_id),
    designation TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE IF NOT EXISTS cases (
    case_id SERIAL PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(project_id),
    created_by INTEGER REFERENCES users(id),
    assigned_officer INTEGER REFERENCES users(id),
    status VARCHAR(50) NOT NULL DEFAULT 'REQUESTED',
    resolution TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE IF NOT EXISTS inspection_requests (
    request_id SERIAL PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(project_id),
    requested_by INTEGER REFERENCES users(id),
    requested_officer INTEGER REFERENCES users(id),
    status TEXT DEFAULT 'REQUESTED',
    request_reason TEXT,
    requested_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    reviewed_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS inspections (
    inspection_id SERIAL PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(project_id),
    officer_id INTEGER NOT NULL REFERENCES users(id),
    inspection_date TIMESTAMP WITH TIME ZONE DEFAULT now(),
    latitude FLOAT,
    longitude FLOAT,
    physical_progress_observed NUMERIC(5,2),
    site_condition TEXT,
    financial_observation TEXT,
    general_observation TEXT,
    recommendation TEXT,
    status TEXT DEFAULT 'SUBMITTED'
);

CREATE TABLE IF NOT EXISTS evidence (
    evidence_id SERIAL PRIMARY KEY,
    inspection_id INTEGER NOT NULL REFERENCES inspections(inspection_id) ON DELETE CASCADE,
    file_reference TEXT,
    evidence_type TEXT,
    latitude FLOAT,
    longitude FLOAT,
    metadata TEXT,
    captured_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE IF NOT EXISTS audit_logs (
    audit_id SERIAL PRIMARY KEY,
    actor_user_id INTEGER REFERENCES users(id),
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    metadata TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Indices
CREATE INDEX idx_projects_state ON projects(state_id);
CREATE INDEX idx_projects_district ON projects(district_id);
CREATE INDEX idx_projects_status ON projects(project_status);
CREATE INDEX idx_cases_project ON cases(project_id);
CREATE INDEX idx_cases_officer ON cases(assigned_officer);
CREATE INDEX idx_inspections_project ON inspections(project_id);

-- We won't seed everything here. We will use a python script (data-pipeline) to seed synthetic data.
-- We will just seed the Admin user for now.
INSERT INTO states (state_id, state_name) VALUES (1, 'Andhra Pradesh') ON CONFLICT DO NOTHING;
INSERT INTO districts (district_id, district_name, state_id) VALUES (1, 'Visakhapatnam', 1) ON CONFLICT DO NOTHING;

-- Seed Admin User (Ministry)
-- password: CivicShieldAdmin@2026!
INSERT INTO users (id, username, email, full_name, role, password, is_active) VALUES
(1, 'admin.demo', 'admin@civicshield.gov.in', 'CivicShield Admin', 'MINISTRY', '$2b$12$DmgYVzZ9e3hXjNfGgC1Y9.e/d8G1U1W0b8x2f1k6G4v0r.7r1e8Gq', true)
ON CONFLICT (username) DO NOTHING;
