CREATE TABLE IF NOT EXISTS agencies (
    agency_id SERIAL PRIMARY KEY,
    agency_name  TEXT NOT NULL,
    district  TEXT,
    state      TEXT
);

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
    expected_completion_datw       DATE,
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

-- Initial seed data for MPLADS prototype
INSERT INTO agencies (agency_id, agency_name, district, state) VALUES
(1, 'Public Works Department (PWD)', 'Visakhapatnam', 'Andhra Pradesh'),
(2, 'Rural Water Supply & Sanitation', 'Guntur', 'Andhra Pradesh'),
(3, 'Municipal Corporation', 'Vijayawada', 'Andhra Pradesh')
ON CONFLICT (agency_id) DO NOTHING;

INSERT INTO projects (project_id, constituency, district, state, sanctioned_amount, released_amount, expenditure, project_status, implementing_agency_id, project_category, progress_percent) VALUES
('PRJ-2026-001', 'Visakhapatnam North', 'Visakhapatnam', 'Andhra Pradesh', 5000000.00, 5000000.00, 4800000.00, 'completed', 1, 'Infrastructure', 100.00),
('PRJ-2026-002', 'Guntur West', 'Guntur', 'Andhra Pradesh', 3500000.00, 2000000.00, 1500000.00, 'ongoing', 2, 'Water & Sanitation', 60.00),
('PRJ-2026-003', 'Vijayawada Central', 'Vijayawada', 'Andhra Pradesh', 7500000.00, 7500000.00, 1000000.00, 'stalled', 3, 'Healthcare', 15.00)
ON CONFLICT (project_id) DO NOTHING;
