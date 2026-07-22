import json
import re 
import uuid
from pathlib import Path


SOURCE_FILE = Path("data/processed/unified_experiments_database.json")
TEST_OUTPUT_DIR = Path("data/migration_full_test")

TEST_PROJECTS_FILE = TEST_OUTPUT_DIR / "projects.json"
TEST_MATERIALS_FILE = TEST_OUTPUT_DIR / "materials.json"
TEST_FORMULATIONS_FILE = TEST_OUTPUT_DIR / "formulations.json"
TEST_FORMULATION_COMPONENTS_FILE = TEST_OUTPUT_DIR / "formulation_components.json"
TEST_CHARACTERIZATIONS_FILE = TEST_OUTPUT_DIR / "characterizations.json"
TEST_SETUPS_FILE = TEST_OUTPUT_DIR / "setups.json"
TEST_RUNS_FILE = TEST_OUTPUT_DIR / "runs.json"
TEST_RESULTS_FILE = TEST_OUTPUT_DIR / "results.json"


def load_source_records():
    with SOURCE_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(records, file_path):
    TEST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=4, ensure_ascii=False, default=str)


def has_value(value):
    return value not in ("", None, [], {})


def normalize_text(value):
    if value is None:
        return ""
    return str(value).strip()


def safe_float(value):
    try:
        if value in ("", None):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None

def parse_numeric_with_raw(value):
    if value in ["", None]:
        return None, ""

    if isinstance(value, (int, float)):
        return float(value), str(value)

    raw = str(value).strip()

    normalized = raw.replace(",", ".")

    match = re.search(
        r"-?\d+(?:\.\d+)?",
        normalized
    )

    if not match:
        return None, raw

    try:
        numeric_value = float(
            match.group()
        )
    except ValueError:
        numeric_value = None

    return numeric_value, raw


def stable_id(prefix, *parts):
    raw = "|".join(normalize_text(part) for part in parts)
    return f"{prefix}{uuid.uuid5(uuid.NAMESPACE_URL, raw)}"


def setup_signature(project_code, setup):
    old_setup_id = normalize_text(setup.get("setup_id", ""))
    if old_setup_id:
        return ("setup_id", project_code, old_setup_id)

    return (
        "signature",
        project_code,
        normalize_text(setup.get("setup_number", "")),
        normalize_text(setup.get("machine", "")).lower(),
        normalize_text(setup.get("platform", "")).lower(),
    )


def build_dry_run_summary(records):
    project_ids = set()
    formulation_keys = set()
    setup_keys = set()
    run_ids = set()

    result_count = 0
    incomplete_run_count = 0
    records_with_composition = 0
    records_with_properties = 0
    records_with_results = 0

    for index, experiment in enumerate(records, start=1):
        project_code = normalize_text(experiment.get("project_code", ""))
        if project_code:
            project_ids.add(project_code)

        formula_id = normalize_text(experiment.get("formula_id", ""))
        if formula_id:
            formulation_keys.add((project_code, formula_id))

        composition = experiment.get("solution_composition", {}) or {}
        if composition:
            records_with_composition += 1

        properties = experiment.get("solution_properties", {}) or {}
        if properties:
            records_with_properties += 1

        setup = experiment.get("setup", {}) or {}
        setup_keys.add(setup_signature(project_code, setup))

        experiment_id = normalize_text(experiment.get("experiment_id", ""))
        if not experiment_id:
            experiment_id = f"historical_run_{index}"
        run_ids.add(experiment_id)

        process = experiment.get("process_parameters", {}) or {}
        results = experiment.get("results", {}) or {}

        processability = results.get(
            "processability_grade",
            process.get("processability_grade", "")
        )
        process_comments = results.get(
            "process_comments",
            process.get("process_comments", "")
        )
        sem_comments = results.get(
            "sem_comments",
            process.get("sem_comments", "")
        )
        fiber_diameter = results.get(
            "avg_fiber_diameter_nm",
            process.get("avg_fiber_diameter_nm", "")
        )

        if any(
            has_value(value)
            for value in (
                processability,
                process_comments,
                sem_comments,
                fiber_diameter,
            )
        ):
            records_with_results += 1
            result_count += 1

        required_run_fields = [
            project_code,
            formula_id,
            process.get("flow_rate_q1_ml_h"),
            process.get("hv_positive_kv"),
            process.get("temperature_c"),
            process.get("relative_humidity_percent"),
        ]

        if not all(has_value(value) for value in required_run_fields):
            incomplete_run_count += 1

    return {
        "source_experiments": len(records),
        "unique_projects": len(project_ids),
        "unique_nonempty_formulations": len(formulation_keys),
        "unique_setups": len(setup_keys),
        "runs_to_create": len(run_ids),
        "results_to_create": result_count,
        "records_with_composition": records_with_composition,
        "records_with_solution_properties": records_with_properties,
        "records_with_results": records_with_results,
        "incomplete_runs": incomplete_run_count,
    }


