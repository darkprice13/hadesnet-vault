import streamlit as st
import os
import json
from document_agent import read_text_invoice, parse_purchase_order, evaluate_document_risk, run_resolution_broker

# Set page configuration for a premium enterprise feel
st.set_page_config(page_title="LogiShield AI", page_icon="🛡️", layout="wide")

st.title("🛡️ LogiShield AI — Autonomous Document Reconciliation")
st.caption("Enterprise multi-agent engine auditing inbound transactional vectors.")

st.markdown("---")

# Layout columns for splitting actions
col1, col2 = st.columns([1, 2])

with col1:
    st.header("📋 Input Feed")
    # Simulate picking a document file in our system
    target_file = "sample_invoice.txt"
    
    if os.path.exists(target_file):
        st.success(f"Target Document Detected: `{target_file}`")
        with open(target_file, "r") as f:
            file_contents = f.read()
        st.text_area("Raw Document Text View", file_contents, height=300)
        
        trigger_audit = st.button("🚀 Execute Multi-Agent Audit", use_container_width=True)
    else:
        st.error("Missing `sample_invoice.txt` in directory. Please regenerate.")
        trigger_audit = False

with col2:
    st.header("🤖 Agentic Trace Workspace")
    
    if trigger_audit:
        # --- Trigger Agent A ---
        with st.status("Agent A executing ingestion & parsing...", expanded=True) as status:
            raw_text = read_text_invoice(target_file)
            structured_data = parse_purchase_order(raw_text)
            report = evaluate_document_risk(structured_data)
            status.update(label="Agent A Evaluation Complete", state="complete")
        
        # Display Agent A Findings
        if report["status"] == "FLAGGED_FOR_REVIEW":
            st.error(f"⚠️ Document Status: FLAGGED FOR REVIEW")
            for anomaly in report["anomalies"]:
                st.markdown(f"- **Discrepancy:** {anomaly}")
                
            # --- Trigger Agent B ---
            st.markdown("---")
            with st.status("🤖 Passing control to Agent B (Resolution)...", expanded=True) as status:
                resolution = run_resolution_broker(report)
                status.update(label="Agent B Intervention Complete", state="complete")
                
            st.subheader("📬 Auto-Generated Vendor Communications Dispatch")
            st.code(resolution["comms_payload"], language="text")
            
            # Show underlying JSON asset
            with st.expander("👁️ View System Ledger Metadata JSON"):
                st.json(resolution)
        else:
            st.success("✅ Document Status: APPROVED FOR ERP INTEGRATION")
            st.json(report["data"])
    else:
        st.info("Awaiting pipeline trigger. Click 'Execute Multi-Agent Audit' to start.")