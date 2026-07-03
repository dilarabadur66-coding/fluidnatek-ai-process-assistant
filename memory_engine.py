import json
import os
import uuid
import numpy as np
import pandas as pd

from datetime import datetime
class SmartMemory:
    def __init__(self, storage_file="smart_memory_database.json"):
        self.storage_file = storage_file
        self.history = self._load_database()
        if not self.history:
            self._bootstrap_initial_data()
        self.model_coefficients = {}
        self._rebuild_models_from_history()

    def _load_database(self):
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_database(self):
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=4, ensure_ascii=False)
        except Exception:
            pass

    def _bootstrap_initial_data(self):
        baseline_experiments = [
            {"conc": 8.0, "flow": 1.0, "volt": 15.0, "quality": 75.0},
            {"conc": 8.0, "flow": 1.5, "volt": 15.0, "quality": 85.0},
            {"conc": 10.0, "flow": 1.2, "volt": 15.0, "quality": 82.0},
            {"conc": 8.0, "flow": 1.2, "volt": 18.0, "quality": 84.0}
        ]
        for i, exp in enumerate(baseline_experiments):
            session_id = f"EXP_PCL_BASELINE_{i+1}"
            self.history[session_id] = {
                "metadata": {"operator_name": "System_Bootstrap", "target_db_table": "telemetry_pcl", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
                "inputs": {"polymer_type": "PCL", "solvent_type": "ACETONE", "solution_percentage": exp["conc"], "target_voltage_kv": exp["volt"], "collector_distance_cm": 15.0, "flow_rate_ml_h": exp["flow"]},
                "outputs": {"process_quality_index": exp["quality"]}
            }
        self._save_database()

    def registra_operazione(self, polymer: str, solvent: str, concentration: float, voltage: float, distance: float, flow_rate: float, quality_output: float, operator: str, db_table: str):
        unique_suffix = uuid.uuid4().hex[:6]
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id = f"EXP_{str(polymer).upper()}_{timestamp_str}_{unique_suffix}"
        
        self.history[session_id] = {
            "metadata": {"operator_name": str(operator), "target_db_table": str(db_table), "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
            "inputs": {"polymer_type": str(polymer).upper().strip(), "solvent_type": str(solvent).upper().strip(), "solution_percentage": float(concentration), "target_voltage_kv": float(voltage), "collector_distance_cm": float(distance), "flow_rate_ml_h": float(flow_rate)},
            "outputs": {"process_quality_index": float(quality_output)}
        }
        self._save_database()
        self._rebuild_models_from_history()
        return session_id

    def _rebuild_models_from_history(self):
        if not self.history:
            return
        groups = {}
        for x_id, data in self.history.items():
            try:
                key = f"{data['inputs']['polymer_type']}_{data['inputs']['solvent_type']}"
                if key not in groups:
                    groups[key] = []
                groups[key].append([
                    float(data['inputs']['solution_percentage']),
                    float(data['inputs']['flow_rate_ml_h']),
                    float(data['inputs']['target_voltage_kv']),
                    float(data['outputs']['process_quality_index'])
                ])
            except Exception:
                continue
                
        for key, records in groups.items():
            if len(records) < 3:
                continue
            try:
                df = pd.DataFrame(records, columns=['conc', 'flow', 'volt', 'target'])
                X = df[['conc', 'flow', 'volt']].copy()
                X['intercept'] = 1.0
                y = df['target']
                X_mat = X.to_numpy()
                y_mat = y.to_numpy()
                beta = np.linalg.pinv(X_mat.T @ X_mat) @ X_mat.T @ y_mat
                self.model_coefficients[key] = beta
            except Exception:
                pass

    def invert_process_realtime(self, polymer: str, solvent: str, concentration: float, voltage: float, target_quality: float) -> dict:
        key = f"{str(polymer).upper().strip()}_{str(solvent).upper().strip()}"
        beta = self.model_coefficients.get(key)
        if beta is None:
            return {"estimated_flow_rate_ml_h": 1.5, "status": "FALLBACK_NO_HISTORICAL_DATA"}
        try:
            b_conc = float(beta[0])
            b_flow = float(beta[1])
            b_volt = float(beta[2])
            intercept = float(beta[3])
            if abs(b_flow) < 1e-5:
                b_flow = 1.0
            calculated_flow = (float(target_quality) - intercept - (b_conc * float(concentration)) - (b_volt * float(voltage))) / b_flow
            return {
                "estimated_flow_rate_ml_h": round(max(0.1, float(calculated_flow)), 2),
                "status": "CALCULATED_VIA_INVERSE_REGRESSION"
            }
        except Exception:
            return {"estimated_flow_rate_ml_h": 1.5, "status": "ERROR_IN_CALCULATION"}
       