import streamlit as st
import pandas as pd
import json
import os
import re
import urllib.parse
from datetime import datetime
import sqlite3

#  WRSE ENGINE CORE & MASTER 15-SHEET CSV MULTI-ASSET INDEXER

DEFAULT_KEYWORDS = {
    "production server":  (0.90, "Infrastructure Core Assets"),
    "domain controller":  (0.95, "Infrastructure Core Assets"),
    "database string":    (0.90, "Infrastructure Core Assets"),
    "active directory":   (0.90, "Infrastructure Core Assets"),
    "source code":        (0.85, "Corporate Intellectual Property"),
    "api key":            (0.90, "Corporate Intellectual Property"),
    "proprietary logic":  (0.85, "Corporate Intellectual Property"),
    "hl7 protocol":       (0.85, "Medical Records (PHI)"),
    "patient records":    (0.95, "Medical Records (PHI)"),
    "prescription data":  (0.90, "Medical Records (PHI)"),
}

ASSET_TIERS = [
    "Medical Records (PHI)",
    "Infrastructure Core Assets",
    "Corporate Intellectual Property",
    "Financial Data",
    "HR / Employee Records",
    "Research & Development",
    "Legal & Compliance",
    "Customer PII",
]

W_S, W_D, W_U = 0.50, 0.25, 0.25

#  FILE PATHS 
LOG_FILE           = "/home/izu/ShadowAI_Framework/Section1_DataIngestion/wrse_comprehensive_audit.log"
DATA_SHEETS_DIR    = "/home/izu/ShadowAI_Framework/data Sheets"
CUSTOM_ASSETS_FILE = "/home/izu/ShadowAI_Framework/Section3_Dashboard/custom_assets.json"

UNIQUE_ID_COLS = {
    "PATIENT ID", "INSURANCE ID", "POLICY NUMBER", "MEDICARE ID", "INSURANCE CLAIM", "BILLING STATEMENT",
    "SAML TOKEN HASH", "API KEY HASH", "API SECRET REF", "JWT SECRET ID", "DB CONNECTION STRING", 
    "IP ADDRESS", "GIT REPOSITORY", "CONTRACT ID", "HL7 MESSAGE HEADER", "SUBNET", "PRICING SHEET REF", 
    "DOCUMENT TAG", "AD FOREST", "KERBEROS REALM"
}


#  CUSTOM ASSET MANAGER 
def load_custom_assets():
    if os.path.exists(CUSTOM_ASSETS_FILE):
        try:
            with open(CUSTOM_ASSETS_FILE, "r") as f:
                return json.load(f).get("assets", [])
        except Exception:
            return []
    return []


def save_custom_assets(assets_list):
    with open(CUSTOM_ASSETS_FILE, "w") as f:
        json.dump({"assets": assets_list}, f, indent=2)


def get_keywords_db():
    db = dict(DEFAULT_KEYWORDS)
    for a in load_custom_assets():
        db[a["keyword"].lower()] = (float(a["weight"]), a["tier"])
    return db


