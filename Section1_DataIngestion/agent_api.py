from flask import Flask, request, jsonify, Response
import json
import os

app = Flask(__name__)

# Constants
REGISTRY_FILE = "/home/izu/ShadowAI_Framework/Section1_DataIngestion/agent_registry.json"
DOMAINS_FILE = "/home/izu/ShadowAI_Framework/Section1_DataIngestion/domains.json"
MITMPROXY_CERT = "/root/.mitmproxy/mitmproxy-ca-cert.cer"
PROXY_SERVER = "192.168.89.132:8080"

def load_registry():
    if os.path.exists(REGISTRY_FILE):
        try:
            with open(REGISTRY_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return {}

def save_registry(registry):
    with open(REGISTRY_FILE, "w") as f:
        json.dump(registry, f, indent=4)

@app.route('/register', methods=['POST'])
def register_agent():
    data = request.json
    if not data or 'ip' not in data or 'username' not in data:
        return jsonify({"error": "Missing IP or username"}), 400
    
    agent_ip = data['ip']
    username = data['username']
    
    # Simple role mapping based on name, can be expanded
    role = "Standard Staff"
    if "admin" in username.lower() or "root" in username.lower():
        role = "Privileged Admin"
    elif "dr" in username.lower() or "med" in username.lower():
        role = "Medical Specialist"
        
    registry = load_registry()
    registry[agent_ip] = {
        "username": username,
        "role": role,
        "last_seen": "now" # Could use actual timestamp
    }
    save_registry(registry)
    
    print(f"[+] Agent Registered: {agent_ip} -> {username} ({role})")
    return jsonify({"status": "success", "role": role}), 200

@app.route('/proxy.pac', methods=['GET'])
def get_pac():
    domains = []
    if os.path.exists(DOMAINS_FILE):
        with open(DOMAINS_FILE, "r") as f:
            domains = json.load(f)
    else:
        domains = ["chatgpt.com", "claude.ai", "gemini.google.com", "grok.com", "grok.x.ai", "perplexity.ai", "mistral.ai"]

    matchers = " || ".join([f'shExpMatch(host, "*{d}")' for d in domains])
    
    pac_content = f"""function FindProxyForURL(url, host) {{
    // Bypass local networks
    if (isPlainHostName(host) || 
        shExpMatch(host, "127.0.0.1") || 
        shExpMatch(host, "localhost") || 
        shExpMatch(host, "192.168.*") ||
        shExpMatch(host, "10.*")) {{
        return "DIRECT";
    }}

    // Intercept only AI Domains
    if ({matchers}) {{
        return "PROXY {PROXY_SERVER}";
    }}

    // All other traffic goes direct (No Network Breakage!)
    return "DIRECT";
}}
"""
    return Response(pac_content, mimetype='application/x-ns-proxy-autoconfig')

@app.route('/cert', methods=['GET'])
def get_cert():
    """Serve the mitmproxy CA certificate for auto-installation on Windows agents."""
    cert_path = MITMPROXY_CERT
    # Try user home as fallback
    import glob
    if not os.path.exists(cert_path):
        matches = glob.glob(os.path.expanduser("~/.mitmproxy/mitmproxy-ca-cert.cer"))
        if matches:
            cert_path = matches[0]
    if not os.path.exists(cert_path):
        return jsonify({"error": "Certificate not found"}), 404
    with open(cert_path, "rb") as f:
        cert_data = f.read()
    return Response(
        cert_data,
        mimetype='application/x-x509-ca-cert',
        headers={"Content-Disposition": "attachment; filename=ShadowAI_CA.cer"}
    )

if __name__ == '__main__':
    print(f"[*] Starting ShadowAI Agent API on 0.0.0.0:5000")
    print(f"[*] PAC Script available at http://192.168.89.132:5000/proxy.pac")
    app.run(host='0.0.0.0', port=5000)
