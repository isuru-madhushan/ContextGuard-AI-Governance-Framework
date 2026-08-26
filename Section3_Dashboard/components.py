import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime
import altair as alt
from data_core import score_bar_html

#  MONITOR STATUS PERSISTENCE (SQLite) 
_MON_DB = "/home/izu/ShadowAI_Framework/Section3_Dashboard/users.db"
_MON_OPTIONS = ["Open", "In Progress", "Close"]

def _init_monitor_table():
    """Create monitor_status table if it doesn't exist yet."""
    conn = sqlite3.connect(_MON_DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS monitor_status (
            event_id TEXT PRIMARY KEY,
            status   TEXT DEFAULT 'Open'
        )
    """)
    conn.commit()
    conn.close()

def _get_monitor_status(event_id):
    """Return saved status for event_id, default 'Open'."""
    try:
        conn = sqlite3.connect(_MON_DB)
        row = conn.execute(
            "SELECT status FROM monitor_status WHERE event_id = ?", (event_id,)
        ).fetchone()
        conn.close()
        return row[0] if row else "Open"
    except Exception:
        return "Open"

def _save_monitor_status(event_id, status):
    """Upsert the status for an event."""
    try:
        conn = sqlite3.connect(_MON_DB)
        conn.execute("""
            INSERT INTO monitor_status (event_id, status)
            VALUES (?, ?)
            ON CONFLICT(event_id) DO UPDATE SET status = excluded.status
        """, (event_id, status))
        conn.commit()
        conn.close()
    except Exception:
        pass

_init_monitor_table()

# 
#  THREATMON REUSABLE UI COMPONENTS (ZERO INDENTATION HTML TO PREVENT CODE BLOCKS)
# 

def render_threatmon_top_strip(df_all, phi_mc, custom_assets_count):
    """
    Renders the exact horizontal icon circle strip seen in ThreatMon:
    11 circular icons with metrics underneath.
    """
    total_ev = len(df_all) if not df_all.empty else 0
    dests = df_all["Destination"].nunique() if not df_all.empty else 0
    ips = df_all["Source IP"].nunique() if not df_all.empty else 0
    crit_n = len(df_all[df_all["Severity"] == "CRITICAL"]) if not df_all.empty else 0
    med_n = len(df_all[df_all["Severity"] == "MEDIUM"]) if not df_all.empty else 0
    low_n = len(df_all[df_all["Severity"] == "LOW"]) if not df_all.empty else 0
    tiers_n = df_all["Data Tier"].nunique() if not df_all.empty else 1
    bots_n = len(df_all[df_all["Identity"] == "Automated Bot"]) if not df_all.empty else 0
    humans_n = len(df_all[df_all["Identity"] == "Human Session"]) if not df_all.empty else 0

    strip_html = f"""<div class="tm-asset-strip">
<div class="tm-asset-item">
<div class="tm-cy-top">
<span>Total Events</span>
<span class="tm-cy-trend up">+12%</span>
</div>
<div class="tm-cy-bottom">
<span class="tm-cy-num">{total_ev}</span>
<div class="tm-cy-chart">
<div class="cy-bar" style="height:40%; background:#10B981;"></div>
<div class="cy-bar" style="height:70%; background:#10B981;"></div>
<div class="cy-bar" style="height:100%; background:#10B981;"></div>
<div class="cy-bar" style="height:60%; background:#10B981;"></div>
<div class="cy-bar" style="height:80%; background:#10B981;"></div>
</div>
</div>
</div>
<div class="tm-asset-item">
<div class="tm-cy-top">
<span>Critical Risk</span>
<span class="tm-cy-trend warn">+8%</span>
</div>
<div class="tm-cy-bottom">
<span class="tm-cy-num">{crit_n}</span>
<div class="tm-cy-chart" style="align-items: center; justify-content: center;">
<div class="cy-donut" style="border-color: #F59E0B;"></div>
</div>
</div>
</div>
<div class="tm-asset-item">
<div class="tm-cy-top">
<span>Asset Matches</span>
<span class="tm-cy-trend up">+2%</span>
</div>
<div class="tm-cy-bottom">
<span class="tm-cy-num">{phi_mc}</span>
<div class="tm-cy-chart" style="align-items: center; justify-content: center;">
<div class="cy-donut" style="border-color: #10B981;"></div>
</div>
</div>
</div>
<div class="tm-asset-item">
<div class="tm-cy-top">
<span>Active Tiers</span>
<span class="tm-cy-trend down">-1%</span>
</div>
<div class="tm-cy-bottom">
<span class="tm-cy-num">{(df_all["Data Tier"].nunique() if not df_all.empty else 1)}</span>
<div class="tm-cy-chart">
<div class="cy-bar" style="height:80%; background:#FF2D5B;"></div>
<div class="cy-bar" style="height:60%; background:#FF2D5B;"></div>
<div class="cy-bar" style="height:40%; background:#FF2D5B;"></div>
<div class="cy-bar" style="height:30%; background:#FF2D5B;"></div>
<div class="cy-bar" style="height:10%; background:#FF2D5B;"></div>
</div>
</div>
</div>
</div>"""
    st.markdown(strip_html, unsafe_allow_html=True)


def render_segmented_metrics_row(df_all):
    if df_all.empty:
        return

    total = len(df_all)
    
    # 1. Leakage Proportions (Asset Confirmed - Critical & High Only)
    phi_matches = len(df_all[(df_all["PHI Matched"] != "—") & (df_all["Severity"].isin(["CRITICAL", "HIGH"]))])
    pct1 = phi_matches / total if total > 0 else 0
    segments = 32
    active_seg1 = int(pct1 * segments)
    svg1 = ""
    for i in range(segments):
        angle = i * (360 / segments)
        color = "#00F0FF" if i < active_seg1 else "#1A2542"
        svg1 += f'<line x1="100" y1="15" x2="100" y2="40" transform="rotate({angle} 100 100)" stroke="{color}" stroke-width="5" stroke-linecap="round"/>\\n'
        
    card1 = f"""<div class="tm-card" style="height: 280px; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 24px;">
<div style="position: relative; width: 200px; height: 180px;">
<svg width="200" height="180" viewBox="0 0 200 200">
{svg1}
</svg>
<div style="position: absolute; top: 0; left: 0; width: 200px; height: 180px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
<div style="font-size: 34px; font-weight: 800; color: white; line-height: 1; font-family: 'Inter', sans-serif;">{phi_matches}</div>
<div style="font-size: 11px; font-weight: 600; color: var(--text-sub); margin-top: 6px;">Asset Confirmed</div>
</div>
</div>
<div style="margin-top: auto; text-align: center;">
<div style="font-size: 13px; font-weight: 700; color: #00F0FF; letter-spacing: 0.5px;">LEAKAGE PROPORTION</div>
<div style="font-size: 11px; color: var(--text-muted); margin-top: 6px; max-width: 220px; line-height: 1.4;">Critical/High severity matched entities out of total traffic.</div>
</div>
</div>"""

    # 2. Severity Breakdown (Segmented Bars)
    crit_n = len(df_all[df_all["Severity"] == "CRITICAL"])
    med_n  = len(df_all[df_all["Severity"] == "MEDIUM"])
    low_n  = len(df_all[df_all["Severity"] == "LOW"])
    
    def get_bar(count, color):
        p = count / total if total > 0 else 0
        segs = 12
        active = int(p * segs)
        if count > 0 and active == 0: active = 1
        html = '<div style="display: flex; gap: 4px; flex: 1;">'
        for i in range(segs):
            c = color if i < active else "#1A2542"
            html += f'<div style="height: 10px; flex: 1; background: {c}; border-radius: 4px;"></div>'
        html += '</div>'
        return html
        
    card2 = f"""<div class="tm-card" style="height: 280px; display: flex; flex-direction: column; justify-content: center; padding: 24px 32px;">
<div style="font-size: 13px; font-weight: 700; color: #F59E0B; letter-spacing: 0.5px; margin-bottom: 6px;">SEVERITY BREAKDOWN</div>
<div style="font-size: 34px; font-weight: 800; color: white; line-height: 1; margin-bottom: 32px; font-family: 'Inter', sans-serif;">{total} <span style="font-size: 12px; font-weight: 600; color: var(--text-sub); vertical-align: middle;">Total Events</span></div>
<div style="margin-bottom: 20px;">
<div style="display: flex; justify-content: space-between; font-size: 11px; font-weight: 700; color: white; margin-bottom: 8px;">
<span style="color: var(--text-sub);">CRITICAL</span><span>{crit_n}</span>
</div>
{get_bar(crit_n, "#FF2D5B")}
</div>
<div style="margin-bottom: 20px;">
<div style="display: flex; justify-content: space-between; font-size: 11px; font-weight: 700; color: white; margin-bottom: 8px;">
<span style="color: var(--text-sub);">MEDIUM</span><span>{med_n}</span>
</div>
{get_bar(med_n, "#F59E0B")}
</div>
<div>
<div style="display: flex; justify-content: space-between; font-size: 11px; font-weight: 700; color: white; margin-bottom: 8px;">
<span style="color: var(--text-sub);">LOW</span><span>{low_n}</span>
</div>
{get_bar(low_n, "#10B981")}
</div>
</div>"""

    # 3. AI Platform Usage (Top Destination)
    top_dest = df_all["Destination"].mode()[0] if not df_all.empty else "None"
    dest_count = len(df_all[df_all["Destination"] == top_dest])
    pct3 = dest_count / total if total > 0 else 0
    active_seg3 = int(pct3 * segments)
    svg3 = ""
    for i in range(segments):
        angle = i * (360 / segments)
        color = "#B534FF" if i < active_seg3 else "#1A2542"
        svg3 += f'<line x1="100" y1="15" x2="100" y2="40" transform="rotate({angle} 100 100)" stroke="{color}" stroke-width="5" stroke-linecap="round"/>\\n'
        
    card3 = f"""<div class="tm-card" style="height: 280px; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 24px;">
<div style="position: relative; width: 200px; height: 180px;">
<svg width="200" height="180" viewBox="0 0 200 200">
{svg3}
</svg>
<div style="position: absolute; top: 0; left: 0; width: 200px; height: 180px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
<div style="font-size: 34px; font-weight: 800; color: white; line-height: 1; font-family: 'Inter', sans-serif;">{dest_count}</div>
<div style="font-size: 11px; font-weight: 600; color: var(--text-sub); margin-top: 6px;">Sessions</div>
</div>
</div>
<div style="margin-top: auto; text-align: center;">
<div style="font-size: 13px; font-weight: 700; color: #B534FF; letter-spacing: 0.5px;">TOP DESTINATION</div>
<div style="font-size: 11px; color: var(--text-muted); margin-top: 6px; max-width: 220px; line-height: 1.4;">{top_dest} is the most frequently accessed AI platform.</div>
</div>
</div>"""

    st.markdown(f'<div class="tm-middle-grid">{card1}{card2}{card3}</div>', unsafe_allow_html=True)

def render_premium_timeline_section(df_all):
    if df_all.empty:
        return
        
    c1, c2 = st.columns([3, 2], gap="large")
    
    with c1:
        st.markdown("""
        <div id="timeline-card"></div>
        <style>
        div[data-testid="column"]:has(#timeline-card) {
            background: var(--bg-panel);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 24px;
        }
        </style>
        <div class="tm-card-title" style="margin-bottom: 16px;">📈 Event Frequency Timeline</div>
        """, unsafe_allow_html=True)
        
        df_all["IsCritical"] = df_all["Severity"] == "CRITICAL"
        t_df = df_all.groupby(["Timestamp", "IsCritical"]).size().reset_index(name="Events")
        t_df["Type"] = t_df["IsCritical"].map({True: "Critical", False: "Other"})
        
        chart = alt.Chart(t_df).mark_area(
            interpolate='monotone', opacity=0.8
        ).encode(
            x=alt.X('Timestamp:O', axis=alt.Axis(labels=True, ticks=False, title=None, grid=True, gridColor="#1A2542")),
            y=alt.Y('Events:Q', axis=alt.Axis(labels=True, ticks=False, title=None, grid=True, gridColor="#1A2542")),
            color=alt.Color('Type:N', scale=alt.Scale(domain=['Critical', 'Other'], range=['#FF2D5B', '#B534FF']), legend=alt.Legend(title=None, orient='top', labelColor="#647E9C")),
            tooltip=['Timestamp', 'Type', 'Events']
        ).properties(height=230).configure_view(strokeWidth=0).configure(background='transparent')
        
        st.altair_chart(chart, use_container_width=True)
        
    with c2:
        top_dests = df_all["Destination"].value_counts().head(4)
        max_val = top_dests.max() if not top_dests.empty else 1
        colors = ["#FF2D5B", "#F59E0B", "#00F0FF", "#B534FF"]
        
        dests = list(top_dests.items())
        while len(dests) < 4:
            dests.append(("---", 0))
        
        def get_eq_row(name, count, color):
            pct = count / max_val if max_val > 0 else 0
            segs = 18
            active = int(pct * segs)
            if count > 0 and active == 0: active = 1
            html = '<div style="display: flex; gap: 4px; margin-bottom: 20px; align-items: center;">'
            html += '<div style="display: flex; gap: 3px; flex: 1;">'
            for i in range(segs):
                c = color if i < active else "#1A2542"
                html += f'<div style="height: 14px; flex: 1; background: {c}; border-radius: 2px;"></div>'
            html += '</div>'
            html += f'<div style="width: 70px; text-align: right; color: white; font-size: 10px; font-weight: 700; text-transform: uppercase;">{name[:10]}<br><span style="color: {color}; font-size: 12px;">{count}</span></div>'
            html += '</div>'
            return html
            
        eq_html = ""
        for i, (dest, count) in enumerate(dests):
            eq_html += get_eq_row(dest, count, colors[i])
            
        card_html = f"""<div class="tm-card" style="height: 335px; display: flex; flex-direction: row; align-items: center; padding: 24px;">
<div style="flex: 2; padding-right: 24px; border-right: 1px solid var(--border);">
    <div style="font-size: 13px; font-weight: 700; color: #00F0FF; letter-spacing: 0.5px; margin-bottom: 24px;">TOP AI PLATFORMS</div>
    {eq_html}
</div>
<div style="flex: 1; padding-left: 24px;">
    <div style="font-size: 16px; font-weight: 800; color: #00F0FF; margin-bottom: 12px; line-height: 1.2;">PLATFORM<br>ACTIVITY</div>
    <div style="font-size: 11px; color: var(--text-muted); line-height: 1.5; margin-bottom: 16px;">Visualizes the distribution of event traffic across the top 4 AI platforms.</div>
    <div style="font-size: 11px; color: var(--text-muted); line-height: 1.5;">Higher intensity indicates greater usage frequency.</div>
</div>
</div>"""
        st.markdown(card_html, unsafe_allow_html=True)


def nav_to_alert(event_id):
    st.session_state.inspect_button_clicked = True
    st.session_state.selected_alert_id = event_id
    st.session_state.nav_radio = "💬 Prompt Inspector"
    st.query_params["page"] = "Prompt Inspector"


def render_custom_table(df, rows_per_page=50):
    """
    Renders the sleek ThreatMon live interactive table using Streamlit columns
    with fully functional Monitor switches and Action inspect auto-navigation buttons.
    """
    if df.empty:
        st.markdown("<div class='info-box'>No data available for table.</div>", unsafe_allow_html=True)
        return

    st.markdown('<div class="sec-title" style="margin-top:16px;">🛡️ Live Digital Assets Attack Surface Table</div>', unsafe_allow_html=True)
    
    # Table Header
    cols = st.columns([1.5, 2.0, 1.8, 1.2, 1.2, 1.0, 1.0, 1.0, 1.2])
    headers = ["AI Platform", "Status / Match", "Category Tier", "Source IP", "Session Type", "WRSE Score", "Last Update", "Monitor", "Actions"]
    for c, h in zip(cols, headers):
        c.markdown(f"**{h}**")
    st.markdown("<hr style='border:none;height:1px;background:#1D3364;margin:8px 0;'>", unsafe_allow_html=True)

    import math
    total_rows = len(df)
    total_pages = max(1, math.ceil(total_rows / rows_per_page))

    if "table_page" not in st.session_state:
        st.session_state.table_page = 1
    
    if st.session_state.table_page > total_pages:
        st.session_state.table_page = total_pages

    start_idx = (st.session_state.table_page - 1) * rows_per_page
    end_idx = start_idx + rows_per_page
    df_page = df.iloc[start_idx:end_idx]

    for idx, row in df_page.iterrows():
        cols = st.columns([1.5, 2.0, 1.8, 1.2, 1.2, 1.0, 1.0, 1.0, 1.2])
        
        # AI Platform
        cols[0].markdown(f"`{row.get('Destination', 'Unknown')}`")
        
        # Status / Match
        sev = row.get("Severity", "LOW")
        phi_match_val = row.get("PHI Matched", "—")
        if phi_match_val != "—":
            tier_str = str(row.get("Data Tier", ""))
            icon = "🗂️" if ("+" in phi_match_val or "," in tier_str) else ("🖥️" if ("Infrastructure" in tier_str or "Tier 2" in tier_str) else ("💡" if ("IP" in tier_str or "Tier 3" in tier_str) else "⚕️"))
            pill = f'<span class="pill-custom">{icon} {phi_match_val}</span>'
        elif sev == "CRITICAL":
            pill = '<span class="pill-passive">Critical Risk</span>'
        elif sev == "MEDIUM":
            pill = '<span class="pill-custom">Medium Risk</span>'
        else:
            pill = '<span class="pill-active">Low Risk</span>'
        cols[1].markdown(pill, unsafe_allow_html=True)
        
        # Category Tier
        cols[2].markdown(f"<span style='font-size:12px;color:#E2EBF8;'>{row.get('Data Tier', 'Tier 1 - PHI')}</span>", unsafe_allow_html=True)
        
        # Source IP
        cols[3].markdown(f"`{row.get('Source IP', '192.168.89.134')}`")
        
        # Session Type
        cols[4].markdown(f"<span style='font-size:12px;color:#8C9BAE;'>{row.get('Identity', 'Human Session')}</span>", unsafe_allow_html=True)
        
        # WRSE Score
        cols[5].markdown(f"<span style='font-family:monospace;font-weight:700;color:#F59E0B;'>{row.get('WRSE Score', 0)}%</span>", unsafe_allow_html=True)
        
        # Last Update
        ts = row.get("Timestamp", "N/A")
        ts_short = ts.split(" ")[1] if " " in ts else ts
        cols[6].markdown(f"<span style='font-family:monospace;font-size:11px;color:#647E9C;'>{ts_short}</span>", unsafe_allow_html=True)
        
        # Monitor Status Selectbox  persisted in SQLite
        evt_id = row.get("Event ID", f"evt_{idx}")
        saved_status  = _get_monitor_status(evt_id)
        saved_index   = _MON_OPTIONS.index(saved_status) if saved_status in _MON_OPTIONS else 0

        def _on_monitor_change(eid=evt_id):
            _save_monitor_status(eid, st.session_state[f"mon_{eid}"])

        cols[7].selectbox(
            "Monitor",
            options=_MON_OPTIONS,
            index=saved_index,
            key=f"mon_{evt_id}",
            label_visibility="collapsed",
            on_change=_on_monitor_change,
        )
        
        # Actions Button (Auto Navigation to Alerts & Payloads!)
        cols[8].button("🔍 Inspect", key=f"act_{evt_id}", on_click=nav_to_alert, args=(evt_id,))
        
        st.markdown("<hr style='border:none;height:1px;background:#101D3A;margin:4px 0;'>", unsafe_allow_html=True)

    #  PAGINATION CONTROLS 
    if total_pages > 1:
        st.markdown("<br>", unsafe_allow_html=True)
        pc1, pc2, pc3 = st.columns([1, 2, 1])
        
        with pc1:
            if st.button("⬅️ Previous Page", disabled=(st.session_state.table_page <= 1), use_container_width=True, key="prev_pg"):
                st.session_state.table_page -= 1
                st.rerun()
                
        with pc2:
            st.markdown(f"<div style='text-align:center; padding-top:8px; font-weight:bold; color:#8C9BAE;'>Page <span style='color:#06B6D4;'>{st.session_state.table_page}</span> of {total_pages} &nbsp;&nbsp;|&nbsp;&nbsp; Total Records: {total_rows}</div>", unsafe_allow_html=True)
            
        with pc3:
            if st.button("Next Page ➡️", disabled=(st.session_state.table_page >= total_pages), use_container_width=True, key="next_pg"):
                st.session_state.table_page += 1
                st.rerun()