#  WRSE CORE FUNCTIONS 
def forensic_normalize(text):
    import urllib.parse
    import base64
    import json
    
    # 1. Multi-pass URL Entity Unquoting
    prev_text = ""
    while prev_text != text and "%" in text:
        prev_text = text
        text = urllib.parse.unquote(text)
        
    # 2. Google Gemini f.req= parser
    # Extract actual user prompt payload from Google internal JSON wrappers
    if "f.req=" in text:
        try:
            # Usually f.req is followed by an array string. 
            match = re.search(r'f\.req=(.*?)(?:&|$)', text)
            if match:
                payload = match.group(1)
                parsed = json.loads(payload)
                # It's usually nested arrays. Just flatten all string values
                def extract_strings(obj):
                    res = []
                    if isinstance(obj, str): res.append(obj)
                    elif isinstance(obj, list):
                        for item in obj: res.extend(extract_strings(item))
                    elif isinstance(obj, dict):
                        for val in obj.values(): res.extend(extract_strings(val))
                    return res
                strings = extract_strings(parsed)
                text = " ".join([s for s in strings if len(s) > 5])
        except Exception:
            pass
            
    # 3. Automated Base64 Payload Inspector
    b64_pattern = r'(?:[A-Za-z0-9+/]{4}){4,}(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?'
    b64_matches = re.findall(b64_pattern, text)
    for b64 in b64_matches:
        try:
            decoded = base64.b64decode(b64).decode('utf-8', errors='ignore')
            if len(decoded.strip()) > 5:
                text += " " + decoded
        except Exception:
            pass

    # Basic cleanup (like before)
    strings = re.findall(r'"([a-zA-Z0-9\s\.\,\!\?\:\-\_\/\@\#\$\%\^\&\*\(\)\+]{6,})"', text)
    if strings:
        valid = [s for s in strings if s not in ["en-US","N/A"] and not s.startswith(("c_","r_"))]
        text_from_quotes = max(valid, key=len) if valid else strings[0]
        text = text + " " + text_from_quotes
        
    text = text.replace('\\"', '').replace('"', '').replace('[', '').replace(']', '').strip()
    clean = re.sub(r'[^\w\s\.]', ' ', text.lower())
    
    # 4. Whitespace/Delimiter Stripping (zero-space alphanumeric)
    compressed = re.sub(r'[\s\-_]+', '', text).lower()
    
    return clean, text, compressed


def calculate_wrse(prompt_text, dest_trust_w, user_auth_w, asset_matches=None):
    clean_text, original_str, compressed_str = forensic_normalize(prompt_text)
    detected_keywords = []
    detected_tiers = set()
    KEYWORDS_DB = get_keywords_db()

    s_score = 0.0

    #  STANDARD TEXT PROMPT SCORING (FILE UPLOAD REMOVED) 
    if asset_matches:
        # Class 1: Deterministic Match (assigns Tier-based score instead of summation)
        for m in asset_matches:
            tier_str = str(m.get("DATA TIER", ""))
            tier_score = 0.95 if "Tier 1" in tier_str else (0.90 if "Tier 2" in tier_str else 0.85)
            s_score = max(s_score, tier_score)
            detected_keywords.append(f"Match:{m.get('RECORD ID', 'Asset')} (S={tier_score})")
            detected_tiers.add(tier_str)

    # Class 1: Standalone High-Entropy Primary Identifiers
    
    # Stripe / Live API Keys (checks compressed string for obfuscation too)
    if re.search(r'sk_live_[a-zA-Z0-9]{20,}', original_str) or re.search(r'sklive[a-zA-Z0-9]{20,}', compressed_str):
        s_score = max(s_score, 0.85)
        detected_keywords.append("API Secret Key")
        detected_tiers.add("Tier 3 - SourceCodeAPI")
        
    # JWT Tokens
    if re.search(r'eyJ[a-zA-Z0-9_-]{10,}\.eyJ[a-zA-Z0-9_-]{10,}', original_str):
        s_score = max(s_score, 0.85)
        detected_keywords.append("JWT Token")
        detected_tiers.add("Tier 3 - SourceCodeAPI")
        
    # Private RFC-1918 IPv4 Blocks
    if re.search(r'\b(10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3})\b', original_str):
        s_score = max(s_score, 0.90)
        detected_keywords.append("Internal RFC-1918 IPv4")
        detected_tiers.add("Tier 2 - NetworkNodes")
        
    # Database URIs
    if re.search(r'(mysql|postgresql|mongodb)://', original_str, re.IGNORECASE):
        s_score = max(s_score, 0.90)
        detected_keywords.append("Database URI")
        detected_tiers.add("Tier 2 - DBConnections")
        
    # US SSN
    if re.search(r'\b\d{3}-\d{2}-\d{4}\b', original_str):
        s_score = max(s_score, 0.95)
        detected_keywords.append("US SSN")
        detected_tiers.add("Tier 1 - PHI")
        
    # Patient ID format
    if re.search(r'\bTM-202[0-9]-[0-9]{4}\b', original_str):
        s_score = max(s_score, 0.95)
        detected_keywords.append("Patient ID")
        detected_tiers.add("Tier 1 - PHI")
        
    # Formatted Record IDs (Tier 1 - PHI)
    if re.search(r'\b(CLN|INS|LAB|REC|RX)-\d{4,8}\b', original_str):
        s_score = max(s_score, 0.95)
        detected_keywords.append("Formatted Record ID (PHI)")
        detected_tiers.add("Tier 1 - PHI")

    # Formatted Record IDs (Tier 2 - Infrastructure)
    if re.search(r'\b(DB|IAM|NET|TOP|SEC)-\d{4,8}\b', original_str):
        s_score = max(s_score, 0.90)
        detected_keywords.append("Formatted Record ID (Infra)")
        detected_tiers.add("Tier 2 - NetworkNodes")

    # Formatted Record IDs (Tier 3 - Corporate IP)
    if re.search(r'\b(HL7|ALG|SRC|STR|VND)-\d{4,8}\b', original_str):
        s_score = max(s_score, 0.85)
        detected_keywords.append("Formatted Record ID (IP)")
        detected_tiers.add("Tier 3 - StrategicBlueprints")

    # Class 2: Quasi-Identifiers & Context Correlation
    quasi_matches = 0
    highest_quasi_tier_score = 0.85 # Default to Tier 3
    
    for word, (weight, tier) in KEYWORDS_DB.items():
        if word in clean_text:
            quasi_matches += 1
            detected_keywords.append(word)
            detected_tiers.add(tier)
            if "Tier 1" in tier:
                highest_quasi_tier_score = max(highest_quasi_tier_score, 0.95)
            elif "Tier 2" in tier:
                highest_quasi_tier_score = max(highest_quasi_tier_score, 0.90)
            
    if quasi_matches == 1:
        # Isolated Occurrence
        pass # s_score remains max(s_score, 0)
    elif quasi_matches >= 2:
        # Combinatorial Leak elevates S
        s_score = max(s_score, highest_quasi_tier_score)

    rs = (0.50 * s_score) + (0.25 * dest_trust_w) + (0.25 * user_auth_w)
    return round(rs * 100, 2), detected_keywords, list(detected_tiers), clean_text, original_str

