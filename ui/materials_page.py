import streamlit as st
import uuid

from database.entities import Material
from database.section_a_database import (
    add_material,
    list_materials,
)


def render_materials_page():
    st.title("Materials")

    materials = list_materials()

    st.subheader("Existing Materials")

    if materials:
        material_labels = {
            (
                f"{material.get('material_name', '')} | "
                f"{material.get('molecular_weight', '')} | "
                f"{material.get('supplier', '')}"
            ): material
            for material in materials
        }

        selected_label = st.selectbox(
            "Select Material",
            list(material_labels.keys())
        )

        selected_material = material_labels[selected_label]

        st.write("### Material Details")
        st.json(selected_material)

    else:
        st.info("No materials have been created yet.")

    st.write("---")

    st.subheader("Create New Material")

    with st.form("create_material_form"):
        col1, col2 = st.columns(2)

        with col1:
            material_name = st.text_input("Material Name")

            material_type = st.selectbox(
                "Material Type",
                [
                    "polymer",
                    "solvent",
                    "additive",
                    "other",
                ]
            )

            molecular_weight = st.text_input(
                "Molecular Weight"
            )

            supplier = st.text_input(
                "Supplier"
            )

        with col2:
            article_number = st.text_input(
                "Article / Reference Number"
            )

            batch_number = st.text_input(
                "Batch Number"
            )

            notes = st.text_area(
                "Notes"
            )

        submitted = st.form_submit_button(
            "Create Material"
        )

    if submitted:
     if not material_name.strip():
        st.error("Material Name is required.")
        return

    existing_materials = list_materials()

    duplicate_material = any(
        material.get("material_name", "").strip().lower()
        == material_name.strip().lower()
        and material.get("molecular_weight", "").strip().lower()
        == molecular_weight.strip().lower()
        and material.get("supplier", "").strip().lower()
        == supplier.strip().lower()
        and material.get("article_number", "").strip().lower()
        == article_number.strip().lower()
        and material.get("batch_number", "").strip().lower()
        == batch_number.strip().lower()
        for material in existing_materials
    )

    if duplicate_material:
        st.error(
            "This material already exists with the same traceability information."
        )
        return

    material = Material(
        material_id=str(uuid.uuid4()),
        material_name=material_name.strip(),
        material_type=material_type,
        molecular_weight=molecular_weight.strip(),
        supplier=supplier.strip(),
        article_number=article_number.strip(),
        batch_number=batch_number.strip(),
        notes=notes.strip(),
    )

    try:
        add_material(material)

        st.success(
            f"Material created successfully: "
            f"{material_name}"
        )

        st.rerun()

    except ValueError as error:
        st.error(str(error))