import json
from pathlib import Path


SECTION_A_DIR = Path("data/section_a")


def load_json(filename):
    path = SECTION_A_DIR / filename

    if not path.exists():
        return []

    with path.open(
        "r",
        encoding="utf-8"
    ) as file:
        data = json.load(file)

    if not isinstance(data, list):
        return []

    return data


def build_section_a_memory_records():
    projects = load_json("projects.json")
    materials = load_json("materials.json")
    formulations = load_json("formulations.json")
    components = load_json("formulation_components.json")
    setups = load_json("setups.json")
    runs = load_json("runs.json")
    results = load_json("run_result.json")

    projects_by_id = {
        item.get("project_id"): item
        for item in projects
    }

    materials_by_id = {
        item.get("material_id"): item
        for item in materials
    }

    formulations_by_id = {
        item.get("formulation_id"): item
        for item in formulations
    }

    setups_by_id = {
        item.get("setup_id"): item
        for item in setups
    }

    run_result_by_run_id = {
        item.get("run_id"): item
        for item in results
    }

    components_by_formulation = {}

    for component in components:
        formulation_id = component.get(
            "formulation_id"
        )

        components_by_formulation.setdefault(
            formulation_id,
            []
        ).append(component)

    memory_records = []

    for run in runs:
        project = projects_by_id.get(
            run.get("project_id"),
            {}
        )

        formulation = formulations_by_id.get(
            run.get("formulation_id"),
            {}
        )

        setup = setups_by_id.get(
            run.get("setup_id"),
            {}
        )

        result = run_result_by_run_id.get(
            run.get("run_id"),
            {}
        )

        formulation_components = (
            components_by_formulation.get(
                run.get("formulation_id"),
                []
            )
        )

        polymer_name = ""
        polymer_percentage = None

        solvent_name = ""
        solvent_percentage = None

        for component in formulation_components:
            material = materials_by_id.get(
                component.get("material_id"),
                {}
            )

            role = component.get(
                "component_role",
                ""
            )

            if role == "polymer":
                polymer_name = material.get(
                    "material_name",
                    ""
                )

                polymer_percentage = (
                    component.get(
                        "concentration"
                    )
                )

            elif role == "solvent":
                solvent_name = material.get(
                    "material_name",
                    ""
                )

                solvent_percentage = (
                    component.get(
                        "ratio"
                    )
                )

        experiment_id = run.get(
            "run_id",
            ""
        )

        project_code = project.get(
            "project_code",
            run.get(
                "project_id",
                ""
            )
        )

        formula_id = formulation.get(
            "formulation_id",
            run.get(
                "formulation_id",
                ""
            )
        )

        record = {
            "experiment_id":
                experiment_id,

            "project_code":
                project_code,

            "project": {
                "project_code":
                    project_code,

                "client":
                    project.get(
                        "client",
                        ""
                    ),

                "rd_leader":
                    project.get(
                        "rd_leader",
                        ""
                    ),

                "beas_code":
                    project.get(
                        "beas_code",
                        ""
                    ),

                "year":
                    project.get(
                        "year"
                    ),
            },

            "materials": [],

            "formula_id":
                formula_id,

            "formulation": {
                "formula_id":
                    formula_id,

                "polymer_a":
                    polymer_name,

                "polymer_a_percentage":
                    polymer_percentage,

                "solvent_a":
                    solvent_name,

                "solvent_a_percentage":
                    solvent_percentage,
            },

            "characterization": {},

            "setup": {
                "setup_id":
                    run.get(
                        "setup_id",
                        ""
                    ),

                "machine":
                    setup.get(
                        "machine",
                        ""
                    ),

                "platform":
                    setup.get(
                        "platform",
                        ""
                    ),

                "number_of_needles":
                    setup.get(
                        "number_of_needles"
                    ),

                "needle_gauge":
                    setup.get(
                        "needle_gauge",
                        ""
                    ),

                "custom_configuration":
                    setup.get(
                        "custom_configuration",
                        {}
                    ),
            },

            "run_parameters": {
                "experiment_id":
                    experiment_id,

                "project_code":
                    project_code,

                "sample_code":
                    run.get(
                        "sample_code",
                        ""
                    ),

                "formula_id":
                    formula_id,

                "date":
                    run.get(
                        "date",
                        ""
                    ),

                "purpose":
                    run.get(
                        "purpose",
                        ""
                    ),

                "flow_rate_q1_ml_h":
                    run.get(
                        "flow_rate"
                    ),

                "flow_rate_q1_raw":
                    run.get(
                        "flow_rate_raw",
                        ""
                    ),

                "hv_positive_kv":
                    run.get(
                        "injector_voltage"
                    ),

                "hv_positive_raw":
                    run.get(
                        "injector_voltage_raw",
                        ""
                    ),

                "hv_negative_kv":
                    run.get(
                        "collector_voltage"
                    ),

                "hv_negative_raw":
                    run.get(
                        "collector_voltage_raw",
                        ""
                    ),

                "temperature_c":
                    run.get(
                        "temperature"
                    ),

                "temperature_raw":
                    run.get(
                        "temperature_raw",
                        ""
                    ),

                "relative_humidity_percent":
                    run.get(
                        "relative_humidity"
                    ),

                "relative_humidity_raw":
                    run.get(
                        "relative_humidity_raw",
                        ""
                    ),

                "dz_mm":
                    run.get(
                        "working_distance"
                    ),

                "dz_raw":
                    run.get(
                        "working_distance_raw",
                        ""
                    ),

                "drum_speed_rpm":
                    run.get(
                        "drum_speed"
                    ),

                "processability_grade":
                    run.get(
                        "processability_score"
                    ),

                "process_comments":
                    run.get(
                        "process_comments",
                        ""
                    ),
            },

            "run_result": {
                "processability_grade":
                    run.get(
                        "processability_score"
                    ),

                "process_comments":
                    run.get(
                        "process_comments",
                        ""
                    ),

                "sem_comments":
                    result.get(
                        "sem_morphology",
                        ""
                    ),

                "filtration_performance":
                    result.get(
                        "filtration_performance",
                        ""
                    ),

                "result_notes":
                    result.get(
                        "notes",
                        ""
                    ),
            },

            "is_incomplete":
                run.get(
                    "is_incomplete",
                    False
                ),

            "source":
                "section_a",
        }

        memory_records.append(
            record
        )

    return memory_records