def get_severity(score):
    if score > 80:    return "CRITICAL", ""
    elif score >= 70: return "HIGH",     ""
    elif score >= 55: return "MEDIUM",   ""
    else:             return "LOW",      ""


def score_bar_html(score):
    color = "#FF2D5B" if score > 80 else ("#F59E0B" if score >= 55 else "#10B981")
    return f'<div class="score-bar-wrap"><div class="score-bar" style="width:{min(score,100)}%;background:{color};"></div></div>'


#  MASTER 15-SHEET CSV ASSET DATASET LOADING & MATCHING 
@st.cache_data(show_spinner=False)
def load_master_dataset():
    DB_PATH = "/home/izu/ShadowAI_Framework/Section3_Dashboard/assets.db"
    if not os.path.exists(DB_PATH):
        return {}, {}
    
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    
    all_sheets = {}
    sheet_names = pd.read_sql("SELECT DISTINCT sheet_name FROM master_assets", conn)['sheet_name'].tolist()
    for s in sheet_names:
        df = pd.read_sql(f"SELECT * FROM master_assets WHERE sheet_name='{s}'", conn)
        df.rename(columns={
            "sheet_name": "SHEET_NAME",
            "record_id": "RECORD ID",
            "patient_name": "PATIENT NAME",
            "patient_id": "PATIENT ID",
            "ssn": "SSN",
            "date_of_birth": "DATE OF BIRTH",
            "blood_type": "BLOOD TYPE",
            "nationality": "NATIONALITY",
            "data_tier": "DATA TIER",
            "section": "SECTION",
            "original_attributes": "_original_attributes"
        }, inplace=True)
        all_sheets[s] = df

    idx = {
        "record_ids": {},
        "patient_ids": {},
        "tokens": {},
    }
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM master_assets")
    rows = cursor.fetchall()
    col_names = [desc[0] for desc in cursor.description]
    
    for row in rows:
        row_dict = dict(zip(col_names, row))
        record = {
            "SHEET_NAME":          row_dict["sheet_name"],
            "RECORD ID":           row_dict["record_id"],
            "PATIENT NAME":        row_dict["patient_name"],
            "PATIENT ID":          row_dict["patient_id"],
            "SSN":                 row_dict["ssn"],
            "DATE OF BIRTH":       row_dict["date_of_birth"],
            "BLOOD TYPE":          row_dict["blood_type"],
            "NATIONALITY":         row_dict["nationality"],
            "DATA TIER":           row_dict["data_tier"],
            "SECTION":             row_dict["section"],
            "_original_attributes": json.loads(row_dict["original_attributes"]) if row_dict["original_attributes"] else {},
        }
        rec_id = str(row_dict["record_id"]).strip().upper()
        if rec_id: idx["record_ids"][rec_id] = record
        
        pid = str(row_dict["patient_id"]).strip().upper()
        if pid: idx["patient_ids"][pid] = record

    cursor.execute("SELECT token_value, record_id FROM asset_tokens")
    for token_val, rec_id in cursor.fetchall():
        token = str(token_val).strip()
        rec_id_up = str(rec_id).strip().upper()
        if rec_id_up in idx["record_ids"]:
            idx["tokens"][token] = idx["record_ids"][rec_id_up]

    conn.close()
    return all_sheets, idx