def migrate_records(records):
    projects = {}
    materials = {}
    formulations = {}
    formulation_components = {}
    characterizations = {}
    setups = {}
    runs = {}
    results = {}

    for index, experiment in enumerate(records, start=1):
        # -------------------------
        # PROJECT
        # -------------------------
        project_code = normalize_text(experiment.get("project_code", ""))
        if not project_code:
            project_code = "UNKNOWN_PROJECT"

        project_data = experiment.get("project", {}) or {}

        if project_code not in projects:
            projects[project_code] = {
                "project_id": project_code,
                "project_code": project_code,
                "beas_code": "",
                "client": normalize_text(project_data.get("client", "")),
                "rd_leader": normalize_text(project_data.get("rd_leader", "")),
                "year": None,
            }

        # -------------------------
        # MATERIALS FROM OLD LIST
        # -------------------------
        old_materials = experiment.get("materials", []) or []

        for old_material in old_materials:
            material_name = normalize_text(old_material.get("material_name", ""))
            if not material_name:
                continue

            article_number = normalize_text(old_material.get("article_number", ""))
            material_key = (
                material_name.lower(),
                article_number.lower(),
            )

            if material_key not in materials:
                materials[material_key] = {
                    "material_id": stable_id(
                        "MIG_MAT_",
                        material_name.lower(),
                        article_number.lower(),
                    ),
                    "material_name": material_name,
                    "material_type": "unknown",
                    "molecular_weight": "",
                    "supplier": "",
                    "article_number": article_number,
                    "batch_number": "",
                    "notes": "Migrated from historical unified database.",
                }

        # -------------------------
        # FORMULATION
        # -------------------------
        raw_formula_id = normalize_text(experiment.get("formula_id", ""))

        if raw_formula_id:
            formulation_key = (project_code, raw_formula_id)
        else:
            # Missing formula IDs cannot safely be merged.
            formulation_key = (
                project_code,
                f"__MISSING_FORMULA__{index}",
            )

        formulation_id = stable_id(
            "MIG_FORM_",
            formulation_key[0],
            formulation_key[1],
        )

        composition = experiment.get("solution_composition", {}) or {}
        polymer_concentration = safe_float(
            composition.get("polymer_a_percentage", "")
        )

        if formulation_key not in formulations:
            notes = "Migrated historical formulation."
            if raw_formula_id:
                notes += f" Original formula ID: {raw_formula_id}"
            else:
                notes += " Original formula ID was missing; review required."

            formulations[formulation_key] = {
                "formulation_id": formulation_id,
                "project_id": project_code,
                "polymer_concentration": polymer_concentration,
                "notes": notes,
            }

        # -------------------------
        # MATERIALS FROM COMPOSITION
        # -------------------------
        def get_or_create_composition_material(material_name, material_type):
            material_name = normalize_text(material_name)
            if not material_name:
                return None

            # Match by name-only only when no article/reference is available.
            material_key = (material_name.lower(), "")

            if material_key not in materials:
                materials[material_key] = {
                    "material_id": stable_id(
                        "MIG_MAT_",
                        material_name.lower(),
                        "",
                    ),
                    "material_name": material_name,
                    "material_type": material_type,
                    "molecular_weight": "",
                    "supplier": "",
                    "article_number": "",
                    "batch_number": "",
                    "notes": "Migrated from historical composition.",
                }

            return materials[material_key]["material_id"]

        polymer_name = normalize_text(composition.get("polymer_a", ""))
        solvent_name = normalize_text(composition.get("solvent_a", ""))
        solvent_ratio = safe_float(composition.get("solvent_a_percentage", ""))

        polymer_material_id = get_or_create_composition_material(
            polymer_name,
            "polymer",
        )
        solvent_material_id = get_or_create_composition_material(
            solvent_name,
            "solvent",
        )

        if polymer_material_id:
            component_key = (
                formulation_id,
                polymer_material_id,
                "polymer",
            )
            if component_key not in formulation_components:
                formulation_components[component_key] = {
                    "formulation_component_id": stable_id(
                        "MIG_COMP_",
                        formulation_id,
                        polymer_material_id,
                        "polymer",
                    ),
                    "formulation_id": formulation_id,
                    "material_id": polymer_material_id,
                    "component_role": "polymer",
                    "concentration": polymer_concentration,
                    "ratio": None,
                }

        if solvent_material_id:
            component_key = (
                formulation_id,
                solvent_material_id,
                "solvent",
            )
            if component_key not in formulation_components:
                formulation_components[component_key] = {
                    "formulation_component_id": stable_id(
                        "MIG_COMP_",
                        formulation_id,
                        solvent_material_id,
                        "solvent",
                    ),
                    "formulation_id": formulation_id,
                    "material_id": solvent_material_id,
                    "component_role": "solvent",
                    "concentration": None,
                    "ratio": solvent_ratio,
                }

        # -------------------------
        # CHARACTERIZATION
        # -------------------------
        properties = experiment.get("solution_properties", {}) or {}

        if properties:
            characterization_key = (
                formulation_id,
                index,
            )
            characterizations[characterization_key] = {
                "characterization_id": stable_id(
                    "MIG_CHAR_",
                    formulation_id,
                    index,
                ),
                "formulation_id": formulation_id,
                "measurement_date": "",
                "viscosity": safe_float(properties.get("viscosity_cP", "")),
                "conductivity": safe_float(
                    properties.get("conductivity_microS", "")
                ),
                "surface_tension": safe_float(
                    properties.get("surface_tension", "")
                ),
                "solid_content": safe_float(
                    properties.get("solid_content", "")
                ),
                "notes": "Migrated historical characterization.",
            }

        # -------------------------
        # SETUP
        # -------------------------
        old_setup = experiment.get("setup", {}) or {}
        setup_key = setup_signature(project_code, old_setup)

        old_setup_id = normalize_text(old_setup.get("setup_id", ""))
        setup_number = normalize_text(old_setup.get("setup_number", ""))
        machine = normalize_text(old_setup.get("machine", ""))
        platform = normalize_text(old_setup.get("platform", ""))

        if old_setup_id:
            generated_setup_id = old_setup_id
        else:
            generated_setup_id = stable_id(
                "MIG_SETUP_",
                *setup_key,
            )

        if setup_key not in setups:
            setups[setup_key] = {
                "setup_id": generated_setup_id,
                "name": setup_number or old_setup_id or "Historical Setup",
                "machine": machine,
                "injector_model_id": "",
                "collector_model_id": "",
                "number_of_needles": safe_float(
                    old_setup.get("number_of_needles", "")
                ),
                "needle_gauge": normalize_text(
                    old_setup.get("needle_gauge", "")
                ),
                "platform": platform,
                "custom_configuration": {
                    "legacy_setup": old_setup
                },
                "notes": "Migrated historical setup.",
            }

        # -------------------------
        # RUN
        # -------------------------
        process = experiment.get("process_parameters", {}) or {}

        experiment_id = normalize_text(experiment.get("experiment_id", ""))
        if not experiment_id:
            experiment_id = f"MIG_RUN_{index}"

        sample_code = normalize_text(process.get("sample_code", ""))
        if not sample_code:
            sample_code = experiment_id

        required_values = [
            project_code,
            raw_formula_id,
            process.get("flow_rate_q1_ml_h"),
            process.get("hv_positive_kv"),
            process.get("temperature_c"),
            process.get("relative_humidity_percent"),
        ]

        is_incomplete = not all(
            has_value(value)
            for value in required_values
        )

        flow_rate, flow_rate_raw = parse_numeric_with_raw(
            process.get(
                "flow_rate_q1_ml_h",
                ""
            )
        )

        injector_voltage, injector_voltage_raw = (
            parse_numeric_with_raw(
                process.get(
                    "hv_positive_kv",
                    ""
                )
            )
        )

        collector_voltage, collector_voltage_raw = (
            parse_numeric_with_raw(
                process.get(
                    "hv_negative_kv",
                    ""
                )
            )
        )

        temperature, temperature_raw = parse_numeric_with_raw(
            process.get(
                "temperature_c",
                ""
            )
        )

        relative_humidity, relative_humidity_raw = (
            parse_numeric_with_raw(
                process.get(
                    "relative_humidity_percent",
                    ""
                )
            )
        )

        working_distance, working_distance_raw = (
            parse_numeric_with_raw(
                process.get(
                    "dz_mm",
                    ""
                )
            )
        )

        runs[experiment_id] = {
            "run_id": experiment_id,
            "sample_code": sample_code,
            "project_id": project_code,
            "formulation_id": formulation_id,
            "setup_id": generated_setup_id,
            "date": normalize_text(process.get("date", "")),
            "purpose": normalize_text(process.get("purpose", "")),
            "flow_rate": flow_rate,
            "flow_rate_raw": flow_rate_raw,
            "injector_voltage": injector_voltage,
            "injector_voltage_raw": injector_voltage_raw,
            "collector_voltage": collector_voltage,
            "collector_voltage_raw": collector_voltage_raw,
            "relative_humidity": relative_humidity,
            "relative_humidity_raw": relative_humidity_raw,
            "temperature": temperature,
            "temperature_raw": temperature_raw,
            "drum_speed": safe_float(process.get("drum_speed_rpm", "")),
            "working_distance": working_distance,
            "working_distance_raw": working_distance_raw,
            "processability_score": safe_float(
                (experiment.get("results", {}) or {}).get(
                    "processability_grade",
                    ""
                )
            ),
            "process_comments": normalize_text(
                (experiment.get("results", {}) or {}).get(
                    "process_comments",
                    ""
                )
            ),
            "is_incomplete": is_incomplete,
        }

        # -------------------------
        # RESULT
        # -------------------------
        old_results = experiment.get("results", {}) or {}

        if any(has_value(value) for value in old_results.values()):
            results[experiment_id] = {
                "result_id": stable_id(
                    "MIG_RESULT_",
                    experiment_id,
                ),
                "run_id": experiment_id,
                "sem_morphology": normalize_text(
                    old_results.get("sem_comments", "")
                ),
                "filtration_performance": "",
                "notes": (
                    "Historical result migrated. "
                    "Original avg fiber diameter: "
                    + normalize_text(
                        old_results.get("avg_fiber_diameter_nm", "")
                    )
                ),
            }

    output = {
        "projects": list(projects.values()),
        "materials": list(materials.values()),
        "formulations": list(formulations.values()),
        "formulation_components": list(formulation_components.values()),
        "characterizations": list(characterizations.values()),
        "setups": list(setups.values()),
        "runs": list(runs.values()),
        "results": list(results.values()),
    }

    return output


