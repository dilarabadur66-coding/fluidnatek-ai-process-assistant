class RecommendationEngine:
    def __init__(self, memory):
        self.memory = memory

    def find_experiments_by_material(self, material_name):
        return self.memory.search_by_material(material_name)

    def find_best_experiments(self, experiments, min_grade=3):
        best_experiments = []

        for experiment in experiments:
            process = experiment.get("process_parameters", {})
            grade = process.get("processability_grade", "")

            try:
                if float(grade) >= min_grade:
                    best_experiments.append(experiment)
            except Exception:
                continue

        return best_experiments

    def suggest_process_parameters(self, experiments):
        values = {
            "flow_rate_q1_ml_h": [],
            "hv_positive_kv": [],
            "hv_negative_kv": [],
            "temperature_c": [],
            "relative_humidity_percent": [],
            "dz_mm": [],
        }

        for experiment in experiments:
            process = experiment.get("process_parameters", {})

            for key in values:
                value = process.get(key, "")

                try:
                    values[key].append(float(value))
                except Exception:
                    continue

        suggestions = {}

        for key, numeric_values in values.items():
            if numeric_values:
                suggestions[key] = {
                    "min": min(numeric_values),
                    "max": max(numeric_values),
                    "average": sum(numeric_values) / len(numeric_values),
                }
            else:
                suggestions[key] = {
                    "min": None,
                    "max": None,
                    "average": None,
                }

        return suggestions

    def recommend_next_experiment(
        self,
        material_name,
        min_grade=3
    ):
        matching_experiments = self.find_experiments_by_material(material_name)
        best_experiments = self.find_best_experiments(
            matching_experiments,
            min_grade=min_grade
        )

        suggestions = self.suggest_process_parameters(best_experiments)

        return {
            "material_name": material_name,
            "matching_experiments_count": len(matching_experiments),
            "best_experiments_count": len(best_experiments),
            "suggested_process_window": suggestions,
            "reference_experiments": [
                self.memory.summarize_experiment(experiment)
                for experiment in best_experiments
            ],
        }