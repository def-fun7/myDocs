import os
import tkinter as tk
from tkinter import filedialog 
from .fileprocessor import FileProcessor
from .config import PROCESS_OPTIONS_A, PROCESS_OPTIONS_B

# --- 1. Checkbox Group Frame (Updated) ---

class CheckboxGroup(tk.LabelFrame):
    def __init__(self, master, title, options, run_callback):
        super().__init__(master, text=title, padx=10, pady=5)
        self.options = options
        self.checkbox_vars = {}
        self.run_callback = run_callback # The callback to run_process
        
        self.select_all_var = tk.BooleanVar(value=False)
        self.controls_enabled = True # Tracks if the group is globally disabled (by the master radio button)
        
        self._create_widgets()

    def _create_widgets(self):
        # Select All Checkbox (A1 or B1 equivalent)
        first_option_name = self.options[0] # This is A1 or B1
        first_option_var = tk.BooleanVar(value=False)
        self.checkbox_vars[first_option_name] = first_option_var
        
        # We handle A1/B1 logic slightly differently from the rest
        tk.Checkbutton(self, 
                       text=first_option_name, 
                       variable=first_option_var,
                       command=lambda: self._handle_exclusive_check(first_option_var) # Runs when A1/B1 is clicked
                       ).pack(anchor=tk.W)
        
        tk.Frame(self, height=1, bg="gray").pack(fill=tk.X, pady=5) # Separator
        
        # Individual Checkboxes (Start from index 1)
        for name in self.options[1:]:
            var = tk.BooleanVar(value=False)
            self.checkbox_vars[name] = var
            # Add a command to uncheck A1/B1 if any other option is selected
            tk.Checkbutton(self, 
                           text=name, 
                           variable=var,
                           command=lambda v=first_option_var: self._handle_sub_check(v)
                           ).pack(anchor=tk.W)

    def _handle_exclusive_check(self, exclusive_var):
        """Disables/enables other checkboxes when A1/B1 is checked."""
        if not self.controls_enabled:
            return

        is_checked = exclusive_var.get()
        
        # Disable/Enable all other checkboxes
        for name, var in self.checkbox_vars.items():
            if name != self.options[0]:
                if is_checked:
                    var.set(False) # Uncheck others
                self._set_state(name, tk.DISABLED if is_checked else tk.NORMAL)

    def _handle_sub_check(self, exclusive_var):
        """Ensures A1/B1 is unchecked when any other box is clicked."""
        if not self.controls_enabled:
            return
            
        exclusive_var.set(False)
        self._set_state(self.options[0], tk.NORMAL) # Ensure A1/B1 is enabled if a sub-option is selected

    def _set_state(self, option_name, state):
        """Helper to find and set the state of a specific checkbutton."""
        for child in self.winfo_children():
            if child.winfo_class() == 'Checkbutton' and child.cget('text') == option_name:
                child.config(state=state)
                return

    def set_group_state(self, state):
        """Sets the state of ALL controls in this group (used by the master radio button)."""
        self.controls_enabled = (state == tk.NORMAL)
        for child in self.winfo_children():
            # Exclude the separator frame
            if child.winfo_class() != 'Frame':
                 child.config(state=state)
