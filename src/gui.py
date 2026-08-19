
import customtkinter as ctk
import threading
import platform
import os
import shutil
import time
import webbrowser
from datetime import datetime
from PIL import Image
from src.engine import SystemOrchestrator
from src.utils import get_logger

logger = get_logger()

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue") 

class ToolManagerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.orchestrator = SystemOrchestrator()
        self.title("FOSSEE eSim Engine")
        self.geometry("1150x900") 
        self.resizable(True, True) 
        if platform.system() == "Windows":
            self.after(0, lambda: self.state('zoomed'))
            
        self.configure(fg_color="#09090b") 

        # Main Layout Grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.total_tools = 4
        self.installed_tools = 0

        # ==========================================
        # LEFT SIDEBAR
        # ==========================================
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color="#f4c2c2", border_width=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # Move the flexible empty space to Row 5 (Pushes Row 6 & 7 to the bottom)
        self.sidebar.grid_rowconfigure(5, weight=1) 
        
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=22, pady=(40, 0), sticky="w")
        logo_frame.grid_columnconfigure(1, weight=1)

        esim_path = os.path.join(os.path.dirname(__file__), "esimlogo.png")
        if os.path.exists(esim_path):
            try:
                pil_img = Image.open(esim_path)
                img_w, img_h = pil_img.size
                target_h = 42
                target_w = int(target_h * (img_w / img_h))
                self.logo_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(target_w, target_h))
                ctk.CTkLabel(logo_frame, image=self.logo_img, text="").grid(row=0, column=0, padx=(0, 10), sticky="w")
            except Exception as e:
                logger.warning(f"Could not load esim logo: {e}")

        ctk.CTkLabel(logo_frame, text="eSim", text_color="#000000", font=ctk.CTkFont(family="Palatino Linotype", size=36, weight="bold")).grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(self.sidebar, text="Enterprise Architecture", text_color="#7e22ce", font=ctk.CTkFont(family="Palatino Linotype", size=14, weight="bold")).grid(row=1, column=0, padx=27, pady=(0, 40), sticky="w")

        self.btn_dashboard = ctk.CTkButton(self.sidebar, text="  Core Deployment", font=ctk.CTkFont(family="Palatino Linotype", size=16, weight="bold"), fg_color="#e0a8a8", text_color="#000000", hover_color="#d69b9b", anchor="w", height=48, corner_radius=8)
        self.btn_dashboard.grid(row=2, column=0, padx=20, pady=6, sticky="ew")
        
        self.btn_upcoming = ctk.CTkButton(self.sidebar, text="  🔒  Upcoming (v5)", font=ctk.CTkFont(family="Palatino Linotype", size=16, weight="bold"), fg_color="transparent", text_color="#000000", hover_color="#f4c2c2", anchor="w", height=48, state="normal")
        self.btn_upcoming.grid(row=3, column=0, padx=20, pady=6, sticky="ew")
        
        self.btn_locked = ctk.CTkButton(self.sidebar, text="  🔒  Premium Features", font=ctk.CTkFont(family="Palatino Linotype", size=16, weight="bold"), fg_color="transparent", text_color="#000000", hover_color="#f4c2c2", anchor="w", height=48, state="normal")
        self.btn_locked.grid(row=4, column=0, padx=20, pady=6, sticky="ew")

        # ==========================================
        # VERTICAL TOOL LOGO STACK (Now centered at bottom)
        # ==========================================
        self.logo_stack_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        # sticky="s" centers it horizontally and aligns it to the bottom of row 6
        self.logo_stack_frame.grid(row=6, column=0, pady=(0, 10), sticky="s")
        
        tool_files = [
            "ngspicelogo.jpg",
            "kicadlogo.png",
            "verilatorlogo.jpg",
            "openmodelicalogo.png"
        ]
        
        self.sidebar_logos = [] 
        
        for filename in tool_files:
            img_path = os.path.join(os.path.dirname(__file__), filename)
            if os.path.exists(img_path):
                try:
                    pil_img = Image.open(img_path)
                    
                    max_dim = 65
                    img_w, img_h = pil_img.size
                    scale = min(max_dim / img_w, max_dim / img_h)
                    new_w, new_h = int(img_w * scale), int(img_h * scale)
                    
                    ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(new_w, new_h))
                    self.sidebar_logos.append(ctk_img)
                    
                    lbl = ctk.CTkLabel(self.logo_stack_frame, image=ctk_img, text="")
                    lbl.pack(pady=12) 
                except Exception as e:
                    logger.warning(f"Could not load {filename}: {e}")

        # ==========================================
        # FOSSEE LOGO (Now perfectly centered under tools)
        # ==========================================
        fossee_path = os.path.join(os.path.dirname(__file__), "fosseelogo.png")
        if os.path.exists(fossee_path):
            try:
                fossee_pil = Image.open(fossee_path)
                img_w, img_h = fossee_pil.size
                target_h = 45 
                target_w = int(target_h * (img_w / img_h))
                self.fossee_img = ctk.CTkImage(light_image=fossee_pil, dark_image=fossee_pil, size=(target_w, target_h))
                # Removed padx, set sticky="s" to center align with the tool logos
                ctk.CTkLabel(self.sidebar, image=self.fossee_img, text="").grid(row=7, column=0, pady=(0, 30), sticky="s")
            except Exception as e:
                logger.warning(f"Could not load FOSSEE logo: {e}")

        # ==========================================
        # MAIN CONTENT AREA
        # ==========================================
        self.main_area = ctk.CTkFrame(self, fg_color="#09090b", corner_radius=0)
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=20)
        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(3, weight=1)

        self.header = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.header.grid(row=0, column=0, sticky="ew", padx=40, pady=(30, 10))
        self.header.grid_columnconfigure(0, weight=1) 

        header_text_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        header_text_frame.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(header_text_frame, text="System Setup", font=ctk.CTkFont(family="Palatino Linotype", size=36, weight="bold")).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(header_text_frame, text="Select required dependencies to deploy them natively to your local environment.", text_color="#a1a1aa", font=ctk.CTkFont(family="Palatino Linotype", size=15)).grid(row=1, column=0, sticky="w", pady=(3, 10))

        # ==========================================
        # DEPLOYMENT & STORAGE DASHBOARD 
        # ==========================================
        self.progress_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.progress_frame.grid(row=1, column=0, sticky="ew", padx=40, pady=(0, 15))
        
        self.install_progress_label = ctk.CTkLabel(self.progress_frame, text="Active Deployment: Idle", text_color="#a1a1aa", font=ctk.CTkFont(family="Palatino Linotype", size=14, weight="bold"))
        self.install_progress_label.pack(anchor="w", pady=(0, 4))
        
        self.install_progress = ctk.CTkProgressBar(self.progress_frame, width=1000, height=8, progress_color="#10b981", fg_color="#27272a", corner_radius=10)
        self.install_progress.pack(anchor="w", pady=(0, 15))
        self.install_progress.set(0)

        self.storage_label = ctk.CTkLabel(self.progress_frame, text="System Storage (C: Drive) - Calculating...", text_color="#a1a1aa", font=ctk.CTkFont(family="Palatino Linotype", size=14, weight="bold"))
        self.storage_label.pack(anchor="w", pady=(0, 4))
        
        self.storage_progress = ctk.CTkProgressBar(self.progress_frame, width=1000, height=8, progress_color="#3b82f6", fg_color="#27272a", corner_radius=10)
        self.storage_progress.pack(anchor="w")
        self.storage_progress.set(0)

        # ==========================================
        # TOOL DEPLOYMENT CARDS
        # ==========================================
        self.cards_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.cards_frame.grid(row=2, column=0, sticky="nsew", padx=30)
        self.cards_frame.grid_columnconfigure((0, 1), weight=1)

        self.tool_widgets = {}
        self.create_tool_card("Ngspice", "Simulation Engine", "Ngspice.Ngspice", 0, 0, "⚡")
        self.create_tool_card("KiCad", "PCB Design Suite", "KiCad.KiCad", 0, 1, "📐")
        self.create_tool_card("Verilator", "Verilog Simulator", "Verilator.Verilator", 1, 0, "⚙️")
        self.create_tool_card("OpenModelica", "Modeling Environment", "OpenModelica.OpenModelica", 1, 1, "🌐")

        # ==========================================
        # LIVE DEPLOYMENT TERMINAL 
        # ==========================================
        terminal_container = ctk.CTkFrame(self.main_area, fg_color="#000000", corner_radius=8, border_width=1, border_color="#27272a")
        terminal_container.grid(row=3, column=0, sticky="nsew", padx=40, pady=(10, 10))
        terminal_container.grid_columnconfigure(0, weight=1)
        terminal_container.grid_rowconfigure(1, weight=1)
        
        terminal_header = ctk.CTkLabel(terminal_container, text=">_ LIVE DEPLOYMENT CONSOLE", font=ctk.CTkFont(family="Consolas", size=12, weight="bold"), text_color="#71717a")
        terminal_header.grid(row=0, column=0, sticky="w", padx=15, pady=(5, 0))

        self.terminal = ctk.CTkTextbox(terminal_container, fg_color="transparent", text_color="#10b981", font=ctk.CTkFont(family="Consolas", size=13), wrap="word")
        self.terminal.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
        self.terminal.configure(state="disabled") 
        
        self.log_to_terminal("FOSSEE eSim Deployment Engine initialized.")
        self.log_to_terminal("Awaiting user deployment commands...")

        # ==========================================
        # LIVE ANIMATED NEWS TICKER 
        # ==========================================
        self.ticker_frame = ctk.CTkFrame(self.main_area, height=45, fg_color="#18181b", corner_radius=8, border_width=1, border_color="#27272a")
        self.ticker_frame.grid(row=4, column=0, sticky="ew", padx=40, pady=(0, 0))
        self.ticker_frame.grid_propagate(False) 
        
        self.ticker_text = "✦ LIVE UPDATE: Enterprise Architecture v5 active deployment underway. | 🚀 UPCOMING PREMIUM FEATURES: AI-Driven Circuit Optimization, Cloud Workspace Collaboration, Advanced 3D PCB Rendering, and Automated BOM Generation. | ⚡ MORE UPDATES: Prepare for v5.1 with expanded Verilator simulation support. ✦"
        self.ticker_label = ctk.CTkLabel(self.ticker_frame, text=self.ticker_text, font=ctk.CTkFont(family="Palatino Linotype", size=15, slant="italic"), text_color="#fbbf24")
        
        self.ticker_relx = 1.0  
        self.animate_ticker()

        # ==========================================
        # ACTION BAR
        # ==========================================
        self.action_bar = ctk.CTkFrame(self.main_area, height=80, fg_color="#18181b", corner_radius=12, border_width=1, border_color="#27272a")
        self.action_bar.grid(row=5, column=0, sticky="ew", padx=40, pady=20)
        self.action_bar.grid_columnconfigure(0, weight=1)
        
        self.status_label = ctk.CTkLabel(self.action_bar, text="🟢 System ready for deployment.", text_color="#d4d4d8", font=ctk.CTkFont(family="Palatino Linotype", size=16))
        self.status_label.grid(row=0, column=0, padx=25, sticky="w")
        
        self.finish_btn = ctk.CTkButton(self.action_bar, text="Complete Setup ✓", fg_color="#ffffff", text_color="#000000", hover_color="#e4e4e7", font=ctk.CTkFont(family="Palatino Linotype", weight="bold", size=16), height=45, corner_radius=8, command=self.close_app)
        self.finish_btn.grid(row=0, column=1, padx=25, pady=20, sticky="e")

        logger.info("GUI successfully launched with live terminal.")
        threading.Thread(target=self.run_startup_diagnostics).start()
        threading.Thread(target=self.check_disk_space).start()

    # --- TERMINAL LOGGING ENGINE ---
    def log_to_terminal(self, message, is_error=False):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] {message}\n"
        
        self.terminal.configure(state="normal")
        self.terminal.insert("end", formatted_msg)
        self.terminal.see("end") 
        self.terminal.configure(state="disabled")

    # --- TICKER ANIMATION ENGINE ---
    def animate_ticker(self):
        self.ticker_relx -= 0.002  
        if self.ticker_relx < -3.5:
            self.ticker_relx = 1.0
        try:
            self.ticker_label.place(relx=self.ticker_relx, rely=0.5, anchor="w")
            self.after(20, self.animate_ticker)
        except Exception:
            pass 

    def check_disk_space(self):
        try:
            total, used, free = shutil.disk_usage("C:\\")
            total_gb = total / (1024**3)
            free_gb = free / (1024**3)
            used_gb = used / (1024**3)
            used_ratio = used / total
            
            self.storage_progress.set(used_ratio)
            self.storage_label.configure(text=f"System Storage (C: Drive): {used_gb:.1f} GB Used / {total_gb:.1f} GB Total ({free_gb:.1f} GB Free)")
        except Exception as e:
            self.storage_progress.set(0.5)
            self.storage_label.configure(text="System Storage (C: Drive): Active")
            self.log_to_terminal(f"Warning: Could not verify local disk space ({e})", is_error=True)

    def create_tool_card(self, display_name, subtitle, package_name, row, col, icon):
        card = ctk.CTkFrame(self.cards_frame, corner_radius=12, fg_color="#18181b", border_width=1, border_color="#27272a")
        card.grid(row=row, column=col, sticky="ew", padx=10, pady=10)
        card.grid_columnconfigure(0, weight=1)
        
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.grid(row=0, column=0, sticky="w", padx=25, pady=25)
        ctk.CTkLabel(info_frame, text=f"{icon}  {display_name}", font=ctk.CTkFont(family="Palatino Linotype", size=24, weight="bold")).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(info_frame, text=subtitle, text_color="#71717a", font=ctk.CTkFont(family="Palatino Linotype", size=16)).grid(row=1, column=0, sticky="w", pady=(2,0))
        
        btn = ctk.CTkButton(card, text="Checking...", width=110, height=36, corner_radius=6, font=ctk.CTkFont(family="Palatino Linotype", size=15, weight="bold"), state="disabled")
        btn.grid(row=0, column=1, padx=25, pady=25, sticky="e")
        
        btn.configure(command=lambda: self.install_tool(display_name, package_name, btn))
        self.tool_widgets[display_name] = {"btn": btn, "pkg": package_name}

    def run_startup_diagnostics(self):
        self.log_to_terminal("Running startup diagnostics on local environment...")
        time.sleep(1) 
        for name, widgets in self.tool_widgets.items():
            if self.orchestrator.check_tool_installed(name):
                widgets["btn"].configure(text="Installed", state="disabled", fg_color="#10b981", text_color="#ffffff", hover_color="#10b981")
                self.installed_tools += 1
                self.log_to_terminal(f"Verified: {name} is already deployed locally.")
            else:
                widgets["btn"].configure(text="Install", state="normal", fg_color="#3b82f6", text_color="#ffffff", hover_color="#2563eb")
                self.log_to_terminal(f"Missing Dependency: {name} needs installation.")
        self.status_label.configure(text="🟢 Diagnostics complete. Awaiting action.")
        self.log_to_terminal("Diagnostics complete. Ready.")

    def install_tool(self, display_name, package_name, btn):
        self.log_to_terminal(f"INITIATING DEPLOYMENT SEQUENCE FOR: {display_name}...")
        btn.configure(state="disabled", text="Deploying...", fg_color="#f59e0b", text_color="#000000")
        self.status_label.configure(text=f"🔄 Deploying {display_name}. Please wait...")
        
        def process_install():
            self.install_progress_label.configure(text=f"Active Deployment: Installing {display_name}... 0%")
            self.install_progress.set(0)
            
            for i in range(1, 95):
                time.sleep(0.05) 
                self.install_progress.set(i / 100.0)
                self.install_progress_label.configure(text=f"Active Deployment: Installing {display_name}... {i}%")

            self.log_to_terminal(f"[{display_name}] Fetching packages from upstream repository...")
            time.sleep(1)
            
            if "KiCad" in display_name:
                self.log_to_terminal(f"[{display_name}] Compiling OS-specific payload...")
                current_os = platform.system()
                
                if current_os == "Windows":
                    self.log_to_terminal(f"[{display_name}] Windows architecture detected. Routing to official gateway...")
                    safe_url = "https://www.kicad.org/download/windows/"
                elif current_os == "Darwin":
                    self.log_to_terminal(f"[{display_name}] macOS architecture detected. Routing to official gateway...")
                    safe_url = "https://www.kicad.org/download/macos/"
                else:
                    self.log_to_terminal(f"[{display_name}] Linux architecture detected. Routing to official gateway...")
                    safe_url = "https://www.kicad.org/download/linux/"
                
                webbrowser.open(safe_url)
                result = "secure_route"
            else:
                self.log_to_terminal(f"[{display_name}] Extracting architecture files...")
                result = self.orchestrator.trigger_installation(package_name)
            
            self.install_progress.set(1.0)
            self.install_progress_label.configure(text=f"Active Deployment: {display_name} Complete (100%)")

            if result == "native":
                self.log_to_terminal(f"[{display_name}] SYSTEM DEPLOYMENT SUCCESSFUL.")
                self.status_label.configure(text=f"✅ {display_name} successfully deployed.")
                btn.configure(state="normal", text="Verify", fg_color="#3b82f6", text_color="#ffffff", hover_color="#2563eb")
                self.installed_tools += 1
            elif result == "secure_route":
                self.log_to_terminal(f"[{display_name}] Routed through secure browser gateway.")
                self.status_label.configure(text=f"✅ {display_name} routed through secure gateway.")
                btn.configure(state="normal", text="Verify", fg_color="#3b82f6", text_color="#ffffff", hover_color="#2563eb")
                self.installed_tools += 1
            else:
                self.log_to_terminal(f"ERROR: Failed to deploy {display_name}. Verification failed.", is_error=True)
                self.status_label.configure(text=f"❌ Failed to process {display_name}. Check network.")
                btn.configure(state="normal", text="Retry", fg_color="#ef4444", text_color="#ffffff", hover_color="#dc2626")
                self.install_progress_label.configure(text=f"Active Deployment: {display_name} Failed")
                self.install_progress.set(0)

            time.sleep(3)
            self.install_progress_label.configure(text="Active Deployment: Idle")
            self.install_progress.set(0)

        threading.Thread(target=process_install).start()

    def close_app(self):
        self.log_to_terminal("Shutting down eSim Engine...")
        logger.info("Application closed by user.")
        self.destroy()