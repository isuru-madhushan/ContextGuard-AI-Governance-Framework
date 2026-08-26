# 
#  THREATMON-STYLE ADVANCED CSS DESIGNS (FIXED COLLAPSE BUG & SIDEBAR MENU)
# 

THREATMON_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

:root {
    /* Exact ThreatMon screenshot palette */
    --bg-base:      #050B1A; 
    --bg-panel:     #0A142B;
    --bg-card:      #111E3E;
    --bg-card-hover:#16274E;
    --border:       #1D3364;
    --border-glow:  rgba(24, 119, 242, 0.3);
    
    /* ThreatMon Icon Palette */
    --tm-blue:      #1877F2;
    --tm-orange:    #FF8A00;
    --tm-purple:    #8B5CF6;
    --tm-red:       #FF2D5B;
    --tm-cyan:      #06B6D4;
    --tm-green:     #10B981;
    --tm-navy:      #1E3E62;
    
    --text-main:    #E2EBF8;
    --text-muted:   #647E9C;
    --text-sub:     #8C9BAE;
    
    --grad-main:    linear-gradient(135deg, #1877F2, #00D4AA);
}

/* ── BASE RESET & ANIMATIONS ── */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes pulseGlow {
    0% { box-shadow: 0 0 0 0 rgba(255, 45, 91, 0.4); }
    70% { box-shadow: 0 0 0 8px rgba(255, 45, 91, 0); }
    100% { box-shadow: 0 0 0 0 rgba(255, 45, 91, 0); }
}
@keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}

/* ── PREMIUM SCROLLBAR ── */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: var(--bg-base); 
}
::-webkit-scrollbar-thumb {
    background: var(--border); 
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: var(--tm-cyan); 
}

html, body, .stApp { 
    background: var(--bg-base) !important; 
    color: var(--text-main) !important; 
    font-family: 'Inter', sans-serif !important; 
}
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
    max-width: 98% !important;
}
#MainMenu, footer, .stDeployButton { visibility: hidden; display: none; }

/* ── FIXED STREAMLIT SIDEBAR COLLAPSE / REOPEN BUG ── */
header { 
    background: transparent !important; 
    box-shadow: none !important;
}
[data-testid="collapsedControl"] {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    color: #1877F2 !important; 
    background: #0A142B !important; 
    border: 1px solid #1D3364 !important; 
    border-radius: 8px !important; 
    padding: 6px 10px !important; 
    margin-top: 12px !important;
    margin-left: 12px !important;
    z-index: 999999 !important; 
    box-shadow: 0 4px 14px rgba(0,0,0,0.4) !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
}
[data-testid="collapsedControl"]:hover {
    background: #111E3E !important;
    border-color: #1877F2 !important;
    box-shadow: 0 4px 16px rgba(24,119,242,0.4) !important;
}

/* ── THREATMON EXACT SIDEBAR MENU ── */
[data-testid="stSidebar"] {
    background: #040916 !important;
    border-right: 1px solid var(--border) !important;
}
.sb-brand-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px 20px 18px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 16px;
}
.sb-logo-icon {
    font-size: 28px;
    color: var(--tm-cyan);
    filter: drop-shadow(0 0 12px rgba(6, 182, 212, 0.8));
    animation: pulseGlow 3s infinite alternate;
}
.sb-brand-text {
    font-size: 20px;
    font-weight: 800;
    letter-spacing: 0.5px;
    color: #FFFFFF;
}
.sb-menu-title {
    font-size: 11px;
    font-family: 'Inter', sans-serif;
    font-weight: 700;
    text-transform: uppercase;
    color: var(--text-muted);
    letter-spacing: 1px;
    padding: 4px 14px;
    margin-top: 12px;
    margin-bottom: 8px;
}

/* ── CONTEXTGUARD SIDEBAR MENU STYLING (FLAWLESS NO-CIRCLE PREMIUM LOOK) ── */
section[data-testid="stSidebar"] div[role="radiogroup"] {
    display: flex !important;
    flex-direction: column !important;
    gap: 6px !important;
    padding: 0 12px !important;
    background: transparent !important;
    border: none !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] > label {
    width: 100% !important;
    padding: 10px 14px !important;
    margin: 0 !important;
    border-radius: 8px !important;
    background: transparent !important;
    border: none !important;
    color: #8C9BAE !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    font-family: 'Inter', sans-serif !important;
    text-align: left !important;
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    transition: all 0.2s ease-in-out !important;
    cursor: pointer !important;
    box-shadow: none !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
    color: #FFFFFF !important;
    background: rgba(6, 182, 212, 0.15) !important;
    border: none !important;
    box-shadow: none !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] > label[aria-checked="true"],
