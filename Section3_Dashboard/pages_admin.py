import streamlit as st
import sqlite3
import pandas as pd
import json
import os
from auth import get_all_users, add_user, delete_user

DB_PATH = "/home/izu/ShadowAI_Framework/Section3_Dashboard/users.db"
ASSETS_DB_PATH = "/home/izu/ShadowAI_Framework/Section3_Dashboard/assets.db"
DOMAINS_FILE = "/home/izu/ShadowAI_Framework/Section1_DataIngestion/domains.json"

def render_user_management():
    import sqlite3
    import pandas as pd
    
    try:
        conn = sqlite3.connect("/home/izu/ShadowAI_Framework/Section3_Dashboard/users.db")
        df_users = pd.read_sql_query("SELECT username, role FROM users", conn)
        # The `users` table for Dashboard Admins doesn't have an account_status column.
        # We'll treat all existing accounts in this table as "Active".
        df_users["account_status"] = "Active"
        conn.close()
    except Exception as e:
        st.error(f"Failed to load users: {e}")
        df_users = pd.DataFrame()

    # Calculate KPIs
    active_count = len(df_users) if not df_users.empty else 0
    admin_count = len(df_users[df_users["role"].isin(["L2"])]) if not df_users.empty else 0
    l1_count = len(df_users[df_users["role"] == "L1"]) if not df_users.empty else 0
    disabled_count = 0 # No disabled users in the `users` table

    # KPI Row
    st.markdown(f"""
        <div style="display: flex; gap: 16px;">
            <div class="um-kpi-card" style="flex: 1;">
                <div class="um-kpi-left">
                    <span class="um-kpi-title">ACTIVE USERS</span>
                    <span class="um-kpi-value">{active_count}</span>
                </div>
                <div class="um-kpi-icon um-icon-green"></div>
            </div>
            <div class="um-kpi-card" style="flex: 1;">
                <div class="um-kpi-left">
                    <span class="um-kpi-title">ADMIN (L2) ACCOUNTS</span>
                    <span class="um-kpi-value">{admin_count}</span>
                </div>
                <div class="um-kpi-icon um-icon-blue"></div>
            </div>
            <div class="um-kpi-card" style="flex: 1;">
                <div class="um-kpi-left">
                    <span class="um-kpi-title">L1 STAFF ACCOUNTS</span>
                    <span class="um-kpi-value">{l1_count}</span>
                </div>
                <div class="um-kpi-icon um-icon-purple"></div>
            </div>
            <div class="um-kpi-card" style="flex: 1;">
                <div class="um-kpi-left">
                    <span class="um-kpi-title">DISABLED USERS</span>
                    <span class="um-kpi-value">{disabled_count}</span>
                </div>
                <div class="um-kpi-icon um-icon-red"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([1.5, 1], gap="large")

    with c1:
        html_str = '<div class="um-list-container">\n'
        html_str += '<div class="um-list-header"><span>SYSTEM USERS</span><span>STATUS</span></div>\n'
        
        if not df_users.empty:
            for _, row in df_users.iterrows():
                u_name = str(row["username"])
                u_role = str(row["role"])
                u_status = str(row["account_status"])
                avatar_letter = u_name[0].upper() if u_name else "?"
                status_class = "suspended" if u_status != "Active" else ""
                
                html_str += f"""<div class="um-user-row">
<div class="um-user-info-wrapper">
<div class="um-avatar">{avatar_letter}</div>
<div class="um-user-details">
<span class="um-username">{u_name}</span>
<span class="um-role">{u_role}</span>
</div>
</div>
<div class="um-status {status_class}">{u_status.upper()}</div>
</div>"""
        
        html_str += '</div>'
        st.markdown(html_str, unsafe_allow_html=True)

    with c2:
        # Inject CSS to style the stForm to match the screenshot
        st.markdown("""
        <style>
        div[data-testid="stForm"] {
            background: rgba(14, 25, 52, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            padding: 16px;
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown('<div class="um-section-title">CREATE NEW USER</div>', unsafe_allow_html=True)
        with st.form("create_new_user", clear_on_submit=True):
            new_user = st.text_input("Username")
            new_pass = st.text_input("Password", type="password")
            new_role = st.selectbox("Role", ["L1", "L2"])
            if st.form_submit_button("Create Account", type="primary", use_container_width=True):
                if new_user and new_pass:
                    try:
                        import hashlib
                        pass_hash = hashlib.sha256(new_pass.encode()).hexdigest()
                        conn = sqlite3.connect("/home/izu/ShadowAI_Framework/Section3_Dashboard/users.db")
                        conn.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                                     (new_user, pass_hash, new_role))
                        conn.commit()
                        conn.close()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            
        st.markdown('<div class="um-section-title red">DELETE USER</div>', unsafe_allow_html=True)
        del_user = st.selectbox("Select user to remove:", df_users["username"].tolist() if not df_users.empty else [], key="del_user_sb")
        if st.button("Delete Selected User", type="primary", use_container_width=True):
            if del_user:
                try:
                    conn = sqlite3.connect("/home/izu/ShadowAI_Framework/Section3_Dashboard/users.db")
                    conn.execute("DELETE FROM users WHERE username=?", (del_user,))
                    conn.commit()
                    conn.close()
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")



def render_asset_management():
    ASSETS_DB_PATH = "/home/izu/ShadowAI_Framework/Section3_Dashboard/assets.db"
    DOMAINS_FILE = "/home/izu/ShadowAI_Framework/Section1_DataIngestion/domains.json"

    # Calculate KPIs
    try:
        conn = sqlite3.connect(ASSETS_DB_PATH)
        total_assets = conn.execute("SELECT COUNT(*) FROM master_assets").fetchone()[0]
        critical_assets = conn.execute("SELECT COUNT(*) FROM master_assets WHERE sensitivity_level='CRITICAL'").fetchone()[0]
        conn.close()
    except:
        total_assets, critical_assets = 0, 0
        
    try:
        with open(DOMAINS_FILE, "r") as f: d = json.load(f)
        total_domains = len(d)
    except: total_domains = 0
    
    try:
        conn = sqlite3.connect("/home/izu/ShadowAI_Framework/Section3_Dashboard/users.db")
        total_users = conn.execute("SELECT COUNT(*) FROM monitored_users").fetchone()[0]
        conn.close()
    except:
        total_users = 0

    st.markdown(f"""
        <div style="display: flex; gap: 16px; margin-bottom: 24px;">
            <div class="um-kpi-card" style="flex: 1;">
                <div class="um-kpi-left">
                    <span class="um-kpi-title">TOTAL ASSETS</span>
                    <span class="um-kpi-value">{total_assets}</span>
                </div>
                <div class="um-kpi-icon um-icon-blue"></div>
            </div>
            <div class="um-kpi-card" style="flex: 1;">
                <div class="um-kpi-left">
                    <span class="um-kpi-title">TRACKED DOMAINS</span>
                    <span class="um-kpi-value">{total_domains}</span>
                </div>
                <div class="um-kpi-icon um-icon-green"></div>
            </div>
            <div class="um-kpi-card" style="flex: 1;">
                <div class="um-kpi-left">
                    <span class="um-kpi-title">MONITORED USERS</span>
                    <span class="um-kpi-value">{total_users}</span>
                </div>
                <div class="um-kpi-icon um-icon-purple"></div>
            </div>
            <div class="um-kpi-card" style="flex: 1;">
                <div class="um-kpi-left">
                    <span class="um-kpi-title">CRITICAL ASSETS</span>
                    <span class="um-kpi-value">{critical_assets}</span>
                </div>
                <div class="um-kpi-icon" style="background: rgba(255,51,102,0.1); color: #ff3366; border-radius: 8px; width: 40px; height: 40px;"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # --- 1. SENSITIVE ASSETS DATABASE ---
    with st.container(border=True):
        st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(0, 212, 255, 0.02) 100%); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); border: 1px solid rgba(0, 212, 255, 0.2); border-left: 4px solid #00d4ff; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3); padding: 16px 20px; margin-bottom: 20px; border-radius: 8px;">
                <h3 style="margin: 0; color: #00d4ff; font-size: 20px; font-weight: 600; letter-spacing: 1px;">MASTER SENSITIVE ASSETS</h3>
                <p style="margin: 6px 0 0 0; color: #a0aec0; font-size: 15px;">Active records tracked by the system. If intercepted data matches any of these, it triggers semantic alerts.</p>
            </div>
        """, unsafe_allow_html=True)
        
        try:
            conn = sqlite3.connect(ASSETS_DB_PATH)
            
            # --- Search Bar ---
            search_q = st.text_input("🔍 Search Assets (by Record ID, Name, SSN, or content)", placeholder="Type to filter...")
            
            if search_q:
                df_assets = pd.read_sql_query("SELECT * FROM master_assets WHERE original_attributes LIKE ? OR record_id LIKE ? LIMIT 100", conn, params=('%'+search_q+'%', '%'+search_q+'%'))
                if not df_assets.empty:
                    st.dataframe(df_assets, use_container_width=True, height=250, hide_index=True)
                else:
                    st.warning("No assets found for the given search.")
            else:
                df_assets = pd.DataFrame()
                st.info("👆 Please use the search bar above to query assets.")
            
            # Extract schemas dynamically
            c = conn.cursor()
            c.execute('SELECT section, original_attributes FROM master_assets GROUP BY section')
            schemas = {}
            for row in c.fetchall():
                try:
                    schemas[row[0]] = list(json.loads(row[1]).keys())
                except: pass
                
        except Exception as e:
            st.error(f"Error loading assets database: {e}")
            df_assets = pd.DataFrame()
            schemas = {"Default Category": ["RECORD ID", "DATA TIER", "SENSITIVITY LEVEL", "ASSET WEIGHT", "SECTION"]}
            
        st.markdown('<div class="um-section-title green">➕ ADD NEW ASSET (DYNAMIC SCHEMA)</div>', unsafe_allow_html=True)
        
        # Select Category First (outside form so it triggers rerun and updates form fields)
        selected_section = st.selectbox("Select Asset Category (Schema):", list(schemas.keys()), key="asset_cat_select")
        
        with st.form("add_asset_form", clear_on_submit=True):
            st.markdown(f"Fill out the dynamic fields for **{selected_section}**.")
            
            fields = schemas.get(selected_section, [])
            input_vals = {}
            
            cols = st.columns(3)
            for i, field in enumerate(fields):
                # Put in columns sequentially
                col = cols[i % 3]
                # Try to determine if it should be a selectbox or default
                if field.upper() == "SENSITIVITY LEVEL":
                    input_vals[field] = col.selectbox(field, ["LOW", "MEDIUM", "HIGH", "CRITICAL"])
                elif field.upper() == "DATA TIER":
                    input_vals[field] = col.selectbox(field, ["Tier 1 - PHI", "Tier 2", "Tier 3"])
                elif field.upper() == "SEVERITY":
                    input_vals[field] = col.selectbox(field, ["Low", "Moderate", "High", "Severe", "Critical"])
                else:
                    input_vals[field] = col.text_input(field)
                    
            if st.form_submit_button("Save Asset to Database", type="primary", use_container_width=True):
                # Validate at least one field has data
                has_data = any(str(v).strip() for v in input_vals.values())
                if has_data:
                    try:
                        # Extract core fields if they exist in schema, else default
                        rec_id = input_vals.get("RECORD ID", "").strip()
                        if not rec_id: rec_id = str(uuid.uuid4())[:8]
                        
                        a_name = input_vals.get("PATIENT NAME", input_vals.get("SERVER NAME", input_vals.get("USERNAME", "")))
                        a_ssn = input_vals.get("SSN", "")
                        a_pat_id = input_vals.get("PATIENT ID", "")
                        a_dob = input_vals.get("DATE OF BIRTH", "")
                        a_bld = input_vals.get("BLOOD TYPE", "")
                        a_nat = input_vals.get("NATIONALITY", "")
                        
                        a_tier = input_vals.get("DATA TIER", "Tier 3")
                        a_sens = input_vals.get("SENSITIVITY LEVEL", "LOW")
                        
                        # Fix weight logic
                        weight_str = str(input_vals.get("ASSET WEIGHT", "0.5")).strip()
                        try:
                            a_weight = float(weight_str) if weight_str else 0.5
                        except:
                            a_weight = 0.95 if a_sens == "CRITICAL" else (0.8 if a_sens == "HIGH" else 0.5)
                        
                        # Enforce RECORD ID in json
                        input_vals["RECORD ID"] = rec_id
                        
                        c = conn.cursor()
                        c.execute("""
                            INSERT INTO master_assets 
                            (sheet_name, record_id, patient_name, patient_id, ssn, date_of_birth, blood_type, nationality, data_tier, section, asset_weight, sensitivity_level, original_attributes) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, ("Manual Entry", rec_id, a_name, a_pat_id, a_ssn, a_dob, a_bld, a_nat, a_tier, selected_section, a_weight, a_sens, json.dumps(input_vals)))
                        
                        if a_name: c.execute("INSERT OR IGNORE INTO asset_tokens (token_value, record_id) VALUES (?, ?)", (a_name.lower(), rec_id))
                        if a_ssn:  c.execute("INSERT OR IGNORE INTO asset_tokens (token_value, record_id) VALUES (?, ?)", (a_ssn.lower(), rec_id))
                        
                        conn.commit()
                        st.success(f"Asset '{rec_id}' added successfully to '{selected_section}'!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to add asset: {e}")
                else:
                    st.warning("Please fill out at least one field.")

        st.markdown('<div class="um-section-title red" style="margin-top:20px;">❌ DELETE ASSET</div>', unsafe_allow_html=True)
        del_asset = st.selectbox("Select Asset to Remove:", df_assets["record_id"].tolist() if not df_assets.empty else [], key="del_asset_sb")
        if st.button("Delete Selected Asset", type="primary", use_container_width=True):
            if del_asset:
                try:
                    c = conn.cursor()
                    c.execute("DELETE FROM master_assets WHERE record_id=?", (del_asset,))
                    c.execute("DELETE FROM asset_tokens WHERE record_id=?", (del_asset,))
                    conn.commit()
                    st.success(f"Deleted Asset {del_asset}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error deleting asset: {e}")
        try: conn.close()
        except: pass

    # --- 2. TRACKED AI DOMAINS (FULL WIDTH) ---
    with st.container(border=True):
        st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(14, 203, 129, 0.1) 0%, rgba(14, 203, 129, 0.02) 100%); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); border: 1px solid rgba(14, 203, 129, 0.2); border-left: 4px solid #0ecb81; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3); padding: 16px 20px; margin-bottom: 20px; border-radius: 8px; margin-top: 10px;">
                <h3 style="margin: 0; color: #0ecb81; font-size: 20px; font-weight: 600; letter-spacing: 1px;">TRACKED AI DOMAINS</h3>
                <p style="margin: 6px 0 0 0; color: #a0aec0; font-size: 15px;">Traffic to these external LLM endpoints and domains is actively intercepted and monitored.</p>
            </div>
        """, unsafe_allow_html=True)
        try:
            with open(DOMAINS_FILE, "r") as f: domains = json.load(f)
        except:
            domains = ["chatgpt.com", "claude.ai", "gemini.google.com"]
            
        # Display domains as neat inline badges
        badges = " ".join([f'<span style="background-color:#0A122A; border: 1px solid #16244C; padding: 4px 10px; border-radius: 12px; font-size: 13px; margin: 4px; display: inline-block;">{d}</span>' for d in domains])
        st.markdown(f'<div style="line-height: 2.5;">{badges}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        c1, c2 = st.columns(2)
        with c1:
            with st.form("add_domain_form", clear_on_submit=True):
                st.markdown("**➕ Add New Domain**")
                new_domain = st.text_input("e.g. copilot.microsoft.com", label_visibility="collapsed")
                if st.form_submit_button("Add Domain", use_container_width=True, type="primary"):
                    if new_domain and new_domain not in domains:
                        domains.append(new_domain)
                        with open(DOMAINS_FILE, "w") as f: json.dump(domains, f)
                        st.rerun()
        with c2:
            st.markdown("**❌ Delete Domain**")
            del_domain = st.selectbox("Select Domain to Remove:", domains, key="del_dom_sb", label_visibility="collapsed")
            if st.button("Delete Selected Domain", type="primary", use_container_width=True):
                if del_domain:
                    domains.remove(del_domain)
                    with open(DOMAINS_FILE, "w") as f: json.dump(domains, f)
                    st.rerun()

    # --- 3. MONITORED SYSTEM USERS ---
    with st.container(border=True):
        st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(162, 89, 255, 0.1) 0%, rgba(162, 89, 255, 0.02) 100%); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); border: 1px solid rgba(162, 89, 255, 0.2); border-left: 4px solid #a259ff; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3); padding: 16px 20px; margin-bottom: 20px; border-radius: 8px; margin-top: 10px;">
                <h3 style="margin: 0; color: #a259ff; font-size: 20px; font-weight: 600; letter-spacing: 1px;">MONITORED SYSTEM USERS (ADMIN LIST)</h3>
                <p style="margin: 6px 0 0 0; color: #a0aec0; font-size: 15px;">System users whose actions and data transfers are actively monitored by ContextGuard.</p>
            </div>
        """, unsafe_allow_html=True)
        
        try:
            conn_u = sqlite3.connect("/home/izu/ShadowAI_Framework/Section3_Dashboard/users.db")
            df_monitored = pd.read_sql_query("SELECT * FROM monitored_users", conn_u)
            st.dataframe(df_monitored, use_container_width=True, height=250, hide_index=True)
        except Exception as e:
            st.error(f"Error loading monitored_users: {e}")
            df_monitored = pd.DataFrame()
            
        with st.expander("➕ Add New Monitored User"):
            with st.form("add_monitored_form", clear_on_submit=True):
                mc1, mc2, mc3 = st.columns(3)
                with mc1:
                    m_uid = st.text_input("User ID (e.g. 1050)")
                    m_uname = st.text_input("Username")
                    m_fname = st.text_input("Full Name")
                with mc2:
                    m_email = st.text_input("Email")
                    m_dept = st.text_input("Department")
                    m_role = st.selectbox("Role", ["Standard Staff", "Privileged Admin", "Medical Specialist", "Automated Bot"])
                with mc3:
                    m_weight = st.number_input("User Weight (0.0 to 1.0)", value=0.65, step=0.05)
                    m_asset = st.text_input("Managed Asset Registry", placeholder="e.g. Master Assets DB")
                    m_status = st.selectbox("Account Status", ["Active", "Suspended"])
                    
                if st.form_submit_button("Save Monitored User", type="primary", use_container_width=True):
                    if m_uid and m_uname:
                        try:
                            c = conn_u.cursor()
                            c.execute("""
                                INSERT INTO monitored_users 
                                (user_id, username, full_name, email, department, role, u_weight, managed_asset_registry, account_status)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (m_uid, m_uname, m_fname, m_email, m_dept, m_role, m_weight, m_asset, m_status))
                            conn_u.commit()
                            st.success(f"Added {m_uname}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error adding user: {e}")
                    else:
                        st.warning("User ID and Username are required.")

        st.markdown('<div class="um-section-title red" style="margin-top:20px;">❌ REMOVE MONITORED USER</div>', unsafe_allow_html=True)
        del_mon = st.selectbox("Select User to Remove:", df_monitored["username"].tolist() if not df_monitored.empty else [], key="del_mon_sb")
        if st.button("Delete Monitored User", type="primary", use_container_width=True):
            if del_mon:
                try:
                    c = conn_u.cursor()
                    c.execute("DELETE FROM monitored_users WHERE username=?", (del_mon,))
                    conn_u.commit()
                    st.success(f"Deleted {del_mon}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error deleting user: {e}")
        try: conn_u.close()
        except: pass
