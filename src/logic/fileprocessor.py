import os
import shutil
# import logging # Good idea for later

class FileProcessor:
    def __init__(self, gui_app):
        # Store a reference to the GUI instance for logging/updating status
        self.gui = gui_app
        
        # Define the available processing steps (mapping option names to methods)
        self.processing_map = {
            "Option A1": self._process_a1,
            "Option A2": self._process_a2,
            "Option A3": self._process_a3,
            "Option B1": self._process_b1,
            "Option B2": self._process_b2,
        }

    def run_all(self, file_paths, selected_options, separate_folders):
        """
        The main method called by the GUI's 'Run Process' button.
        """
        if not file_paths:
            self.gui.log_message("ERROR: No files selected. Processing aborted.")
            return

        if not selected_options:
            self.gui.log_message("WARNING: No processing options selected. Nothing to do.")
            return
            
        self.gui.log_message(f"Starting process on {len(file_paths)} files...")

        # Find the actual methods to run based on the selected option names
        methods_to_run = [self.processing_map[opt] for opt in selected_options if opt in self.processing_map]
        
        for file_path in file_paths:
            self.process_single_file(file_path, methods_to_run, separate_folders)
            
        self.gui.log_message("\n--- ALL PROCESSING COMPLETE ---")


    def process_single_file(self, file_path, methods_to_run, separate_folders):
        """Handles the processing steps for an individual file."""
        self.gui.log_message(f"--> Processing file: {os.path.basename(file_path)}")
        
        # 1. Determine output location (implementation depends on 'separate_folders')
        # For simplicity now, we just log it.
        if separate_folders:
            self.gui.log_message("    (Output will be in a separate directory.)")
        
        # 2. Run all selected processing methods on the file
        for method in methods_to_run:
            try:
                # We assume each method returns a status message
                status = method(file_path) 
                self.gui.log_message(f"    - {method.__name__}: {status}")
            except Exception as e:
                self.gui.log_message(f"    - ERROR in {method.__name__}: {e}")

    # --- PROCESSING METHODS (The actual work is done here) ---

    def _process_a1(self, file_path):
        """Example: Simple file operation, like reading the first line."""
        with open(file_path, 'r') as f:
            first_line = f.readline().strip()
        return f"Read first line: '{first_line[:20]}...'"
        
    def _process_a2(self, file_path):
        """Example: Simulating a modification."""
        return "Simulated text cleaning."
        
    def _process_a3(self, file_path):
        """Example: Simulating a failure or error."""
        # raise ValueError("Simulated network connection failure.")
        return "Simulated image conversion."

    def _process_b1(self, file_path):
        """Example: Simulating a data export."""
        return "Simulated data export to CSV."

    def _process_b2(self, file_path):
        """Example: Another simulated modification."""
        return "Simulated file rename/move."