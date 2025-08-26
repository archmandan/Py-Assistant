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

voices = {
    "UK": "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-GB_HAZEL_11.0",
    "US_David": "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_DAVID_11.0",
    "US_Zira": "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_ZIRA_11.0"
}

def checkSpeech(speech):
    for intent in intents.weather:
        ratio = fuzz.ratio(speech, intent)
        print(ratio)
        if ratio >= 60:
            weather.openwindow()
            break

def say(text, voice="UK"):
    global speaking
    if speaking:
        return

    def task():
        eng = pyttsx3.init()
        global speaking # type: ignore[unknown-name]
        speaking = True
        eng.setProperty('voice', voices.get(voice, voices["UK"]))
        eng.say(text)
        saidSpeech.append(f"IAN: {text}")
        eng.runAndWait()
        speaking = False
        eng.stop()
    threading.Thread(target=task, daemon=True).start()

mic_lock = threading.Lock()

def listen():
    if not mic_lock.acquire(blocking=False):
        return
    try:
        try:
            with mic as source:
                r.adjust_for_ambient_noise(source, duration=0.3)
                audio = r.listen(source, timeout=3)
            try:
                speech = r.recognize_google(audio) # type: ignore[missing-attribute]
                saidSpeech.append(f"IAN: {speech}")
                print(speech)
                checkSpeech(speech)
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
        root.deiconify()
        threading.Thread(target=listen, daemon=True).start()

def quit_app(icon, item):
    icon.stop()
    root.after(0, root.destroy) # type: ignore[bad-argument-type]

class intents:
    weather = [
        "what's the weather like today",
        "tell me today's forecast",
        "is it going to rain today",
        "do I need an umbrella today",
        "what's the temperature today",
        "how's the weather looking today",
        "is it sunny today",
        "what's the weather right now",
        "whats the forecast looking like today"
    ]

# == Classes for different operations ==
class weather():
    weather_codes = {
        395: "Moderate or heavy snow in area with thunder",
        392: "Patchy light snow in area with thunder",
        389: "Moderate or heavy rain in area with thunder",
        386: "Patchy light rain in area with thunder",
        377: "Moderate or heavy showers of ice pellets",
        374: "Light showers of ice pellets",
        371: "Moderate or heavy snow showers",
        368: "Light snow showers",
        365: "Moderate or heavy sleet showers",
        362: "Light sleet showers",
        359: "Torrential rain shower",
        356: "Moderate or heavy rain shower",
        353: "Light rain shower",
        350: "Ice pellets",
        338: "Heavy snow",
        335: "Patchy heavy snow",
        332: "Moderate snow",
        329: "Patchy moderate snow",
        326: "Light snow",
        323: "Patchy light snow",
        320: "Moderate or heavy sleet",
        317: "Light sleet",
        314: "Moderate or Heavy freezing rain",
        311: "Light freezing rain",
        308: "Heavy rain",
        305: "Heavy rain at times",
        302: "Moderate rain",
        299: "Moderate rain at times",
        296: "Light rain",
        293: "Patchy light rain",
        284: "Heavy freezing drizzle",
        281: "Freezing drizzle",
        266: "Light drizzle",
        263: "Patchy light drizzle",
        260: "Freezing fog",
        248: "Fog",
        230: "Blizzard",
        227: "Blowing snow",
        200: "Thundery outbreaks in nearby",
        185: "Patchy freezing drizzle nearby",
        182: "Patchy sleet nearby",
        179: "Patchy snow nearby",
        176: "Patchy rain nearby",
        143: "Mist",
        122: "Overcast",
        119: "Cloudy",
        116: "Partly Cloudy",
        113: "Clear/Sunny"
    }

    @staticmethod
    def time_to_int(time=""):
        time_num, period = time.split(" ")
        hours, minutes = map(int, time_num.split(":"))

        if period.upper() == "PM" and hours != 12:
            hours += 12
        elif period.upper() == "AM" and hours == 12:
            hours = 0
        if minutes >= 30:
            hours += 1

        return hours * 100

    @staticmethod
    def getWeather(location="Leeds"):
        url = f"https://wttr.in/{location}?format=j1"
        data = requests.get(url).json()

        entries = []

        today = str(date.today())
        time = int(datetime.now().strftime("%H") + "00")

        today_weather = None
        today_sun: dict[str, str | int] = {
            "sunrise": "",
            "sunset": "",
            "intSunset": 0,
            "intSunrise": 0
        }

        for day in data["weather"]:
            if day["date"] == today:
                today_weather = day
                today_sun["sunrise"] = day["astronomy"][0]["sunrise"]
                today_sun["sunset"] = day["astronomy"][0]["sunset"]
                break

        today_sun["intSunrise"] = weather.time_to_int(today_sun["sunrise"])
        today_sun["intSunset"] = weather.time_to_int(today_sun["sunset"])


        for entry in today_weather["hourly"]: # type: ignore[unsupported-operation]
            if entry["time"] <= time:
                entry_dict = {
                    "time": entry["time"],
                    "uvIndex": entry["uvIndex"],
                    "tempC": entry["tempC"],
                    "tempF": entry["tempF"],
                    "FeelsLikeC": entry["FeelsLikeC"],
                    "FeelsLikeF": entry["FeelsLikeF"],
                    "weatherCode": int(entry["weatherCode"]),
                    "description": "",
                    "night": False
                }

                if entry_dict["weatherCode"] == 113:
                    if int(entry_dict["time"]) < today_sun["intSunrise"] and int(entry_dict["time"]) > today_sun["intSunset"]:
                        entry_dict.update({"description": "Clear"})
                        entry_dict.update({"night": True})
                    elif int(entry_dict["time"]) > today_sun["intSunrise"] and int(entry_dict["time"]) < today_sun["intSunset"]:
                        entry_dict.update({"description": "Sunny"})
                        entry_dict.update({"night": False})
                else: 
                    if int(entry_dict["time"]) < today_sun["intSunrise"] and int(entry_dict["time"]) > today_sun["intSunset"]:
                        entry_dict.update({"night": True})
                    elif int(entry_dict["time"]) > today_sun["intSunrise"] and int(entry_dict["time"]) < today_sun["intSunset"]:
                        entry_dict.update({"night": False})
                    entry_dict.update({"description": weather.weather_codes.get(int(entry_dict["weatherCode"]), "Unknown")}) 

                entries.append(entry_dict)

        return entries

    @staticmethod
    def openwindow():
        say("Here is the weather forecast")
        weather_screen = tk.Toplevel(root)
        weather_screen.title("IAN - Weather")
        weather_screen.geometry("500x300")
        weather_screen.resizable(False, False)
        weather_screen.wm_attributes("-topmost", True)
        weather_screen.configure(background="black")
        weather_entries = weather.getWeather()

r = sr.Recognizer()
mic = sr.Microphone()

saidSpeech = []

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

listener = keyboard.Listener(on_release=checkKey)
listener.start()

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
