# voice.py
import time
import speech_recognition as sr
from commands import process_command

class VoiceListener:
    def __init__(self, main_window):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.main_window = main_window

    def listen_for_wake_word(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            print("Listening for wake word...")
            audio = self.recognizer.listen(source)
        try:
            transcript = self.recognizer.recognize_google(audio)
            print("Heard:", transcript)
            if "hey miso" in transcript.lower():
                return True
        except sr.UnknownValueError:
            pass
        return False

    def listen_for_command(self):
        with self.microphone as source:
            print("Listening for command...")
            audio = self.recognizer.listen(source)
        try:
            command = self.recognizer.recognize_google(audio)
            print("Command:", command)
            return command
        except sr.UnknownValueError:
            print("Could not understand the command.")
            return None

    def start_listening(self):
        while True:
            if self.listen_for_wake_word():
                print("Wake word detected!")
                # Signal UI to start glowing
                self.main_window.startGlow()
                command = self.listen_for_command()
                if command:
                    process_command(command)
                # Stop the glow regardless of command result
                self.main_window.stopGlow()
            time.sleep(0.5)
