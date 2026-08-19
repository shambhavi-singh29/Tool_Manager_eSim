import platform
import subprocess
import shutil
import os
import tempfile
import webbrowser
import zipfile
import urllib.request
import urllib.error
from src.utils import get_logger

logger = get_logger()

class SystemOrchestrator:
    def __init__(self):
        self.os_type = platform.system()
        logger.info(f"SystemOrchestrator initialized on OS: {self.os_type}")
        self.tools_meta = {
            "OpenModelica.OpenModelica": {
                "url": "none",
                "filename": "none",
                "fallback_page": "https://openmodelica.org/download/download-windows/",
                "force_browser": True 
            },
            "KiCad.KiCad": {
                "url": "https://github.com/KiCad/kicad-source-mirror/releases/download/8.0.1/kicad-8.0.1-x86_64.exe",
                "filename": "KiCad_Installer.exe",
                "force_browser": False
            },
            "Ngspice.Ngspice": {
                "url": "https://deac-ams.dl.sourceforge.net/project/ngspice/ng-spice-rework/42/ngspice-42_64.zip",
                "filename": "ngspice.zip",
                "fallback_page": "https://sourceforge.net/projects/ngspice/files/latest/download",
                "force_browser": False
            },
            "Verilator.Verilator": {
                "url": "https://github.com/verilator/verilator/archive/refs/tags/v5.022.zip",
                "filename": "verilator.zip",
                "fallback_page": "https://verilator.org/guide/latest/install.html",
                "force_browser": False
            }
        }

    def check_tool_installed(self, tool_name):
        return bool(shutil.which(tool_name.lower()))

    def trigger_installation(self, package_id):
        if self.os_type == "Windows" and package_id in self.tools_meta:
            meta = self.tools_meta[package_id]
            fallback = meta.get("fallback_page")
            
            if meta.get("force_browser"):
                logger.info(f"{package_id} routed to secure gateway.")
                webbrowser.open(fallback)
                return "secure_route"

            url = meta["url"]
            filename = meta["filename"]
            temp_dir = os.path.join(tempfile.gettempdir(), "FOSSEE_eSim_Downloads")
            os.makedirs(temp_dir, exist_ok=True)
            filepath = os.path.join(temp_dir, filename)
            
            logger.info(f"Initiating silent binary fetch for {package_id}...")
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36'}
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=20) as response, open(filepath, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)
                logger.info(f"Download successful. File secured at: {filepath}")

                if filename.endswith(".exe"):
                    logger.info(f"Executing Windows Installer natively for {package_id}")
                    os.startfile(filepath) 
                    return "native"
                elif filename.endswith(".zip"):
                    logger.info(f"Extracting .zip archive for {package_id}")
                    install_dir = os.path.join("C:\\", "FOSSEE_eSim_Tools", package_id.split('.')[0])
                    os.makedirs(install_dir, exist_ok=True)
                    with zipfile.ZipFile(filepath, 'r') as zip_ref:
                        zip_ref.extractall(install_dir)
                    os.startfile(install_dir)
                    logger.info(f"Successfully extracted to {install_dir}")
                    return "native"

            except Exception as e:
                logger.warning(f"Direct stream blocked for {package_id} ({e}). Rerouting to gateway.")
                webbrowser.open(fallback)
                return "secure_route"
        return "failed"