def validate_relationships(output):
    projects = {x["project_id"] for x in output["projects"]}
    formulations = {x["formulation_id"] for x in output["formulations"]}
    materials = {x["material_id"] for x in output["materials"]}
    setups = {x["setup_id"] for x in output["setups"]}
    runs = {x["run_id"] for x in output["runs"]}

    checks = {
        "broken_run_project": sum(
            x["project_id"] not in projects
            for x in output["runs"]
        ),
        "broken_run_formulation": sum(
            x["formulation_id"] not in formulations
            for x in output["runs"]
        ),
        "broken_run_setup": sum(
            x["setup_id"] not in setups
            for x in output["runs"]
        ),
        "broken_component_material": sum(
            x["material_id"] not in materials
            for x in output["formulation_components"]
        ),
        "broken_component_formulation": sum(
            x["formulation_id"] not in formulations
            for x in output["formulation_components"]
        ),
        "broken_characterization_formulation": sum(
            x["formulation_id"] not in formulations
            for x in output["characterizations"]
        ),
        "broken_result_run": sum(
            x["run_id"] not in runs
            for x in output["results"]
        ),
    }

    return checks


def write_test_output(output):
    save_json(output["projects"], TEST_PROJECTS_FILE)
    save_json(output["materials"], TEST_MATERIALS_FILE)
    save_json(output["formulations"], TEST_FORMULATIONS_FILE)
    save_json(
        output["formulation_components"],
        TEST_FORMULATION_COMPONENTS_FILE,
    )
    save_json(
        output["characterizations"],
        TEST_CHARACTERIZATIONS_FILE,
    )
    save_json(output["setups"], TEST_SETUPS_FILE)
    save_json(output["runs"], TEST_RUNS_FILE)
    save_json(output["results"], TEST_RESULTS_FILE)


def main():
    records = load_source_records()

    summary = build_dry_run_summary(records)

    print("")
    print("SECTION A MIGRATION DRY RUN")
    print("===========================")

    for key, value in summary.items():
        print(f"{key}: {value}")

    print("")
    print("Starting full TEST migration...")
    print("No data/section_a files will be modified.")

    output = migrate_records(records)
    checks = validate_relationships(output)
    write_test_output(output)

    print("")
    print("TEST MIGRATION COMPLETE")
    print("=======================")
    print("Projects:", len(output["projects"]))
    print("Materials:", len(output["materials"]))
    print("Formulations:", len(output["formulations"]))
    print("Components:", len(output["formulation_components"]))
    print("Characterizations:", len(output["characterizations"]))
    print("Setups:", len(output["setups"]))
    print("Runs:", len(output["runs"]))
    print("Results:", len(output["results"]))

    print("")
    print("RELATIONSHIP VALIDATION")
    print("=======================")

    for key, value in checks.items():
        print(f"{key}: {value}")

    print("")
    print("Output written only to:")
    print(TEST_OUTPUT_DIR)


if __name__ == "__main__":
    main()