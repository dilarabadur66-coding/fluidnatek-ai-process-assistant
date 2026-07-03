import pandas as pd
import os

def live_dynamic_search():
    print("🚀 SMART MEMORY 3.0 - LIVE MULTI-VARIABLE SEARCH ENGINE...")
    file_path = "Process_optimization.xlsm"
    
    if not os.path.exists(file_path):
        print(f"❌ ERROR: '{file_path}' not found!")
        return

    try:
        # Load the latest state of the machine data (skipping merged header via header=1)
        df = pd.read_excel(file_path, sheet_name='PARÁMETROS', header=1)
        df.columns = df.columns.str.strip()
        
        # Clean completely empty rows and unnamed tracking columns
        df = df.dropna(subset=[df.columns[0], df.columns[1]], how='all')
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    except Exception as e:
        print(f"❌ ERROR: Failed to read Excel file. Details: {e}")
        return

    print(f"\n📊 Live database scanned successfully: {len(df)} active records found.")
    print("🛠️ Available System Variables in Axis:")
    print(", ".join(list(df.columns)))
    print("-" * 70)
    
    print("\n🤖 ENTER PARAMETERS TO CHECK PREVIOUS LIVE STATES:")
    # Prompt commands for the engineers
    input_formula = input("🧪 Formula Code (e.g., FTK-CelAc-003 or leave blank): ").strip()
    input_flow = input("💧 Flow Rate - Q1 (mL/h) (e.g., 1.5 or leave blank): ").strip()
    input_hv = input("⚡ Voltage - HV+ (KV) (e.g., 10 or leave blank): ").strip()
    input_temp = input("🌡️ Temperature - T (ºC) (e.g., 20 or leave blank): ").strip()

    print("\n🔍 Matching multi-variable criteria across all data rows...")
    print("-" * 70)

    # Initialize dynamic filtering mask
    mask = pd.Series([True] * len(df), index=df.index)

    # Apply filters dynamically if input is provided by the engineer
    if input_formula:
        formula_col = next((c for c in df.columns if 'fórm' in c.lower() or 'form' in c.lower()), None)
        if formula_col:
            mask &= df[formula_col].astype(str).str.contains(input_formula, case=False, na=False)
            
    if input_flow:
        flow_col = next((c for c in df.columns if 'q1' in c.lower()), None)
        if flow_col:
            df[flow_col] = df[flow_col].astype(str).str.replace(',', '.')
            mask &= (df[flow_col] == input_flow.replace(',', '.'))
            
    if input_hv:
        hv_col = next((c for c in df.columns if 'hv+' in c.lower() or 'hv' in c.lower()), None)
        if hv_col:
            mask &= (df[hv_col].astype(str).str.strip() == input_hv)

    if input_temp:
        temp_col = next((c for c in df.columns if 't (' in c.lower() or 't(' in c.lower()), None)
        if temp_col:
            mask &= (df[temp_col].astype(str).str.strip() == input_temp)

    matched_results = df[mask]

    # OUTPUT CONTROL SYSTEM
    if len(matched_results) > 0:
        print(f"⚠️ MATCH FOUND! This parameter combination matches {len(matched_results)} previous run(s)!\n")
        
        grade_col = next((c for c in df.columns if 'grado' in c.lower() or 'proces' in c.lower()), None)
        comment_col = next((c for c in df.columns if 'coment' in c.lower() or 'proces' in c.lower()), None)
        
        for idx, row in matched_results.iterrows():
            print(f"📌 [HISTORICAL STATE - Row {idx+3}]")
            # Dynamically display all relevant process specifications
            for col in df.columns:
                if col not in [grade_col, comment_col]:
                    print(f"  ▫️ {col}: {row[col]}")
            
            print(f"  🚨 PROCESSABILITY GRADE (1-4): {row.get(grade_col, 'N/A')}")
            print(f"  💬 PROCESS REMARKS: {row.get(comment_col, 'No comments logged')}")
            print("-" * 50)
    else:
        print("✅ NO MATCHING ERROR FOUND!")
        print("💡 This specific combination is completely safe or unique. You can proceed with the experiment.")
        print("-" * 70)

if __name__ == "__main__":
    live_dynamic_search()
    
    