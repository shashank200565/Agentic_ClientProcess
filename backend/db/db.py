from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Iterator

try:
    from backend.pipeline.schemas import StepScore, Workflow, WorkflowStep
except ModuleNotFoundError:  # Supports the documented `cd backend` launch.
    from pipeline.schemas import StepScore, Workflow, WorkflowStep


DEFAULT_DATABASE_PATH = Path(__file__).resolve().parent.parent / "data" / "app.db"
SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def get_database_path() -> Path:
    configured_path = os.getenv("DATABASE_PATH")
    return Path(configured_path) if configured_path else DEFAULT_DATABASE_PATH


def get_connection(database_path: str | Path | None = None) -> sqlite3.Connection:
    path = Path(database_path) if database_path else get_database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database(connection: sqlite3.Connection) -> None:
    connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
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
        return Workflow(
            workflow_id=workflow_row["workflow_id"],
            name=workflow_row["name"],
            source_type=workflow_row["source_type"],
            status=workflow_row["status"],
            raw_text=workflow_row["raw_text"],
            steps=[WorkflowStep(**dict(row)) for row in step_rows],
            scores=score_models,
        )
    finally:
        if owns_connection:
            connection.close()
