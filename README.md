# 🛡️ ContextGuard: Shadow AI Governance Framework

**ContextGuard** is an automated risk assessment and governance framework designed to detect, analyze and mitigate insider threats arising from the unauthorized use of Large Language Models (LLMs) in corporate environments (Shadow AI).

By establishing a non-intrusive, context-aware inspection plane, the framework intercepts outbound AI API traffic, decodes complex payload structures and evaluates data sensitivity using Natural Language Processing (NLP). It calculates a dynamic **Weighted Risk Scoring Engine (WRSE)** score and routes real-time alerts to a Zero-Trust Security Operations dashboard.

---

## ✨ Key Features
- **Live Network Interception (`mitmproxy`):** Actively intercepts TLS-encrypted POST requests sent to AI domains (`chatgpt.com`, `gemini.google.com`, `claude.ai`).
- **Advanced Double-Plane URL Decoder:** Automatically parses nested OpenAI JSON arrays and unquotes deeply nested Google Gemini string objects (`f.req=`).
- **In-Memory NLP Asset Indexing:** Cross-references prompt text against 15 Master CSV Corporate Asset sheets (Medical Records, Infrastructure Credentials, IP) in sub-second latency.
- **Weighted Risk Scoring Engine (WRSE):** Computes a unified risk coefficient (0-100) based on Data Sensitivity ($W_S$), Destination Trust ($W_D$), and User Authority ($W_U$).
- **Zero-Trust Administrative Dashboard:** A premium glassmorphism Streamlit UI featuring WAF SQLi/XSS sanitization, brute-force lockout, SQLite state persistence, and file-backed session management.

---

## 🏗️ System Architecture
The framework operates on a decoupled 4-tier pipeline:
1. **Tier 1 - Data Ingestion:** `live_mitm_logger.py` captures and logs network metadata and raw prompts into `wrse_comprehensive_audit.log`.
2. **Tier 2 - NLP Inspection Layer:** `data_core.py` executes `forensic_normalize()` and indexes prompts against the Corporate Asset Vault to identify data leaks.
3. **Tier 3 - WRSE Scoring Module:** Calculates the mathematical risk score and assigns severity classifications (`CRITICAL`, `MEDIUM`, `LOW`).
4. **Tier 4 - Governance Visualization:** `app.py` serves the real-time dashboard for administrators.
