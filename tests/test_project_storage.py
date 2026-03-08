"""Project storage tests."""

from __future__ import annotations

from pathlib import Path

from formula_registry.models import CalculationResult, ValidationMessage
from project_storage.project_repository import ProjectRepository
from project_storage.project_service import ProjectService


def test_project_and_case_persistence(tmp_path: Path) -> None:
    repository = ProjectRepository(tmp_path / "test.db")
    service = ProjectService(repository)

    project = service.create_project("案件A", "説明")
    result = CalculationResult(
        formula_id="fluid_reynolds_number",
        formula_name="Reynolds数",
        category="流体",
        input_values={"density": 998.0},
        input_units={"density": "kg/m^3"},
        pressure_bases={},
        normalized_inputs={"density": 998.0},
        normalized_input_units={"density": "kg/m^3"},
        output_values={"reynolds_number": 10000.0},
        output_units={"reynolds_number": "fraction"},
        messages=[ValidationMessage(level="warning", message="代表値計算")],
    )

    saved_case = service.save_result(project.project_id, result)
    listed_cases = service.list_cases(project.project_id)

    assert saved_case.project_id == project.project_id
    assert len(listed_cases) == 1
    assert listed_cases[0].formula_id == "fluid_reynolds_number"


def test_duplicate_case(tmp_path: Path) -> None:
    repository = ProjectRepository(tmp_path / "duplicate.db")
    project = repository.create_project("案件B", "")
    case = repository.save_case(
        project.project_id,
        {
            "formula_id": "heat_lmtd",
            "formula_name": "LMTD",
            "input_values": {"delta_t1": 40.0},
            "input_units": {"delta_t1": "K"},
            "pressure_bases": {},
            "normalized_inputs": {"delta_t1": 40.0},
            "output_values": {"lmtd": 28.8},
            "output_units": {"lmtd": "K"},
            "warnings": [],
            "selected_properties": {},
            "overridden_properties": {},
        },
    )
    duplicated = repository.duplicate_case(case.case_id)
    assert duplicated.case_id != case.case_id
    assert duplicated.formula_id == case.formula_id