def find_master_asset_match(prompt_text, asset_index):
    """
    Check prompt against ALL 15 CSV sheets and return ALL matches found in the payload.
    Ensures multiple assets leaked in a single prompt are fully identified without duplicates!
    """
    matches = []
    seen_records = set()
    matched_token_values = set()

    # 1. Record ID & Patient ID (Any prefix 2-5 alphanumeric chars followed by a dash and 4-8 digits)
    rec_matches = re.findall(r'[A-Z0-9]{2,5}-\d{4,8}', prompt_text, re.IGNORECASE)
    for rm in rec_matches:
        rm_upper = rm.upper()
        rec = None
        if rm_upper in asset_index.get("record_ids", {}):
            rec = asset_index["record_ids"][rm_upper]
        elif rm_upper in asset_index.get("patient_ids", {}):
            rec = asset_index["patient_ids"][rm_upper]
        
        if rec and rec["RECORD ID"] not in seen_records:
            seen_records.add(rec["RECORD ID"])
            matches.append(rec)
            # Store all attribute values of this matched record to prevent duplicate mock collisions in Step 2!
            for val in rec.get("_original_attributes", {}).values():
                val_str = str(val).strip()
                if len(val_str) > 5:
                    matched_token_values.add(val_str)

    # 2. Token / Substring matching (Optimized O(1) Lookups)
    # Tokenize the prompt text to match against the 35,000+ zero-space tokens instantly
    prompt_tokens = set(re.split(r'[^a-zA-Z0-9_\-\.]', prompt_text))
    tokens_db = asset_index.get("tokens", {})
    
    for token in prompt_tokens:
        if len(token) > 5 and token in tokens_db:
            rec = tokens_db[token]
            # Check if this token is already accounted for by an existing matched record
            if token not in matched_token_values and rec and rec["RECORD ID"] not in seen_records:
                seen_records.add(rec["RECORD ID"])
                matches.append(rec)
                for val in rec.get("_original_attributes", {}).values():
                    val_str = str(val).strip()
                    if len(val_str) > 5:
                        matched_token_values.add(val_str)

    return matches


#  LOG INGESTION & PROCESSING 
@st.cache_data(ttl=30, show_spinner=False)
def load_logs():
    if not os.path.exists(LOG_FILE) or os.path.getsize(LOG_FILE) == 0:
        return []
    try:
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []


@st.cache_data(ttl=10, show_spinner=False)
def load_agent_registry():
    REGISTRY_FILE = "/home/izu/ShadowAI_Framework/Section1_DataIngestion/agent_registry.json"
    if os.path.exists(REGISTRY_FILE):
        try:
            with open(REGISTRY_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}


