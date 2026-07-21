import streamlit as st
import uuid

from database.entities import (
    Formulation,
    FormulationComponent,
    Characterization,
)

from database.section_a_database import (
    add_formulation,
    add_formulation_component,
    add_characterization,
    list_formulations,
    list_formulation_components,
    list_characterizations,
    list_materials,
    list_projects,
)


def render_formulations_page():
    st.title("Formulations & Characterization")

    projects = list_projects()
    materials = list_materials()
    formulations = list_formulations()

    active_project = st.session_state.get("active_project")

    if active_project:
        st.info(
            f"Active Project: "
            f"{active_project.get('project_code', '')}"
        )
    else:
        st.warning(
            "No active project selected. "
            "Please select an active project from the Projects page."
        )

    st.write("---")

    # -----------------------------
    # EXISTING FORMULATIONS
    # -----------------------------
    st.subheader("Existing Formulations")

    if formulations:
        formulation_labels = {
            formulation.get("formulation_id", ""): formulation
            for formulation in formulations
        }

        selected_formulation_id = st.selectbox(
            "Select Formulation",
            list(formulation_labels.keys())
        )

        selected_formulation = formulation_labels[
            selected_formulation_id
        ]

        st.write("### Formulation Details")
        st.json(selected_formulation)

        components = [
            component
            for component in list_formulation_components()
            if component.get("formulation_id")
            == selected_formulation_id
        ]

        if components:
            st.write("### Components")
            st.dataframe(
                components,
                use_container_width=True
            )

        characterization_records = [
            record
            for record in list_characterizations()
            if record.get("formulation_id")
            == selected_formulation_id
        ]

        if characterization_records:
            st.write("### Characterization Records")
            st.dataframe(
                characterization_records,
                use_container_width=True
            )

    else:
        st.info("No formulations have been created yet.")

    st.write("---")

    # -----------------------------
    # CREATE FORMULATION
    # -----------------------------
    st.subheader("Create New Formulation")

    if not active_project:
        st.warning(
            "Select an active project before creating a formulation."
        )

    polymer_materials = [
        material
        for material in materials
        if material.get("material_type") == "polymer"
    ]

    solvent_materials = [
        material
        for material in materials
        if material.get("material_type") == "solvent"
    ]

    polymer_options = {
        (
            f"{material.get('material_name', '')} | "
            f"{material.get('molecular_weight', '')} | "
            f"{material.get('supplier', '')}"
        ): material
        for material in polymer_materials
    }

    solvent_options = {
        (
            f"{material.get('material_name', '')} | "
            f"{material.get('supplier', '')}"
        ): material
        for material in solvent_materials
    }

    with st.form("create_formulation_form"):
        formulation_name = st.text_input(
            "Formulation Name / ID"
        )

        col1, col2 = st.columns(2)

        with col1:
            polymer_label = st.selectbox(
                "Polymer",
                list(polymer_options.keys())
                if polymer_options
                else [""]
            )

            polymer_concentration = st.number_input(
                "Polymer Concentration (%)",
                min_value=0.0,
                max_value=100.0,
                value=10.0,
                step=0.1
            )

            solvent_1_label = st.selectbox(
                "Solvent 1",
                list(solvent_options.keys())
                if solvent_options
                else [""]
            )

            solvent_1_ratio = st.number_input(
                "Solvent 1 Ratio (%)",
                min_value=0.0,
                max_value=100.0,
                value=100.0,
                step=0.1
            )

        with col2:
            use_second_solvent = st.checkbox(
                "Use Solvent 2"
            )

            solvent_2_label = st.selectbox(
                "Solvent 2",
                list(solvent_options.keys())
                if solvent_options
                else [""],
                disabled=not use_second_solvent
            )

            solvent_2_ratio = st.number_input(
                "Solvent 2 Ratio (%)",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=0.1,
                disabled=not use_second_solvent
            )

            notes = st.text_area(
                "Formulation Notes"
            )

        submitted = st.form_submit_button(
            "Create Formulation"
        )

    if submitted:
        if not active_project:
            st.error(
                "An active project is required."
            )
            return

        if not formulation_name.strip():
            st.error(
                "Formulation Name / ID is required."
            )
            return

        if not polymer_options:
            st.error(
                "No polymer materials are available."
            )
            return

        if not solvent_options:
            st.error(
                "No solvent materials are available."
            )
            return

        if use_second_solvent:
            total_ratio = (
                solvent_1_ratio
                + solvent_2_ratio
            )

            if abs(total_ratio - 100.0) > 0.01:
                st.error(
                    "Solvent ratios must sum to 100%."
                )
                return

        selected_polymer = polymer_options[
            polymer_label
        ]

        selected_solvent_1 = solvent_options[
            solvent_1_label
        ]

        formulation_id = formulation_name.strip()

        formulation = Formulation(
            formulation_id=formulation_id,
            project_id=active_project["project_id"],
            polymer_concentration=polymer_concentration,
            notes=notes.strip(),
        )

        try:
            add_formulation(formulation)

            polymer_component = FormulationComponent(
                formulation_component_id=str(uuid.uuid4()),
                formulation_id=formulation_id,
                material_id=selected_polymer["material_id"],
                component_role="polymer",
                concentration=polymer_concentration,
            )

            add_formulation_component(
                polymer_component
            )

            solvent_1_component = FormulationComponent(
                formulation_component_id=str(uuid.uuid4()),
                formulation_id=formulation_id,
                material_id=selected_solvent_1["material_id"],
                component_role="solvent",
                ratio=solvent_1_ratio,
            )

            add_formulation_component(
                solvent_1_component
            )

            if use_second_solvent:
                selected_solvent_2 = solvent_options[
                    solvent_2_label
                ]

                solvent_2_component = FormulationComponent(
                    formulation_component_id=str(uuid.uuid4()),
                    formulation_id=formulation_id,
                    material_id=selected_solvent_2["material_id"],
                    component_role="solvent",
                    ratio=solvent_2_ratio,
                )

                add_formulation_component(
                    solvent_2_component
                )

            st.success(
                f"Formulation created successfully: "
                f"{formulation_id}"
            )

            st.rerun()

        except ValueError as error:
            st.error(str(error))

    st.write("---")

    # -----------------------------
    # ADD CHARACTERIZATION
    # -----------------------------
    st.subheader("Add Characterization")

    formulations = list_formulations()

    if not formulations:
        st.info(
            "Create a formulation before adding characterization."
        )
        return

    formulation_options = {
        formulation.get("formulation_id", ""):
        formulation
        for formulation in formulations
    }

    with st.form("add_characterization_form"):
        characterization_formulation_id = st.selectbox(
            "Formulation",
            list(formulation_options.keys())
        )

        measurement_date = st.text_input(
            "Measurement Date"
        )

        col1, col2 = st.columns(2)

        with col1:
            viscosity = st.number_input(
                "Viscosity",
                min_value=0.0,
                value=0.0,
                step=0.1
            )

            conductivity = st.number_input(
                "Conductivity",
                min_value=0.0,
                value=0.0,
                step=0.1
            )

        with col2:
            surface_tension = st.number_input(
                "Surface Tension",
                min_value=0.0,
                value=0.0,
                step=0.1
            )

            solid_content = st.number_input(
                "Solid Content (%)",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=0.1
            )

        characterization_notes = st.text_area(
            "Characterization Notes"
        )

        characterization_submitted = (
            st.form_submit_button(
                "Add Characterization"
            )
            )
    if characterization_submitted:

        # Prevent completely empty characterization records
        has_measurement = any([
            viscosity > 0,
            conductivity > 0,
            surface_tension > 0,
            solid_content > 0,
        ])

        if not has_measurement:
            st.error(
                "At least one characterization measurement must be entered."
            )
            return

    characterization = Characterization(
        characterization_id=str(uuid.uuid4()),
        formulation_id=characterization_formulation_id,
        measurement_date=measurement_date.strip(),
        viscosity=viscosity,
        conductivity=conductivity,
        surface_tension=surface_tension,
        solid_content=solid_content,
        notes=characterization_notes.strip(),
    )

    try:
        add_characterization(
            characterization
        )

        st.success(
            "Characterization added successfully."
        )

        st.rerun()

    except ValueError as error:
        st.error(str(error))