from CTkMessagebox import CTkMessagebox
import keyboard
import webbrowser
import base64
import tempfile
import os
import customtkinter as ctk
import subprocess
import platform
if platform.system() == 'Linux':
    # Resolve "Xlib.error.DisplayConnectionError"
    subprocess.run(['xhost', '+'])
import areacalculator

class TabletAreaGUI:
    """GUI for tablet area calculator application"""
    
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("OsuAreaCalculator")
        self.root.geometry("400x420")
        self.root.resizable(False,False)
        self.tracking = False
        self.setup_gui()
        self.setup_bindings()

        # Create temp file for icon
        icon_file = tempfile.NamedTemporaryFile(delete=False, suffix='.ico')
        icon_file.write(base64.b64decode(areacalculator.ICON))
        icon_file.close()
            
        # Set window icon
        if platform.system() == 'Windows':
            self.root.iconbitmap(icon_file.name)
            
        # Clean up temp file
        os.unlink(icon_file.name)

    def setup_bindings(self):
        """Setup keyboard shortcuts"""
        keyboard.on_press_key('f5', lambda _: self.start_tracking())
        keyboard.on_press_key('f6', lambda _: self.stop_tracking())
        
    def setup_gui(self):
        """Initialize GUI components"""
        # Main container
        container = ctk.CTkFrame(self.root)
        container.pack(fill=ctk.BOTH, expand=True)

        # Dimensions Frame
        dim_frame = ctk.CTkFrame(container)
        dim_frame.pack(fill=ctk.X, padx=10, pady=10)
        dim_frame.configure(fg_color="#333333")

        dim_label = ctk.CTkLabel(dim_frame, text="Tablet Dimensions", font=("Arial", 14, "bold"))
        dim_label.pack(anchor='w', padx=5,)

        # Grid layout for dimensions
        width_frame = ctk.CTkFrame(dim_frame)
        width_frame.configure(fg_color="#333333")
        width_frame.pack(fill=ctk.X, padx=5, pady=5)
        width_label = ctk.CTkLabel(width_frame, text="Width (mm): ", font=("Arial", 12, "bold"))
        width_label.pack(side=ctk.LEFT, padx=5)
        self.width_entry = ctk.CTkEntry(width_frame)
        self.width_entry.pack(side=ctk.LEFT)
        def on_width_enter(event):
            self.height_entry.focus()
        self.width_entry.bind('<Return>', on_width_enter)

        height_frame = ctk.CTkFrame(dim_frame)
        height_frame.configure(fg_color="#333333")
        height_frame.pack(fill=ctk.X, padx=5, pady=5)
        height_label = ctk.CTkLabel(height_frame, text="Height (mm):", font=("Arial", 12, "bold"))
        height_label.pack(side=ctk.LEFT, padx=5)
        self.height_entry = ctk.CTkEntry(height_frame)
        self.height_entry.pack(side=ctk.LEFT)
        def on_height_enter(event):
            self.set_dimensions()
        self.height_entry.bind('<Return>', on_height_enter)
       
        """
        Preset dimensions for areas dropdown:
        - Reference for Wacom Area: https://docs.google.com/spreadsheets/d/125LNzGmidy1gagwYUt12tRhrNdrWFHhWon7kxWY7iWU/edit?gid=854129046#gid=854129046
        - Thanks 5WC PH for the list of other tablet areas
        - Thanks @peroroo for datascraping the tabletInfo.txt file
        
        - Preset dimensions for areas dropdown
        """
        preset_dimensions = {}
        preset_file = os.path.join(os.path.dirname(__file__), "tabletInfo.txt")
        if os.path.exists(preset_file):
            with open(preset_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    try:
                        if line.endswith(","):
                            line = line[:-1]
                            name, dims = line.split(":", 1)
                            dims = dims.strip()
                            if dims.startswith("(") and dims.endswith(")"):
                                dims = dims[1:-1]
                                width, height = map(float, dims.split(","))
                                preset_dimensions[name.strip().strip('"')] = (width, height)
                    except Exception:
                        continue
        else:
            preset_dimensions = {
            "Wacom 471/472/480/490/4100": (152, 95),
            "Wacom 672/680/690/6100": (216, 135),
            "Wacom 470": (147.2, 92),
            "Wacom 670": (216.48, 137),
            "XP-Pen G640": (152.4, 101.6),
            "XP-Pen G640s": (165, 103),
            "XP-Pen G430": (101.6, 76.2),
            "Huion H420": (101.6, 63.5),
            "Huion H640P": (152.4, 95.25),
            "Veikk 640": (152.4, 101.6),
            }

        dim_frame = ctk.CTkFrame(dim_frame)
        dim_frame.pack(fill="x", padx=10, pady=10)

        search_entry = ctk.CTkEntry(
            dim_frame,
            placeholder_text="Search preset...",
            width=250
        )
        search_entry.pack(pady=(0, 5), fill="x")


        self.preset_var = ctk.StringVar(value="Select Preset")
        self.preset_menu = ctk.CTkOptionMenu(
            dim_frame,
            variable=self.preset_var,
            values=list(preset_dimensions.keys()),  # Initial values
            command=lambda selected: self.set_preset_dimensions(selected, preset_dimensions),
            fg_color="#FF7EB8",
            button_color="#FF7EB8",
            dropdown_fg_color="#FF7EB8",
            width=250
        )
        self.preset_menu.pack(pady=(0, 10), fill="x")
        def update_dropdown(event=None):
            search_term = search_entry.get().lower()
    
            filtered = [
                key for key in preset_dimensions.keys()
                if search_term in key.lower()
            ]
    
            if not filtered:
                filtered = ["No match"]
                self.preset_menu.configure(values=filtered)
                self.preset_var.set("No match")
            else:
                self.preset_menu.configure(values=filtered)
                self.preset_var.set(filtered[0])
        search_entry.bind("<KeyRelease>", update_dropdown)
        search_entry.bind("<FocusIn>", lambda e: self.preset_var.set(""))


        # Status
        self.status_label = ctk.CTkLabel(container, text="Enter your tablet dimensions and click Set.\n" "\n" "You need to provide the full dimensions of your tablet's active area.", font=("Arial", 12, "bold"))
        self.status_label.pack(pady=10, padx=10)
        
        # Buttons
        btn_frame = ctk.CTkFrame(container)
        btn_frame.pack(pady=10)
        btn_frame.configure(fg_color="#2B2B2B")
        self.set_btn = ctk.CTkButton(btn_frame, text="Set", font=("Arial", 14, "bold"),
                                 command=self.set_dimensions, fg_color="#FF7EB8")
        self.set_btn.pack(side=ctk.LEFT, padx=5)
        
        self.start_btn = ctk.CTkButton(btn_frame, text="Start (F5)", font=("Arial", 14, "bold"), 
                                   command=self.start_tracking,
                                   state=ctk.DISABLED, fg_color="#FF7EB8")
        self.start_btn.pack(side=ctk.LEFT, padx=5)
        
        # Instructions
        self.show_instructions(container)
        
        # Credits
        self.my_credits(container)
    
    def create_entry(self, parent, label, row):
        """Create labeled entry field"""
        label_widget = ctk.CTkLabel(parent, text=label)
        label_widget.grid(row=row, column=0, padx=5, pady=5)
        entry = ctk.CTkEntry(parent)
        entry.grid(row=row, column=1, padx=5, pady=5)
        return entry
    
    def show_instructions(self, parent):
        """Display usage instructions"""
        instructions = (
            "1. Enter tablet dimensions\n"
            "2. Click Set buttom\n"
            "3. Set your tablet to full area\n"
            "4. Press F5 to start tracking\n"
            "5. Press F6 to stop and show results\n"
            "\n"
            "YOUR GAME NEEDS TO BE IN BORDERLESS FULLSCREEN TO WORK\n" 
        )
        instructions_label = ctk.CTkLabel(parent, text=instructions, justify=ctk.LEFT, wraplength=380, anchor='n', font=("Arial", 12, "bold"))
        instructions_label.pack(pady=10, padx=10)
    
    def my_credits(self, parent):
        """Display credits with clickable link"""
        credits = ctk.CTkLabel(parent, text="Made by KeepGrindingOsu", justify=ctk.LEFT, font=("Helvetica", 10, "bold"), text_color="#FF8EE6", cursor="hand2")
        credits.pack(pady=1)
        credits.bind("<Button-1>", lambda e: self.open_link("https://x.com/KeepGrindingOsu"))

    def display_message(self, message, width, height):
        message_window = ctk.CTkToplevel()
        message_window.title("Coordinate Resolution Info")
        text = ctk.CTkTextbox(message_window, width=width, height=height, font=("Helvetica", 20), wrap='word')
        text.pack(padx=20, pady=20)
        text.insert('0.0', message)

    def open_link(self, url):
        """Open a web link in the default browser"""
        webbrowser.open_new(url)

    def set_dimensions(self):
        """Set tablet dimensions and enable tracking"""
        try:
            width = float(self.width_entry.get())
            height = float(self.height_entry.get())

            if width <= 0 or height <= 0:
                raise ValueError("Dimensions must be positive")
                
            if areacalculator.set_tablet_dimensions(width, height):
                self.status_label.configure(text="Dimensions set. Press F5 to start")
                self.start_btn.configure(state=ctk.NORMAL)
            else:
                raise RuntimeError("Failed to set dimensions")
                
        except ValueError as e:
            CTkMessagebox(title="Error", message=f"Invalid dimensions: You should put numbers there xD")
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Unexpected error: {e}")
    
    def start_tracking(self):
        """Start tracking cursor movement"""
        if not self.tracking:
            self.tracking = True
            self.status_label.configure(text="Tracking... Press F6 to stop")
            self.root.iconify()
            areacalculator.track_cursor_movement(self)
    
    def stop_tracking(self):
        """Stop tracking and show results"""
        if self.tracking:
            self.tracking = False
            self.status_label.configure(text="Tracking stopped. Showing results...")
            self.root.deiconify()
    
    def set_preset_dimensions(self, selected_key, preset_dict):
        """Set dimensions based on selected preset"""
        if selected_key in preset_dict:
            width, height = preset_dict[selected_key]
            self.width_entry.delete(0, 'end')
            self.width_entry.insert(0, str(width))
            self.height_entry.delete(0, 'end')
            self.height_entry.insert(0, str(height))
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = TabletAreaGUI()
    app.run()
   
    if platform.system() == 'Linux':
        # Resetting the access control
        subprocess.run(['xhost', '-'])
