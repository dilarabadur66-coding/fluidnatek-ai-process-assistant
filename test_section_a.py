from database.entities import (
    Project,
    Material,
    Formulation,
    FormulationComponent,
    Characterization,
    InjectorModel,
    CollectorModel,
    Setup,
    Run,
    Result,
)

from database.section_a_database import (
    add_project,
    add_material,
    add_formulation,
    add_formulation_component,
    add_characterization,
    add_injector_model,
    add_collector_model,
    add_setup,
    add_run,
    add_result,
)


print("Starting Section A relationship test...")


# 1. PROJECT

project = Project(
    project_id="TEST_PROJECT_001",
    project_code="TEST_TPU_PROJECT",
    beas_code="TEST_BEAS",
    client="Test Client",
    rd_leader="Test User",
    year=2026,
)

add_project(project)

print("Project created successfully.")


# 2. MATERIALS

polymer = Material(
    material_id="TEST_MATERIAL_TPU",
    material_name="TPU Test Polymer",
    material_type="polymer",
    molecular_weight="Test Molecular Weight",
    supplier="Test Supplier",
    article_number="TEST_ARTICLE_001",
    batch_number="TEST_BATCH_001",
)

solvent = Material(
    material_id="TEST_MATERIAL_DMF",
    material_name="DMF",
    material_type="solvent",
    supplier="Test Supplier",
)

add_material(polymer)
add_material(solvent)

print("Materials created successfully.")


# 3. FORMULATION

formulation = Formulation(
    formulation_id="TEST_FORMULATION_001",
    project_id=project.project_id,
    polymer_concentration=10.0,
    notes="Test formulation",
)

add_formulation(formulation)


polymer_component = FormulationComponent(
    formulation_component_id="TEST_COMPONENT_POLYMER",
    formulation_id=formulation.formulation_id,
    material_id=polymer.material_id,
    component_role="polymer",
    concentration=10.0,
)

solvent_component = FormulationComponent(
    formulation_component_id="TEST_COMPONENT_SOLVENT",
    formulation_id=formulation.formulation_id,
    material_id=solvent.material_id,
    component_role="solvent",
    ratio=100.0,
)

add_formulation_component(polymer_component)
add_formulation_component(solvent_component)

print("Formulation and components created successfully.")


# 4. CHARACTERIZATION

characterization = Characterization(
    characterization_id="TEST_CHARACTERIZATION_001",
    formulation_id=formulation.formulation_id,
    measurement_date="2026-07-21",
    viscosity=500.0,
    conductivity=20.0,
    surface_tension=35.0,
    solid_content=10.0,
)

add_characterization(characterization)

print("Characterization created successfully.")


# 5. INJECTOR AND COLLECTOR MODELS

injector = InjectorModel(
    injector_model_id="TEST_INJECTOR_001",
    name="Test Injector",
)

collector = CollectorModel(
    collector_model_id="TEST_COLLECTOR_001",
    name="Test Drum Collector",
)

add_injector_model(injector)
add_collector_model(collector)

print("Injector and collector created successfully.")


# 6. FLEXIBLE SETUP

setup = Setup(
    setup_id="TEST_SETUP_001",
    name="Test Custom Setup",
    machine="Fluidnatek Test Machine",
    injector_model_id=injector.injector_model_id,
    collector_model_id=collector.collector_model_id,
    number_of_needles=4,
    needle_gauge="21G",
    platform="Test Platform",
    custom_configuration={
        "custom_note": "Temporary test configuration"
    },
)

add_setup(setup)

print("Setup created successfully.")


# 7. EXPERIMENTAL RUN

run = Run(
    run_id="TEST_RUN_001",
    sample_code="TEST_SAMPLE_001",
    project_id=project.project_id,
    formulation_id=formulation.formulation_id,
    setup_id=setup.setup_id,
    date="2026-07-21",
    purpose="Section A relationship test",
    flow_rate=1.0,
    injector_voltage=20.0,
    collector_voltage=-2.0,
    relative_humidity=40.0,
    temperature=25.0,
    drum_speed=500.0,
    working_distance=150.0,
    processability_score=4,
    process_comments="Successful test run",
)

add_run(run)

print("Run created successfully.")


# 8. RESULT

result = Result(
    result_id="TEST_RESULT_001",
    run_id=run.run_id,
    sem_morphology="Uniform fibers",
    filtration_performance="Test filtration result",
    notes="Section A test result",
)

add_result(result)

print("Result created successfully.")


print("")
print("------------------------------------------")
print("SECTION A RELATIONSHIP TEST SUCCESSFUL")
print("------------------------------------------")
print("Project -> Formulation")
print("Formulation -> Materials")
print("Formulation -> Characterization")
print("Injector + Collector -> Setup")
print("Project + Formulation + Setup -> Run")
print("Run -> Result")