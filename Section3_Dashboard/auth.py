import streamlit as st
import streamlit.components.v1 as components
import sqlite3
import hashlib
import os
import re
import time
import base64
import uuid
import json
import extra_streamlit_components as stx

DB_PATH = "/home/izu/ShadowAI_Framework/Section3_Dashboard/users.db"
SESSION_DIR = "/tmp/shadowai_sessions"
os.makedirs(SESSION_DIR, exist_ok=True)

_cookie_manager = None
def get_cookie_manager():
    global _cookie_manager
    if _cookie_manager is None:
        _cookie_manager = stx.CookieManager(key="auth_cm")
    return _cookie_manager

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_auth_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT,
            role TEXT
        )
    ''')
    # Seed default admin only if the database is completely empty
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            'INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)', 
            ("admin", hash_password("adminpassword"), "Admin L2")
        )
    conn.commit()
    
    # Update existing users to new roles just in case
    cursor.execute('UPDATE users SET role = "Admin L2" WHERE role = "Senior Security Architect"')
    cursor.execute('UPDATE users SET role = "L1" WHERE role = "AI Governance Auditor"')
    conn.commit()
    
    conn.close()

#  USER MANAGEMENT HELPERS 
def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT username, role FROM users')
    users = cursor.fetchall()
    conn.close()
    return [{"username": u[0], "role": u[1]} for u in users]

def add_user(username, password, role):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)', (username, hash_password(password), role))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False # User already exists
    conn.close()
    return success

def delete_user(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE username = ?', (username,))
    conn.commit()
    conn.close()

#  SESSION PERSISTENCE HELPERS 
def create_session(username, role):
    """Create a server-side session file. Returns the session token."""
    token = str(uuid.uuid4())
    data  = {"username": username, "role": role, "created": time.time()}
    with open(f"{SESSION_DIR}/{token}.json", "w") as f:
        json.dump(data, f)
    return token

def validate_session(token):
    """Return (username, role) if the token is valid, else (None, None)."""
    if not token:
        return None, None
    path = f"{SESSION_DIR}/{token}.json"
    if not os.path.exists(path):
        return None, None
    try:
        with open(path) as f:
            data = json.load(f)
        # Expire sessions after 12 hours
        if time.time() - data["created"] > 43200:
            os.remove(path)
            return None, None
        return data["username"], data["role"]
    except Exception:
        return None, None

def destroy_session(token):
    """Delete the session file on logout."""
    if token:
        path = f"{SESSION_DIR}/{token}.json"
        if os.path.exists(path):
            os.remove(path)


def check_auth():
    """Return True if already authenticated in session_state,
    OR if a valid session token exists in cookies/URL."""
    if st.session_state.get('authenticated', False):
        return True
    
    cm = get_cookie_manager()
    token = cm.get(cookie="shadowai_sid")
    
    # Fallback to URL token if cookie not immediately available
    if not token:
        token = st.query_params.get("_sid", None)
        
    if token:
        username, role = validate_session(token)
        if username:
            st.session_state['authenticated']  = True
            st.session_state['username']        = username
            st.session_state['user_role']       = role
            st.session_state['session_token']   = token
            st.session_state['login_attempts']  = 0
            st.session_state['lockout_time']    = 0
            # Ensure cookie is set for future tabs
            if not cm.get(cookie="shadowai_sid"):
                cm.set("shadowai_sid", token)
            return True
    return False

def logout_user():
    cm = get_cookie_manager()
    token = st.session_state.get('session_token')
    destroy_session(token)
    cm.delete("shadowai_sid")
    st.session_state['authenticated']  = False
    st.session_state['username']       = None
    st.session_state['user_role']      = None
    st.session_state['login_attempts'] = 0
    st.session_state['session_token']  = None
    # Clear the token from the URL so the login page is clean
    st.query_params.clear()
    st.rerun()

def sanitize_input(val):
    """WAF-style input sanitization — blocks SQLi, XSS, command injection."""
    if not val:
        return False, "Input cannot be empty."
    if len(val) > 50:
        return False, "Input length exceeds security threshold."
    if any(char in val for char in ["'", '"', ';', '--', '/*', '*/', '<', '>', '`', '=']):
        return False, "🛡️ CONTEXTGUARD WAF ALERT: SQL Injection or XSS payload detected. Access Blocked."
    return True, val

def verify_login(username, password):
    """Parameterized query — guarantees absolute SQLi protection."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT password_hash, role FROM users WHERE username = ?', (username,))
    row = cursor.fetchone()
    conn.close()
    if row and row[0] == hash_password(password):
        return True, row[1]
    return False, None


# 
def render_login_page():
# 
    if 'login_attempts' not in st.session_state:
        st.session_state['login_attempts'] = 0
    if 'lockout_time' not in st.session_state:
        st.session_state['lockout_time'] = 0

    #  Encode logo as base64 for inline embedding 
    logo_path = "/home/izu/ShadowAI_Framework/Logo/ContextGuard.png"
    logo_b64 = ""
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode()
    logo_html = f"<img src='data:image/png;base64,{logo_b64}' alt='ContextGuard'/>" if logo_b64 else "🛡️"

    #  Inject full-page CSS 
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

            /* ── FULL PAGE RESET ── */
            html, body {{
                overflow: hidden !important;
                height: 100% !important;
                margin: 0 !important;
                padding: 0 !important;
            }}
            [data-testid="stSidebar"],
            [data-testid="stHeader"],
            [data-testid="stDecoration"],
            [data-testid="stStatusWidget"] {{
                display: none !important;
            }}

            /* ── PAGE BACKGROUND ── */
            section[data-testid="stMain"] {{
                overflow: hidden !important;
                height: 100vh !important;
                padding: 0 !important;
                margin: 0 !important;
                background: #050d1f !important;
                background-image:
                    radial-gradient(ellipse 90% 70% at 15% 50%, rgba(6,182,212,0.08) 0%, transparent 65%),
                    radial-gradient(ellipse 70% 90% at 85% 25%, rgba(99,102,241,0.07) 0%, transparent 65%),
                    radial-gradient(ellipse 80% 60% at 50% 95%, rgba(14,165,233,0.05) 0%, transparent 60%) !important;
            }}

            /* ── CENTER BLOCK ── */
            div[data-testid="stMainBlockContainer"] {{
                padding: 0 !important;
                margin: 0 !important;
                width: 100% !important;
                max-width: 100% !important;
                height: 100vh !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
            }}

            /* ── CARD ── */
            div[data-testid="stForm"] {{
                background: rgba(10, 18, 42, 0.75) !important;
                backdrop-filter: blur(28px) !important;
                -webkit-backdrop-filter: blur(28px) !important;
                border: 1px solid rgba(6, 182, 212, 0.2) !important;
                border-radius: 22px !important;
                box-shadow:
                    0 0 0 1px rgba(255,255,255,0.04) inset,
                    0 28px 60px rgba(0,0,0,0.55),
                    0 0 80px rgba(6,182,212,0.07) !important;
                padding: 48px 52px 40px !important;
                width: 460px !important;
                max-width: 92vw !important;
                margin: auto !important;
            }}

            /* ── LOGO HEADER ── */
            .cg-header {{
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 16px;
                margin-bottom: 40px;
            }}
            .cg-logo-wrap {{
                width: 76px;
                height: 76px;
                border-radius: 20px;
                background: linear-gradient(135deg, rgba(6,182,212,0.15), rgba(14,165,233,0.08));
                border: 1px solid rgba(6,182,212,0.3);
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 8px 32px rgba(6,182,212,0.18), inset 0 1px 1px rgba(255,255,255,0.08);
                overflow: hidden;
                padding: 8px;
            }}
            .cg-logo-wrap img {{
                width: 100%;
                height: 100%;
                object-fit: contain;
            }}
            .cg-brand-name {{
                font-family: 'Inter', sans-serif;
                font-size: 28px;
                font-weight: 800;
                letter-spacing: -0.8px;
                line-height: 1;
                margin: 0;
                text-align: center;
            }}
            .cg-brand-name .w {{ color: #E8F0FE; }}
            .cg-brand-name .c {{ color: #06B6D4; }}
            .cg-tagline {{
                font-family: 'Inter', sans-serif;
                font-size: 10.5px;
                color: rgba(148,163,184,0.6);
                letter-spacing: 2.5px;
                text-transform: uppercase;
                margin-top: 2px;
                text-align: center;
            }}
            .cg-rule {{
                width: 36px;
                height: 2px;
                background: linear-gradient(90deg, transparent, rgba(6,182,212,0.8), transparent);
                border-radius: 1px;
            }}

            /* ── FIELD LABELS ── */
            div[data-testid="stForm"] label p,
            div[data-testid="stForm"] [data-testid="stWidgetLabel"] p {{
                font-family: 'Inter', sans-serif !important;
                font-size: 11px !important;
                font-weight: 600 !important;
                color: rgba(148,163,184,0.75) !important;
                letter-spacing: 1.5px !important;
                text-transform: uppercase !important;
                margin-bottom: 8px !important;
            }}

            /* ── WRAPPER RESET ── */
            div[data-testid="stForm"] div[data-testid="stTextInput"] > div,
            div[data-testid="stForm"] div[data-testid="stTextInput"] > div > div {{
                background: transparent !important;
                border: none !important;
                box-shadow: none !important;
                padding: 0 !important;
                margin: 0 !important;
            }}
            div[data-testid="stForm"] div[data-testid="stTextInput"] {{
                margin-bottom: 10px !important;
            }}

            /* ── INPUT BOX ── */
            div[data-testid="stForm"] div[data-baseweb="input"] {{
                position: relative !important;
                display: flex !important;
                align-items: center !important;
                background: rgba(255,255,255,0.04) !important;
                border: 1px solid rgba(255,255,255,0.09) !important;
                border-radius: 12px !important;
                padding: 0 !important;
                transition: border-color 0.2s ease, box-shadow 0.2s ease, background 0.2s ease !important;
                overflow: hidden !important;
                box-sizing: border-box !important;
            }}
            div[data-testid="stForm"] div[data-baseweb="input"]:focus-within {{
                border-color: rgba(6,182,212,0.65) !important;
                background: rgba(6,182,212,0.04) !important;
                box-shadow: 0 0 0 3px rgba(6,182,212,0.1) !important;
            }}

            /* NUKE BASEWEB INTERNAL STYLES */
            div[data-testid="stForm"] div[data-baseweb="input"] * {{
                background: transparent !important;
                background-color: transparent !important;
                border: none !important;
                box-shadow: none !important;
            }}
            div[data-testid="stForm"] div[data-baseweb="base-input"] {{
                display: flex !important;
                flex: 1 !important;
                width: 100% !important;
                min-width: 0 !important;
                padding: 0 !important;
                margin: 0 !important;
            }}

            /* INPUT ELEMENT */
            div[data-testid="stForm"] input {{
                flex: 1 !important;
                width: 100% !important;
                color: #E2EBF8 !important;
                font-family: 'Inter', sans-serif !important;
                font-size: 14.5px !important;
                font-weight: 400 !important;
                padding: 15px 48px 15px 16px !important;
                margin: 0 !important;
                outline: none !important;
                -webkit-appearance: none !important;
                caret-color: #06B6D4 !important;
            }}
            div[data-testid="stForm"] input::placeholder {{
                color: rgba(148,163,184,0.38) !important;
                font-size: 13.5px !important;
            }}
            div[data-testid="stForm"] input:-webkit-autofill,
            div[data-testid="stForm"] input:-webkit-autofill:focus {{
                -webkit-box-shadow: 0 0 0 1000px rgba(10,18,42,0.95) inset !important;
                -webkit-text-fill-color: #E2EBF8 !important;
                caret-color: #06B6D4 !important;
            }}

            /* HIDE STREAMLIT SUFFIX BOX & NATIVE EYE */
            div[data-testid="stForm"] div[data-baseweb="input"] > div:not([data-baseweb="base-input"]) {{
                display: none !important;
                width: 0 !important;
                overflow: hidden !important;
            }}
            div[data-testid="stForm"] div[data-baseweb="input"] button {{
                display: none !important;
            }}

            /* CUSTOM EYE TOGGLE BUTTON (injected by JS) */
            .cg-eye-btn {{
                position: absolute !important;
                right: 13px !important;
                top: 50% !important;
                transform: translateY(-50%) !important;
                background: none !important;
                border: none !important;
                cursor: pointer !important;
                padding: 5px !important;
                display: flex !important;
                align-items: center !important;
                z-index: 20 !important;
                border-radius: 6px !important;
                opacity: 0.45 !important;
                transition: opacity 0.2s !important;
            }}
            .cg-eye-btn:hover {{ opacity: 0.9 !important; }}

            /* ── SUBMIT BUTTON ── */
            div[data-testid="stForm"] div[data-testid="stFormSubmitButton"] button {{
                font-family: 'Inter', sans-serif !important;
                background: linear-gradient(135deg, #0EA5E9 0%, #06B6D4 100%) !important;
                color: #fff !important;
                border: none !important;
                border-radius: 12px !important;
                padding: 15px 24px !important;
                font-weight: 600 !important;
                font-size: 14px !important;
                letter-spacing: 0.3px !important;
                box-shadow: 0 4px 20px rgba(6,182,212,0.35) !important;
                transition: box-shadow 0.25s ease, transform 0.2s ease !important;
                width: 100% !important;
                cursor: pointer !important;
                margin-top: 10px !important;
            }}
            div[data-testid="stForm"] div[data-testid="stFormSubmitButton"] button:hover {{
                box-shadow: 0 10px 32px rgba(6,182,212,0.55) !important;
                transform: translateY(-1px) !important;
            }}

            /* HIDE "Press Enter to submit form" */
            div[data-testid="stForm"] [data-testid="InputInstructions"],
            div[data-testid="stForm"] small {{
                display: none !important;
            }}
        </style>

        <!-- ── LOGO + BRAND HEADER ── -->
        <div class="cg-header">
            <div class="cg-logo-wrap">{logo_html}</div>
            <div>
                <div class="cg-brand-name">
                    <span class="w">Context</span><span class="c">Guard</span>
                </div>
                <div class="cg-tagline">AI Governance Framework</div>
            </div>
            <div class="cg-rule"></div>
        </div>
    """, unsafe_allow_html=True)

    #  Brute-force lockout 
    if st.session_state['login_attempts'] >= 5:
        elapsed = time.time() - st.session_state['lockout_time']
        if elapsed < 30:
            st.error(f"🚨 **Security Lockout Active** — Too many failed attempts. Wait {int(30 - elapsed)}s.")
            st.stop()
        else:
            st.session_state['login_attempts'] = 0

    with st.form(key="login_form"):
        username = st.text_input("Username", placeholder="admin or user")
        password = st.text_input("Password", type="password", placeholder="Enter your password")

        #  JS: Inject custom SVG eye-toggle button at exact right edge 
        components.html("""
        <script>
        function injectEye() {
            try {
                var doc = window.parent.document;
                doc.querySelectorAll('div[data-baseweb="input"] input').forEach(function(inp) {
                    var box = inp.closest('div[data-baseweb="input"]');
                    if (!box || box.querySelector('.cg-eye-btn')) return;
                    var btn = doc.createElement('button');
                    btn.type = 'button';
                    btn.className = 'cg-eye-btn';
                    btn.title = 'Show / Hide password';
                    var open = '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#94A3B8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>';
                    var off  = '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#94A3B8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>';
                    btn.innerHTML = open;
                    btn.addEventListener('click', function(e) {
                        e.preventDefault(); e.stopPropagation();
                        if (inp.type === 'password') { inp.type = 'text';     btn.innerHTML = off;  }
                        else                         { inp.type = 'password'; btn.innerHTML = open; }
                    });
                    box.appendChild(btn);
                });
            } catch(e) {}
        }
        injectEye();
        setTimeout(injectEye, 150);
        setTimeout(injectEye, 500);
        setTimeout(injectEye, 1100);
        </script>
        """, height=0)

        submit = st.form_submit_button("Sign In →", use_container_width=True)

        if submit:
            if not username or not password:
                st.error("⚠️ Please enter both username and password.")
            else:
                valid, msg = sanitize_input(username)
                if not valid:
                    st.error(msg)
                else:
                    success, role = verify_login(username, password)
                    if success:
                        cm = get_cookie_manager()
                        # Create persistent session token
                        token = create_session(username, role)
                        cm.set("shadowai_sid", token)
                        st.session_state['authenticated']  = True
                        st.session_state['username']       = username
                        st.session_state['user_role']      = role
                        st.session_state['session_token']  = token
                        st.session_state['login_attempts'] = 0
                        st.session_state['nav_radio']       = "🤖 AI Discovery"
                        st.session_state['last_seen_radio'] = "🤖 AI Discovery"
                        st.session_state['last_seen_url']   = "AI Discovery"
                        st.query_params["_sid"]  = token
                        st.query_params["page"]  = "AI Discovery"
                        st.rerun()
                    else:
                        st.session_state['login_attempts'] += 1
                        if st.session_state['login_attempts'] >= 5:
                            st.session_state['lockout_time'] = time.time()
                            st.error("🚨 **Security Lockout:** 5 failed attempts. Locked for 30 seconds.")
                        else:
                            st.error(f"❌ Invalid credentials. (Attempt {st.session_state['login_attempts']}/5)")
