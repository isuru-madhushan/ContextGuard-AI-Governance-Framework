import streamlit as st
import os
import pandas as pd
from datetime import datetime, timedelta
from PIL import Image
from streamlit_autorefresh import st_autorefresh

# 
#  PAGE CONFIG (MUST BE FIRST)
# 
page_logo_path = "/home/izu/ShadowAI_Framework/Logo/ContextGuard.png"
fav_icon = Image.open(page_logo_path) if os.path.exists(page_logo_path) else "🛡️"

st.set_page_config(
    page_title="ContextGuard",
    layout="wide",
    page_icon=fav_icon,
    initial_sidebar_state="expanded"
)

#  IMPORTS 
from styles import THREATMON_CSS
from data_core import LOG_FILE, process_events, load_custom_assets
from pages_contextguard import (
    render_dashboard_page,
    render_alert_feed_page,
    render_forensic_page,
    render_phi_registry_page,
    render_asset_manager_page,
    render_wrse_ref_page
)
from pages_admin import (
    render_user_management,
    render_asset_management
)
from auth import init_auth_db, check_auth, render_login_page, logout_user
from components import _get_monitor_status

#  INJECT CSS 
st.markdown(THREATMON_CSS, unsafe_allow_html=True)

#  DYNAMIC BACKGROUND WATERMARK 
try:
    import base64
    logo_path = "/home/izu/ShadowAI_Framework/Logo/ContextGuard.png"
    with open(logo_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    
    bg_css = f"""
    <style>
    .stApp::before {{
        content: "";
        position: fixed;
        top: 50%;
        left: 50%;
        width: 650px;
        height: 650px;
        background-image: url('data:image/png;base64,{b64}');
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
        opacity: 0.04;
        transform: translate(-50%, -50%);
        pointer-events: none;
        z-index: 0;
        animation: floatLogo 12s ease-in-out infinite;
    }}
    @keyframes floatLogo {{
        0%   {{ transform: translate(-50%, -50%) scale(1) rotate(0deg); opacity: 0.03; }}
        50%  {{ transform: translate(-50%, -53%) scale(1.05) rotate(1.5deg); opacity: 0.06; }}
        100% {{ transform: translate(-50%, -50%) scale(1) rotate(0deg); opacity: 0.03; }}
    }}
    </style>
    """
    st.markdown(bg_css, unsafe_allow_html=True)
except Exception as e:
    pass


#  AUTHENTICATION CHECK 
init_auth_db()
if not check_auth():
    render_login_page()
    st.stop()

# Load core data
df_raw, phi_mc, all_sheets = process_events()
custom_assets = load_custom_assets()

# 
#  SIDEBAR  ContextGuard Menu & Real Logo
# 
with st.sidebar:
    logo_path = "/home/izu/ShadowAI_Framework/Logo/ContextGuard.png"
    if os.path.exists(logo_path):
        col_l, col_m, col_r = st.columns([1, 1.8, 1])
        with col_m:
            st.image(logo_path, use_container_width=True)
    
    st.markdown("""<div style="text-align:center;margin-top:-5px;margin-bottom:15px;">
<div style="font-size:26px;font-weight:900;letter-spacing:-0.5px;"><span style="color:#E2EBF8;">Context</span><span style="color:#06B6D4;">Guard</span></div>
<div style="font-size:10px;color:#647E9C;font-family:monospace;letter-spacing:0.5px;margin-top:2px;">CONTEXT-AWARE AI GOVERNANCE FRAMEWORK</div>
</div>""", unsafe_allow_html=True)

    st.markdown("""<div class="live-badge">
<div class="live-dot"></div>
<span class="live-txt">MONITORING ACTIVE</span>
</div>""", unsafe_allow_html=True)

    #  LOGOUT BUTTON (before user badge) 
    st.markdown("""
        <style>
        div[data-testid="stSidebar"] button[data-testid="baseButton-secondary"] {
            background: rgba(255, 60, 60, 0.07) !important;
            border: 1px solid rgba(255, 80, 80, 0.25) !important;
            color: #FC8181 !important;
            border-radius: 10px !important;
            font-size: 13px !important;
            font-weight: 600 !important;
            letter-spacing: 0.3px !important;
            transition: background 0.2s ease, border 0.2s ease !important;
        }
        div[data-testid="stSidebar"] button[data-testid="baseButton-secondary"]:hover {
            background: rgba(255, 60, 60, 0.18) !important;
            border-color: rgba(255, 80, 80, 0.55) !important;
            color: #FEB2B2 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    if st.button("⏻  Sign Out", use_container_width=True, key="sidebar_logout", type="secondary"):
        logout_user()

    #  USER LOGGED IN BADGE 
    st.markdown(
        f"<div style='font-size:12px;color:#38BDF8;font-family:monospace;text-align:center;padding:6px;background:#0D1938;border-radius:8px;border:1px solid #1D3364;margin-bottom:15px;'>"
        f"👤 Logged in as: <b>{st.session_state.get('username', 'admin')}</b><br>"
        f"<span style='font-size:10px;color:#647E9C;'>{st.session_state.get('user_role', 'Admin')}</span></div>",
        unsafe_allow_html=True
    )

    #  REFRESH CONTROLS (MANUAL & AUTO-REFRESH INTERVAL) 
    st.markdown("<div style='font-size:11px;font-family:monospace;font-weight:700;color:#06B6D4;margin-bottom:6px;letter-spacing:0.5px;'> DATA REFRESH MODE</div>", unsafe_allow_html=True)
    
    ref_col1, ref_col2 = st.columns([1.1, 0.9])
    with ref_col1:
        if st.button("🔄 Manual", use_container_width=True, key="sb_refresh"):
            st.cache_data.clear()
            st.rerun()
            
    with ref_col2:
        auto_interval = st.selectbox("Interval", ["Off", "30s", "1 min", "2 min", "5 min", "10 min"], index=2, key="auto_ref_box", label_visibility="collapsed")
        
    if auto_interval != "Off":
        interval_map = {"30s": 30, "1 min": 60, "2 min": 120, "5 min": 300, "10 min": 600}
        secs = interval_map.get(auto_interval, 60)
        st_autorefresh(interval=secs * 1000, key="threatmon_autorefresh")


    if os.path.exists(LOG_FILE):
        mtime = os.path.getmtime(LOG_FILE)
        last_mod = datetime.fromtimestamp(mtime).strftime("%H:%M:%S")
        log_size = os.path.getsize(LOG_FILE)
        st.markdown(
            f'<div style="font-size:10px;font-family:monospace;color:#647E9C;text-align:center;padding:8px 0;">'
            f'Log updated: <span style="color:#10B981;">{last_mod}</span>  {log_size//1024} KB</div>',
            unsafe_allow_html=True
        )

    st.markdown("<hr style='border:none;height:1px;background:#1D3364;margin:12px 0;'>", unsafe_allow_html=True)
    st.markdown('<div class="sb-menu-title">AI GOVERNANCE SURFACE</div>', unsafe_allow_html=True)

    #  ADVANCED BROWSER BACK/FORWARD NAVIGATION SYNCHRONIZATION 
    user_role = st.session_state.get('user_role', 'L1')
    NAV_ITEMS = [
        "🤖 AI Discovery",
        "💬 Prompt Inspector",
        "🧠 Semantic Analytics",
    ]
    if "Admin" in user_role or "L2" in user_role:
        NAV_ITEMS.extend([
            "👥 User Management",
            "📦 Asset Management"
        ])
    
    NAV_MAP = {item.split(" ", 1)[1]: item for item in NAV_ITEMS}

    # 1. Check current URL query param
    curr_url_page = st.query_params.get("page", None)
    if curr_url_page:
        curr_url_page = curr_url_page.replace("+", " ")
        
    # 2. Check if Inspect button was clicked (flag set by nav_to_alert)
    if st.session_state.get("inspect_button_clicked", False):
        st.session_state.inspect_button_clicked = False
        target_nav = "💬 Prompt Inspector"
        st.session_state.nav_radio = target_nav
        st.query_params["page"] = "Prompt Inspector"
        st.session_state.last_seen_url = "Prompt Inspector"
        st.session_state.last_seen_radio = target_nav

    # 3. Handle Browser Back/Forward vs Radio Click
    else:
        last_url = st.session_state.get("last_seen_url", None)
        last_radio = st.session_state.get("last_seen_radio", None)
        curr_radio = st.session_state.get("nav_radio", "🤖 AI Discovery")
        
        # Case A: Browser URL changed via Back/Forward button! (curr_url_page != last_url)
        if curr_url_page and curr_url_page != last_url and curr_url_page in NAV_MAP:
            target_nav = NAV_MAP[curr_url_page]
            st.session_state.nav_radio = target_nav
            st.session_state.last_seen_url = curr_url_page
            st.session_state.last_seen_radio = target_nav
            st.rerun()

        # Case B: User clicked the st.radio widget! (curr_radio != last_radio)
        elif curr_radio != last_radio:
            clean = curr_radio.split(" ", 1)[1]
            st.query_params["page"] = clean
            st.session_state.last_seen_url = clean
            st.session_state.last_seen_radio = curr_radio

        # Case C: Initial load or no navigation change
        else:
            if not curr_url_page or curr_url_page not in NAV_MAP:
                st.query_params["page"] = curr_radio.split(" ", 1)[1]
                st.session_state.last_seen_url = curr_radio.split(" ", 1)[1]
            else:
                st.session_state.last_seen_url = curr_url_page
            st.session_state.last_seen_radio = curr_radio

    # Render st.radio bound directly to "nav_radio"
    nav = st.radio("Navigation", NAV_ITEMS, key="nav_radio", label_visibility="collapsed")
    
    # Keep last seen state perfectly updated
    st.session_state.last_seen_radio = nav
    st.session_state.last_seen_url = nav.split(" ", 1)[1]

    st.markdown("<hr style='border:none;height:1px;background:#1D3364;margin:16px 0;'>", unsafe_allow_html=True)

    if not df_raw.empty:
        crit_n = len(df_raw[df_raw["Severity"] == "CRITICAL"])
        med_n  = len(df_raw[df_raw["Severity"] == "MEDIUM"])
        low_n  = len(df_raw[df_raw["Severity"] == "LOW"])
        phi_n  = len(df_raw[df_raw["PHI Matched"] != "—"])
        st.markdown(f"""<div style='background: linear-gradient(135deg, #0D1938, #070D1F); border: 1px solid #1D3364; border-radius: 10px; padding: 14px 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.2); margin: 0 10px;'>
<div style='font-size:11px;font-family:monospace;font-weight:700;color:#06B6D4;margin-bottom:12px;letter-spacing:0.5px;'> LIVE SYSTEM METRICS</div>
<div style='display: flex; align-items: center; justify-content: space-between; padding: 6px 10px; background: rgba(255,255,255,0.03); border-radius: 6px; margin-bottom: 8px;'>
<span style='font-size:12px;font-family:monospace;color:#E2EBF8;font-weight:600;'> Total Ingested</span>
<span style='font-size:13px;font-family:monospace;font-weight:800;color:#38BDF8;background: rgba(56,189,248,0.15); padding: 2px 10px; border-radius: 12px; border: 1px solid rgba(56,189,248,0.3);'>{len(df_raw)}</span>
</div>
<div style='display: flex; align-items: center; justify-content: space-between; padding: 6px 10px; background: rgba(255,45,91,0.04); border-radius: 6px; margin-bottom: 8px; border: 1px solid rgba(255,45,91,0.15);'>
<span style='font-size:12px;font-family:monospace;color:#FF8099;font-weight:600;'> Critical Risk</span>
<span style='font-size:13px;font-family:monospace;font-weight:800;color:#FF2D5B;background: rgba(255,45,91,0.2); padding: 2px 10px; border-radius: 12px; border: 1px solid rgba(255,45,91,0.4); box-shadow: 0 0 8px rgba(255,45,91,0.3);'>{crit_n}</span>
</div>
<div style='display: flex; align-items: center; justify-content: space-between; padding: 6px 10px; background: rgba(245,158,11,0.04); border-radius: 6px; margin-bottom: 8px; border: 1px solid rgba(245,158,11,0.15);'>
<span style='font-size:12px;font-family:monospace;color:#FCD34D;font-weight:600;'> Medium Risk</span>
<span style='font-size:13px;font-family:monospace;font-weight:800;color:#F59E0B;background: rgba(245,158,11,0.2); padding: 2px 10px; border-radius: 12px; border: 1px solid rgba(245,158,11,0.4);'>{med_n}</span>
</div>
<div style='display: flex; align-items: center; justify-content: space-between; padding: 6px 10px; background: rgba(16,185,129,0.04); border-radius: 6px; margin-bottom: 8px; border: 1px solid rgba(16,185,129,0.15);'>
<span style='font-size:12px;font-family:monospace;color:#6EE7B7;font-weight:600;'> Low / Normal</span>
<span style='font-size:13px;font-family:monospace;font-weight:800;color:#10B981;background: rgba(16,185,129,0.2); padding: 2px 10px; border-radius: 12px; border: 1px solid rgba(16,185,129,0.4);'>{low_n}</span>
</div>
<div style='display: flex; align-items: center; justify-content: space-between; padding: 6px 10px; background: rgba(139,92,246,0.04); border-radius: 6px; border: 1px solid rgba(139,92,246,0.15);'>
<span style='font-size:12px;font-family:monospace;color:#C4B5FD;font-weight:600;'> Asset Confirmed</span>
<span style='font-size:13px;font-family:monospace;font-weight:800;color:#8B5CF6;background: rgba(139,92,246,0.2); padding: 2px 10px; border-radius: 12px; border: 1px solid rgba(139,92,246,0.4);'>{phi_n}</span>
</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

# 
#  TOP HEADER & TIME RANGE PICKER (Aligned to Top Right exactly like screenshot)
# 
df_all = df_raw.copy()

top_col1, top_col2, top_col3, top_col4 = st.columns([3.0, 1.2, 1.2, 1.2])

with top_col1:
    if nav == "🤖 AI Discovery":
        st.markdown("""<div style="margin-bottom:0;padding-top:10px;">
<div style="font-size:28px;font-weight:900;letter-spacing:-0.5px;"><span style="color:#E2EBF8;">Context</span><span style="color:#06B6D4;">Guard</span> <span style="color:#647E9C;font-size:24px;font-weight:500;">| AI Discovery</span></div>
<div style="font-size:11px;color:#647E9C;font-family:monospace;letter-spacing:1px;margin-top:2px;">CONTEXT-AWARE AI GOVERNANCE FRAMEWORK</div>
</div>""", unsafe_allow_html=True)
    elif nav == "💬 Prompt Inspector":
        st.markdown("""<div style="margin-bottom:0;padding-top:10px;">
<div style="font-size:28px;font-weight:900;letter-spacing:-0.5px;"><span style="color:#E2EBF8;">Context</span><span style="color:#06B6D4;">Guard</span> <span style="color:#647E9C;font-size:24px;font-weight:500;">|  Prompt Inspector & Payload Analysis</span></div>
<div style="font-size:11px;color:#647E9C;font-family:monospace;letter-spacing:1px;margin-top:2px;">CONTEXT-AWARE AI GOVERNANCE FRAMEWORK  FULL UNTRUNCATED PAYLOADS</div>
</div>""", unsafe_allow_html=True)
    elif nav == "🧠 Semantic Analytics":
        st.markdown("""<div style="margin-bottom:0;padding-top:10px;">
<div style="font-size:28px;font-weight:900;letter-spacing:-0.5px;"><span style="color:#E2EBF8;">Context</span><span style="color:#06B6D4;">Guard</span> <span style="color:#647E9C;font-size:24px;font-weight:500;">|  Semantic Analytics & Multi-Vector Search</span></div>
<div style="font-size:11px;color:#647E9C;font-family:monospace;letter-spacing:1px;margin-top:2px;">CONTEXT-AWARE AI GOVERNANCE FRAMEWORK  HOST INTEL  ADVANCED SEARCH</div>
</div>""", unsafe_allow_html=True)
    elif nav == "📊 Risk Profiler":
        st.markdown("""<div style="margin-bottom:0;padding-top:10px;">
<div style="font-size:28px;font-weight:900;letter-spacing:-0.5px;"><span style="color:#E2EBF8;">Context</span><span style="color:#06B6D4;">Guard</span> <span style="color:#647E9C;font-size:24px;font-weight:500;">|  Risk Profiler & Master Asset Registry</span></div>
<div style="font-size:11px;color:#647E9C;font-family:monospace;letter-spacing:1px;margin-top:2px;">CONTEXT-AWARE AI GOVERNANCE FRAMEWORK  15 INDEXED CSV DATA SHEETS</div>
</div>""", unsafe_allow_html=True)
    elif nav == "🔑 Sensitive Keywords":
        st.markdown("""<div style="margin-bottom:0;padding-top:10px;">
<div style="font-size:28px;font-weight:900;letter-spacing:-0.5px;"><span style="color:#E2EBF8;">Context</span><span style="color:#06B6D4;">Guard</span> <span style="color:#647E9C;font-size:24px;font-weight:500;">|  Sensitive Keywords & Dynamic Weight Assignment</span></div>
<div style="font-size:11px;color:#647E9C;font-family:monospace;letter-spacing:1px;margin-top:2px;">CONTEXT-AWARE AI GOVERNANCE FRAMEWORK  WEIGHT DEFINITION DATABASE</div>
</div>""", unsafe_allow_html=True)
    elif nav == "🧮 Scoring Engine":
        st.markdown("""<div style="margin-bottom:0;padding-top:10px;">
<div style="font-size:28px;font-weight:900;letter-spacing:-0.5px;"><span style="color:#E2EBF8;">Context</span><span style="color:#06B6D4;">Guard</span> <span style="color:#647E9C;font-size:24px;font-weight:500;">|  Scoring Engine & WRSE Mathematical Framework</span></div>
<div style="font-size:11px;color:#647E9C;font-family:monospace;letter-spacing:1px;margin-top:2px;">CONTEXT-AWARE AI GOVERNANCE FRAMEWORK  RESEARCH PAPER  SECTION 5.4</div>
</div>""", unsafe_allow_html=True)

# Time filters only on event-driven pages
if nav in ["🤖 AI Discovery", "💬 Prompt Inspector", "🧠 Semantic Analytics"]:
    with top_col2:
        mon_filter = st.selectbox("Monitor Status", ["All Statuses", "Open", "In Progress", "Close"], key="mon_filter_box")
        if mon_filter != "All Statuses" and not df_all.empty:
            df_all = df_all[df_all["Event ID"].apply(lambda eid: _get_monitor_status(eid) == mon_filter)]

    def reset_table_page():
        if "table_page" in st.session_state:
            st.session_state.table_page = 1

    with top_col3:
        time_type = st.selectbox("Time Type", ["relative", "absolute", "custom window"], key="time_type", on_change=reset_table_page)
    
    with top_col4:
        if time_type == "relative":
            time_int = st.selectbox("Time Interval", ["last 15 minutes", "last 1 hour", "last 12 hours", "last 24 hours", "last 7 days", "this past month", "all time"], index=6, key="time_int", on_change=reset_table_page)
            if time_int != "all time" and not df_all.empty:
                now = datetime.now()
                if time_int == "last 15 minutes": delta = timedelta(minutes=15)
                elif time_int == "last 1 hour": delta = timedelta(hours=1)
                elif time_int == "last 12 hours": delta = timedelta(hours=12)
                elif time_int == "last 24 hours": delta = timedelta(hours=24)
                elif time_int == "last 7 days": delta = timedelta(days=7)
                else: delta = timedelta(days=30) # this past month
                
                parsed_ts = df_all["Timestamp_Parsed"]
                mask = parsed_ts >= (now - delta)
                df_all = df_all[mask]

        elif time_type == "absolute":
            time_int = st.selectbox("Time Interval", ["custom absolute range", "2026 Q1", "2026 Q2", "2026 Q3", "2026 Q4"], key="time_int_abs")

        elif time_type == "custom window":
            time_int = st.selectbox("Time Interval", ["all shifts", "morning shift (06:00 - 14:00)", "evening shift (14:00 - 22:00)", "night shift (22:00 - 06:00)"], key="time_int_cst")
            if time_int != "all shifts" and not df_all.empty:
                parsed_ts = df_all["Timestamp_Parsed"]
                hours = parsed_ts.dt.hour
                if time_int == "morning shift (06:00 - 14:00)": mask = (hours >= 6) & (hours < 14)
                elif time_int == "evening shift (14:00 - 22:00)": mask = (hours >= 14) & (hours < 22)
                else: mask = (hours >= 22) | (hours < 6)
                df_all = df_all[mask]

    if time_type == "absolute" and time_int == "custom absolute range":
        with st.expander("📅 Select Absolute Date & Time Range", expanded=True):
            ab_col1, ab_col2, ab_col3, ab_col4 = st.columns(4)
            with ab_col1: start_d = st.date_input("Start Date", value=datetime(2026, 1, 1))
            with ab_col2: end_d   = st.date_input("End Date", value=datetime(2026, 12, 31))
            with ab_col3: start_t = st.time_input("Start Time", value=datetime.strptime("00:00:00", "%H:%M:%S").time())
            with ab_col4: end_t   = st.time_input("End Time", value=datetime.strptime("23:59:59", "%H:%M:%S").time())
            
            if not df_all.empty:
                st_dt = datetime.combine(start_d, start_t)
                end_dt = datetime.combine(end_d, end_t)
                parsed_ts = df_all["Timestamp_Parsed"]
                mask = (parsed_ts >= st_dt) & (parsed_ts <= end_dt)
                df_all = df_all[mask]

st.markdown("<br>", unsafe_allow_html=True)

# 
#  PAGE ROUTER
# 
if nav == "🤖 AI Discovery":
    render_dashboard_page(df_all, phi_mc, len(custom_assets))
elif nav == "💬 Prompt Inspector":
    render_alert_feed_page(df_all)
elif nav == "🧠 Semantic Analytics":
    render_forensic_page(df_all)
elif nav == "📊 Risk Profiler":
    render_phi_registry_page(all_sheets)
elif nav == "🔑 Sensitive Keywords":
    render_asset_manager_page(custom_assets)
elif nav == "🧮 Scoring Engine":
    render_wrse_ref_page(custom_assets)
elif nav == "👥 User Management":
    render_user_management()
elif nav == "📦 Asset Management":
    render_asset_management()