# --- 2. Main Application Frame (The orchestrator) ---

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("myDocs")
        
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

        # Row 1-2: File Selection (unchanged)
        self._setup_file_selection(row_start=1)

        # Row 3: Master Radio Button (NEW)
        self.master_mode_var = tk.StringVar(value="individual") # 'all' or 'individual'
        self._setup_master_radio_buttons(row_start=3)
        
        # Row 4: Checkbox Groups (Moved down to Row 4)
        self.group_a = CheckboxGroup(self, "File Conversions", PROCESS_OPTIONS_A, self.run_process)
        self.group_a.grid(row=4, column=0, columnspan=1, padx=10, pady=5, sticky=tk.NSEW)
        
        self.group_b = CheckboxGroup(self, "JPG/JPEG Compression", PROCESS_OPTIONS_B, self.run_process)
        self.group_b.grid(row=4, column=2, columnspan=1, padx=10, pady=5, sticky=tk.NSEW)

        # Row 5: Run Control Row (Moved down to Row 5)
        self._setup_run_controls(row_start=5)

        # Row 6: Message Area (Moved down to Row 6)
        self.message_area = tk.Text(self, height=5, width=60, state=tk.DISABLED)
        self.message_area.grid(row=6, column=0, columnspan=3, padx=10, pady=(0, 10), sticky=tk.EW)

    def _setup_master_radio_buttons(self, row_start):
        frame = tk.Frame(self)
        frame.grid(row=row_start, column=0, columnspan=3, pady=(0, 10))
        
        # Radio button 1: Individual Selection (Normal mode)
        tk.Radiobutton(frame, 
                       text="Individual Selection Mode", 
                       variable=self.master_mode_var, 
                       value="individual", 
                       command=self._handle_master_mode).pack(side=tk.LEFT, padx=10)
                       
        # Radio button 2: Compress and Convert All (Master A1/B1 mode)
        tk.Radiobutton(frame, 
                       text="Compress and Convert All", 
                       variable=self.master_mode_var, 
                       value="all", 
                       command=self._handle_master_mode).pack(side=tk.LEFT, padx=10)

    def _handle_master_mode(self):
        """Disables/Enables groups and sets A1/B1 based on the radio button selection."""
        mode = self.master_mode_var.get()
        
        if mode == "all":
            # 1. Disable all checkbuttons in both groups
            self.group_a.set_group_state(tk.DISABLED)
            self.group_b.set_group_state(tk.DISABLED)
            
            # 2. Check the A1 and B1 variables manually (first option in each list)
            # This is non-visual, but ensures the options are sent to the processor
            self.group_a.checkbox_vars[PROCESS_OPTIONS_A[0]].set(True)
            self.group_b.checkbox_vars[PROCESS_OPTIONS_B[0]].set(True)
            
        else: # mode == "individual"
            # 1. Enable all checkbuttons in both groups
            self.group_a.set_group_state(tk.NORMAL)
            self.group_b.set_group_state(tk.NORMAL)
            
            # 2. Uncheck the master options
            self.group_a.checkbox_vars[PROCESS_OPTIONS_A[0]].set(False)
            self.group_b.checkbox_vars[PROCESS_OPTIONS_B[0]].set(False)
            

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
        SUPPORTED_EXTS = "*.jpg *.jpeg *.png *.webp *.bmp *.tiff *.pdf"
    
        file_paths = filedialog.askopenfilenames(
            title="Select one or more files to process",
            filetypes=[
                # This is the primary filter group
                ("Convertible & Compressible Files", SUPPORTED_EXTS),
                # General grouping for all supported image types
                ("All Image Files", "*.jpg *.jpeg *.png *.webp *.bmp *.tiff"),
                # Compressable
                ("Compressable Files", "*.jpg *.jpeg"),
                # Specific PDF entry
                ("PDF Documents", "*.pdf"),
                # Keep a general "All files" option
                ("All files", "*.*")
            ]
        )
        
        if file_paths:
            self.selected_files = list(file_paths)
            
            # Display logic: show the count if > 1, otherwise show the path
            if len(file_paths) > 1:
                display_text = f"{len(file_paths)} files selected."
            else:
                # We display the basename (just the file name) to keep the GUI clean
                display_text = os.path.basename(file_paths[0]) 
                
            self.file_path_label.config(text=display_text)
            self.log_message(f"Selected {len(file_paths)} files.")
        else:
            self.log_message("File selection cancelled.")
            self.selected_files = [] 
            self.file_path_label.config(text="No files selected")
                
    def run_process(self):
        # ... (Get input data)
        file_paths = self.selected_files
        separate_folders = self.separate_folders_var.get()
        
        # NEW: Check master mode for selected options
        if self.master_mode_var.get() == "all":
            # If "Compress and Convert All" is selected, force A1 and B1
            selected_options = [PROCESS_OPTIONS_A[0], PROCESS_OPTIONS_B[0]]
            self.log_message("*** Running in 'Compress and Convert All' Mode ***")
        else:
            # Use normal checkbox selection
            selected_options = self.get_selected_options()

        # ... (Clear log and hand off to processor - unchanged)
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