import streamlit as st
import os
import sqlite3
import pandas as pd
from document_agent import read_text_invoice, parse_purchase_order_with_llm, evaluate_document_risk, run_resolution_broker, log_audit_to_vault, dispatch_enterprise_webhook

st.set_page_config(page_title="HadesNet Dashboard", page_icon="🔱", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0b0b0b; color: #e5e5e5; }
    h1 { color: #d4af37 !important; font-family: 'Cinzel', serif; text-shadow: 0px 0px 10px rgba(212, 175, 55, 0.3); }
    h2, h3 { color: #c5a059 !important; font-family: 'Cinzel', serif; }
    [data-testid="stSidebar"] { background-color: #111111; border-right: 1px solid #332200; }
    div.stButton > button:first-child { background-color: #d4af37; color: #0b0b0b; font-weight: bold; border: 1px solid #d4af37; border-radius: 4px; }
    div.stButton > button:first-child:hover { background-color: #0b0b0b; color: #d4af37; border: 1px solid #d4af37; box-shadow: 0px 0px 15px rgba(212, 175, 55, 0.6); }
    code, pre { background-color: #161616 !important; border: 1px solid #332200 !important; color: #d4af37 !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🔱 HADESNET — Autonomous Reclamation Protocol")
st.caption("Engine Version 1.2.0 • Architect: Ssemanda Ethan Price • LLM & Integration Webhooks Live")
st.markdown("---")

# Read Secret Keys from Streamlit Environment Configuration state if existing
default_api_key = st.secrets.get("GEMINI_API_KEY", "")

# Sidebar Node Configurations Panel
with st.sidebar:
    st.header("🔑 Integration Control Panel")
    user_api_key = st.text_input("Gemini API Encryption Key", value=default_api_key, type="password", help="Pass standard Google Gemini API Token keys here to engage semantic intelligence.")
    
    st.markdown("---")
    st.header("🔌 Middleware Routing")
    webhook_target = st.text_input("Outbound Webhook URL Target", value="", placeholder="[https://webhook.site/](https://webhook.site/)...", help="Pass real mock cloud endpoints (e.g., webhook.site) to verify live enterprise pipeline streams.")

effective_key = user_api_key if user_api_key else None

col1, col2 = st.columns([1, 2])

with col1:
    st.header("⚡ Vault Ingestion")
    uploaded_file = st.file_uploader("Upload Manifest Asset (TXT, PNG, JPG)", type=["txt", "png", "jpg", "jpeg"])
    target_file = "sample_invoice.txt"
    
    if uploaded_file is not None:
        target_file = uploaded_file.name
        with open(target_file, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Asset '{target_file}' staged successfully.")

    if os.path.exists(target_file):
        st.markdown(f"### Target Manifest Staged: `{target_file}`")
        trigger_audit = st.button("🔱 Invoke Stygian Audit Engine", use_container_width=True)
    else:
        st.error("Vault ingestion pipeline empty.")
        trigger_audit = False

with col2:
    st.header("👁️ Olympus Agentic Trace")
    
    if trigger_audit:
        # 1. Processing Raw Ingestion Influx File
        with st.status("Agent A: Running Multi-Modal Structural Ingestion...", expanded=False) as status:
            raw_text = read_text_invoice(target_file)
            status.update(label="Ingestion File Transformed", state="complete")
            
        # 2. Engaging the LLM Intelligence Layer
        with st.status("Agent A: Parsing Document Content with Semantic LLM Matrix...", expanded=True) as status:
            structured_data = parse_purchase_order_with_llm(raw_text, api_key=effective_key)
            st.markdown("#### Structured Extraction Fields Rendered:")
            st.json(structured_data)
            status.update(label="Semantic Data Model Map Fixed", state="complete")
            
        # 3. Deterministic Calculations Threshold Matching
        report = evaluate_document_risk(structured_data)
        log_audit_to_vault(report)
        
        # 4. Outbound Integrations Processing Pipeline Execution Loop (Path 3)
        if webhook_target:
            with st.status("🔌 Enterprise Broker: Broadcasting Outbound JSON Sync Webhook...", expanded=True) as status:
                webhook_log = dispatch_enterprise_webhook(report, webhook_target)
                st.write("Webhook Stream Log Response Summary:")
                st.json(webhook_log)
                status.update(label="Webhook Stream Terminated Successfully", state="complete")
        
        # 5. Visual Layout State Render Actions
        if report["status"] == "FLAGGED_FOR_REVIEW":
            st.warning("🚨 ANOMALY RECLAIM LOCK TRIGGERED")
            for anomaly in report["anomalies"]:
                st.markdown(f"**Discrepancy:** `{anomaly}`")
                
            st.markdown("---")
            resolution = run_resolution_broker(report)
            st.subheader("📬 Outbound Reconciliation Dispatch Generated")
            st.code(resolution["comms_payload"], language="text")
        else:
            st.success("✅ Clean Pass. Document Authenticated for direct ERP storage pipelines.")
    else:
        st.markdown("<p style='color:#666;'>System idling... Awaiting activation command.</p>", unsafe_allow_html=True)

# Historical Table Record View Database Component Section
st.markdown("---")
st.header("🗄️ HadesNet Historical Audit Vault Ledger")
if os.path.exists("hadesnet_vault.db"):
    try:
        conn = sqlite3.connect("hadesnet_vault.db")
        df = pd.read_sql_query("SELECT id, purchase_order_id, financial_total, calculated_total, variance, status, timestamp FROM document_audits ORDER BY id DESC", conn)
        conn.close()
        if not df.empty:
            st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Error accessing ledger database: {str(e)}")