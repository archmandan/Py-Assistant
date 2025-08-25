import tkinter as tk
from tkinter import ttk
from pynput import keyboard
import speech_recognition as sr
import pystray
from pystray import MenuItem as item
from PIL import Image
import threading
import pyttsx3

r = sr.Recognizer()
mic = sr.Microphone()

r.pause_threshold = 0.8
r.non_speaking_duration = 0.5

speaking = False

root = tk.Tk()
root.title("IAN - Voice Assistant")
root.geometry("300x300")
root.configure(background="black")
root.resizable(False, False)
root.attributes("-alpha", 0.6)
root.wm_attributes("-topmost", True)
root.overrideredirect(True)
root.eval('tk::PlaceWindow . center')

def say(text):
    global speaking
    if speaking:
        return

    def task():
        eng = pyttsx3.init()
        global speaking # type: ignore[unknown-name]
        speaking = True
        eng.say(text)
        print(text)
        eng.runAndWait()
        speaking = False
        eng.stop()
    threading.Thread(target=task, daemon=True).start()

mic_lock = threading.Lock()

def listen():
    if not mic_lock.acquire(blocking=False):
        return
    try:
        with mic as source:
            r.adjust_for_ambient_noise(source, duration=0.3)
            audio = r.listen(source, timeout=1)
        try:
            speech = r.recognize_google(audio) # type: ignore[missing-attribute]
            say(speech)
        except sr.UnknownValueError:
            say("I didn't catch that.")
        except sr.RequestError:
            say("API error.")
        except sr.exceptions.WaitTimeoutError:
            say("Request timed out")
    finally:
        mic_lock.release()
    root.withdraw()


def checkKey(key):
    if key == keyboard.Key.f23:
        root.deiconify()
        threading.Thread(target=listen, daemon=True).start()


listener = keyboard.Listener(on_release=checkKey)
listener.start()

def quit_app(icon, item):
    icon.stop()
    root.after(0, root.destroy) # type: ignore[bad-argument-type]

# Create the tray menu
menu = (
    item("Exit", quit_app)
)

# Load icon image
icon_image = Image.open("Assets/logo.ico")
tray_icon = pystray.Icon("IAN", icon=icon_image, menu=pystray.Menu(menu))

# Runs tray icon in a separate thread
threading.Thread(target=tray_icon.run, daemon=True).start()

root.wm_iconbitmap("Assets/logo.ico")

root.withdraw()
root.mainloop()
