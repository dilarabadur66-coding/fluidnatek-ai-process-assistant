import streamlit as st
import numpy as np
import pandas as pd
import json
import os
import uuid

from datetime import datetime
from models.memory_engine import SmartMemory
from memory.machine_memory_engine import search_experiment, find_similar_experiments, add_experiment, load_memory 

if 'memory' not in st.session_state:
    st.session_state.memory = SmartMemory()

# ==============================================================================
# 2. INTERFACCIA UTENTE (STREAMLIT DASHBOARD)
# ==============================================================================

st.set_page_config(page_title="Fluidnatek Smart Control", layout="wide")

st.title("🧠 Fluidnatek Process Automation & Smart Memory")
memory_count = len(load_memory())
st.metric("Stored Experiments in Machine Memory", memory_count)

st.write("---")

col1, col2 = st.columns(2)

with col1:
    st.header("📂 Ingestione Dati Ultra-Robusta (CSV / XLSX)")
    st.write("Inserisci il file gigante nella cartella del codice e scrivi il nome sotto:")
    
    nome_file_locale = st.text_input("Nome del file locale con estensione (es. dati.csv oppure dati.xlsx)", value="")
    
    if st.button("🚀 Importa File ed Elabora Modello"):
        if nome_file_locale:
            if os.path.exists(nome_file_locale):
                try:
                    conteggio = 0
                    status_placeholder = st.empty()
                    
                    # ----------------------------------------------------------
                    # CASO CORRETTO: GESTIONE FILE .CSV (Ottimizzato per file Giganti)
                    # ----------------------------------------------------------
                    if nome_file_locale.lower().endswith('.csv'):
                        # 1. Rileva automaticamente se usa la virgola o il punto e virgola italiano
                        with open(nome_file_locale, 'r', encoding='utf-8', errors='ignore') as f:
                            prima_riga = f.readline()
                            separatore = ';' if ';' in prima_riga else ','
                        
                        status_placeholder.info(f"Rilevato file CSV (Separatore: '{separatore}'). Elaborazione a blocchi sicuri...")
                        
                        # 2. Legge a blocchi (chunks) di 10.000 righe per non occupare la RAM
                        for chunk in pd.read_csv(nome_file_locale, sep=separatore, chunksize=10000, low_memory=False):
                            # Pulizia totale delle colonne: tutte in minuscolo e senza spazi
                            chunk.columns = chunk.columns.str.strip().str.lower()
                            
                            for _, row in chunk.iterrows():
                                # Legge i dati accettando sia i nomi lunghi che brevi delle colonne
                                st.session_state.memory.registra_operazione(
                                    polymer=str(row.get('polimero', 'PCL')),
                                    solvent=str(row.get('solvente', 'ACETONE')),
                                    concentration=float(row.get('concentrazione_percentuale', row.get('concentrazione', 8.0))),
                                    voltage=float(row.get('voltaggio_kv', row.get('voltaggio', 15.0))),
                                    distance=float(row.get('distanza_cm', row.get('distanza', 15.0))),
                                    flow_rate=float(row.get('flow_rate_ml_h', row.get('flow_rate', 1.2))),
                                    quality_output=float(row.get('indice_qualita', row.get('qualita', 80.0))),
                                    operator=str(row.get('operatore', 'Tech_Automation')),
                                    db_table=str(row.get('tabella_sql', 'telemetry_pcl'))
                                )
                                conteggio += 1
                            status_placeholder.text(f"⏳ Avanzamento: {conteggio} righe inserite nel Database...")
                    
                    # ----------------------------------------------------------
                    # CASO 2: GESTIONE FILE .XLSX (Solo se di dimensioni normali)
                    # ----------------------------------------------------------
                    else:
                        status_placeholder.info("Caricamento file Excel in corso... Attesa lettura foglio.")
                        df_excel = pd.read_excel(nome_file_locale)
                        df_excel.columns = df_excel.columns.str.strip().str.lower()
                        
                        for _, row in df_excel.iterrows():
                            st.session_state.memory.registra_operazione(
                                polymer=str(row.get('polimero', 'PCL')),
                                solvent=str(row.get('solvente', 'ACETONE')),
                                concentration=float(row.get('concentrazione_percentuale', row.get('concentrazione', 8.0))),
                                voltage=float(row.get('voltaggio_kv', row.get('voltaggio', 15.0))),
                                distance=float(row.get('distanza_cm', row.get('distanza', 15.0))),
                                flow_rate=float(row.get('flow_rate_ml_h', row.get('flow_rate', 1.2))),
                                quality_output=float(row.get('indice_qualita', row.get('qualita', 80.0))),
                                operator=str(row.get('operatore', 'Tech_Automation')),
                                db_table=str(row.get('tabella_sql', 'telemetry_pcl'))
                            )
                            conteggio += 1
                    
                    status_placeholder.success(f"🎉 Successo Totale! Elaborate {conteggio} righe. Memoria OLS aggiornata e stabile al 100%!")
                    
                except Exception as e:
                    st.error(f"Errore durante la lettura o elaborazione dei dati: {e}")
            else:
                st.error(f"File '{nome_file_locale}' non trovato. Controlla che sia scritto bene e sia dentro la cartella del codice.")
        else:
            st.warning("Inserisci il nome del file prima di procedere.")

    st.write("---")
    st.header("🚀 Registra Singolo Esperimento (Manuale)")
    with st.form("ingestion_form"):
        operator = st.text_input("ID Operatore", value="Tech_Automation")
        db_table = st.text_input("Tabella SQL Atterraggio", value="telemetry_pcl")
        p_type = st.text_input("Polimero", value="PCL")
        s_type = st.text_input("Solvente", value="ACETONE")
        conc = st.number_input("Concentrazione soluzione (%)", value=8.0, step=0.1)
        volt = st.number_input("Voltaggio applicato (kV)", value=15.0, step=0.1)
        dist = st.number_input("Distanza ago-collettore (cm)", value=15.0, step=0.1)
        flow = st.number_input("Flow Rate reale (ml/h)", value=1.2, step=0.1)
        quality = st.slider("Indice Qualità registrato", 0.0, 100.0, 80.0)
        if st.form_submit_button("Salva ed esegui Fit"):
            sid = st.session_state.memory.registra_operazione(p_type, s_type, conc, volt, dist, flow, quality, operator, db_table)
            st.success(f"✓ Registrato! ID: {sid}")