section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
    background: linear-gradient(90deg, #06B6D4 0%, #0284C7 100%) !important;
    color: #FFFFFF !important;
    box-shadow: 0 4px 15px rgba(6, 182, 212, 0.35) !important;
    font-weight: 700 !important;
    border: none !important;
}
/* HIDE STREAMLIT RADIO CIRCLES ENTIRELY & ASSURE FLAWLESS LEFT ALIGNMENT IN SIDEBAR */
section[data-testid="stSidebar"] div[role="radiogroup"] input[type="radio"],
section[data-testid="stSidebar"] div[role="radiogroup"] label div[data-testid="stRadioButton"] > div:first-child,
section[data-testid="stSidebar"] div[role="radiogroup"] label span[data-baseweb="radio"] > div:first-child {
    display: none !important;
    opacity: 0 !important;
    width: 0 !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label div:not(:has(p)):not(:has(input)) {
    display: none !important;
    width: 0 !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label div:has(p) {
    margin: 0 !important;
    padding: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    width: 100% !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label p {
    font-size: 14px !important;
    font-weight: 600 !important;
    color: #8C9BAE !important;
    margin: 0 !important;
    padding: 0 !important;
    background: transparent !important;
    border: none !important;
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    width: 100% !important;
    text-align: left !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] > label[aria-checked="true"] p,
section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) p {
    color: #FFFFFF !important;
    font-weight: 700 !important;
    background: transparent !important;
    border: none !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label div[data-testid="stRadioButton"],
section[data-testid="stSidebar"] div[role="radiogroup"] label span[data-baseweb="radio"] {
    width: 100% !important;
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    gap: 0px !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin: 0 !important;
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] > label[data-testid="stWidgetLabel"] {
    display: none !important;
}

/* ── MAIN PAGE HORIZONTAL RADIO BUTTONS (ULTRA-PREMIUM GLASSMORPHISM SEGMENTED CONTROL) ── */
section[data-testid="stMain"] div[role="radiogroup"] {
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    gap: 10px !important;
    background: linear-gradient(135deg, rgba(16, 29, 66, 0.85) 0%, rgba(11, 21, 48, 0.95) 100%) !important;
    backdrop-filter: blur(12px) !important;
    padding: 8px 10px !important;
    border-radius: 12px !important;
    border: 1px solid rgba(6, 182, 212, 0.3) !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35), 0 0 15px rgba(6, 182, 212, 0.1) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    height: 58px !important;
    min-height: 58px !important;
    max-height: 58px !important;
    box-sizing: border-box !important;
}
section[data-testid="stMain"] div[role="radiogroup"]:hover {
    border: 1px solid rgba(6, 182, 212, 0.8) !important;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.45), 0 0 25px rgba(6, 182, 212, 0.35) !important;
    transform: translateY(-2px) !important;
}
section[data-testid="stMain"] div[role="radiogroup"] > label {
    padding: 0 20px !important;
    margin: 0 !important;
    border-radius: 8px !important;
    background: transparent !important;
    border: none !important;
    color: #94A3B8 !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    font-family: 'Inter', sans-serif !important;
    letter-spacing: 0.3px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    cursor: pointer !important;
    height: 42px !important;
    min-height: 42px !important;
    max-height: 42px !important;
    line-height: 1 !important;
    box-sizing: border-box !important;
}
section[data-testid="stMain"] div[role="radiogroup"] > label:hover {
    color: #FFFFFF !important;
    background: rgba(6, 182, 212, 0.2) !important;
    box-shadow: 0 0 12px rgba(6, 182, 212, 0.2) !important;
}
section[data-testid="stMain"] div[role="radiogroup"] > label[aria-checked="true"],
section[data-testid="stMain"] div[role="radiogroup"] > label:has(input:checked) {
    background: linear-gradient(90deg, #0EA5E9 0%, #06B6D4 100%) !important;
    color: #FFFFFF !important;
    box-shadow: 0 4px 15px rgba(14, 165, 233, 0.4), inset 0 1px 1px rgba(255, 255, 255, 0.3) !important;
    font-weight: 700 !important;
}
/* HIDE STREAMLIT RADIO CIRCLES IN MAIN PAGE */
section[data-testid="stMain"] div[role="radiogroup"] input[type="radio"],
section[data-testid="stMain"] div[role="radiogroup"] label div[data-testid="stRadioButton"] > div:first-child,
section[data-testid="stMain"] div[role="radiogroup"] label span[data-baseweb="radio"] > div:first-child {
    display: none !important;
    opacity: 0 !important;
    width: 0 !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}
section[data-testid="stMain"] div[role="radiogroup"] label div:not(:has(p)):not(:has(input)) {
    display: none !important;
    width: 0 !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}
section[data-testid="stMain"] div[role="radiogroup"] label p {
    font-size: 13px !important;
    font-weight: inherit !important;
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1 !important;
}
section[data-testid="stMain"] div[role="radiogroup"] > label[aria-checked="true"] p,
section[data-testid="stMain"] div[role="radiogroup"] > label:has(input:checked) p {
    color: #FFFFFF !important;
    font-weight: 700 !important;
}

/* ── MAIN PAGE CHECKBOX (ULTRA-PREMIUM SYMMETRICAL TOGGLE BUTTON STYLING WITH CUSTOM TICK & GAP) ── */
section[data-testid="stMain"] div[data-testid="stCheckbox"] {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    background: linear-gradient(135deg, rgba(16, 29, 66, 0.85) 0%, rgba(11, 21, 48, 0.95) 100%) !important;
    backdrop-filter: blur(12px) !important;
    padding: 8px 12px !important;
    margin: 0 !important;
    border-radius: 12px !important;
    border: 1px solid rgba(6, 182, 212, 0.3) !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35), 0 0 15px rgba(6, 182, 212, 0.1) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-sizing: border-box !important;
    width: max-content !important;
    min-width: max-content !important;
    white-space: nowrap !important;
    height: 58px !important;
    min-height: 58px !important;
    max-height: 58px !important;
}
section[data-testid="stMain"] div[data-testid="stCheckbox"]:hover {
    border: 1px solid rgba(6, 182, 212, 0.8) !important;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.45), 0 0 25px rgba(6, 182, 212, 0.35) !important;
    transform: translateY(-2px) !important;
}
section[data-testid="stMain"] div[data-testid="stCheckbox"] label {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 12px !important;
    margin: 0 auto !important;
    padding: 0 !important;
    width: max-content !important;
    min-width: max-content !important;
    white-space: nowrap !important;
    cursor: pointer !important;
    box-sizing: border-box !important;
    height: 100% !important;
}
/* CUSTOM CYAN TICK BOX STYLING (PERFECT VERTICAL & HORIZONTAL ALIGNMENT) */
section[data-testid="stMain"] div[data-testid="stCheckbox"] input[type="checkbox"] + span,
section[data-testid="stMain"] div[data-testid="stCheckbox"] input[type="checkbox"] + div,
section[data-testid="stMain"] div[data-testid="stCheckbox"] label > span:first-of-type:not(:has(p)),
section[data-testid="stMain"] div[data-testid="stCheckbox"] label > div:first-of-type:not(:has(p)) {
    background-color: #0A1329 !important;
    border: 2px solid #1D3364 !important;
    border-radius: 6px !important;
    margin: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 22px !important;
    height: 22px !important;
    flex: 0 0 22px !important;
    transition: all 0.2s ease-in-out !important;
}
section[data-testid="stMain"] div[data-testid="stCheckbox"]:hover input[type="checkbox"] + span,
section[data-testid="stMain"] div[data-testid="stCheckbox"]:hover input[type="checkbox"] + div,
section[data-testid="stMain"] div[data-testid="stCheckbox"]:hover label > span:first-of-type:not(:has(p)),
section[data-testid="stMain"] div[data-testid="stCheckbox"]:hover label > div:first-of-type:not(:has(p)) {
    border-color: #06B6D4 !important;
    box-shadow: 0 0 10px rgba(6, 182, 212, 0.3) !important;
}
section[data-testid="stMain"] div[data-testid="stCheckbox"] input[type="checkbox"]:checked + span,
section[data-testid="stMain"] div[data-testid="stCheckbox"] input[type="checkbox"]:checked + div,
section[data-testid="stMain"] div[data-testid="stCheckbox"]:has(input[type="checkbox"]:checked) label > span:first-of-type:not(:has(p)),
section[data-testid="stMain"] div[data-testid="stCheckbox"]:has(input[type="checkbox"]:checked) label > div:first-of-type:not(:has(p)) {
    background: linear-gradient(90deg, #06B6D4 0%, #0284C7 100%) !important;
    background-color: #06B6D4 !important;
    border: none !important;
    box-shadow: 0 0 12px rgba(6, 182, 212, 0.4) !important;
}
section[data-testid="stMain"] div[data-testid="stCheckbox"] input[type="checkbox"] + span svg,
section[data-testid="stMain"] div[data-testid="stCheckbox"] input[type="checkbox"] + div svg,
section[data-testid="stMain"] div[data-testid="stCheckbox"] label > span:first-of-type:not(:has(p)) svg,
section[data-testid="stMain"] div[data-testid="stCheckbox"] label > div:first-of-type:not(:has(p)) svg {
    fill: #FFFFFF !important;
    color: #FFFFFF !important;
    stroke: #FFFFFF !important;
    width: 14px !important;
    height: 14px !important;
    margin: 0 !important;
    padding: 0 !important;
}
/* TURN THE TEXT CONTAINER INTO A GORGEOUS TAB BUTTON WITH PERFECT CENTERING */
section[data-testid="stMain"] div[data-testid="stCheckbox"] label > div {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 0 20px !important;
    margin: 0 !important;
    border-radius: 8px !important;
    background: transparent !important;
    color: #94A3B8 !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    font-family: 'Inter', sans-serif !important;
    letter-spacing: 0.3px !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    width: max-content !important;
    min-width: max-content !important;
    white-space: nowrap !important;
    flex: 0 0 max-content !important;
    text-align: center !important;
    box-sizing: border-box !important;
    height: 42px !important;
    min-height: 42px !important;
    max-height: 42px !important;
    line-height: 1 !important;
}
section[data-testid="stMain"] div[data-testid="stCheckbox"] label:hover > div {
    color: #FFFFFF !important;
    background: rgba(6, 182, 212, 0.2) !important;
    box-shadow: 0 0 12px rgba(6, 182, 212, 0.2) !important;
}
section[data-testid="stMain"] div[data-testid="stCheckbox"]:has(input[type="checkbox"]:checked) label > div,
section[data-testid="stMain"] div[data-testid="stCheckbox"] label:has(input[type="checkbox"]:checked) > div,
section[data-testid="stMain"] div[data-testid="stCheckbox"] label[aria-checked="true"] > div {
    background: linear-gradient(90deg, #0EA5E9 0%, #06B6D4 100%) !important;
    color: #FFFFFF !important;
    box-shadow: 0 4px 15px rgba(14, 165, 233, 0.4), inset 0 1px 1px rgba(255, 255, 255, 0.3) !important;
    font-weight: 700 !important;
}

/* ── ELITE CONTROL DECK COLUMNS (PERFECTLY TIGHT GAP & 100% HORIZONTAL ALIGNMENT) ── */
section[data-testid="stMain"] div[data-testid="stColumns"]:has(div[data-testid="stRadio"]),
section[data-testid="stMain"] div[data-testid="stHorizontalBlock"]:has(div[data-testid="stRadio"]),
section[data-testid="stMain"] div[data-testid="columns"]:has(div[data-testid="stRadio"]) {
    display: flex !important;
    gap: 15px !important;
    justify-content: flex-start !important;
    align-items: flex-start !important;
    margin: 0 !important;
    padding: 0 !important;
}
section[data-testid="stMain"] div[data-testid="stColumns"]:has(div[data-testid="stRadio"]) > div[data-testid="stColumn"],
section[data-testid="stMain"] div[data-testid="stHorizontalBlock"]:has(div[data-testid="stRadio"]) > div[data-testid="stColumn"],
section[data-testid="stMain"] div[data-testid="columns"]:has(div[data-testid="stRadio"]) > div[data-testid="column"] {
    flex: 0 0 auto !important;
    width: auto !important;
    min-width: fit-content !important;
    display: flex !important;
    align-items: flex-start !important;
    margin: 0 !important;
    padding: 0 !important;
}
section[data-testid="stMain"] div[data-testid="stColumns"]:has(div[data-testid="stRadio"]) div[data-testid="stVerticalBlock"],
section[data-testid="stMain"] div[data-testid="stColumns"]:has(div[data-testid="stRadio"]) div[data-testid="stVerticalBlockBorderWrapper"],
section[data-testid="stMain"] div[data-testid="stColumns"]:has(div[data-testid="stRadio"]) div[data-testid="stRadio"] {
    margin: 0 !important;
    padding: 0 !important;
    display: flex !important;
    align-items: flex-start !important;
    gap: 0 !important;
}

.live-badge { 
    display: flex; 
    align-items: center; 
    gap: 8px; 
    background: rgba(16,185,129,.08); 
    border: 1px solid rgba(16,185,129,.25); 
    border-radius: 6px; 
    padding: 8px 14px; 
    margin: 0 20px 16px; 
}
.live-dot { 
    width: 8px; 
    height: 8px; 
    border-radius: 50%; 
    background: var(--tm-green); 
    box-shadow: 0 0 10px var(--tm-green); 
    animation: blink 1.5s ease-in-out infinite; 
}
.live-txt { 
    font-size: 11px; 
    font-family: 'JetBrains Mono', monospace; 
    color: var(--tm-green); 
    font-weight: 700; 
    letter-spacing: 1px; 
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.25} }

/* ── SCREENSHOT TOP TITLE ── */
.tm-main-title {
    font-size: 18px;
    font-weight: 700;
    color: #FFFFFF;
    margin-bottom: 20px;
    padding-left: 4px;
    letter-spacing: 0.5px;
}

/* ── THREATMON TOP ASSETS STRIP ── */
/* ── CY-FOCUS STYLE TOP STRIP ── */
.tm-asset-strip {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;
    margin-bottom: 24px;
}
.tm-card {
    background: rgba(10, 20, 43, 0.6);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(29, 51, 100, 0.8);
    border-radius: 12px;
    padding: 16px 20px;
    position: relative;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    min-height: 110px;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    animation: fadeUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
.tm-card:hover {
    border-color: rgba(6,182,212,0.5);
    box-shadow: 0 8px 30px rgba(6,182,212,0.15);
    transform: translateY(-4px) scale(1.01);
}
.tm-asset-item {
    background: var(--bg-panel);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px 24px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    display: flex;
    flex-direction: column;
    gap: 16px;
    cursor: pointer;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.tm-asset-item:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.4);
}
.tm-cy-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 13px;
    font-weight: 600;
    color: var(--text-sub);
}
.tm-cy-trend {
    font-size: 11px;
    font-weight: 700;
    background: rgba(255,255,255,0.04);
    padding: 4px 8px;
    border-radius: 8px;
}
.tm-cy-trend.up { color: #10B981; }
.tm-cy-trend.warn { color: #F59E0B; }
.tm-cy-trend.down { color: #FF2D5B; }
.tm-cy-bottom {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
}
.tm-cy-num {
    font-size: 32px;
    font-weight: 800;
    color: white;
    font-family: 'Inter', sans-serif;
    line-height: 1;
}
.tm-cy-chart {
    height: 36px;
    width: 60px;
    display: flex;
    align-items: flex-end;
    justify-content: flex-end;
    gap: 4px;
}
.cy-bar { width: 6px; border-radius: 2px; }
.cy-donut {
    width: 36px;
    height: 18px;
    border-radius: 36px 36px 0 0;
    border: 4px solid;
    border-bottom: 0;
    box-sizing: border-box;
}

/* ── MIDDLE CHARTS CARDS ── */
.tm-middle-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
    margin-bottom: 24px;
}
.tm-bottom-grid {
    display: grid;
    grid-template-columns: 3fr 2fr;
    gap: 24px;
    margin-bottom: 24px;
}
.host-card {
    background: #0B1327;
    border: 1px solid #1D3364;
    border-radius: 8px;
    padding: 12px 16px;
    margin-top: 8px;
    margin-bottom: 12px;
    display: grid;
    grid-template-columns: 140px 1fr;
    row-gap: 8px;
    align-items: center;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    animation: fadeUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
.host-card:hover {
    border-color: #38BDF8;
    box-shadow: 0 8px 24px rgba(56, 189, 248, 0.15);
    transform: translateY(-2px);
}
.tm-card {
    background: var(--bg-panel);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 24px;
    height: 100%;
    display: flex;
    flex-direction: column;
    box-shadow: 0 8px 24px rgba(0,0,0,0.25);
}
.tm-card-title {
    font-size: 14px;
    font-weight: 700;
    color: var(--text-main);
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* ── CUSTOM HORIZONTAL STACKED BAR (Main Domains Type) ── */
.stacked-bar-legend {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 16px;
    margin-bottom: 20px;
}
.legend-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 11px;
    color: var(--text-sub);
}
.legend-box { width: 12px; height: 8px; border-radius: 2px; }

.stacked-bar-container {
    display: flex;
    height: 48px;
    width: 100%;
    border-radius: 8px;
    overflow: hidden;
    background: rgba(255, 255, 255, 0.03);
    box-shadow: inset 0 2px 6px rgba(0,0,0,0.4);
}
.stacked-segment {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: white;
    font-weight: 700;
    font-family: 'Inter', sans-serif;
    font-size: 15px;
    transition: all 0.3s ease;
    box-shadow: inset 0 0 10px rgba(0,0,0,0.1);
}
.stacked-segment:hover { opacity: 0.9; }

/* ── CUSTOM DONUT CHART (Active/Passive DNS) ── */
.donut-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin-top: 10px;
}
.donut-ring {
    position: relative;
    width: 125px;
    height: 125px;
    border-radius: 50%;
    background: conic-gradient(#3B82F6 0% 75%, #10B981 75% 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 16px rgba(0,0,0,0.3);
}
.donut-hole {
    width: 90px;
    height: 90px;
    border-radius: 50%;
    background: var(--bg-panel);
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 28px;
    font-weight: 800;
    color: white;
}
.donut-legend {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-top: 10px;
}

/* ── FILTER CONTAINER ── */
.tm-filter-container {
    background: var(--bg-panel);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 24px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.25);
}
.tm-filter-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 13px;
    font-weight: 700;
    color: var(--text-main);
    margin-bottom: 16px;
}
.tm-actions-link {
    color: var(--text-sub);
    font-size: 12px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 4px;
}

/* ── THREATMON DATA TABLE ── */
.tm-table-container {
    background: var(--bg-panel);
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 24px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.25);
}
.tm-table {
    width: 100%;
    border-collapse: collapse;
    text-align: left;
    font-size: 12px;
}
.tm-table th {
    background: #0A142B;
    color: var(--text-muted);
    font-weight: 600;
    padding: 14px 18px;
    border-bottom: 1px solid var(--border);
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.tm-table td {
    padding: 16px 18px;
    border-bottom: 1px solid var(--border);
    color: var(--text-main);
}
.tm-table tr:hover td {
    background: var(--bg-card-hover);
}
.tm-table td.kw-col {
    color: #38BDF8;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
}
.tm-table td.ip-col {
    font-family: 'JetBrains Mono', monospace;
    color: #E2EBF8;
}

/* ── STATUS PILLS & TOGGLES ── */
.pill-passive {
    background: rgba(244, 63, 94, 0.15);
    border: 1px solid rgba(244, 63, 94, 0.4);
    color: #FB7185;
    padding: 4px 12px;
    border-radius: 14px;
    font-size: 11px;
    font-weight: 600;
    display: inline-block;
}
.pill-active {
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid rgba(16, 185, 129, 0.4);
    color: #34D399;
    padding: 4px 12px;
    border-radius: 14px;
    font-size: 11px;
    font-weight: 600;
    display: inline-block;
}
.pill-custom {
    background: rgba(139, 92, 246, 0.15);
    border: 1px solid rgba(139, 92, 246, 0.4);
    color: #C4B5FD;
    padding: 4px 12px;
    border-radius: 14px;
    font-size: 11px;
    font-weight: 600;
    display: inline-block;
}
.tm-switch {
    width: 34px;
    height: 18px;
    background: #1877F2;
    border-radius: 10px;
    position: relative;
    display: inline-block;
    cursor: pointer;
}
.tm-switch::after {
    content: '';
    position: absolute;
    right: 2px;
    top: 2px;
    width: 14px;
    height: 14px;
    background: white;
    border-radius: 50%;
}
.tm-action-dots {
    color: var(--text-muted);
    font-size: 16px;
    cursor: pointer;
    padding: 4px;
}
.tm-action-dots:hover { color: white; }

/* ── PAGE HEADERS & METRICS ── */
.pg-header { 
    background: linear-gradient(135deg, #111E3E, #0A142B); 
    border: 1px solid var(--border); 
    border-radius: 12px; 
    padding: 24px 28px; 
    margin-bottom: 24px; 
    position: relative; 
    overflow: hidden; 
    box-shadow: 0 8px 24px rgba(0,0,0,0.25);
}
.pg-header::before { 
    content: ''; 
    position: absolute; 
    top: 0; left: 0; right: 0; 
    height: 3px; 
    background: var(--grad-main); 
}
.pg-title { 
    font-size: 22px; 
    font-weight: 900; 
    letter-spacing: -0.5px; 
    color: #FFFFFF; 
}
.pg-sub { 
    font-size: 11px; 
    font-family: 'JetBrains Mono', monospace; 
    color: var(--tm-cyan); 
    letter-spacing: 1.5px; 
    text-transform: uppercase; 
    margin-top: 4px; 
}

/* ── ALERT CARDS & PHI INLINES ── */
.alert-card { 
    background: rgba(10, 20, 43, 0.7);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border: 1px solid var(--border); 
    border-radius: 10px; 
    padding: 16px 20px; 
    margin-bottom: 12px; 
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1); 
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    animation: fadeUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
.alert-card:hover { 
    border-color: var(--tm-blue); 
    box-shadow: 0 8px 24px rgba(24,119,242,0.25); 
    transform: translateY(-2px);
}
.alert-card.c-CRITICAL { border-left: 4px solid var(--tm-red); background: rgba(255,45,91,.04); }
.alert-card.c-MEDIUM   { border-left: 4px solid var(--tm-orange); background: rgba(255,138,0,.03); }
.alert-card.c-LOW      { border-left: 4px solid var(--tm-green); background: rgba(16,185,129,.03); }
.alert-card.c-PHI      { border-left: 4px solid var(--tm-purple); background: rgba(139,92,246,.06); }

.alert-header { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; flex-wrap: wrap; }
.alert-ts { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--text-muted); }
.alert-score { font-family: 'JetBrains Mono', monospace; font-size: 14px; font-weight: 800; margin-left: auto; }
.alert-flow { font-size: 14px; font-weight: 600; color: var(--text-main); margin-bottom: 6px; display: flex; align-items: center; gap: 8px; }
.alert-body { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #8C9BAE; line-height: 1.6; }

.sev-CRITICAL { background: rgba(255,45,91,.15); border: 1px solid rgba(255,45,91,.4); color: #FF8099; font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 700; padding: 2px 10px; border-radius: 14px; letter-spacing: 0.8px; animation: pulseGlow 2s infinite; }
.sev-MEDIUM   { background: rgba(255,138,0,.15); border: 1px solid rgba(255,138,0,.4); color: #FCD34D; font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 700; padding: 2px 10px; border-radius: 14px; letter-spacing: 0.8px; }
.sev-LOW      { background: rgba(16,185,129,.15); border: 1px solid rgba(16,185,129,.4); color: #6EE7B7; font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 700; padding: 2px 10px; border-radius: 14px; letter-spacing: 0.8px; }
.phi-tag      { background: rgba(139,92,246,.15); border: 1px solid rgba(139,92,246,.4); color: #C4B5FD; font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 700; padding: 2px 10px; border-radius: 14px; letter-spacing: 0.8px; animation: pulseGlow 3s infinite; }

.score-bar-wrap { background: rgba(255,255,255,.05); border-radius: 3px; height: 4px; margin-top: 12px; overflow: hidden; }
.score-bar { height: 100%; border-radius: 3px; }

.phi-record-inline { 
    margin-top: 12px; 
    padding: 12px 16px; 
    background: rgba(139,92,246,.08); 
    border: 1px solid rgba(139,92,246,.25); 
    border-radius: 8px; 
    font-family: 'JetBrains Mono', monospace; 
    font-size: 11px; 
    color: #C4B5FD; 
    line-height: 1.8; 
}

/* ── STREAMLIT WIDGET ASSIMILATION (PERFECT UNIFIED BASEWEB STYLING) ── */
div[data-baseweb="select"] > div, 
div[data-baseweb="input"], 
div[data-baseweb="base-input"] {
    background-color: #111E3E !important; 
    border: 1px solid var(--border) !important;
    border-radius: 8px !important; 
    color: var(--text-main) !important;
    font-family: 'JetBrains Mono', monospace !important; 
    font-size: 13px !important;
    min-height: 38px !important;
    display: flex !important;
    align-items: center !important;
    padding: 0 12px !important;
    transition: all 0.2s ease !important;
    box-shadow: none !important;
    margin: 0 !important;
    overflow: hidden !important;
}

div[data-baseweb="select"] > div:hover, 
div[data-baseweb="input"]:hover,
div[data-baseweb="base-input"]:hover {
    border-color: var(--tm-blue) !important;
    background-color: #16274E !important;
}

div[data-baseweb="select"] > div:focus-within, 
div[data-baseweb="input"]:focus-within,
div[data-baseweb="base-input"]:focus-within {
    border-color: var(--tm-blue) !important;
    box-shadow: 0 0 10px rgba(24,119,242,0.3) !important;
}

/* MASTER FIX: Prevent ALL inner elements/wrappers from creating double borders/boxes while keeping perfect vertical text alignment */
div[data-baseweb="select"] > div div, 
div[data-baseweb="input"] div,
div[data-baseweb="base-input"] div,
div[data-baseweb="select"] > div input, 
div[data-baseweb="input"] input,
div[data-baseweb="base-input"] input {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: var(--text-main) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
    line-height: normal !important;
    overflow: visible !important;
}

/* Ensure inputs sit perfectly centered vertically */
div[data-baseweb="select"] > div input, 
div[data-baseweb="input"] input,
div[data-baseweb="base-input"] input {
    padding: 0 !important;
    margin: 0 !important;
    height: 100% !important;
}


/* Fix dropdown arrow container styling */
div[data-baseweb="select"] > div > div:last-child {
    background: transparent !important;
    border: none !important;
    padding: 0 4px !important;
}

/* Dropdown menu item styling */
ul[role="listbox"] {
    background-color: #0A142B !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    box-shadow: 0 8px 24px rgba(0,0,0,0.4) !important;
}
ul[role="listbox"] li {
    color: var(--text-main) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
    transition: background 0.2s !important;
}
ul[role="listbox"] li:hover, ul[role="listbox"] li[aria-selected="true"] {
    background-color: #1877F2 !important;
    color: #FFFFFF !important;
}

button[kind="primary"], .stDownloadButton>button {
    background: var(--grad-main) !important; 
    border: none !important; 
    border-radius: 8px !important;
    color: white !important; 
    font-weight: 700 !important; 
    padding: 12px 20px !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 14px rgba(24,119,242,0.3) !important;
}
button[kind="primary"]:hover, .stDownloadButton>button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(24,119,242,0.5) !important;
}
[data-testid="stExpander"] { 
    background: var(--bg-panel) !important; 
    border: 1px solid var(--border) !important; 
    border-radius: 12px !important; 
    box-shadow: 0 4px 16px rgba(0,0,0,0.3) !important;
    overflow: hidden !important;
}
[data-testid="stExpander"] summary {
    background: var(--bg-card) !important;
    color: var(--text-main) !important;
    font-weight: 700 !important;
    border-bottom: 1px solid var(--border) !important;
    padding: 16px 20px !important;
}
[data-testid="stExpander"] summary p {
    color: var(--text-main) !important;
    font-weight: 700 !important;
    font-size: 15px !important;
}
[data-testid="stForm"] { 
    background: #0A142B !important; 
    border: 1px solid var(--border) !important; 
    border-radius: 12px !important; 
    padding: 24px !important; 
}
.sec-title { 
    font-size: 14px; 
    font-weight: 700; 
    color: var(--text-main); 
    display: flex; 
    align-items: center; 
    gap: 8px; 
    margin-bottom: 16px; 
    padding-bottom: 8px; 
    border-bottom: 1px solid var(--border); 
}
.payload-box { 
    background: #050B1A; 
    border: 1px solid rgba(24,119,242,0.2); 
    border-radius: 8px; 
    padding: 16px; 
    font-family: 'JetBrains Mono', monospace; 
    font-size: 11px; 
    color: #38BDF8; 
    line-height: 1.7; 
    max-height: 320px; 
    overflow-y: auto; 
    white-space: pre-wrap; 
    word-break: break-all; 
}
.host-card { 
    background: #111E3E; 
    border: 1px solid var(--border); 
    border-radius: 8px; 
    padding: 16px; 
}
.host-label { 
    font-size: 10px; 
    font-family: 'JetBrains Mono', monospace; 
    color: var(--text-muted); 
    text-transform: uppercase; 
    letter-spacing: 1.5px; 
    margin-bottom: 4px; 
}
.host-val { 
    font-size: 14px; 
    font-family: 'JetBrains Mono', monospace; 
    color: #93C5FD; 
    font-weight: 700; 
    margin-bottom: 12px; 
    word-break: break-all; 
}
.host-val.danger { color: #FF8099; }
.host-val.ok { color: #34D399; }

/* ── STREAMLIT BUTTON STYLING (SLEEK FUTURISTIC ENTERPRISE GLOW) ── */
div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #16274E 0%, #0D1938 100%) !important;
    border: 1px solid #1D3364 !important;
    border-radius: 8px !important;
    color: #06B6D4 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    padding: 6px 16px !important;
    min-height: 38px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2) !important;
    width: 100% !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

div[data-testid="stButton"] > button:hover {
    background: linear-gradient(135deg, #1D3364 0%, #16274E 100%) !important;
    border-color: #06B6D4 !important;
    color: #FFFFFF !important;
    box-shadow: 0 4px 16px rgba(6, 182, 212, 0.3) !important;
    transform: translateY(-1px) !important;
}

div[data-testid="stButton"] > button:active {
    transform: translateY(1px) !important;
}

/* ── HIDE STREAMLIT RUNNING SPINNER & TOP RIGHT STATUS WIDGET ── */
div[data-testid="stStatusWidget"],
div[data-testid="stTopRightStatus"],
.stApp [data-testid="stTopRightStatus"],
.stApp [data-testid="stStatusWidget"] {
    display: none !important;
    opacity: 0 !important;
    visibility: hidden !important;
    pointer-events: none !important;
}
/* ── MONITOR STATUS SELECTBOX — compact table cell style ── */
div[data-testid="stSelectbox"][aria-label="Monitor"] > div,
div[class*="stSelectbox"] > div[data-baseweb="select"] {
    min-height: 0 !important;
}
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background: rgba(6, 182, 212, 0.08) !important;
    border: 1px solid rgba(6, 182, 212, 0.25) !important;
    border-radius: 8px !important;
    padding: 2px 6px !important;
    min-height: 28px !important;
    font-size: 11.5px !important;
    font-family: monospace !important;
    font-weight: 600 !important;
    color: #94A3B8 !important;
    cursor: pointer !important;
    transition: border-color 0.2s ease !important;
}
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:hover {
    border-color: rgba(6, 182, 212, 0.6) !important;
}

/* --- USER MANAGEMENT CUSTOM UI --- */

/* KPI Cards */
.um-kpi-card {
    background: linear-gradient(145deg, rgba(14, 25, 52, 0.7) 0%, rgba(10, 18, 42, 0.9) 100%);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-top: 1px solid rgba(6, 182, 212, 0.3);
    border-radius: 16px;
    padding: 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);
    margin-bottom: 24px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.um-kpi-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.2);
    border-color: rgba(6, 182, 212, 0.5);
}
.um-kpi-left {
    display: flex;
    flex-direction: column;
}
.um-kpi-title {
    font-size: 11px;
    letter-spacing: 1.5px;
    color: #8C9BAE;
    text-transform: uppercase;
    margin-bottom: 8px;
    font-weight: 600;
}
.um-kpi-value {
    font-size: 36px;
    font-weight: 800;
    color: #FFFFFF;
    line-height: 1;
    text-shadow: 0 0 20px rgba(255, 255, 255, 0.2);
    font-family: 'JetBrains Mono', monospace;
}
.um-kpi-icon {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3), inset 0 2px 4px rgba(255, 255, 255, 0.2);
}
.um-icon-green { background: linear-gradient(135deg, #34D399, #059669); }
.um-icon-blue { background: linear-gradient(135deg, #38BDF8, #0284C7); }
.um-icon-purple { background: linear-gradient(135deg, #A78BFA, #7C3AED); }
.um-icon-red { background: linear-gradient(135deg, #FB7185, #E11D48); }

.um-icon-green::after { content: "🟢"; font-size: 20px; }
.um-icon-blue::after { content: "👑"; font-size: 20px; }
.um-icon-purple::after { content: "🛡️"; font-size: 20px; }
.um-icon-red::after { content: "🛑"; font-size: 20px; }

/* System Users List */
.um-list-container {
    background: rgba(14, 25, 52, 0.4);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 16px;
}
.um-list-header {
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    letter-spacing: 1px;
    color: #0EA5E9;
    font-weight: 700;
    margin-bottom: 16px;
    text-transform: uppercase;
}
.um-user-row {
    background: rgba(10, 18, 38, 0.4);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    padding: 12px 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
    transition: background 0.2s;
}
.um-user-row:hover {
    background: rgba(20, 32, 64, 0.8);
}
.um-user-info-wrapper {
    display: flex;
    align-items: center;
    gap: 16px;
}
.um-avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: rgba(14, 165, 233, 0.1);
    border: 1px solid rgba(14, 165, 233, 0.4);
    display: flex;
    justify-content: center;
    align-items: center;
    font-weight: 700;
    color: #0EA5E9;
    font-size: 14px;
}
.um-user-details {
    display: flex;
    flex-direction: column;
}
.um-username {
    font-size: 14px;
    font-weight: 600;
    color: #F8FAFC;
    margin-bottom: 2px;
}
.um-role {
    font-size: 11px;
    color: #94A3B8;
}
.um-status {
    padding: 4px 12px;
    border-radius: 4px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
    border: 1px solid rgba(16, 185, 129, 0.3);
    color: #10B981;
    background: rgba(16, 185, 129, 0.05);
}
.um-status.suspended {
    border-color: rgba(244, 63, 94, 0.3);
    color: #F43F5E;
    background: rgba(244, 63, 94, 0.05);
}

/* Forms Sections */
.um-section-title {
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1px;
    color: #0EA5E9;
    text-transform: uppercase;
    margin-bottom: 12px;
}
.um-section-title.red {
    color: #F43F5E;
    margin-top: 24px;
}
.um-form-box {
    background: rgba(14, 25, 52, 0.4);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 16px;
}

/* Glassmorphism for stForm */
div[data-testid="stForm"],
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(14, 25, 52, 0.4) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 12px !important;
    padding: 20px !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
}

/* Override Streamlit Primary Button Color */
div[data-testid="stFormSubmitButton"] > button,
button[kind="primaryFormSubmit"] {
    background: linear-gradient(135deg, #0EA5E9 0%, #2563EB 100%) !important;
    color: white !important;
    border: 1px solid rgba(14, 165, 233, 0.5) !important;
    box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3) !important;
}
div[data-testid="stFormSubmitButton"] > button:hover,
div[data-testid="stFormSubmitButton"] > button:hover,
button[kind="primaryFormSubmit"]:hover {
    background: linear-gradient(135deg, #38BDF8 0%, #3B82F6 100%) !important;
    box-shadow: 0 6px 16px rgba(14, 165, 233, 0.5) !important;
}

/* --- SEMANTIC ANALYTICS CUSTOM UI --- */
.fs-search-container {
    background: rgba(14, 25, 52, 0.4);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
}
.fs-kpi-bar {
    background: rgba(14, 25, 52, 0.4);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 16px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 10px;
    margin-bottom: 20px;
}
.fs-kpi-icon-box {
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    box-shadow: inset 0 2px 5px rgba(255, 255, 255, 0.05);
}
.fs-kpi-stats {
    display: flex;
    gap: 12px;
}
.fs-kpi-tag {
    background: rgba(0, 0, 0, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 13px;
    font-family: monospace;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 6px;
}
.fs-event-inspector {
    background: rgba(14, 25, 52, 0.4);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    margin-top: 15px;
}

</style>
"""
