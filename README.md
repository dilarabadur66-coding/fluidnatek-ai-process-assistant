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
Excel Project Files
        |
        v
Excel Loader
        |
        v
Processed JSON Databases
        |
        v
Unified Experiment Database
        |
        v
Similarity Search
        |
        v
AI Process Interpretation
        |
        v
Recommended Process Window


## Current Status

Current historical memory contains:

- 108 imported historical experiments
- 4 historical projects
- User-generated experiments from the Streamlit interface

The current version supports:
- historical similarity search
- AI-assisted process interpretation
- process window recommendation
- experiment registration
- sample code tracking
```