with col2:
    st.header("🧠 Machine Memory Search")

    pred_formula = st.text_input("Formula", value="")
    pred_flow = st.number_input("Flow Rate (mL/h)", value=1.6, step=0.1, key="search_flow")
    pred_volt = st.number_input("Voltage (kV)", value=16.0, step=0.1, key="search_voltage")
    pred_temp = st.number_input("Temperature (°C)", value=25.0, step=0.1, key="search_temp")

    search_clicked = st.button("🔍 Search Machine Memory")

    if search_clicked:
        matches = search_experiment(flow=pred_flow, voltage=pred_volt, temperature=pred_temp)

        if matches:
            exp = matches[0]
            st.success(f"✅ KNOWN PROCESS WINDOW — {len(matches)} match(es) found")
            st.subheader("🧠 Previous Experiment Result")
            st.write(f"**Formula:** {exp.get('Fórmula', exp.get('formula', 'N/A'))}")
            st.write(f"**Flow Rate:** {exp.get('Q1 (mL/h)', exp.get('flow', 'N/A'))} mL/h")
            st.write(f"**Voltage:** {exp.get('HV+ (KV)', exp.get('voltage', 'N/A'))} kV")
            st.write(f"**Temperature:** {exp.get('T (ºC)', exp.get('temperature', 'N/A'))} °C")
            st.write(f"**Grade:** {exp.get('Grado de Procesabilidad', exp.get('grade', 'N/A'))}")
            st.write(f"**Comments:** {exp.get('Comentarios del Proceso', exp.get('comments', 'No comments found.'))}")

        else:
            st.warning("⚠️ NEW PROCESS CONDITION")
            similar_experiments = find_similar_experiments(pred_flow, pred_volt, pred_temp)

            if similar_experiments:
                st.info("🟡 Similar experiments found")

                for i, exp in enumerate(similar_experiments, start=1):
                    with st.container(border=True):
                        st.subheader(f"Similar Experiment #{i}")
                        st.write(f"**Formula:** {exp.get('Fórmula', exp.get('formula', 'N/A'))}")
                        st.write(f"**Flow:** {exp.get('Q1 (mL/h)', exp.get('flow', 'N/A'))}")
                        st.write(f"**Voltage:** {exp.get('HV+ (KV)', exp.get('voltage', 'N/A'))}")
                        st.write(f"**Temperature:** {exp.get('T (ºC)', exp.get('temperature', 'N/A'))}")
                        st.write(f"**Grade:** {exp.get('Grado de Procesabilidad', exp.get('grade', 'N/A'))}")
                        st.write(f"**Comments:** {exp.get('Comentarios del Proceso', exp.get('comments', 'No comments found.'))}")

    st.write("---")
    st.subheader("💾 Save New Experiment")

    new_grade = st.number_input("New Experiment Grade", min_value=1, max_value=4, value=3, key="new_grade")
    new_comments = st.text_area("New Experiment Comments", key="new_comments")

    if st.button("💾 Save New Experiment", key="save_new_experiment"):
        add_experiment(
            formula=pred_formula,
            flow=pred_flow,
            voltage=pred_volt,
            temperature=pred_temp,
            grade=new_grade,
            comments=new_comments,
            source="Streamlit App"
        )
        st.success("✅ New experiment saved successfully!")