@st.cache_data(ttl=30, show_spinner=False)
def process_events():
    agent_registry = load_agent_registry()
    raw_logs = load_logs()
    all_sheets, asset_idx = load_master_dataset()
    if not raw_logs:
        return pd.DataFrame(), 0, all_sheets

    events = []
    asset_match_count = 0

    # Load AI domains once (outside loop for performance)
    DOMAINS_FILE = "/home/izu/ShadowAI_Framework/Section1_DataIngestion/domains.json"
    try:
        with open(DOMAINS_FILE, "r") as _f:
            all_ai_domains = [d.lower() for d in json.load(_f)]
    except Exception:
        all_ai_domains = ["chatgpt.com", "claude.ai", "gemini.google.com", "openai.com", "anthropic.com"]

    for idx_e, entry in enumerate(raw_logs):

        timestamp   = entry.get("timestamp", "N/A")
        source      = entry.get("source_node", {})
        client_ip   = source.get("client_ip", "192.168.89.134")
        client_port = str(source.get("source_port", "?"))
        dest        = entry.get("destination_node", {})
        dest_domain = dest.get("destination_domain", "unknown")
        dest_ip     = dest.get("destination_ip", "?")
        dest_url    = dest.get("full_url", "?")
        http_method = entry.get("connection_metadata", {}).get("http_method", "POST")
        user_agent  = entry.get("connection_metadata", {}).get("user_agent", "Unknown")
        raw_prompt  = entry.get("captured_payload", {}).get("prompt", "N/A")

        # Skip only completely empty or pure garbage - AI domain traffic always kept
        is_known_ai = any(d in dest_domain.lower() for d in all_ai_domains)
        if raw_prompt in ("Dynamic Content", "N/A") or "conversation_mode" in str(raw_prompt):
            # (REMOVED FILTER: Show all events)
            # if not is_known_ai:
            #     continue
            # else:
            if is_known_ai:
                # Known AI domain but unreadable payload - label it
                raw_prompt = "[Encrypted / Unknown Payload Format]"

        dest_domain_lower = dest_domain.lower()

        if any(d in dest_domain_lower for d in all_ai_domains):
            dest_weight = 0.95
        elif any(d in dest_domain_lower for d in ["copilot", "enterprise", "internal"]):
            dest_weight = 0.30
        else:
            dest_weight = 0.10




        is_bot = (any(b in str(user_agent).lower() for b in ["python", "curl", "postman", "wget", "bot", "httpie", "insomnia"]) or
                  str(raw_prompt).startswith("trace=") or 
                  "PCck7e" in str(raw_prompt) or
                  "aPya6c" in str(raw_prompt))
        
        if is_bot:
            user_weight = 0.20
            identity = "Automated Bot"
            identity_icon = "🤖"
        else:
            agent_info = agent_registry.get(client_ip)
            if agent_info:
                identity = agent_info.get("username", "Unknown Agent")
                
                # Fetch exact weight and role from the new monitored_users DB
                conn = sqlite3.connect("/home/izu/ShadowAI_Framework/Section3_Dashboard/users.db")
                cursor = conn.cursor()
                cursor.execute('SELECT role, u_weight FROM monitored_users WHERE username = ?', (identity,))
                db_user = cursor.fetchone()
                conn.close()
                
                if db_user:
                    role = db_user[0]
                    user_weight = float(db_user[1])
                else:
                    # Fallback if user not in DB but is in registry
                    role = agent_info.get("role", "Standard Staff")
                    if role == "Privileged Admin": user_weight = 0.90
                    elif role == "Medical Specialist": user_weight = 0.75
                    else: user_weight = 0.65
                
                if "Admin" in role:
                    identity_icon = "👑"
                elif "Medical" in role or "Doc" in role:
                    identity_icon = "⚕️"
                else:
                    identity_icon = "🧑‍💻"
            else:
                user_weight = 0.50
                identity = f"Unregistered ({client_ip})"
                identity_icon = "👤"

        # Normal text prompt  full WRSE keyword + asset matching pipeline
        asset_matches = find_master_asset_match(str(raw_prompt), asset_idx)
        score, keywords, tiers, clean_prompt, norm_str = calculate_wrse(
            str(raw_prompt), dest_weight, user_weight,
            asset_matches=asset_matches,
        )


        # (REMOVED FILTER: The user wants to see ALL ~1500 alerts, including background telemetry and non-AI traffic)
        # if len(clean_prompt.strip()) <= 3 and score < 30 and not asset_matches and not is_known_ai:
        #     continue

        sev_label, sev_icon = get_severity(score)
        if asset_matches: asset_match_count += len(asset_matches)

        primary_match = asset_matches[0] if asset_matches else None

        if asset_matches:
            if len(asset_matches) > 1:
                phi_matched_label = f"{primary_match['PATIENT NAME']} (+{len(asset_matches)-1} Assets)"
                phi_record_id = ", ".join(m["RECORD ID"] for m in asset_matches if m.get("RECORD ID"))
                data_tier = ", ".join(sorted(set(m["DATA TIER"] for m in asset_matches)))
                asset_section = ", ".join(sorted(set(m["SECTION"] for m in asset_matches)))
                sens_levels = [m.get("SENSITIVITY LEVEL", "HIGH") for m in asset_matches]
                asset_sensitivity = "CRITICAL" if "CRITICAL" in sens_levels else "HIGH"
            else:
                phi_matched_label = primary_match["PATIENT NAME"]
                phi_record_id = primary_match["RECORD ID"]
                data_tier = primary_match["DATA TIER"]
                asset_section = primary_match["SECTION"]
                asset_sensitivity = primary_match.get("SENSITIVITY LEVEL", "HIGH")
        else:
            phi_matched_label = ""
            phi_record_id = ""
            data_tier = tiers[0] if tiers else ""
            asset_section = ""
            asset_sensitivity = "CRITICAL" if score > 80 else ("HIGH" if score >= 70 else ("MODERATE" if score >= 55 else "LOW"))

        event_id = f"EVT-{idx_e}-{timestamp.replace(' ', '-').replace(':', '')}"



        events.append({
            # Core
            "Event ID":          event_id,
            "Timestamp":         timestamp,
            "Source IP":         client_ip,
            "Source Port":       client_port,
            "Source (full)":     f"{client_ip}:{client_port}",
            "Destination":       dest_domain,
            "Dest IP":           dest_ip,
            "Full URL":          dest_url,
            "HTTP Method":       http_method,
            "User Agent":        user_agent,
            "Identity":          identity,
            "Identity Icon":     identity_icon,
            # Payload
            "Raw Prompt":        str(raw_prompt),
            "Extracted Prompt":  clean_prompt[:200] if clean_prompt else norm_str[:150],
            # WRSE
            "Triggered Keys":    ", ".join(keywords) if keywords else "None",
            "Data Tier":         data_tier,
            "Asset Section":     asset_section,
            "WRSE Score":        score,
            "Severity":          sev_label,
            "Sev Icon":          sev_icon,
            # Master Asset Match info
            "PHI Matched":       phi_matched_label,
            "PHI Patient ID":    primary_match["PATIENT ID"] if primary_match else "",
            "PHI Record ID":     phi_record_id,
            "PHI Blood Type":    primary_match["BLOOD TYPE"] if primary_match else "",
            "PHI Nationality":   primary_match["NATIONALITY"] if primary_match else "",
            "PHI DOB":           primary_match["DATE OF BIRTH"] if primary_match else "",
            "Sensitivity Level": asset_sensitivity,
            "Upload Type":       "",
            "Filename":          "",
            "File Size (KB)":    0,
            "_phi_records":      asset_matches, # FULL LIST OF MATCHES
            "_raw_entry":        entry,
        })

    df = pd.DataFrame(events)
    #  GUARANTEE NEWEST ALERTS FIRST (AT THE TOP) 
    if not df.empty:
        df["Timestamp_Parsed"] = pd.to_datetime(df["Timestamp"], errors="coerce")
        df = df.sort_values("Timestamp_Parsed", ascending=False).reset_index(drop=True)

    return df, asset_match_count, all_sheets
