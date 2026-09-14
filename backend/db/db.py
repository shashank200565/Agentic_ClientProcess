from __future__ import annotations

import json
import os
import sqlite3
from uuid import uuid4
from pathlib import Path
from typing import Iterator

try:
    from backend.pipeline.schemas import (
        AutomationBlueprint,
        RedesignProposal,
        StaticWorkflowDiagram,
        StepScore,
        WorkflowSession,
        Workflow,
        WorkflowStep,
    )
except ModuleNotFoundError:  # Supports the documented `cd backend` launch.
    from pipeline.schemas import AutomationBlueprint, RedesignProposal, StaticWorkflowDiagram, StepScore, Workflow, WorkflowSession, WorkflowStep


DEFAULT_DATABASE_PATH = Path(__file__).resolve().parent.parent / "data" / "app.db"
SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def get_database_path() -> Path:
    configured_path = os.getenv("DATABASE_PATH")
    if not configured_path:
        return DEFAULT_DATABASE_PATH
    path = Path(configured_path)
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[2] / path
    return path.resolve()


def get_connection(database_path: str | Path | None = None) -> sqlite3.Connection:
    path = Path(database_path) if database_path else get_database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database(connection: sqlite3.Connection) -> None:
    connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    try:
        connection.execute(
            "ALTER TABLE redesign_proposals ADD COLUMN diagram_json TEXT NOT NULL DEFAULT '{\"nodes\": [], \"edges\": []}'"
        )
    except sqlite3.OperationalError as exc:
        if "duplicate column name" not in str(exc):
            raise
    connection.commit()


