import tkinter as tk
from tkinter import ttk
from pynput import keyboard
import speech_recognition as sr
import pystray
from pystray import MenuItem as item
from PIL import Image
import threading
from fuzzywuzzy import fuzz
from speech_recognition import WaitTimeoutError
import requests
import pyttsx3
from datetime import datetime, date
import random
import wikipedia
from wikipedia.exceptions import DisambiguationError

eng = pyttsx3.init()

voices = {
    "UK": "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-GB_HAZEL_11.0",
    "US_David": "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_DAVID_11.0",
    "US_Zira": "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_ZIRA_11.0",
    "AU_Catherine": "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\MSTTS_V110_enAU_CatherineM"
}

speech = ""

class funcs:
    @staticmethod
    def getTime():
        now = str(datetime.now().strftime("%I:%M %p"))
        response = random.choice(responses["time"]).format(time=now)
        say(response, printing=True)

    @staticmethod
    def greeting():
        response = random.choice(responses["greeting"])
        say(response, printing=True)

    @staticmethod
    def search(query):
        try:
            result = wikipedia.search(query, sentences=3)
            say(result, printing=True)
        except DisambiguationError as e:
            say("You'll need to be more specific\nDid you mean?", printing=True)
            say(f"{random.choice(e.options)}")
intents = {
    "time": [
        "What time is it?",
        "Can you tell me the time?",
        "What's the current time?",
        "Do you know the time?",
        "Give me the time."
    ],
    "greeting": [
        "Hi",
        "Hello",
        "Hey",
        "Good morning",
        "Good evening"
    ],
}

intent_funcs = {
#    "weather": None,
    "time": funcs.getTime,
    "greeting": funcs.greeting,
}

responses = {
    "time": [
        "The current time is {time}.",
        "Right now it's {time}.",
        "It's {time} at the moment.",
        "The clock says {time}.",
        "According to my calculations, it's {time}.",
        "As of now, the time is {time}.",
        "You're looking at {time}.",
        "My circuits tell me it's {time}.",
        "Guess what? It's {time}.",
        "Not to alarm you, but it's {time}.",
        "If you must know, it's {time}.",
        "Time check: {time}.",
        "Your watch should say {time}.",
        "Last I checked, it's {time}.",
        "The official time is {time}.",
        "Currently, it's {time}.",
        "My internal clock says {time}.",
        "Let me save you the suspense: {time}.",
        "I can confirm it's {time}.",
        "It's exactly {time}.",
        "Drumroll please… it's {time}.",
        "Tick-tock, it's {time}.",
        "Surprise! It's {time}.",
        "Breaking news: it's {time}.",
        "Fun fact: the time is {time}."
    ],
    "greeting": [
        "Hello!",
        "Hi there!",
        "Hey!",
        "Good morning!",
        "Good afternoon!",
        "Good evening!",
        "Hi, how's it going?",
        "Hey! Nice to see you.",
        "Hello! What's up?",
        "Greetings!",
        "Hey there, friend!",
        "Hi! How are you today?",
        "Hello! How’s your day going?",
        "Hey! Long time no see.",
        "Hi! Ready to chat?",
        "Good day!",
        "Hey! Hope you're doing well.",
        "Hello there!",
        "Hi! What's happening?",
        "Hey! How’s everything?"
    ]
}


def checkForIntents(text):
    for key, value_list in intents.items():
        key = key.lower()
        for item in value_list:
            item = item.upper()
            text = text.upper()
            ratio = fuzz.partial_ratio(text, item)
            if ratio > 60:
                intent_funcs[key]() # type: ignore


def say(text, voice="AU_Catherine", printing=False):
    global speaking
    if speaking:
        return

    def task():
        global speaking # type: ignore[unknown-name]
        speaking = True
        eng.setProperty('voice', voices.get(voice, voices["UK"]))
        eng.say(text)
        if printing:
            print(text)
        eng.runAndWait()
        speaking = False
    threading.Thread(target=task, daemon=True).start()

mic_lock = threading.Lock()

def listen(intent=False):
    global speech
    if not mic_lock.acquire(blocking=False):
        return
    try:
        try:
            root.deiconify()
            with mic as source:
                r.adjust_for_ambient_noise(source, duration=0.3)
                audio = r.listen(source, timeout=3)
            try:
                speech = r.recognize_google(audio) # type: ignore[missing-attribute]
                print(speech)
                if intent:
                    checkForIntents(speech)
            except sr.UnknownValueError:
                say("I didn't catch that.")
            except sr.RequestError:
                say("API error.")
        except sr.WaitTimeoutError:
            say("Request timed out")
    except Exception as e:
        # Catch any other unexpected exceptions
        say(f"An error occurred: {str(e)}")
    finally:
        mic_lock.release()
    root.withdraw()

def checkKey(key):
    if key == keyboard.Key.f23:
        threading.Thread(target=lambda: listen(intent=True), daemon=True).start()

def quit_app(icon, item):
    icon.stop()
    root.after(0, root.destroy) # type: ignore[bad-argument-type]

r = sr.Recognizer()
mic = sr.Microphone()

speaking = False

root = tk.Tk()
root.title("SARAH - Voice Assistant")
root.geometry("300x300")
root.configure(background="black")
root.resizable(False, False)
root.attributes("-alpha", 0.6)
root.wm_attributes("-topmost", True)
root.overrideredirect(True)
root.eval('tk::PlaceWindow . center')

listener = keyboard.Listener(on_release=checkKey)
listener.start()

# Create the tray menu
menu = pystray.Menu(
    item("Listen", lambda icon, item: checkKey(keyboard.Key.f23)),
    item("Exit", quit_app)
)

# Load icon image
icon_image = Image.open("Assets/logo.ico")
tray_icon = pystray.Icon("SARAH", icon=icon_image, menu=menu)

# Runs tray icon in a separate thread
threading.Thread(target=tray_icon.run, daemon=True).start()

root.wm_iconbitmap("Assets/logo.ico")

root.withdraw()
root.mainloop()
eng.stop()