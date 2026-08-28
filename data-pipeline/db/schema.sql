CREATE TABLE IF NOT EXISTS agencies (
    agency_id SERIAL PRIMARY KEY,
    agency_name  TEXT NOT NULL,
    district  TEXT,
    state      TEXT
);


CREATE TABLE IF NOT EXISTS projects (
    project_id      TEXT NOT NULL,
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



