# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""SQLite repository for projects and calculation cases."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from project_storage.project_models import CalculationCase, Project
from runtime_paths import get_project_db_path


DEFAULT_DB_PATH = get_project_db_path()


class ProjectRepository:
    """Persist projects and cases in SQLite."""

    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path or get_project_db_path()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    project_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS calculation_cases (
                    case_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    formula_id TEXT NOT NULL,
                    formula_name TEXT NOT NULL,
                    input_values TEXT NOT NULL,
                    input_units TEXT NOT NULL,
                    pressure_bases TEXT NOT NULL,
                    normalized_inputs TEXT NOT NULL,
                    output_values TEXT NOT NULL,
                    output_units TEXT NOT NULL,
                    warnings TEXT NOT NULL,
                    selected_properties TEXT NOT NULL,
                    overridden_properties TEXT NOT NULL,
                    calculation_mode TEXT NOT NULL DEFAULT 'forward',
                    solve_metadata TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(project_id) REFERENCES projects(project_id)
                );
                """
            )
            columns = {row["name"] for row in connection.execute("PRAGMA table_info(calculation_cases)").fetchall()}
            if "calculation_mode" not in columns:
                connection.execute("ALTER TABLE calculation_cases ADD COLUMN calculation_mode TEXT NOT NULL DEFAULT 'forward'")
            if "solve_metadata" not in columns:
                connection.execute("ALTER TABLE calculation_cases ADD COLUMN solve_metadata TEXT NOT NULL DEFAULT '{}'")

    def create_project(self, name: str, description: str = "") -> Project:
        """Create and persist a new project."""

        now = datetime.now(timezone.utc)
        project = Project(
            project_id=str(uuid.uuid4()),
            name=name,
            description=description,
            created_at=now,
            updated_at=now,
        )
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO projects (project_id, name, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                (project.project_id, project.name, project.description, project.created_at.isoformat(), project.updated_at.isoformat()),
            )
        return project

    def list_projects(self) -> list[Project]:
        """Return saved projects ordered by update time."""

        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM projects ORDER BY updated_at DESC").fetchall()
        return [
            Project(
                project_id=row["project_id"],
                name=row["name"],
                description=row["description"],
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
            )
            for row in rows
        ]

    def get_project(self, project_id: str) -> Project | None:
        """Return a single project or None."""

        with self._connect() as connection:
            row = connection.execute("SELECT * FROM projects WHERE project_id = ?", (project_id,)).fetchone()
        if row is None:
            return None
        return Project(
            project_id=row["project_id"],
            name=row["name"],
            description=row["description"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def save_case(self, project_id: str, payload: dict[str, object]) -> CalculationCase:
        """Persist a calculation case payload."""

        now = datetime.now(timezone.utc)
        case = CalculationCase(
            case_id=str(uuid.uuid4()),
            project_id=project_id,
            formula_id=str(payload["formula_id"]),
            formula_name=str(payload["formula_name"]),
            input_values=payload.get("input_values", {}),
            input_units=payload.get("input_units", {}),
            pressure_bases=payload.get("pressure_bases", {}),
            normalized_inputs=payload.get("normalized_inputs", {}),
            output_values=payload.get("output_values", {}),
            output_units=payload.get("output_units", {}),
            warnings=list(payload.get("warnings", [])),
            selected_properties=payload.get("selected_properties", {}),
            overridden_properties=payload.get("overridden_properties", {}),
            calculation_mode=str(payload.get("calculation_mode", "forward")),
            solve_metadata=payload.get("solve_metadata", {}),
            created_at=now,
            updated_at=now,
        )
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO calculation_cases (
                    case_id, project_id, formula_id, formula_name,
                    input_values, input_units, pressure_bases, normalized_inputs,
                    output_values, output_units, warnings,
                    selected_properties, overridden_properties, calculation_mode, solve_metadata,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    case.case_id,
                    case.project_id,
                    case.formula_id,
                    case.formula_name,
                    json.dumps(case.input_values, ensure_ascii=False),
                    json.dumps(case.input_units, ensure_ascii=False),
                    json.dumps(case.pressure_bases, ensure_ascii=False),
                    json.dumps(case.normalized_inputs, ensure_ascii=False),
                    json.dumps(case.output_values, ensure_ascii=False),
                    json.dumps(case.output_units, ensure_ascii=False),
                    json.dumps(case.warnings, ensure_ascii=False),
                    json.dumps(case.selected_properties, ensure_ascii=False),
                    json.dumps(case.overridden_properties, ensure_ascii=False),
                    case.calculation_mode,
                    json.dumps(case.solve_metadata, ensure_ascii=False),
                    case.created_at.isoformat(),
                    case.updated_at.isoformat(),
                ),
            )
            connection.execute(
                "UPDATE projects SET updated_at = ? WHERE project_id = ?",
                (now.isoformat(), project_id),
            )
        return case

    def list_cases(self, project_id: str) -> list[CalculationCase]:
        """List all cases for a project."""

        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM calculation_cases WHERE project_id = ? ORDER BY updated_at DESC",
                (project_id,),
            ).fetchall()
        return [self._case_from_row(row) for row in rows]

    def get_case(self, case_id: str) -> CalculationCase | None:
        """Return a single case or None."""

        with self._connect() as connection:
            row = connection.execute("SELECT * FROM calculation_cases WHERE case_id = ?", (case_id,)).fetchone()
        return self._case_from_row(row) if row else None

    def duplicate_case(self, case_id: str) -> CalculationCase:
        """Duplicate an existing case and return the new copy."""

        case = self.get_case(case_id)
        if case is None:
            raise KeyError("指定されたケースが見つかりません。")

        payload = case.model_dump()
        payload.pop("case_id", None)
        payload.pop("project_id", None)
        payload.pop("created_at", None)
        payload.pop("updated_at", None)
        return self.save_case(case.project_id, payload)

    def _case_from_row(self, row: sqlite3.Row) -> CalculationCase:
        return CalculationCase(
            case_id=row["case_id"],
            project_id=row["project_id"],
            formula_id=row["formula_id"],
            formula_name=row["formula_name"],
            input_values=json.loads(row["input_values"]),
            input_units=json.loads(row["input_units"]),
            pressure_bases=json.loads(row["pressure_bases"]),
            normalized_inputs=json.loads(row["normalized_inputs"]),
            output_values=json.loads(row["output_values"]),
            output_units=json.loads(row["output_units"]),
            warnings=json.loads(row["warnings"]),
            selected_properties=json.loads(row["selected_properties"]),
            overridden_properties=json.loads(row["overridden_properties"]),
            calculation_mode=row["calculation_mode"],
            solve_metadata=json.loads(row["solve_metadata"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
