# Fluidnatek AI Process Assistant

## Project Overview

This project is an AI-assisted experimental memory system for electrospinning processes performed with Fluidnatek equipment.

The main purpose is to collect historical project data, convert it into a common structure, search for similar experiments, estimate expected results, and support engineers when selecting process parameters.

## Main Objectives

- Use the current Excel template as the reference structure
- Import historical project files
- Store project, formulation, setup, process, and result data
- Search for similar historical experiments
- Estimate processability and fiber diameter when data is available
- Recommend successful process parameter windows
- Save new experiments
- Track experiments using a sample code

## Reference Excel Structure

The system uses the following sheets from the reference Excel template:

- `Lista_materiales`
- `Detalles_proyecto`
- `Materiales`
- `Soluciones_composicion`
- `Soluciones_propiedades`
- `Setup`
- `Parametros_proceso`

The following sheets are not stored because they are used only for calculations, printing, or stock control:

- `Formulacion`
- `Imprimir`

## Data Workflow

```text
# Fluidnatek AI Process Assistant

## Project Overview

This project is an AI-assisted experimental memory system for electrospinning processes performed with Fluidnatek equipment.

The main purpose is to collect historical project data, convert it into a common structure, search for similar experiments, estimate expected results, and support engineers during process parameter selection.

The implementation follows the current Fluidnatek Excel template proposed as the reference structure for future developments and historical project conversion.

---

## Main Objectives

- Use the current Excel template as the reference structure.
- Import historical electrospinning projects.
- Store project, formulation, setup, process and result information.
- Build a unified experimental memory database.
- Search for similar historical experiments.
- Estimate expected processability and fiber diameter.
- Recommend successful process parameter windows.
- Support decision making during process optimization.
- Register and store new experiments.
- Track experiments using sample codes.

---

## Reference Excel Structure

The system uses the following sheets from the reference Excel template:

- `Lista_materiales`
- `Detalles_proyecto`
- `Materiales`
- `Soluciones_composicion`
- `Soluciones_propiedades`
- `Setup`
- `Parametros_proceso`

The following sheets are intentionally ignored because they are only used for calculations, printing or stock control:

- `Formulacion`
- `Imprimir`

---

## Minimum Stored Information

### Project Information
- Project code
- Client
- R&D leader
- Date

### Formulation Information
- Formula ID
- Polymer(s)
- Polymer concentration(s)
- Solvent(s)
- Solvent ratio(s)

### Solution Properties
- Viscosity
- Conductivity

### Setup Information
- Setup number
- Machine
- Platform

### Process Parameters
- Q1 (mL/h)
- HV+ (kV)
- HV- (kV)
- Temperature (°C)
- Relative Humidity (%)
- Position Y
- dZ (mm)

### Results
- Processability grade
- Process comments
- SEM comments
- Average fiber diameter (nm)

### Traceability
- Sample code

---

## Data Workflow

```text
Historical Excel Files
        |
        v
Excel Import Pipeline
        |
        v
Processed Databases
        |
        v
Unified Experiment Database
        |
        v
Similarity Search Engine
        |
        v
AI Interpretation Layer
        |
        v
Recommended Process Window
        |
        v
Experiment Registration
```

---

## Current Application Workflow

1. The user selects:
   - Project
   - Formula
   - Polymer
   - Solvent
   - Machine

2. The user enters the critical electrospinning parameters.

3. The application searches the historical memory.

4. Similar experiments are filtered using a similarity threshold.

5. The application displays:
   - Relevant historical experiments
   - Historical success rate
   - Expected processability
   - Expected fiber diameter
   - Recommended process ranges
   - Historical engineer comments
   - Risk warnings

6. The user evaluates the suggested historical information.

7. The user can save the current experiment.

8. A sample code is stored to support future characterization linkage.

---

## Current Status

Current historical memory contains:

- 108 imported historical experiments
- 4 imported historical projects
- User-generated experiments from the Streamlit interface

Imported historical projects:

- `1_2021_CROXX_Nov.xlsm`
- `3_2023_PAN.xlsm`
- `5_POCS_CAF.xlsm`
- `6_POCS_PEO.xlsm`

Historical files are stored in:

```text
data/raw/historical_projects/
```

---

## Current Features

The current implementation supports:

- Historical experiment ingestion
- Unified experiment database
- Similarity search
- AI-assisted process interpretation
- Historical success rate estimation
- Processability estimation
- Fiber diameter estimation
- Recommended process windows
- Historical engineer comments retrieval
- Experiment registration
- Sample code tracking

---

## Main Database

The central memory currently uses:

```text
data/processed/unified_experiments_database.json
```

Each experiment contains information related to:

```text
experiment_id
sample_code
project_code
project
materials
formula_id
solution_composition
solution_properties
setup
process_parameters
results
source
```

---

## Installation

Install the required packages:

```bash
pip install streamlit pandas openpyxl
```

---

## Run Application

Run the application using:

```bash
streamlit run app.py
```

The application will be available at:

```text
http://localhost:8501
```

---

## Current Limitations

- Historical templates contain structural differences.
- Some historical experiments do not contain fiber diameter information.
- Some historical experiments contain incomplete formulation information.
- Materials are not yet managed in an independent database.
- Characterization data is not yet linked through sample codes.
- The current Streamlit implementation is still concentrated inside a single `app.py` file.

---

## Future Development

Planned improvements include:

- Additional historical project ingestion.
- Independent materials database.
- Formulation normalization.
- Characterization database integration.
- SEM image linkage through sample codes.
- Improved prediction algorithms.
- More advanced recommendation models.
- Modular application architecture.
- Automated testing and validation.

---

## Author

Developed during an R&D internship project focused on electrospinning process intelligence and historical experiment retrieval for Fluidnatek technologies.

---
```
