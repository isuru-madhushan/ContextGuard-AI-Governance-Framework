from mitmproxy import http
import json
import datetime
import os
import re
import time
import urllib.parse

LOG_FILE = "/home/izu/ShadowAI_Framework/Section1_DataIngestion/wrse_comprehensive_audit.log"
DOMAINS_FILE = "/home/izu/ShadowAI_Framework/Section1_DataIngestion/domains.json"


def load_monitored_domains():
    """Load AI domains dynamically from domains.json so all 60+ AI tools are captured."""
    try:
        with open(DOMAINS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        # Fallback to core domains if file is missing
        return [
            "chatgpt.com", "api.openai.com", "openai.com",
            "gemini.google.com", "ai.google.com",
            "claude.ai", "anthropic.com",
            "deepseek.com", "copilot.microsoft.com",
            "perplexity.ai", "mistral.ai", "groq.com",
            "huggingface.co", "cohere.com", "replicate.com",
            "poe.com", "character.ai", "you.com",
            "together.ai", "x.ai", "pi.ai"
        ]

def request(flow: http.HTTPFlow) -> None:
    monitored_domains = load_monitored_domains()
    request_host = flow.request.pretty_host.lower()

    # Check if this traffic is to ANY known AI domain
    is_ai_traffic = any(domain.lower() in request_host for domain in monitored_domains)

    if is_ai_traffic and flow.request.method in ("POST", "PUT", "PATCH"):
        # --- NEW TELEMETRY FILTER ---
        req_url = flow.request.url.lower()
        if any(x in req_url for x in ["/events", "/metrics", "/lat/", "/log", "/telemetry", "/ces/v1", "/track", "/stats"]):
            return
        # ----------------------------
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 
            
            # 
            # PHASE 1+: Normal text prompt parsing (existing logic)
            # 
            flow.request.decode()
            raw_content = flow.request.get_text()

            #  ADVANCED MULTI-FORMAT AI PAYLOAD PARSER
            # Supports: OpenAI, Claude, Gemini, Perplexity, Mistral, HuggingFace, Cohere, Grok, etc.
            prompt_text = None
            import base64

            # Stage 0: Grok / xAI SSE format  data=<base64_encoded_json>
            if raw_content.strip().startswith("data=") or "\ndata=" in raw_content:
                try:
                    for line in raw_content.splitlines():
                        line = line.strip()
                        if line.startswith("data="):
                            b64_value = urllib.parse.unquote(line[5:])  # Strip "data=" prefix
                            try:
                                decoded_bytes = base64.b64decode(b64_value + "==")  # Pad for safety
                                decoded_str = decoded_bytes.decode("utf-8", errors="ignore")
                                inner = json.loads(decoded_str)
                                # Try known Grok keys
                                for key in ["message", "userMessage", "prompt", "query", "text", "content", "requestMessage", "humanTurn"]:
                                    if key in inner:
                                        val = inner[key]
                                        prompt_text = val if isinstance(val, str) else str(val)
                                        break
                                if not prompt_text:
                                    # Log the keys so we can add them
                                    print(f"[🔍 GROK KEY DUMP] Keys: {list(inner.keys())}")
                                    prompt_text = decoded_str[:400]
                            except Exception:
                                # Not valid base64 JSON - try raw URL decode
                                prompt_text = urllib.parse.unquote(line[5:])[:400]
                            if prompt_text:
                                break
                except Exception as e:
                    print(f"[!] Grok SSE parse error: {e}")

            # Stage 1: Form Data & URL-encoded format (ChatGPT Web, Gemini)
            if not prompt_text:
                parsed_qs = urllib.parse.parse_qs(raw_content)
                if "prompt" in parsed_qs:
                    prompt_text = parsed_qs["prompt"][0]
                elif "f.req" in parsed_qs:
                    prompt_text = parsed_qs["f.req"][0]
                elif "f.req=" in raw_content:
                    decoded_stage = urllib.parse.unquote(raw_content)
                    prompt_text = decoded_stage.split("f.req=")[-1].split("&")[0].strip()

            # Stage 2: JSON parsing - try all known AI API formats
            if not prompt_text or len(prompt_text.strip()) < 5:
                try:
                    data = json.loads(raw_content)

                    # --- OpenAI / ChatGPT format ---
                    if "messages" in data:
                        msg_list = data.get("messages", [])
                        texts = []
                        for msg in msg_list:
                            content = msg.get("content", "")
                            if isinstance(content, str) and content.strip():
                                texts.append(content.strip())
                            elif isinstance(content, list):
                                for part in content:
                                    if isinstance(part, dict) and part.get("type") == "text":
                                        texts.append(part.get("text", ""))
                            elif isinstance(content, dict):
                                parts = content.get("parts", [])
                                if isinstance(parts, list):
                                    for part in parts:
                                        if isinstance(part, str):
                                            texts.append(part.strip())
                        prompt_text = " | ".join(texts) if texts else None

                    # --- Perplexity format ---
                    elif "query_str" in data:
                        prompt_text = str(data["query_str"])
                    elif "search_query" in data:
                        prompt_text = str(data["search_query"])

                    # --- Anthropic / Claude format ---
                    elif "prompt" in data:
                        prompt_text = str(data["prompt"])

                    # --- HuggingFace / Inference API ---
                    elif "inputs" in data:
                        inp = data["inputs"]
                        prompt_text = inp if isinstance(inp, str) else str(inp)

                    # --- Cohere format ---
                    elif "message" in data:
                        prompt_text = str(data["message"])
                    elif "chat_history" in data:
                        history = data.get("chat_history", [])
                        if history:
                            prompt_text = str(history[-1].get("message", ""))

                    # --- Generic / Mistral / Groq / Together / Replicate ---
                    elif "text" in data:
                        prompt_text = str(data["text"])
                    elif "query" in data:
                        prompt_text = str(data["query"])
                    elif "q" in data:
                        prompt_text = str(data["q"])
                    elif "input" in data:
                        inp = data["input"]
                        prompt_text = inp if isinstance(inp, str) else str(inp)
                    elif "content" in data:
                        prompt_text = str(data["content"])

                except json.JSONDecodeError:
                    pass

            # GROK DEBUG: Print what we got so we can identify the format
            if "grok" in request_host or "x.ai" in request_host:
                print(f"\n[🔍 GROK DEBUG] URL: {flow.request.url}")
                print(f"[🔍 GROK DEBUG] Content-Type: {flow.request.headers.get('Content-Type', 'N/A')}")
                print(f"[🔍 GROK DEBUG] Raw (first 300 chars): {raw_content[:300]}")
                print(f"[🔍 GROK DEBUG] Parsed prompt: {str(prompt_text)[:200] if prompt_text else 'NONE'}\n")

            if not prompt_text or len(str(prompt_text).strip()) < 3:
                return # Skip logging if prompt is empty or less than 3 chars
            if prompt_text:
                pt_str = str(prompt_text).strip()
                if len(pt_str) < 3 and pt_str.lower() not in ["hi", "ok", "no"]:
                    return

                # Filter Gemini background telemetry
                if pt_str.startswith('[[["') and '","[' in pt_str:
                    if len(pt_str) < 150 or '"generic"]]]' in pt_str:
                        return




            client_ip = flow.client_conn.peername[0]
            client_port = flow.client_conn.peername[1]
            user_agent = flow.request.headers.get("User-Agent", "Unknown")
            
            dest_ip = "N/A"
            if flow.server_conn and flow.server_conn.peername:
                dest_ip = flow.server_conn.peername[0]

            os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

            log_entry = {
                "timestamp": timestamp,
                "connection_metadata": {
                    "http_method": flow.request.method,
                    "user_agent": user_agent
                },
                "source_node": {
                    "client_ip": client_ip,
                    "source_port": client_port
                },
                "destination_node": {
                    "destination_domain": request_host,
                    "destination_ip": dest_ip,
                    "full_url": flow.request.url
                },
                "captured_payload": {
                    "prompt": prompt_text
                }
            }

            logs = []
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, "r") as f:
                    try: logs = json.load(f)
                    except json.JSONDecodeError: logs = []
                        
            logs.append(log_entry)
            with open(LOG_FILE, "w") as f:
                json.dump(logs, f, indent=4)
                
            print(f"[🛡️ CAPTURED] {request_host} | From: {client_ip} | Prompt: {str(prompt_text)[:80]}...")
        except Exception as e:
            print(f"[!] Logger error: {e}")
            pass