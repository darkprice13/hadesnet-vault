import re
import json
import os
import sqlite3
from PIL import Image
import pytesseract

def read_text_invoice(file_path):
    """
    Advanced Ingestion Layer: Detects file types and automatically routes 
    images to the OCR Vision Engine or standard text streams.
    """
    print(f"Agent A: Ingesting asset payload from file path: {file_path}")
    ext = os.path.splitext(file_path)[1].lower()
    
    # Handle Image Ingestion via OCR Vision Engine
    if ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
        print("👁️ Vision Engine Activated: Processing raw image matrices...")
        try:
            image = Image.open(file_path)
            extracted_text = pytesseract.image_to_string(image)
            print("👁️ Vision Engine: Structural text extraction complete.")
            return extracted_text
        except Exception as e:
            print(f"⚠️ Vision Engine Fallback: Tesseract binary not configured locally. Details: {str(e)}")
            print("Attempting to look for a matching .txt manifest for testing...")
            txt_fallback = os.path.splitext(file_path)[0] + ".txt"
            if os.path.exists(txt_fallback):
                with open(txt_fallback, 'r') as f:
                    return f.read()
            return None
            
    # Handle Standard Native Text Files
    else:
        try:
            with open(file_path, 'r') as f:
                return f.read()
        except Exception as e:
            print(f"Agent A Ingestion Error: {str(e)}")
            return None

def parse_purchase_order(text):
    print("Agent A: Analyzing text layers for supply chain parameters...")
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
            "sku": match[0],
            "quantity": int(match[1]),
            "unit_price": float(match[2].replace(',', ''))
        })
    return parsed_data

def evaluate_document_risk(parsed_data):
    print("Agent A: Finalizing verification rules...")
    errors = []
    
    if parsed_data["purchase_order_id"] == "UNKNOWN":
        errors.append("Missing Purchase Order Identifier.")
    if not parsed_data["line_items"]:
        errors.append("No line items extracted from payload body.")
        
    calculated_total = sum(item["quantity"] * item["unit_price"] for item in parsed_data["line_items"])
    variance = calculated_total - parsed_data["financial_total"]
    
    if abs(variance) > 0.01:
        errors.append(f"Financial Mismatch! Header total is ${parsed_data['financial_total']:.2f}, but line item sum is ${calculated_total:.2f}. Variance: ${variance:.2f}")

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
    
    resolution_payload = {
        "action_taken": "VENDOR_NOTIFICATION_GENERATED",
        "target_po": po_id,
        "discrepancy_value": variance,
        "comms_payload": email_draft.strip()
    }
    return resolution_payload

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
        print(f"🔱 Database Error: Failed to write to vault. Details: {str(e)}")