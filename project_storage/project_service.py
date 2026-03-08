# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""High-level project service wrappers."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from formula_registry.models import CalculationResult
from project_storage.project_repository import DEFAULT_DB_PATH, ProjectRepository


class ProjectService:
    """Coordinate persistence of projects and calculation results."""

    def __init__(self, repository: ProjectRepository) -> None:
        self.repository = repository

    def create_project(self, name: str, description: str = ""):
        """Create a project."""

        return self.repository.create_project(name, description)

    def list_projects(self):
        """List projects."""

        return self.repository.list_projects()

    def get_project(self, project_id: str):
        """Get one project."""

        return self.repository.get_project(project_id)

    def save_result(self, project_id: str, result: CalculationResult):
        """Save a calculation result as a case."""

        warnings = [message.message for message in result.messages if message.level == "warning"]
        payload = {
            "formula_id": result.formula_id,
            "formula_name": result.formula_name,
            "input_values": result.input_values,
            "input_units": result.input_units,
            "pressure_bases": result.pressure_bases,
            "normalized_inputs": result.normalized_inputs,
            "output_values": result.output_values,
            "output_units": result.output_units,
            "warnings": warnings,
            "selected_properties": result.selected_properties,
            "overridden_properties": result.overridden_properties,
        }
        return self.repository.save_case(project_id, payload)

    def list_cases(self, project_id: str):
        """List cases for a project."""

        return self.repository.list_cases(project_id)

    def get_case(self, case_id: str):
        """Get a case."""

        return self.repository.get_case(case_id)

    def duplicate_case(self, case_id: str):
        """Duplicate a case."""

        return self.repository.duplicate_case(case_id)


@lru_cache(maxsize=1)
def get_project_service(db_path: str | Path | None = None) -> ProjectService:
    """Return a cached project service."""

    repository = ProjectRepository(Path(db_path) if db_path else DEFAULT_DB_PATH)
    return ProjectService(repository)
