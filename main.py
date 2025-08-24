import speech_recognition as sr
import tkinter as tk

# == Function for recognising speech ==
def listening():
    r = sr.Recognizer()
    mic = sr.Microphone()

# == Main GUI Code and program code ==
def main():
    root = tk.Tk()
    root.geometry("300x300")
    root.title("")

    root.mainloop()

if __name__ == "__main__":
    main()