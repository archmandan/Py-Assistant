import tkinter as tk
from pynput import keyboard
import speech_recognition as sr
import pyttsx3
from datetime import date, datetime

speechList = []
speech = ""

def say(text):
    engine = pyttsx3.init()
    engine.say(text)
    speechList.append(f"IAN: {text}")
    engine.runAndWait()
    engine.stop()

def writeToLog(speechList):
    today = str(date.today())
    time = datetime.now().strftime("%H-%M-%S")
    with open(f"LOG_{today}_{time}", "a") as file:
        for line in speechList:
            file.write(line + "\n")

def listen():
    global speech
    r = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        audio = r.listen(source)
        speech = r.recognize_google(audio) # type: ignore
    speechList.append(f"USER: {speech}")


def checkKey(key):
    if key == keyboard.Key.f23:
        listen()

root = tk.Tk()
root.title("IAN")
root.geometry("200x200")
root.configure(background="black")

listener = keyboard.Listener(on_press=checkKey)
listener.start()

root.mainloop()
writeToLog(speechList)