def save_workflow(
    workflow: Workflow,
    connection: sqlite3.Connection | None = None,
) -> None:
    owns_connection = connection is None
    connection = connection or get_connection()
    try:
        initialize_database(connection)
        connection.execute(
            """
            INSERT INTO workflows (workflow_id, name, source_type, status, raw_text)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(workflow_id) DO UPDATE SET
                name = excluded.name,
                source_type = excluded.source_type,
                status = excluded.status,
                raw_text = excluded.raw_text
            """,
            (
                workflow.workflow_id,
                workflow.name,
                workflow.source_type,
                workflow.status,
                workflow.raw_text,
            ),
        )
        connection.execute(
            "DELETE FROM workflow_steps WHERE workflow_id = ?",
            (workflow.workflow_id,),
        )
        connection.executemany(
            """
            INSERT INTO workflow_steps (workflow_id, step_id, name, description, position)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (
                    workflow.workflow_id,
                    step.step_id,
                    step.name,
                    step.description,
                    position,
                )
                for position, step in enumerate(workflow.steps)
            ],
        )
        connection.executemany(
            """
            INSERT INTO step_scores (
                workflow_id, step_id, repetitiveness, judgment_need,
                compliance_sensitivity, ai_suitability, reasoning, verdict
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    score.workflow_id,
                    score.step_id,
                    score.scores.repetitiveness,
                    score.scores.judgment_need,
                    score.scores.compliance_sensitivity,
                    score.scores.ai_suitability,
                    score.reasoning,
                    score.verdict,
                )
                for score in workflow.scores
            ],
        )
        connection.executemany(
            "INSERT OR REPLACE INTO automation_blueprints (workflow_id, step_id, blueprint_json) VALUES (?, ?, ?)",
            [
                (item.workflow_id, item.step_id, item.model_dump_json())
                for item in workflow.automation_blueprints
            ],
        )
        connection.executemany(
            """
            INSERT OR REPLACE INTO redesign_proposals (
                workflow_id, step_id, current_step_json, problem_statement,
                proposed_design, agent_responsibilities_json, human_controls_json,
                expected_benefits_json, diagram_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    item.workflow_id,
                    item.step_id,
                    item.current_step.model_dump_json(),
                    item.problem_statement,
                    item.proposed_design,
                    json.dumps(item.agent_responsibilities),
                    json.dumps(item.human_controls),
                    json.dumps(item.expected_benefits),
                    item.diagram.model_dump_json(),
                )
                for item in workflow.redesign_proposals
            ],
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        if owns_connection:
            connection.close()


def get_workflow(
    workflow_id: str,
    connection: sqlite3.Connection | None = None,
) -> Workflow | None:
    owns_connection = connection is None
    connection = connection or get_connection()
    try:
        initialize_database(connection)
        workflow_row = connection.execute(
            "SELECT * FROM workflows WHERE workflow_id = ?",
            (workflow_id,),
        ).fetchone()
        if workflow_row is None:
            return None

        step_rows = connection.execute(
            """
            SELECT step_id, name, description
            FROM workflow_steps
            WHERE workflow_id = ?
            ORDER BY position
            """,
            (workflow_id,),
        ).fetchall()
        score_rows = connection.execute(
            """
            SELECT workflow_id, step_id, repetitiveness, judgment_need,
                   compliance_sensitivity, ai_suitability, reasoning, verdict
            FROM step_scores
            WHERE workflow_id = ?
            """,
            (workflow_id,),
        ).fetchall()
        score_models = [
            StepScore(
                workflow_id=row["workflow_id"],
                step_id=row["step_id"],
                scores={
                    "repetitiveness": row["repetitiveness"],
                    "judgment_need": row["judgment_need"],
                    "compliance_sensitivity": row["compliance_sensitivity"],
                    "ai_suitability": row["ai_suitability"],
                },
                reasoning=row["reasoning"],
                verdict=row["verdict"],
            )
            for row in score_rows
        ]
        blueprint_models = [
            AutomationBlueprint.model_validate(json.loads(row["blueprint_json"]))
            for row in connection.execute(
                "SELECT blueprint_json FROM automation_blueprints WHERE workflow_id = ?",
                (workflow_id,),
            ).fetchall()
        ]
        redesign_models = [
            RedesignProposal(
                workflow_id=row["workflow_id"],
                step_id=row["step_id"],
                current_step=WorkflowStep(**json.loads(row["current_step_json"])),
                problem_statement=row["problem_statement"],
                proposed_design=row["proposed_design"],
                agent_responsibilities=json.loads(row["agent_responsibilities_json"]),
                human_controls=json.loads(row["human_controls_json"]),
                expected_benefits=json.loads(row["expected_benefits_json"]),
                diagram=StaticWorkflowDiagram.model_validate(json.loads(row["diagram_json"]))
                if "diagram_json" in row.keys()
                else {"nodes": [], "edges": []},
            )
            for row in connection.execute(
                "SELECT * FROM redesign_proposals WHERE workflow_id = ?",
                (workflow_id,),
            ).fetchall()
        ]
        return Workflow(
            workflow_id=workflow_row["workflow_id"],
            name=workflow_row["name"],
            source_type=workflow_row["source_type"],
            status=workflow_row["status"],
            raw_text=workflow_row["raw_text"],
            steps=[WorkflowStep(**dict(row)) for row in step_rows],
            scores=score_models,
            automation_blueprints=blueprint_models,
            redesign_proposals=redesign_models,
        )
    finally:
        if owns_connection:
            connection.close()


def get_analyzed_workflows(
    connection: sqlite3.Connection | None = None,
) -> list[Workflow]:
    owns_connection = connection is None
    connection = connection or get_connection()
    try:
        initialize_database(connection)
        workflow_ids = connection.execute(
            "SELECT workflow_id FROM workflows WHERE status = 'analyzed' ORDER BY created_at DESC"
        ).fetchall()
        return [workflow for row in workflow_ids if (workflow := get_workflow(row["workflow_id"], connection)) is not None]
    finally:
        if owns_connection:
            connection.close()


def save_session(session: WorkflowSession) -> None:
    connection = get_connection()
    try:
        initialize_database(connection)
        connection.execute(
            """INSERT OR REPLACE INTO workflow_sessions
            (session_id, workflow_id, current_stage, completed_step_ids_json, workflow_json)
            VALUES (?, ?, ?, ?, ?)""",
            (session.session_id, session.workflow_id, session.current_stage, json.dumps(session.completed_step_ids), session.workflow.model_dump_json()),
        )
        connection.commit()
    finally:
        connection.close()


def get_session(session_id: str) -> WorkflowSession | None:
    connection = get_connection()
    try:
        initialize_database(connection)
        row = connection.execute("SELECT * FROM workflow_sessions WHERE session_id = ?", (session_id,)).fetchone()
        if row is None:
            return None
        return WorkflowSession(
            session_id=row["session_id"],
            workflow_id=row["workflow_id"],
            current_stage=row["current_stage"],
            completed_step_ids=json.loads(row["completed_step_ids_json"]),
            workflow=json.loads(row["workflow_json"]),
        )
    finally:
        connection.close()


def save_workflow_session(workflow: Workflow, current_stage: str) -> WorkflowSession:
    connection = get_connection()
    try:
        initialize_database(connection)
        row = connection.execute(
            "SELECT session_id, completed_step_ids_json FROM workflow_sessions WHERE workflow_id = ? ORDER BY updated_at DESC LIMIT 1",
            (workflow.workflow_id,),
        ).fetchone()
        completed = set(json.loads(row["completed_step_ids_json"])) if row else set()
        completed.update(score.step_id for score in workflow.scores)
        completed.update(item.step_id for item in workflow.automation_blueprints)
        completed.update(item.step_id for item in workflow.redesign_proposals)
        session = WorkflowSession(
            session_id=row["session_id"] if row else uuid4().hex,
            workflow_id=workflow.workflow_id,
            current_stage=current_stage,
            completed_step_ids=sorted(completed),
            workflow=workflow,
        )
        save_session(session)
        return session
    finally:
        connection.close()


def get_sessions(limit: int = 50) -> list[WorkflowSession]:
    connection = get_connection()
    try:
        initialize_database(connection)
        rows = connection.execute("SELECT session_id FROM workflow_sessions ORDER BY updated_at DESC LIMIT ?", (limit,)).fetchall()
        sessions = [get_session(row["session_id"]) for row in rows]
        return [session for session in sessions if session is not None]
    finally:
        connection.close()
