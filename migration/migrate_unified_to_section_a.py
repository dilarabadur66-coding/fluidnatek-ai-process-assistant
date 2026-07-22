import json
from pathlib import Path


SOURCE_FILE = Path(
    "data/processed/unified_experiments_database.json"
)


def load_source_records():
    with open(
        SOURCE_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def has_value(value):
    return value not in [
        "",
        None,
        [],
        {},
    ]


def normalize_text(value):
    if value is None:
        return ""

    return str(value).strip()


def build_dry_run_summary(records):
    project_ids = set()
    formulation_ids = set()
    setup_ids = set()
    run_ids = set()

    result_count = 0
    incomplete_run_count = 0
    records_with_composition = 0
    records_with_properties = 0
    records_with_results = 0

    for index, experiment in enumerate(
        records,
        start=1
    ):
        project_code = normalize_text(
            experiment.get(
                "project_code",
                ""
            )
        )

        if project_code:
            project_ids.add(
                project_code
            )

        formula_id = normalize_text(
            experiment.get(
                "formula_id",
                ""
            )
        )

        if formula_id:
            formulation_ids.add(
                (
                    project_code,
                    formula_id
                )
            )

        composition = experiment.get(
            "solution_composition",
            {}
        )

        if composition:
            records_with_composition += 1

        properties = experiment.get(
            "solution_properties",
            {}
        )

        if properties:
            records_with_properties += 1

        setup = experiment.get(
            "setup",
            {}
        )

        setup_id = normalize_text(
            setup.get(
                "setup_id",
                ""
            )
        )

        if not setup_id:
            setup_number = normalize_text(
                setup.get(
                    "setup_number",
                    ""
                )
            )

            machine = normalize_text(
                setup.get(
                    "machine",
                    ""
                )
            )

            setup_id = (
                f"{project_code}|"
                f"{setup_number}|"
                f"{machine}"
            )

        if setup_id.strip("|"):
            setup_ids.add(
                setup_id
            )

        experiment_id = normalize_text(
            experiment.get(
                "experiment_id",
                ""
            )
        )

        if not experiment_id:
            experiment_id = (
                f"historical_run_{index}"
            )

        run_ids.add(
            experiment_id
        )

        process = experiment.get(
            "process_parameters",
            {}
        )

        results = experiment.get(
            "results",
            {}
        )

        processability = results.get(
            "processability_grade",
            process.get(
                "processability_grade",
                ""
            )
        )

        process_comments = results.get(
            "process_comments",
            process.get(
                "process_comments",
                ""
            )
        )

        sem_comments = results.get(
            "sem_comments",
            process.get(
                "sem_comments",
                ""
            )
        )

        fiber_diameter = results.get(
            "avg_fiber_diameter_nm",
            process.get(
                "avg_fiber_diameter_nm",
                ""
            )
        )

        if any([
            has_value(processability),
            has_value(process_comments),
            has_value(sem_comments),
            has_value(fiber_diameter),
        ]):
            records_with_results += 1
            result_count += 1

        required_run_fields = [
            project_code,
            formula_id,
            process.get(
                "flow_rate_q1_ml_h"
            ),
            process.get(
                "hv_positive_kv"
            ),
            process.get(
                "temperature_c"
            ),
            process.get(
                "relative_humidity_percent"
            ),
        ]

        if not all(
            has_value(value)
            for value
            in required_run_fields
        ):
            incomplete_run_count += 1

    return {
        "source_experiments":
            len(records),

        "unique_projects":
            len(project_ids),

        "unique_formulations":
            len(formulation_ids),

        "unique_setups":
            len(setup_ids),

        "runs_to_create":
            len(run_ids),

        "results_to_create":
            result_count,

        "records_with_composition":
            records_with_composition,

        "records_with_solution_properties":
            records_with_properties,

        "records_with_results":
            records_with_results,

        "incomplete_runs":
            incomplete_run_count,
    }


def main():
    records = load_source_records()

    summary = build_dry_run_summary(
        records
    )

    print("")
    print(
        "SECTION A MIGRATION DRY RUN"
    )
    print(
        "==========================="
    )

    for key, value in summary.items():
        print(
            f"{key}: {value}"
        )

    print("")
    print(
        "DRY RUN ONLY."
    )
    print(
        "No Section A database files "
        "were modified."
    )


if __name__ == "__main__":
    main()