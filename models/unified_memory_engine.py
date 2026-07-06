import json
from pathlib import Path


DEFAULT_UNIFIED_DATABASE_PATH = "data/processed/unified_experiments_database.json"


class UnifiedMemory:
    def __init__(self, database_path=DEFAULT_UNIFIED_DATABASE_PATH):
        self.database_path = Path(database_path)
        self.experiments = self.load_database()

    def load_database(self):
        if not self.database_path.exists():
            return []

        with open(self.database_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def count_experiments(self):
        return len(self.experiments)

    def get_all_experiments(self):
        return self.experiments

    def search_by_formula(self, formula_id):
        results = []

        for experiment in self.experiments:
            if str(experiment.get("formula_id", "")).lower() == str(formula_id).lower():
                results.append(experiment)

        return results

    def search_by_project(self, project_code):
        results = []

        for experiment in self.experiments:
            if str(experiment.get("project_code", "")).lower() == str(project_code).lower():
                results.append(experiment)

        return results

    def search_by_material(self, material_name):
        results = []

        for experiment in self.experiments:
            materials = experiment.get("materials", [])

            for material in materials:
                if str(material_name).lower() in str(material.get("material_name", "")).lower():
                    results.append(experiment)
                    break

        return results

    def get_successful_experiments(self, min_grade=3):
        results = []

        for experiment in self.experiments:
            process = experiment.get("process_parameters", {})
            grade = process.get("processability_grade", "")

            try:
                if float(grade) >= min_grade:
                    results.append(experiment)
            except Exception:
                continue

        return results

    def summarize_experiment(self, experiment):
        process = experiment.get("process_parameters", {})
        setup = experiment.get("setup", {})
        composition = experiment.get("solution_composition", {})
        properties = experiment.get("solution_properties", {})

        return {
            "experiment_id": experiment.get("experiment_id", ""),
            "project_code": experiment.get("project_code", ""),
            "formula_id": experiment.get("formula_id", ""),
            "sample_code": experiment.get("sample_code", ""),
            "machine": setup.get("machine", ""),
            "flow_rate_q1_ml_h": process.get("flow_rate_q1_ml_h", ""),
            "hv_positive_kv": process.get("hv_positive_kv", ""),
            "hv_negative_kv": process.get("hv_negative_kv", ""),
            "temperature_c": process.get("temperature_c", ""),
            "relative_humidity_percent": process.get("relative_humidity_percent", ""),
            "dz_mm": process.get("dz_mm", ""),
            "processability_grade": process.get("processability_grade", ""),
            "avg_fiber_diameter_nm": experiment.get("results", {}).get("avg_fiber_diameter_nm", ""),
            "polymer_a": composition.get("polymer_a", ""),
            "polymer_a_percentage": composition.get("polymer_a_percentage", ""),
            "solvent_a": composition.get("solvent_a", ""),
            "solvent_a_percentage": composition.get("solvent_a_percentage", ""),
            "viscosity_cP": properties.get("viscosity_cP", ""),
            "conductivity_microS": properties.get("conductivity_microS", ""),
        }