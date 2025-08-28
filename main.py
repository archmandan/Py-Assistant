# Import required libraries
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from pystray import Menu, MenuItem as Item, Icon
from PIL import Image
from threading import Thread

# Function Class
class funcs:
    @staticmethod
    def quit_app(icon, item):
        close = messagebox.askyesno(title="NINA - Exiting", message="Are you sure you want to close the app?")
        if close:
            icon.stop()
            root.destroy()

# Setup root window
root = tk.Tk()
root.geometry("400x400")
root.title("NINA - Voice Assistant") # Not Important, Not Interested
root.resizable(False, False)
root.configure(background="black")
root.attributes("-alpha", 0.6)
root.protocol("WM_DELETE_WINDOW", lambda: root.withdraw())

# Setup System Tray icon
image = Image.open("Assets\\logo.ico")
menu = Menu(
    Item(text="Open", action=lambda icon, item: root.deiconify()),
    Item(text="Quit", action=funcs.quit_app)
)
icon = Icon("Test", image, menu=menu)


root.withdraw()
Thread(target=icon.run, daemon=True).start()

# Run Program
root.mainloop()