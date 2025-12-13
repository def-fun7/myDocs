import tkinter as tk
from tkinter import filedialog 

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("File Processor App")

        # --- MOVE THESE LINES TO THE START ---
        # Initialize variables for the widgets FIRST
        self.radio_var_1 = tk.StringVar(value="Option A1")
        self.radio_var_2 = tk.StringVar(value="Option B1")
        self.separate_folders_var = tk.BooleanVar(value=False)
        # -------------------------------------

        self.pack(fill=tk.BOTH, expand=True) 
        self.create_widgets()
        
        # Configure grid column weights for center alignment
        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1) 

    # ... (rest of the Application class remains the same)
    # ... (create_widgets, setup_radio_groups, select_files, etc.)
    
    def create_widgets(self):
        # --- Row 0: App Title ---
        title_label = tk.Label(self, 
                               text="File Processor App", 
                               font=("Arial", 16, "bold"))
        # Use columnspan to center the title across all columns
        title_label.grid(row=0, column=0, columnspan=3, pady=(10, 15))

        # --- Row 1: Select File Button ---
        select_button = tk.Button(self, text="Select File or Files", command=self.select_files)
        select_button.grid(row=1, column=0, columnspan=3, pady=5)
        
        # --- Row 2: File Path Display ---
        self.file_path_label = tk.Label(self, text="No files selected", wraplength=400)
        self.file_path_label.grid(row=2, column=0, columnspan=3, pady=(0, 10))

        # --- Row 3 & 4: Radio Button Groups ---
        self.setup_radio_groups(3)

        # --- Row 5: Checkbox ---
        self.separate_folders_check = tk.Checkbutton(self, 
                                                     text="Make separate folders", 
                                                     variable=self.separate_folders_var)
        self.separate_folders_check.grid(row=5, column=0, columnspan=3, pady=(10, 10))

        # --- Row 6: Run Button ---
        run_button = tk.Button(self, text="Run Process", bg="green", fg="white", 
                               command=self.run_process) # We'll fill this in later!
        run_button.grid(row=6, column=0, columnspan=3, pady=(5, 15), ipadx=20, ipady=5)

        # --- Row 7: Message Area ---
        self.message_area = tk.Text(self, height=5, width=60, state=tk.DISABLED)
        # Use sticky="ew" to make the Text widget stretch horizontally
        self.message_area.grid(row=7, column=0, columnspan=3, padx=10, pady=(0, 10), sticky=tk.EW)

    def setup_radio_groups(self, start_row):
        # Create a frame for the first radio group to visually group it
        group_frame_1 = tk.LabelFrame(self, text="Processing Type 1", padx=10, pady=5)
        group_frame_1.grid(row=start_row, column=0, columnspan=1, padx=10, pady=5, sticky=tk.NSEW)
        
        tk.Radiobutton(group_frame_1, text="Option A1", variable=self.radio_var_1, value="Option A1").pack(anchor=tk.W)
        tk.Radiobutton(group_frame_1, text="Option A2", variable=self.radio_var_1, value="Option A2").pack(anchor=tk.W)
        tk.Radiobutton(group_frame_1, text="Option A3", variable=self.radio_var_1, value="Option A3").pack(anchor=tk.W)

        # Create a frame for the second radio group
        group_frame_2 = tk.LabelFrame(self, text="Processing Type 2", padx=10, pady=5)
        group_frame_2.grid(row=start_row, column=2, columnspan=1, padx=10, pady=5, sticky=tk.NSEW)
        
        tk.Radiobutton(group_frame_2, text="Option B1", variable=self.radio_var_2, value="Option B1").pack(anchor=tk.W)
        tk.Radiobutton(group_frame_2, text="Option B2", variable=self.radio_var_2, value="Option B2").pack(anchor=tk.W)

    def select_files(self):
        # Placeholder for the file selection logic
        file_paths = filedialog.askopenfilenames(
            title="Select one or more files",
            filetypes=[("All files", "*.*"), ("Text files", "*.txt")]
        )
        if file_paths:
            # Update the label to show the selected files (or a count)
            if len(file_paths) == 1:
                display_text = file_paths[0]
            else:
                display_text = f"{len(file_paths)} files selected."
                
            self.file_path_label.config(text=display_text)
            self.selected_files = file_paths
            self.log_message(f"Selected {len(file_paths)} files.")
        else:
            self.log_message("File selection cancelled.")
            
    def run_process(self):
        # Placeholder for the main logic
        self.log_message("--- RUNNING PROCESS ---")
        self.log_message(f"Selected files: {getattr(self, 'selected_files', 'None')}")
        self.log_message(f"Radio Group 1: {self.radio_var_1.get()}")
        self.log_message(f"Radio Group 2: {self.radio_var_2.get()}")
        self.log_message(f"Separate Folders: {self.separate_folders_var.get()}")
        self.log_message("Process finished! (Logic implementation pending.)")
        
    def log_message(self, message):
        """Helper function to print messages to the text area."""
        self.message_area.config(state=tk.NORMAL)
        self.message_area.insert(tk.END, message + "\n")
        self.message_area.see(tk.END) # Scroll to the bottom
        self.message_area.config(state=tk.DISABLED)