import tkinter as tk
from tkinter import filedialog 
from .logic.fileprocessor import FileProcessor
from config import PROCESS_OPTIONS_A, PROCESS_OPTIONS_B

class CheckboxGroup(tk.LabelFrame):
    def __init__(self, master, title, options, on_select_all_callback):
        super().__init__(master, text=title, padx=10, pady=5)
        self.options = options
        self.checkbox_vars = {}
        
        # Initialize variables
        self.select_all_var = tk.BooleanVar(value=False)
        self.on_select_all_callback = on_select_all_callback
        
        self._create_widgets()

    def _create_widgets(self):
        # Select All Checkbox
        tk.Checkbutton(self, text="Select All", variable=self.select_all_var,
                       command=self._toggle_all).pack(anchor=tk.W)

        # Individual Checkboxes
        for name in self.options:
            var = tk.BooleanVar(value=False)
            self.checkbox_vars[name] = var
            tk.Checkbutton(self, text=name, variable=var).pack(anchor=tk.W)
            
    def _toggle_all(self):
        """Checks or unchecks all individual checkboxes."""
        set_value = self.select_all_var.get()
        for var in self.checkbox_vars.values():
            var.set(set_value)

# --- 2. Main Application Frame (The orchestrator) ---

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("File Processor App")
        
        # --- Control Variables ---
        self.separate_folders_var = tk.BooleanVar(value=False) 
        self.selected_files = []
        
        self.file_processor = FileProcessor(self) # Pass 'self' (the GUI instance) to the processor
        
        self.pack(fill=tk.BOTH, expand=True) 
        self._configure_grid()
        self._create_widgets()


    def _configure_grid(self):
        # Configure grid column weights for center alignment
        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1) 

    def _create_widgets(self):
        # Row 0: App Title
        tk.Label(self, text="File Processor App", font=("Arial", 16, "bold")).grid(
            row=0, column=0, columnspan=3, pady=(10, 15))

        # Row 1-2: File Selection
        self._setup_file_selection(row_start=1)

        # Row 3: Checkbox Groups (Using the new CheckboxGroup class)
        self.group_a = CheckboxGroup(self, "Processing Type 1", PROCESS_OPTIONS_A, self.run_process)
        self.group_a.grid(row=3, column=0, columnspan=1, padx=10, pady=5, sticky=tk.NSEW)
        
        self.group_b = CheckboxGroup(self, "Processing Type 2", PROCESS_OPTIONS_B, self.run_process)
        self.group_b.grid(row=3, column=2, columnspan=1, padx=10, pady=5, sticky=tk.NSEW)

        # Row 4: Run Control Row
        self._setup_run_controls(row_start=4)

        # Row 5: Message Area
        self.message_area = tk.Text(self, height=5, width=60, state=tk.DISABLED)
        self.message_area.grid(row=5, column=0, columnspan=3, padx=10, pady=(0, 10), sticky=tk.EW)
        
    def _setup_file_selection(self, row_start):
        # Select Button
        select_button = tk.Button(self, text="Select File or Files", command=self.select_files)
        select_button.grid(row=row_start, column=0, columnspan=3, pady=5)
        
        # File Path Display
        self.file_path_label = tk.Label(self, text="No files selected", wraplength=400)
        self.file_path_label.grid(row=row_start + 1, column=0, columnspan=3, pady=(0, 10))

    def _setup_run_controls(self, row_start):
        # Separate Folders Checkbox
        tk.Checkbutton(self, 
                       text="Make separate folders", 
                       variable=self.separate_folders_var).grid(
            row=row_start, column=0, columnspan=2, padx=(10, 0), pady=(10, 15), sticky=tk.W)

        # Run Button
        tk.Button(self, text="Run Process", bg="green", fg="white", 
                  command=self.run_process).grid(
            row=row_start, column=2, pady=(10, 15), padx=10, sticky=tk.E) 

    # --- Logic Methods ---

    def get_selected_options(self):
        """Combines selected options from both checkbox groups."""
        selected = []
        # Get selections from Group A
        for name, var in self.group_a.checkbox_vars.items():
            if var.get():
                selected.append(name)
        # Get selections from Group B
        for name, var in self.group_b.checkbox_vars.items():
            if var.get():
                selected.append(name)
        return selected

    def select_files(self):
        file_paths = filedialog.askopenfilenames(
            title="Select one or more files",
            filetypes=[("All files", "*.*"), ("Text files", "*.txt")]
        )
        # ... (rest of select_files remains the same)
        if file_paths:
            self.selected_files = list(file_paths)
            display_text = f"{len(file_paths)} files selected." if len(file_paths) > 1 else file_paths[0]
            self.file_path_label.config(text=display_text)
            self.log_message(f"Selected {len(file_paths)} files.")
        else:
            self.log_message("File selection cancelled.")
            self.selected_files = [] 
            
    def run_process(self):
        # 1. Gather all necessary input data
        file_paths = self.selected_files
        selected_options = self.get_selected_options()
        separate_folders = self.separate_folders_var.get()

        # 2. Clear the log area and start the process in the background
        self.message_area.config(state=tk.NORMAL)
        self.message_area.delete(1.0, tk.END) # Clear previous log
        self.message_area.config(state=tk.DISABLED)

        # 3. Hand off the task to the processor
        self.file_processor.run_all(file_paths, selected_options, separate_folders)
            
    def log_message(self, message):
        """Helper function to print messages to the text area."""
        self.message_area.config(state=tk.NORMAL)
        self.message_area.insert(tk.END, message + "\n")
        self.message_area.see(tk.END) 
        self.message_area.config(state=tk.DISABLED)