import os
import sys
import shutil
from PIL import Image
from pdf2image import convert_from_path # Requires Poppler installation

class FileProcessor:
    def __init__(self, gui_app):
        self.gui = gui_app
        
        # --- NEW: Set up the base output directory when the processor initializes ---
        self.APP_ROOT = self._get_app_root_dir()
        self.OUTPUT_BASE_DIR = os.path.join(self.APP_ROOT, 'myDocs')
        os.makedirs(self.OUTPUT_BASE_DIR, exist_ok=True) # Create 'myDocs' if it doesn't exist
        
        self.TARGET_SIZES = {
            "250 KB": 250 * 1024,
            "500 KB": 500 * 1024,
            "1 MB": 1 * 1024 * 1024,
            "5 MB": 5 * 1024 * 1024,
        }
        
        # Mapping selected option names to their methods (UPDATED)
        self.processing_map = {
            "A1: Convert All (Image to all types, PDF to JPEG)": self._conversion_process_entry,
            "A2: Convert Image/PDF to PDF": self._single_target_to_pdf,
            "A3: Convert Image/PDF to PNG": self._single_target_to_png,
            "A4: Convert Image/PDF to JPG/JPEG": self._single_target_to_jpeg,
            "A5: Convert Image/PDF to WebP": self._single_target_to_webp,
            "A6: Convert Image/PDF to BMP": self._single_target_to_bmp,
            "A7: Convert Image/PDF to TIFF": self._single_target_to_tiff,
            
            "B1: Compress to All Target Sizes (250kb, 500kb, 1MB, 5MB)": self._compress_all_sizes_entry,
            "B2: Compress to < 250 KB": lambda fp, od, sf: self._compress_to_size_entry(fp, od, sf, "250 KB"),
            "B3: Compress to < 500 KB": lambda fp, od, sf: self._compress_to_size_entry(fp, od, sf, "500 KB"),
            "B4: Compress to < 1 MB": lambda fp, od, sf: self._compress_to_size_entry(fp, od, sf, "1 MB"),
            "B5: Compress to < 5 MB": lambda fp, od, sf: self._compress_to_size_entry(fp, od, sf, "5 MB"),
        }
        # List of all supported image extensions
        self.IMAGE_EXTS = ['jpg', 'jpeg', 'png', 'webp', 'bmp', 'tiff']
    def _get_app_root_dir(self):
        """Finds the directory where the main application script (main.py) is located."""
        # Cleaned up method, relies only on sys.argv[0]
        return os.path.dirname(os.path.abspath(sys.argv[0]))
    # --- CORE CONVERSION FUNCTIONS ---

    def _img_to_img(self, input_path, base_output_dir, target_format, separate_folders):
        """Converts one image file to another image format, including WebP."""
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        
        # New Logic: If Separate Folders is ON, create an extension subfolder
        if separate_folders:
            final_dest_dir = os.path.join(base_output_dir, target_format.lower())
            os.makedirs(final_dest_dir, exist_ok=True)
        else:
            final_dest_dir = base_output_dir

        output_path = os.path.join(final_dest_dir, f"{base_name}.{target_format.lower()}")
        if os.path.exists(output_path):
            return f"Skipped. Target file already exists: {os.path.basename(output_path)}"

        try:
            img = Image.open(input_path).convert("RGB") # Use RGB for safety
            # Pillow uses 'jpeg' for both .jpg and .jpeg, and 'webp' for .webp
            pillow_format = 'jpeg' if target_format in ('jpg', 'jpeg') else target_format
            
            img.save(output_path, pillow_format)
            return f"Converted to {target_format.upper()} at {output_path}"
        except Exception as e:
            return f"Failed to convert to {target_format.upper()}: {e}"

    def _img_to_pdf(self, input_path, base_output_dir, separate_folders):
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        
        if separate_folders:
            final_dest_dir = os.path.join(base_output_dir, 'pdf') # Target is 'pdf'
            os.makedirs(final_dest_dir, exist_ok=True)
        else:
            final_dest_dir = base_output_dir

        output_path = os.path.join(final_dest_dir, f"{base_name}.pdf")

        if os.path.exists(output_path):
            return f"Skipped. Target file already exists: {os.path.basename(output_path)}"

        try:
            img = Image.open(input_path)
            # Ensure proper conversion for PDF saving
            pdf = img.convert("RGB") 
            pdf.save(output_path, save_all=True) # save_all=True is useful for multi-page TIFFs
            return f"Converted image to PDF at {output_path}"
        except Exception as e:
            return f"Failed to convert image to PDF: {e}"

    def _pdf_to_img(self, input_path, base_output_dir, target_format='jpeg', separate_folders=False): # <-- ADDED ARG
        # ...
        
        # New Logic: If Separate Folders is ON, create an extension subfolder
        if separate_folders:
            final_dest_dir = os.path.join(base_output_dir, target_format.lower()) # Target is 'jpeg', 'png', etc.
            os.makedirs(final_dest_dir, exist_ok=True)
        else:
            final_dest_dir = base_output_dir
            
        try:
            # Use 'poppler_path' argument if poppler is not in your system PATH
            pdfs = convert_from_path(input_path)
        except Exception as e:
            return f"PDF conversion failed (Is Poppler installed?): {e}"

        results = []
        for i, pdf in enumerate(pdfs):
            # Output file name includes page number for multi-page PDFs
            output_name = f"{base_output_dir}_page_{i+1}.{target_format.lower()}"
            output_path = os.path.join(base_output_dir, output_name)
            
            try:
                if os.path.exists(output_path):
                    results.append(f"Page {i+1} skipped (exists).")
                    continue
                
                pdf.save(output_path, target_format)
                results.append(f"Page {i+1} converted to {target_format.upper()}.")
            except Exception as e:
                results.append(f"Page {i+1} failed conversion: {e}")
                
        return f"PDF to {target_format.upper()} finished. Details: {', '.join(results)}"


    # In logic/fileprocessor.py (add these new methods)

    # --- SINGLE TARGET CONVERSION WRAPPERS ---

    def _convert_to_target(self, file_path, output_dir, target_format, separate_folders):
        """Generic wrapper to handle single-target conversion logic."""
        extension = os.path.splitext(file_path)[-1].lower().strip('.')
        results = []

        if extension in self.IMAGE_EXTS:
            if target_format == 'pdf':
                results.append(self._img_to_pdf(file_path, output_dir, separate_folders))
            else:
                results.append(self._img_to_img(file_path, output_dir, target_format, separate_folders))
        elif extension == 'pdf':
            # PDFs can only be converted to images (or PDF-to-PDF which is usually a copy, ignored here)
            if target_format in self.IMAGE_EXTS:
                results.append(self._pdf_to_img(file_path, output_dir, target_format))
            else:
                return f"Skipped: PDF cannot be converted to {target_format.upper()}."
        else:
            return f"Skipped: Unsupported source extension '{extension}'."
            
        return "\n    ".join(results)

    # These methods map directly to the checkboxes:
    def _single_target_to_pdf(self, file_path, output_dir, separate_folders):
        return self._convert_to_target(file_path, output_dir, 'pdf', separate_folders)

    def _single_target_to_png(self, file_path, output_dir, separate_folders):
        return self._convert_to_target(file_path, output_dir, 'png', separate_folders)

    def _single_target_to_jpeg(self, file_path, output_dir, separate_folders):
        return self._convert_to_target(file_path, output_dir, 'jpeg', separate_folders)

    def _single_target_to_webp(self, file_path, output_dir, separate_folders):
        return self._convert_to_target(file_path, output_dir, 'webp', separate_folders)
        
    def _single_target_to_bmp(self, file_path, output_dir, separate_folders):
        return self._convert_to_target(file_path, output_dir, 'bmp', separate_folders)
        
    def _single_target_to_tiff(self, file_path, output_dir, separate_folders):
        return self._convert_to_target(file_path, output_dir, 'tiff', separate_folders)
        
    # --- The A1 Conversion Entry is simplified but still works: ---
    
    def _conversion_process_entry(self, file_path, output_dir, separate_folders ):
        """
        The main handler for 'Option A1' - manages all conversions for a single file.
        This remains the 'Convert All' option.
        """
        extension = os.path.splitext(file_path)[-1].lower().strip('.')
        
        if extension in self.IMAGE_EXTS:
            return self._image_conversion_suite(file_path, output_dir, extension, separate_folders)
        elif extension == 'pdf':
            return self._pdf_conversion_suite(file_path, output_dir)
        else:
            return f"Skipped: Unsupported extension '{extension}' for conversion."
    # --- DEDICATED SUITES ---
    def _image_conversion_suite(self, file_path, output_dir, current_ext, separate_folders):
        """Manages all required conversions for an image file."""
        results = []
        
        # Convert to other image types (excluding self)
        target_formats = [ext for ext in ['png', 'jpeg', 'webp', 'bmp', 'tiff'] if ext != current_ext]
        for target_format in target_formats:
            results.append(self._img_to_img(file_path, output_dir, target_format, separate_folders))
            
        # Convert to PDF
        results.append(self._img_to_pdf(file_path, output_dir, separate_folders))
        
        return "\n    ".join(results)

    def _pdf_conversion_suite(self, file_path, output_dir):
        """Manages all required conversions for a PDF file."""
        results = []
        
        # PDF to image conversion
        results.append(self._pdf_to_img(file_path, output_dir, target_format='jpeg' ))
        
        return "\n    ".join(results)
    
    # In logic/fileprocessor.py

    # Old method was named _move_original_file
    def _copy_original_file(self, file_path, base_output_dir, separate_folders):
        """Copies the original file into the same output directory."""
        
        # 1. Determine the exact destination directory path
        if separate_folders:
            extension = os.path.splitext(file_path)[-1].lower().strip('.')
            # When separate_folders is True, the output_dir passed in is myDocs/FILE_NAME_NO_EXT/
            # We append the extension subfolder (e.g., myDocs/FILE_NAME_NO_EXT/png/)
            final_dest_dir = os.path.join(base_output_dir, extension)
            os.makedirs(final_dest_dir, exist_ok=True)
        else:
            # When separate_folders is False, the output_dir passed in is myDocs/EXTENSION/
            final_dest_dir = base_output_dir
        
        # 2. Determine the full destination path (including file name)
        file_name = os.path.basename(file_path)
        final_dest_path = os.path.join(final_dest_dir, file_name)
        
        # 3. Check for existence and copy (The new part!)
        try:
            if os.path.exists(final_dest_path):
                return f"Skipped: Original file copy already exists in {os.path.basename(final_dest_dir)}"
            
            shutil.copy2(file_path, final_dest_path) # Copy to the final path
            return f"Copied original file to {os.path.basename(final_dest_dir)}"
            
        except Exception as e:
            return f"Failed to copy original file: {e}"
        
    # In logic/fileprocessor.py (add these new methods)

    # --- CORE COMPRESSION ALGORITHM ---
    
    def _compress_file(self, file_path, output_dir, size_key, separate_folders):
        """
        Attempts to compress an image to a target file size using iterative quality reduction.
        Currently focuses on JPEG as it supports compression quality.
        """
        extension = os.path.splitext(file_path)[-1].lower().strip('.')
        target_bytes = self.TARGET_SIZES[size_key]
        
        if extension not in ('jpg', 'jpeg'):
            return f"Skipped: Compression logic only implemented for JPG/JPEG."
        
        # 1. Determine Output Path (Reusing the subfolder logic)
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        
        if separate_folders:
            final_dest_dir = os.path.join(output_dir, 'compressed') # Use a generic 'compressed' subfolder
            os.makedirs(final_dest_dir, exist_ok=True)
        else:
            final_dest_dir = output_dir

        output_path = os.path.join(final_dest_dir, f"{base_name}_comp_{size_key.replace(' ', '')}.jpg")
        
        if os.path.exists(output_path):
            return f"Skipped. Target compressed file already exists: {os.path.basename(output_path)}"

        # 2. Iterative Compression
        try:
            img = Image.open(file_path).convert('RGB')
            quality = 90
            
            while quality >= 10:
                img.save(output_path, 'jpeg', quality=quality)
                current_size = os.path.getsize(output_path)
                
                if current_size <= target_bytes:
                    return f"Successfully compressed to {size_key} at Q={quality} ({round(current_size / 1024)} KB)"
                
                quality -= 10 # Drop quality and try again
                
            # If the loop finishes without success
            os.remove(output_path) # Clean up the largest failed attempt
            return f"Failed to compress to {size_key}. Smallest size achieved was {round(current_size / 1024)} KB."

        except Exception as e:
            return f"Compression failed: {e}"

    # --- ENTRY POINTS (Called by processing_map) ---
    
    def _compress_to_size_entry(self, file_path, output_dir, separate_folders, size_key):
        """Entry method for B2, B3, B4, B5 (single target size)."""
        return self._compress_file(file_path, output_dir, size_key, separate_folders)

    def _compress_all_sizes_entry(self, file_path, output_dir, separate_folders):
        """Entry method for B1 (all target sizes)."""
        results = []
        
        # Sort by largest size first for efficiency (since we create a new file each time)
        for size_key in reversed(list(self.TARGET_SIZES.keys())):
            results.append(self._compress_file(file_path, output_dir, size_key, separate_folders))
            
        return "\n    ".join(results)
    
    # --- run_all and process_single_file will need updates next ---
    # (The following code replaces the run_all and process_single_file from before)

    def run_all(self, file_paths, selected_options, separate_folders):
        # ... (Same as before, checks for files/options)
        if not file_paths:
            self.gui.log_message("ERROR: No files selected. Processing aborted.")
            return

        if not selected_options:
            self.gui.log_message("WARNING: No processing options selected. Nothing to do.")
            return
            
        self.gui.log_message(f"Starting process on {len(file_paths)} files...")

        methods_to_run = [self.processing_map[opt] for opt in selected_options if opt in self.processing_map]
        
        for file_path in file_paths:
            self.process_single_file(file_path, methods_to_run, separate_folders)
            
        self.gui.log_message("\n--- ALL PROCESSING COMPLETE ---")


    def process_single_file(self, file_path, methods_to_run, separate_folders):
        self.gui.log_message(f"--> Processing file: {os.path.basename(file_path)}")
        
        # 1. DETERMINE OUTPUT DIRECTORY (Implements Point 3 Logic)
        extension = os.path.splitext(file_path)[-1].lower().strip('.')
        output_dir = self.OUTPUT_BASE_DIR # Base is always 'myDocs'
        
        # Standard Mode (If 'separate_folders' is NOT checked)
        if not separate_folders:
            self.gui.log_message(f"    Standard Output Folder: {os.path.basename(output_dir)}/")
        
        # Separate Folder Mode (If 'separate_folders' IS checked)
        else:
            self.gui.log_message(f"    Separate Folders based on extension Created in: {output_dir}/")

        self.gui.log_message(f"    Outputting to: {os.path.relpath(output_dir, self.APP_ROOT)}")

        # 2. Run all selected processing methods
        for method in methods_to_run:
            status = method(file_path, output_dir, separate_folders)
            self.gui.log_message(f"    - {method.__name__}: {status}")

        # 3. Move the original file (Implements Point 2)
        copy_status = self._copy_original_file(file_path, output_dir, separate_folders)
        self.gui.log_message(f"    - {copy_status}")