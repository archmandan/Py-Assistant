from pynput import keyboard # type: ignore
import tkinter as tk
from tkinter import messagebox
import speech_recognition as sr

# == Listening ==
def micListening():
    listen_button.config(text="🎙️ Listening...", command="None")

    r = sr.Recognizer()
    mic = sr.Microphone()

    listen_button.config(text="🎙️ Listen", command=micListening)

# == Check if key is Copilot key ==
def checkKey(key):
    if key == keyboard.Key.f23:
        msg = messagebox.showinfo("IAN", "Listening started")
        micListening()

# == Window Setup ==
root = tk.Tk()
root.geometry("300x200")
root.title("IAN")

# == Widgets ==
listen_button = tk.Button(root, text="🎙️ Listen", command=micListening)

# == Layout ==
listen_button.grid(column=1, row=1)

root.mainloop()