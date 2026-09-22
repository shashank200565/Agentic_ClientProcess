PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS workflows (
    workflow_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    source_type TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('uploaded', 'extracted', 'analyzed')),
    raw_text TEXT,
    consistency_flags_json TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS workflow_steps (
    workflow_id TEXT NOT NULL,
    step_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    position INTEGER NOT NULL,
    PRIMARY KEY (workflow_id, step_id),
    FOREIGN KEY (workflow_id) REFERENCES workflows(workflow_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS step_scores (
    workflow_id TEXT NOT NULL,
    step_id TEXT NOT NULL,
    repetitiveness INTEGER NOT NULL CHECK (repetitiveness BETWEEN 1 AND 5),
    judgment_need INTEGER NOT NULL CHECK (judgment_need BETWEEN 1 AND 5),
    compliance_sensitivity INTEGER NOT NULL CHECK (compliance_sensitivity BETWEEN 1 AND 5),
    ai_suitability INTEGER NOT NULL CHECK (ai_suitability BETWEEN 1 AND 5),
    reasoning TEXT NOT NULL,
    verdict TEXT NOT NULL CHECK (verdict IN ('leave_as_is', 'automate', 'redesign')),
    PRIMARY KEY (workflow_id, step_id),
    FOREIGN KEY (workflow_id, step_id)
        REFERENCES workflow_steps(workflow_id, step_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS redesign_proposals (
    workflow_id TEXT NOT NULL,
    step_id TEXT NOT NULL,
    current_step_json TEXT NOT NULL,
    problem_statement TEXT NOT NULL,
    proposed_design TEXT NOT NULL,
    agent_responsibilities_json TEXT NOT NULL,
    human_controls_json TEXT NOT NULL,
    expected_benefits_json TEXT NOT NULL,
    diagram_json TEXT NOT NULL,
    PRIMARY KEY (workflow_id, step_id),
    FOREIGN KEY (workflow_id, step_id)
        REFERENCES workflow_steps(workflow_id, step_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS automation_blueprints (
    workflow_id TEXT NOT NULL,
    step_id TEXT NOT NULL,
    blueprint_json TEXT NOT NULL,
    PRIMARY KEY (workflow_id, step_id),
    FOREIGN KEY (workflow_id, step_id)
        REFERENCES workflow_steps(workflow_id, step_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS workflow_sessions (
    session_id TEXT PRIMARY KEY,
    workflow_id TEXT NOT NULL,
    current_stage TEXT NOT NULL,
    completed_step_ids_json TEXT NOT NULL,
    workflow_json TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
