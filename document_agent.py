import re
import json
import os
import sqlite3
import requests
from PIL import Image
import pytesseract

def read_text_invoice(file_path):
    print(f"Agent A: Ingesting asset payload from file path: {file_path}")
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
        print("👁️ Vision Engine Activated: Processing raw image matrices...")
        try:
            image = Image.open(file_path)
            extracted_text = pytesseract.image_to_string(image)
            return extracted_text
        except Exception as e:
            print(f"⚠️ Vision Engine Fallback: {str(e)}")
            txt_fallback = os.path.splitext(file_path)[0] + ".txt"
            if os.path.exists(txt_fallback):
                with open(txt_fallback, 'r') as f:
                    return f.read()
            return None
    else:
        try:
            with open(file_path, 'r') as f:
                return f.read()
        except Exception as e:
            print(f"Agent A Ingestion Error: {str(e)}")
            return None

def parse_purchase_order_with_llm(text, api_key=None):
    """
    Path 2 Upgrade: Replaces rigid regex loops with layout-agnostic 
    semantic parsing powered by Generative AI.
    """
    print("Agent A: Deploying LLM Semantic Parser layer...")
    
    # Fallback to local regex engine if no API key is specified yet
    if not api_key:
        print("⚠️ No LLM API Key detected. Engaging local Regex backup engine.")
        po_number_match = re.search(r"PO[-_\s]?(\d+)", text, re.IGNORECASE)
        total_value_match = re.search(r"(?:Total\s+Amount\s+Due|Total|Amount)[:\s]*\$?([\d,]+\.\d{2})", text, re.IGNORECASE)
        sku_matches = re.findall(r"(SKU\d+)\s+(\d+)\s+([\d,]+\.\d{2})", text)
        
        parsed_data = {
            "purchase_order_id": po_number_match.group(1) if po_number_match else "UNKNOWN",
            "financial_total": float(total_value_match.group(1).replace(',', '')) if total_value_match else 0.0,
            "line_items": []
        }
        for match in sku_matches:
            parsed_data["line_items"].append({
                "sku": match[0], "quantity": int(match[1]), "unit_price": float(match[2].replace(',', ''))
            })
        return parsed_data

    # Execute dynamic Gemini LLM parsing structured JSON call
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    prompt = f"""
    You are an expert procurement audit engine. Extract the supply chain metrics from this text document.
    Return ONLY a valid JSON object matching this exact structure. Do not wrap in markdown block text.
    
    {{
        "purchase_order_id": "string or UNKNOWN",
        "financial_total": float_value,
        "line_items": [
            {{"sku": "string", "quantity": integer, "unit_price": float_value}}
        ]
    }}
    
    Document Text Payload:
    {text}
    """
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response_data = response.json()
        raw_output = response_data['candidates'][0]['content']['parts'][0]['text'].strip()
        
        # Clean any accidental markdown output wrappers
        if raw_output.startswith("```json"):
            raw_output = raw_output.replace("```json", "").replace("```", "").strip()
        elif raw_output.startswith("```"):
            raw_output = raw_output.replace("```", "").strip()
            
        return json.loads(raw_output)
    except Exception as e:
        print(f"❌ LLM Parsing Core Failed: {str(e)}. Defaulting to backup fields.")
        return {"purchase_order_id": "ERROR_FALLBACK", "financial_total": 0.0, "line_items": []}

def evaluate_document_risk(parsed_data):
    print("Agent A: Executing deterministic risk verification metrics...")
    errors = []
    
    if parsed_data.get("purchase_order_id") in ["UNKNOWN", "ERROR_FALLBACK"]:
        errors.append("Incomplete or missing Purchase Order tracing token.")
    if not parsed_data.get("line_items"):
        errors.append("Zero line items extracted from raw text payload body.")
        
    calculated_total = sum(item["quantity"] * item["unit_price"] for item in parsed_data.get("line_items", []))
    variance = calculated_total - parsed_data.get("financial_total", 0.0)
    
    if abs(variance) > 0.01:
        errors.append(f"Financial Mismatch! Stated header total is ${parsed_data.get('financial_total'):.2f}, but line item calculations total ${calculated_total:.2f}. Variance Delta: ${variance:.2f}")

    if errors:
        return {"status": "FLAGGED_FOR_REVIEW", "anomalies": errors, "calculated_total": calculated_total, "data": parsed_data}
    return {"status": "APPROVED_FOR_ERP", "calculated_total": calculated_total, "data": parsed_data}

def run_resolution_broker(report):
    print("\n🤖 Agent B: Anomaly flagged! Initiating recovery operations...")
    po_id = report["data"]["purchase_order_id"]
    claimed = report["data"]["financial_total"]
    actual = report["calculated_total"]
    variance = abs(claimed - actual)
    
    email_draft = f"""
    SUBJECT: ACTION REQUIRED: Billing Discrepancy Found in Purchase Order PO-{po_id}
    
    Dear Vendor Operations Team,
    
    Our automated system has flagged a financial mismatch regarding document reference PO-{po_id}.
    
    - Stated Document Total: ${claimed:,.2f}
    - Calculated Verified Total: ${actual:,.2f}
    - Total Discrepancy Amount: ${variance:,.2f} Overcharge
    
    Please review the line-item calculations immediately and resubmit the corrected manifest. 
    The transaction cannot be processed into our ERP platform until this mismatch is resolved.
    
    System Audit Hash Ref: SYSTEM_AGENT_B_AUTO_GEN
    Authorizations Protocol: HADESNET
    """
    return {
        "action_taken": "VENDOR_NOTIFICATION_GENERATED",
        "target_po": po_id,
        "discrepancy_value": variance,
        "comms_payload": email_draft.strip()
    }

def log_audit_to_vault(report):
    try:
        conn = sqlite3.connect("hadesnet_vault.db")
        cursor = conn.cursor()
        po_id = report["data"]["purchase_order_id"]
        claimed = report["data"]["financial_total"]
        actual = report["calculated_total"]
        variance = claimed - actual
        status = report["status"]
        
        cursor.execute("""
            INSERT INTO document_audits (purchase_order_id, financial_total, calculated_total, variance, status)
            VALUES (?, ?, ?, ?, ?)
        """, (po_id, claimed, actual, variance, status))
        conn.commit()
        conn.close()
        print("🔱 Database Sync: Transaction logged to secure ledger successfully.")
    except Exception as e:
        print(f"🔱 Database Error: {str(e)}")

def dispatch_enterprise_webhook(report, target_url):
    """
    Path 3 Upgrade: Transmits structured JSON transactions directly 
    to external downstream cloud endpoints (middleware connector).
    """
    if not target_url:
        return {"status": "SKIPPED", "message": "No enterprise endpoint target url configured."}
    
    print(f"🚀 Outbound Integration: Streaming synchronized data to {target_url}...")
    try:
        response = requests.post(target_url, json=report, headers={"Content-Type": "application/json"}, timeout=5)
        return {
            "status": "SUCCESS" if response.status_code in [200, 201, 202] else "FAILED",
            "status_code": response.status_code,
            "response_body": response.text[:200]
        }
    except Exception as e:
        return {"status": "CONNECTION_ERROR", "message": str(e)}