import streamlit as st
import os
import sqlite3
import pandas as pd
from document_agent import read_text_invoice, parse_purchase_order, evaluate_document_risk, run_resolution_broker, log_audit_to_vault

st.set_page_config(page_title="HadesNet Dashboard", page_icon="🔱", layout="wide")

# Olympus Dark Gold & Black Theme Stylesheet
st.markdown("""
    <style>
    .stApp { background-color: #0b0b0b; color: #e5e5e5; }
    h1 { color: #d4af37 !important; font-family: 'Cinzel', serif; text-shadow: 0px 0px 10px rgba(212, 175, 55, 0.3); }
    h2, h3 { color: #c5a059 !important; font-family: 'Cinzel', serif; }
    [data-testid="stSidebar"] { background-color: #111111; border-right: 1px solid #332200; }
    div.stButton > button:first-child { background-color: #d4af37; color: #0b0b0b; font-weight: bold; border: 1px solid #d4af37; border-radius: 4px; }
    div.stButton > button:first-child:hover { background-color: #0b0b0b; color: #d4af37; border: 1px solid #d4af37; box-shadow: 0px 0px 15px rgba(212, 175, 55, 0.6); }
    code, pre { background-color: #161616 !important; border: 1px solid #332200 !important; color: #d4af37 !important; }
    .stDataFrame div { background-color: #111111 !important; border: 1px solid #332200 !important; }
    hr { border-top: 1px solid #332200; }
    </style>
""", unsafe_allow_html=True)

st.title("🔱 HADESNET — Autonomous Reclamation Protocol")
st.caption("Engine Version 1.1.0 • Architect: Ssemanda Ethan Price • OCR Vision Enabled")
st.markdown("---")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("⚡ Vault Ingestion")
    
    # Enhanced file uploader to seamlessly support both text manifests and raw scan assets
    uploaded_file = st.file_uploader("Upload Manifest Asset (TXT, PNG, JPG)", type=["txt", "png", "jpg", "jpeg"])
    
    # Fallback to local test file if no custom upload is provided
    target_file = "sample_invoice.txt"
    
    if uploaded_file is not None:
        # Save uploaded buffer locally to pass into our multi-agent framework
        target_file = uploaded_file.name
        with open(target_file, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Asset '{target_file}' staged in vault buffer.")

    if os.path.exists(target_file):
        st.markdown(f"### Target Manifest Staged: `{target_file}`")
        trigger_audit = st.button("🔱 Invoke Stygian Audit Engine", use_container_width=True)
    else:
        st.error("Vault ingestion pipeline empty. Drop an asset file to proceed.")
        trigger_audit = False

with col2:
    st.header("👁️ Olympus Agentic Trace")
    
    if trigger_audit:
        with st.status("Agent A: Executing Multi-Modal Ingestion Engine...", expanded=True) as status:
            raw_text = read_text_invoice(target_file)
            if raw_text:
                structured_data = parse_purchase_order(raw_text)
                report = evaluate_document_risk(structured_data)
                status.update(label="Agent A: Extraction and Verification Complete", state="complete")
            else:
                status.update(label="Agent A: Failed to process asset payload", state="error")
                report = None
        
        if report:
            log_audit_to_vault(report)
            
            if report["status"] == "FLAGGED_FOR_REVIEW":
                st.warning("🚨 ANOMALY DETECTED IN THE VAULT")
                for anomaly in report["anomalies"]:
                    st.markdown(f"**Discrepancy Log:** `{anomaly}`")
                    
                st.markdown("---")
                with st.status("Agent B: Deploying Resolution Protocols...", expanded=True) as status:
                    resolution = run_resolution_broker(report)
                    status.update(label="Agent B: Resolution Strategy Rendered", state="complete")
                    
                st.subheader("📬 Outbound Reconciliation Dispatch")
                st.code(resolution["comms_payload"], language="text")
                
                with st.expander("🔱 Inspect HadesNet System Ledger Hashing"):
                    st.json(resolution)
            else:
                st.success("Verified Clean. Safe for ERP insertion.")
                st.json(report["data"])
    else:
        st.markdown("<p style='color:#666;'>System idling... Awaiting activation command.</p>", unsafe_allow_html=True)

# --- HISTORICAL VAULT SECTOR ---
st.markdown("---")
st.header("🗄️ HadesNet Historical Audit Vault Ledger")

if os.path.exists("hadesnet_vault.db"):
    try:
        conn = sqlite3.connect("hadesnet_vault.db")
        df = pd.read_sql_query(
            "SELECT id, purchase_order_id, financial_total, calculated_total, variance, status, timestamp FROM document_audits ORDER BY id DESC", 
            conn
        )
        conn.close()
        
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Vault ledger database file is currently empty.")
    except Exception as e:
        st.error(f"Error compiling secure ledger stream: {str(e)}")
else:
    st.info("Vault database file missing. Run initialize_db.py first.")