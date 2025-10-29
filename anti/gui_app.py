import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import time
from database_manager import DatabaseManager
from file_scanner import FileScanner

class SplashScreen:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)
        self.root.configure(bg='#0a0e27')
        
        # Center the window
        window_width = 600
        window_height = 400
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f'{window_width}x{window_height}+{x}+{y}')
        
        # Create canvas for animation
        self.canvas = tk.Canvas(self.root, width=600, height=400, 
                               bg='#0a0e27', highlightthickness=0)
        self.canvas.pack()
        
        # Shield icon (simple circle with text)
        self.shield = self.canvas.create_oval(250, 100, 350, 200, 
                                             fill='#00d9ff', outline='#0099cc', width=3)
        self.shield_text = self.canvas.create_text(300, 150, 
                                                   text='S', font=('Arial', 60, 'bold'),
                                                   fill='#0a0e27')
        
        # Title
        self.title = self.canvas.create_text(300, 250, 
                                            text='SecureGuard Antivirus',
                                            font=('Arial', 28, 'bold'),
                                            fill='#00d9ff')
        
        # Subtitle
        self.subtitle = self.canvas.create_text(300, 290,
                                               text='Advanced Threat Protection',
                                               font=('Arial', 12),
                                               fill='#808080')
        
        # Progress bar
        self.progress_bg = self.canvas.create_rectangle(150, 330, 450, 345,
                                                        fill='#1a1f3a', outline='#00d9ff')
        self.progress_bar = self.canvas.create_rectangle(150, 330, 150, 345,
                                                         fill='#00d9ff', outline='')
        
        self.progress_text = self.canvas.create_text(300, 360,
                                                     text='Initializing...',
                                                     font=('Arial', 10),
                                                     fill='#808080')
        
        # Start animation
        self.animate_intro()
    
    def animate_intro(self):
        # Pulse shield
        for i in range(3):
            self.canvas.itemconfig(self.shield, width=3+i*2)
            self.root.update()
            time.sleep(0.1)
        
        # Progress bar animation
        steps = ['Initializing Database...', 'Loading Signatures...', 
                'Starting Engine...', 'Ready!']
        
        for i, step in enumerate(steps):
            progress_width = 150 + (300 * (i + 1) / len(steps))
            self.canvas.coords(self.progress_bar, 150, 330, progress_width, 345)
            self.canvas.itemconfig(self.progress_text, text=step)
            self.root.update()
            time.sleep(0.5)
        
        time.sleep(0.3)
        self.root.destroy()

class AntivirusGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SecureGuard Antivirus")
        self.root.geometry("1100x750")
        self.root.configure(bg="#0a0e27")
        
        # Initialize database
        DatabaseManager.initialize_database()
        
        # Scanning state
        self.scanning = False
        self.detected_threats = []
        
        # Create UI
        self.create_sidebar()
        self.create_main_area()
        
        # Show scan tab by default
        self.show_scan_tab()
    
    def create_sidebar(self):
        sidebar = tk.Frame(self.root, bg="#16213e", width=250)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        # Logo area
        logo_frame = tk.Frame(sidebar, bg="#16213e", height=120)
        logo_frame.pack(fill=tk.X, pady=20)
        logo_frame.pack_propagate(False)
        
        # Shield icon
        shield_canvas = tk.Canvas(logo_frame, width=80, height=80, 
                                 bg="#16213e", highlightthickness=0)
        shield_canvas.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        shield_canvas.create_oval(10, 10, 70, 70, fill="#00d9ff", outline="#0099cc", width=3)
        shield_canvas.create_text(40, 40, text="S", font=("Arial", 40, "bold"), fill="#16213e")
        
        tk.Label(sidebar, text="SecureGuard", font=("Arial", 16, "bold"),
                bg="#16213e", fg="#00d9ff").pack()
        
        # Navigation buttons
        self.nav_buttons = []
        nav_items = [
            ("Scan", self.show_scan_tab, "🔍"),
            ("Allowed Threats", self.show_allowed_tab, "✅"),
            ("Quarantine", self.show_quarantine_tab, "🚫"),
            ("History", self.show_history_tab, "📜")
        ]
        
        for text, command, icon in nav_items:
            btn = tk.Button(sidebar, text=f"{icon}  {text}", command=command,
                          bg="#16213e", fg="white", font=("Arial", 12),
                          bd=0, padx=20, pady=15, cursor="hand2",
                          activebackground="#0f3460", activeforeground="white",
                          anchor="w")
            btn.pack(fill=tk.X, padx=10, pady=5)
            self.nav_buttons.append(btn)
        
        # Footer
        footer = tk.Frame(sidebar, bg="#16213e", height=60)
        footer.pack(side=tk.BOTTOM, fill=tk.X)
        tk.Label(footer, text="Version 1.0", font=("Arial", 9),
                bg="#16213e", fg="#808080").pack(pady=10)
    
    def create_main_area(self):
        self.main_area = tk.Frame(self.root, bg="#0a0e27")
        self.main_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Container for different tabs
        self.content_frame = tk.Frame(self.main_area, bg="#0a0e27")
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Reset button colors
        for btn in self.nav_buttons:
            btn.config(bg="#16213e")
    
    def highlight_nav(self, index):
        self.nav_buttons[index].config(bg="#0f3460")
    
    def show_scan_tab(self):
        self.clear_content()
        self.highlight_nav(0)
        
        # Header
        header = tk.Frame(self.content_frame, bg="#0a0e27")
        header.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(header, text="System Scan", font=("Arial", 28, "bold"),
                bg="#0a0e27", fg="white").pack(anchor="w")
        tk.Label(header, text="Protect your system from threats",
                bg="#0a0e27", fg="#808080", font=("Arial", 11)).pack(anchor="w")
        
        # Quick Scan Card
        quick_card = tk.Frame(self.content_frame, bg="#16213e", relief=tk.FLAT)
        quick_card.pack(fill=tk.X, pady=10)
        
        card_content = tk.Frame(quick_card, bg="#16213e")
        card_content.pack(padx=30, pady=30)
        
        tk.Label(card_content, text="Quick Scan", font=("Arial", 18, "bold"),
                bg="#16213e", fg="white").pack(anchor="w")
        tk.Label(card_content, text="Scan Downloads, Desktop, Documents, and Temp folders",
                bg="#16213e", fg="#b0b0b0", font=("Arial", 10)).pack(anchor="w", pady=(5, 15))
        
        self.quick_scan_btn = tk.Button(card_content, text="Start Quick Scan",
                                       command=self.quick_scan,
                                       bg="#00d9ff", fg="#0a0e27",
                                       font=("Arial", 12, "bold"),
                                       padx=30, pady=12, bd=0, cursor="hand2",
                                       activebackground="#0099cc")
        self.quick_scan_btn.pack(anchor="w")
        
        # Custom Scan Card
        custom_card = tk.Frame(self.content_frame, bg="#16213e", relief=tk.FLAT)
        custom_card.pack(fill=tk.X, pady=10)
        
        card_content = tk.Frame(custom_card, bg="#16213e")
        card_content.pack(padx=30, pady=30)
        
        tk.Label(card_content, text="Custom Scan", font=("Arial", 18, "bold"),
                bg="#16213e", fg="white").pack(anchor="w")
        tk.Label(card_content, text="Select a specific file or folder to scan",
                bg="#16213e", fg="#b0b0b0", font=("Arial", 10)).pack(anchor="w", pady=(5, 15))
        
        path_frame = tk.Frame(card_content, bg="#16213e")
        path_frame.pack(fill=tk.X)
        
        self.path_entry = tk.Entry(path_frame, font=("Arial", 11), bg="#0f3460",
                                   fg="white", insertbackground="white", bd=0,
                                   relief=tk.FLAT)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, ipadx=10)
        
        tk.Button(path_frame, text="Browse", command=self.browse_path,
                 bg="#1a2332", fg="white", font=("Arial", 10),
                 bd=0, padx=15, pady=8, cursor="hand2").pack(side=tk.LEFT, padx=(10, 0))
        
        self.custom_scan_btn = tk.Button(path_frame, text="Scan",
                                        command=self.custom_scan,
                                        bg="#00d9ff", fg="#0a0e27",
                                        font=("Arial", 10, "bold"),
                                        bd=0, padx=20, pady=8, cursor="hand2")
        self.custom_scan_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Scan Results
        results_card = tk.Frame(self.content_frame, bg="#16213e", relief=tk.FLAT)
        results_card.pack(fill=tk.BOTH, expand=True, pady=10)
        
        tk.Label(results_card, text="Scan Results", font=("Arial", 16, "bold"),
                bg="#16213e", fg="white").pack(anchor="w", padx=30, pady=(20, 10))
        
        self.results_text = scrolledtext.ScrolledText(results_card,
                                                     bg="#0f3460", fg="white",
                                                     font=("Consolas", 10),
                                                     wrap=tk.WORD, bd=0,
                                                     insertbackground="white")
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 20))
    
    def show_allowed_tab(self):
        self.clear_content()
        self.highlight_nav(1)
        
        # Header
        tk.Label(self.content_frame, text="Allowed Threats",
                font=("Arial", 28, "bold"), bg="#0a0e27", fg="white").pack(anchor="w")
        
        # Toolbar
        toolbar = tk.Frame(self.content_frame, bg="#0a0e27")
        toolbar.pack(fill=tk.X, pady=20)
        
        tk.Button(toolbar, text="🔄 Refresh", command=self.load_allowed_threats,
                 bg="#16213e", fg="white", font=("Arial", 10),
                 bd=0, padx=20, pady=10, cursor="hand2").pack(side=tk.LEFT)
        
        # List container
        list_card = tk.Frame(self.content_frame, bg="#16213e")
        list_card.pack(fill=tk.BOTH, expand=True)
        
        # Scrollable list
        list_frame = tk.Frame(list_card, bg="#16213e")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.threats_listbox = tk.Listbox(list_frame, bg="#0f3460", fg="white",
                                         font=("Arial", 11), selectmode=tk.SINGLE,
                                         yscrollcommand=scrollbar.set, bd=0,
                                         highlightthickness=0, selectbackground="#00d9ff",
                                         selectforeground="#0a0e27")
        self.threats_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.threats_listbox.yview)
        
        # Action buttons
        btn_frame = tk.Frame(list_card, bg="#16213e")
        btn_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        tk.Button(btn_frame, text="Move to Quarantine",
                 command=self.move_threat_to_quarantine,
                 bg="#ff9800", fg="black", font=("Arial", 11, "bold"),
                 bd=0, padx=20, pady=10, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Delete",
                 command=self.delete_allowed_threat,
                 bg="#f44336", fg="white", font=("Arial", 11, "bold"),
                 bd=0, padx=20, pady=10, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        self.load_allowed_threats()
    
    def show_quarantine_tab(self):
        self.clear_content()
        self.highlight_nav(2)
        
        # Header
        tk.Label(self.content_frame, text="Quarantine",
                font=("Arial", 28, "bold"), bg="#0a0e27", fg="white").pack(anchor="w")
        
        # Toolbar
        toolbar = tk.Frame(self.content_frame, bg="#0a0e27")
        toolbar.pack(fill=tk.X, pady=20)
        
        tk.Button(toolbar, text="🔄 Refresh", command=self.load_quarantine_files,
                 bg="#16213e", fg="white", font=("Arial", 10),
                 bd=0, padx=20, pady=10, cursor="hand2").pack(side=tk.LEFT)
        
        # List container
        list_card = tk.Frame(self.content_frame, bg="#16213e")
        list_card.pack(fill=tk.BOTH, expand=True)
        
        list_frame = tk.Frame(list_card, bg="#16213e")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.quarantine_listbox = tk.Listbox(list_frame, bg="#0f3460", fg="white",
                                            font=("Arial", 11), selectmode=tk.SINGLE,
                                            yscrollcommand=scrollbar.set, bd=0,
                                            highlightthickness=0, selectbackground="#00d9ff",
                                            selectforeground="#0a0e27")
        self.quarantine_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.quarantine_listbox.yview)
        
        # Action buttons
        btn_frame = tk.Frame(list_card, bg="#16213e")
        btn_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        tk.Button(btn_frame, text="Move to Allowed",
                 command=self.move_quarantine_to_allowed,
                 bg="#4caf50", fg="white", font=("Arial", 11, "bold"),
                 bd=0, padx=20, pady=10, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Delete",
                 command=self.delete_quarantine_file,
                 bg="#f44336", fg="white", font=("Arial", 11, "bold"),
                 bd=0, padx=20, pady=10, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        self.load_quarantine_files()
    
    def show_history_tab(self):
        self.clear_content()
        self.highlight_nav(3)
        
        # Header
        tk.Label(self.content_frame, text="Protection History",
                font=("Arial", 28, "bold"), bg="#0a0e27", fg="white").pack(anchor="w")
        
        # Toolbar
        toolbar = tk.Frame(self.content_frame, bg="#0a0e27")
        toolbar.pack(fill=tk.X, pady=20)
        
        tk.Button(toolbar, text="🔄 Refresh", command=self.load_history,
                 bg="#16213e", fg="white", font=("Arial", 10),
                 bd=0, padx=20, pady=10, cursor="hand2").pack(side=tk.LEFT)
        
        # History container
        history_card = tk.Frame(self.content_frame, bg="#16213e")
        history_card.pack(fill=tk.BOTH, expand=True)
        
        self.history_text = scrolledtext.ScrolledText(history_card,
                                                     bg="#0f3460", fg="white",
                                                     font=("Consolas", 10),
                                                     wrap=tk.WORD, bd=0)
        self.history_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.load_history()
    
    def browse_path(self):
        path = filedialog.askdirectory()
        if path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)
    
    def quick_scan(self):
        if self.scanning:
            messagebox.showwarning("Scanning", "A scan is already in progress!")
            return
        
        self.scanning = True
        self.detected_threats = []
        self.results_text.delete(1.0, tk.END)
        self.quick_scan_btn.config(state=tk.DISABLED, text="Scanning...")
        
        thread = threading.Thread(target=self._perform_quick_scan)
        thread.daemon = True
        thread.start()
    
    def _perform_quick_scan(self):
        try:
            FileScanner.detected_threats = []
            self.results_text.insert(tk.END, "Starting Quick Scan...\n\n")
            
            for directory in FileScanner.QUICK_SCAN_DIRECTORIES:
                if directory and os.path.exists(directory):
                    self.results_text.insert(tk.END, f"Scanning: {directory}\n")
                    self.root.update_idletasks()
                    FileScanner.scan_directory(directory)
            
            self.detected_threats = FileScanner.detected_threats
            self.results_text.insert(tk.END, f"\n{'='*60}\n")
            self.results_text.insert(tk.END, f"Scan Complete!\n")
            self.results_text.insert(tk.END, f"Threats Found: {len(self.detected_threats)}\n")
            self.results_text.insert(tk.END, f"{'='*60}\n\n")
            
            if self.detected_threats:
                for idx, threat in enumerate(self.detected_threats, 1):
                    self.results_text.insert(tk.END, f"{idx}. {threat['file_path']}\n")
                    self.results_text.insert(tk.END, f"   Type: {threat['threat_type']}\n\n")
                
                # Show threat action window
                self.root.after(100, self.show_threat_action_window)
            else:
                self.results_text.insert(tk.END, "No threats detected. System is clean!\n")
        
        except Exception as e:
            self.results_text.insert(tk.END, f"\nError: {str(e)}\n")
        finally:
            self.scanning = False
            self.quick_scan_btn.config(state=tk.NORMAL, text="Start Quick Scan")
    
    def custom_scan(self):
        path = self.path_entry.get().strip()
        if not path:
            messagebox.showerror("Error", "Please enter a path to scan")
            return
        
        if not os.path.exists(path):
            messagebox.showerror("Error", "Path does not exist")
            return
        
        if self.scanning:
            messagebox.showwarning("Scanning", "A scan is already in progress!")
            return
        
        self.scanning = True
        self.detected_threats = []
        self.results_text.delete(1.0, tk.END)
        self.custom_scan_btn.config(state=tk.DISABLED, text="Scanning...")
        
        thread = threading.Thread(target=self._perform_custom_scan, args=(path,))
        thread.daemon = True
        thread.start()
    
    def _perform_custom_scan(self, path):
        try:
            FileScanner.detected_threats = []
            self.results_text.insert(tk.END, f"Scanning: {path}\n\n")
            
            if os.path.isdir(path):
                FileScanner.scan_directory(path)
            else:
                FileScanner.scan_file(path)
            
            self.detected_threats = FileScanner.detected_threats
            self.results_text.insert(tk.END, f"\n{'='*60}\n")
            self.results_text.insert(tk.END, f"Scan Complete!\n")
            self.results_text.insert(tk.END, f"Threats Found: {len(self.detected_threats)}\n")
            self.results_text.insert(tk.END, f"{'='*60}\n\n")
            
            if self.detected_threats:
                for idx, threat in enumerate(self.detected_threats, 1):
                    self.results_text.insert(tk.END, f"{idx}. {threat['file_path']}\n")
                    self.results_text.insert(tk.END, f"   Type: {threat['threat_type']}\n\n")
                
                # Show threat action window
                self.root.after(100, self.show_threat_action_window)
            else:
                self.results_text.insert(tk.END, "No threats detected!\n")
        
        except Exception as e:
            self.results_text.insert(tk.END, f"\nError: {str(e)}\n")
        finally:
            self.scanning = False
            self.custom_scan_btn.config(state=tk.NORMAL, text="Scan")
    
    def show_threat_action_window(self):
        if not self.detected_threats:
            return
        
        self.threat_window = tk.Toplevel(self.root)
        self.threat_window.title("Threats Detected")
        self.threat_window.geometry("700x500")
        self.threat_window.configure(bg="#0a0e27")
        self.threat_window.transient(self.root)
        
        # Header
        header = tk.Frame(self.threat_window, bg="#16213e")
        header.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(header, text=f"⚠️ {len(self.detected_threats)} Threats Detected",
                font=("Arial", 20, "bold"), bg="#16213e", fg="#ff9800").pack()
        tk.Label(header, text="Choose an action for each threat",
                font=("Arial", 11), bg="#16213e", fg="#b0b0b0").pack()
        
        # Scrollable threat list
        list_frame = tk.Frame(self.threat_window, bg="#0a0e27")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        canvas = tk.Canvas(list_frame, bg="#0a0e27", highlightthickness=0)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#0a0e27")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add each threat with action buttons
        for idx, threat in enumerate(self.detected_threats):
            threat_card = tk.Frame(scrollable_frame, bg="#16213e", relief=tk.FLAT)
            threat_card.pack(fill=tk.X, pady=10, padx=5)
            
            info_frame = tk.Frame(threat_card, bg="#16213e")
            info_frame.pack(fill=tk.X, padx=20, pady=(15, 10))
            
            tk.Label(info_frame, text=f"Threat {idx+1}:",
                    font=("Arial", 11, "bold"), bg="#16213e", fg="#ff9800").pack(anchor="w")
            tk.Label(info_frame, text=threat['file_path'],
                    font=("Arial", 9), bg="#16213e", fg="white",
                    wraplength=600, justify="left").pack(anchor="w", pady=2)
            tk.Label(info_frame, text=f"Type: {threat['threat_type']}",
                    font=("Arial", 9), bg="#16213e", fg="#b0b0b0").pack(anchor="w")
            
            btn_frame = tk.Frame(threat_card, bg="#16213e")
            btn_frame.pack(fill=tk.X, padx=20, pady=(5, 15))
            
            tk.Button(btn_frame, text="✅ Allow",
                     command=lambda t=threat: self.handle_threat_action(t, 'allow'),
                     bg="#4caf50", fg="white", font=("Arial", 10, "bold"),
                     bd=0, padx=15, pady=8, cursor="hand2").pack(side=tk.LEFT, padx=5)
            
            tk.Button(btn_frame, text="🚫 Quarantine",
                     command=lambda t=threat: self.handle_threat_action(t, 'quarantine'),
                     bg="#ff9800", fg="black", font=("Arial", 10, "bold"),
                     bd=0, padx=15, pady=8, cursor="hand2").pack(side=tk.LEFT, padx=5)
            
            tk.Button(btn_frame, text="🗑️ Delete",
                     command=lambda t=threat: self.handle_threat_action(t, 'delete'),
                     bg="#f44336", fg="white", font=("Arial", 10, "bold"),
                     bd=0, padx=15, pady=8, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bottom button
        bottom_frame = tk.Frame(self.threat_window, bg="#0a0e27")
        bottom_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Button(bottom_frame, text="Close",
                 command=self.threat_window.destroy,
                 bg="#16213e", fg="white", font=("Arial", 11),
                 bd=0, padx=30, pady=10, cursor="hand2").pack()
    
    def handle_threat_action(self, threat, action):
        try:
            if action == 'allow':
                FileScanner.allow_threat(threat['file_path'], threat['threat_type'])
                messagebox.showinfo("Success", f"Threat allowed:\n{threat['file_path']}")
            elif action == 'quarantine':
                FileScanner.quarantine_threat(threat['file_path'], threat['threat_type'])
                messagebox.showinfo("Success", f"Threat quarantined:\n{threat['file_path']}")
            elif action == 'delete':
                FileScanner.delete_threat(threat['file_path'])
                messagebox.showinfo("Success", f"Threat deleted:\n{threat['file_path']}")
            
            DatabaseManager.remove_threat_info(threat['file_path'])
            
            # Remove from detected threats list
            self.detected_threats.remove(threat)
            
            # Close window if all threats handled
            if not self.detected_threats and hasattr(self, 'threat_window'):
                self.threat_window.destroy()
        
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def load_allowed_threats(self):
        self.threats_listbox.delete(0, tk.END)
        threats = DatabaseManager.get_allowed_threats()
        
        if not threats:
            self.threats_listbox.insert(tk.END, "  No allowed threats")
            return
        
        for threat in threats:
            path = threat.get('allowed_file_path') or threat.get('file_path', 'Unknown')
            display = f"  [{threat['threat_type']}] {path}"
            self.threats_listbox.insert(tk.END, display)
        
        self.threats_data = threats
    
    def load_quarantine_files(self):
        self.quarantine_listbox.delete(0, tk.END)
        files = DatabaseManager.get_quarantine_files()
        
        if not files:
            self.quarantine_listbox.insert(tk.END, "  No quarantine files")
            return
        
        for file in files:
            path = file.get('quarantine_file_path') or file.get('file_path', 'Unknown')
            display = f"  [{file['threat_type']}] {path}"
            self.quarantine_listbox.insert(tk.END, display)
        
        self.quarantine_data = files
    
    def load_history(self):
        self.history_text.delete(1.0, tk.END)
        conn = DatabaseManager.get_connection()
        
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM Protection_History ORDER BY action_time DESC LIMIT 100")
                history = cursor.fetchall()
                
                if not history:
                    self.history_text.insert(tk.END, "No history available\n")
                else:
                    for entry in history:
                        self.history_text.insert(tk.END, f"{'='*60}\n")
                        self.history_text.insert(tk.END, f"Action: {entry['action']}\n")
                        self.history_text.insert(tk.END, f"File: {entry['file_path']}\n")
                        self.history_text.insert(tk.END, f"Type: {entry['threat_type']}\n")
                        self.history_text.insert(tk.END, f"Time: {entry['action_time']}\n")
                        self.history_text.insert(tk.END, "\n")
                
                cursor.close()
                conn.close()
            except Exception as e:
                self.history_text.insert(tk.END, f"Error: {str(e)}\n")
    
    def move_threat_to_quarantine(self):
        selection = self.threats_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a threat")
            return
        
        idx = selection[0]
        if hasattr(self, 'threats_data') and idx < len(self.threats_data):
            threat = self.threats_data[idx]
            if messagebox.askyesno("Confirm", "Move this threat to quarantine?"):
                try:
                    file_path = threat.get('allowed_file_path') or threat.get('file_path')
                    DatabaseManager.move_allowed_to_quarantine(threat['id'], file_path)
                    messagebox.showinfo("Success", "Moved to quarantine")
                    self.load_allowed_threats()
                except Exception as e:
                    messagebox.showerror("Error", str(e))
    
    def delete_allowed_threat(self):
        selection = self.threats_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a threat")
            return
        
        idx = selection[0]
        if hasattr(self, 'threats_data') and idx < len(self.threats_data):
            threat = self.threats_data[idx]
            if messagebox.askyesno("Confirm", "Delete this threat permanently?"):
                try:
                    DatabaseManager.delete_allowed_threat(threat['id'])
                    messagebox.showinfo("Success", "Threat deleted")
                    self.load_allowed_threats()
                except Exception as e:
                    messagebox.showerror("Error", str(e))
    
    def move_quarantine_to_allowed(self):
        selection = self.quarantine_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a file")
            return
        
        idx = selection[0]
        if hasattr(self, 'quarantine_data') and idx < len(self.quarantine_data):
            file = self.quarantine_data[idx]
            if messagebox.askyesno("Confirm", "Move this file to allowed?"):
                try:
                    DatabaseManager.move_quarantine_to_allowed(file['id'])
                    messagebox.showinfo("Success", "Moved to allowed")
                    self.load_quarantine_files()
                except Exception as e:
                    messagebox.showerror("Error", str(e))
    
    def delete_quarantine_file(self):
        selection = self.quarantine_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a file")
            return
        
        idx = selection[0]
        if hasattr(self, 'quarantine_data') and idx < len(self.quarantine_data):
            file = self.quarantine_data[idx]
            if messagebox.askyesno("Confirm", "Delete this file permanently?"):
                try:
                    DatabaseManager.delete_quarantine_threat(file['id'])
                    messagebox.showinfo("Success", "File deleted")
                    self.load_quarantine_files()
                except Exception as e:
                    messagebox.showerror("Error", str(e))

def main():
    # Show splash screen
    splash_root = tk.Tk()
    splash = SplashScreen(splash_root)
    splash_root.mainloop()
    
    # Show main application
    root = tk.Tk()
    app = AntivirusGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()