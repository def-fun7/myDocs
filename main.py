import tkinter as tk
from src.gui import Application

if __name__ == "__main__":
    # Create the root window
    root = tk.Tk()
    
    # Instantiate the Application class
    app = Application(master=root)
    
    # Start the main loop
    app.mainloop()