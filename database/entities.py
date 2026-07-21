from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Project:
    project_id: str
    project_code: str
    beas_code: str = ""
    client: str = ""
    rd_leader: str = ""
    year: Optional[int] = None


@dataclass
class Material:
    material_id: str
    material_name: str
    material_type: str
    molecular_weight: str = ""
    supplier: str = ""
    article_number: str = ""
    batch_number: str = ""
    notes: str = ""


@dataclass
class Formulation:
    formulation_id: str
    project_id: str
    polymer_concentration: Optional[float] = None
    notes: str = ""


@dataclass
class FormulationComponent:
    formulation_component_id: str
    formulation_id: str
    material_id: str
    component_role: str
    concentration: Optional[float] = None
    ratio: Optional[float] = None


@dataclass
class Characterization:
    characterization_id: str
    formulation_id: str
    measurement_date: str = ""
    viscosity: Optional[float] = None
    conductivity: Optional[float] = None
    surface_tension: Optional[float] = None
    solid_content: Optional[float] = None
    notes: str = ""


@dataclass
class InjectorModel:
    injector_model_id: str
    name: str
    description: str = ""


@dataclass
class CollectorModel:
    collector_model_id: str
    name: str
    description: str = ""


@dataclass
class Setup:
    setup_id: str
    name: str
    machine: str = ""
    injector_model_id: str = ""
    collector_model_id: str = ""
    number_of_needles: Optional[int] = None
    needle_gauge: str = ""
    platform: str = ""
    custom_configuration: dict = field(default_factory=dict)
    notes: str = ""


@dataclass
class Run:
    run_id: str
    sample_code: str
    project_id: str
    formulation_id: str
    setup_id: str
    date: str = ""
    purpose: str = ""

    flow_rate: Optional[float] = None
    injector_voltage: Optional[float] = None
    collector_voltage: Optional[float] = None
    relative_humidity: Optional[float] = None
    temperature: Optional[float] = None
    drum_speed: Optional[float] = None
    working_distance: Optional[float] = None

    processability_score: Optional[int] = None
    process_comments: str = ""

    is_incomplete: bool = False


@dataclass
class Result:
    result_id: str
    run_id: str
    sem_morphology: str = ""
    filtration_performance: str = ""
    notes: str = ""