# voice.py
import time
import speech_recognition as sr
from rapidfuzz import fuzz  # pip install rapidfuzz
from PyQt5.QtCore import QTimer  # (not needed for our signal approach now)

TARGET_WAKE_WORD = "hey miso"
WAKE_WORD_THRESHOLD = 70  # Adjust threshold (0-100) to tolerate minor deviations

class VoiceListener:
    def __init__(self, main_window):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.main_window = main_window

    def is_wake_word(self, transcript):
        # Calculate similarity using partial_ratio
        score = fuzz.partial_ratio(transcript.lower(), TARGET_WAKE_WORD)
        print(f"Similarity score for '{transcript}' vs '{TARGET_WAKE_WORD}': {score}")
        return score >= WAKE_WORD_THRESHOLD

    def listen_for_wake_word(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            print("Listening for wake word...")
            audio = self.recognizer.listen(source)
        try:
            transcript = self.recognizer.recognize_google(audio)
            print("Heard:", transcript)
            if self.is_wake_word(transcript):
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
                # Emit the start glow signal (executed on the main thread)
                self.main_window.startGlowSignal.emit()
                command = self.listen_for_command()
                if command:
                    # Emit the command string so that it gets processed on the main thread.
                    self.main_window.commandReceived.emit(command)
                # Emit the stop glow signal (executed on the main thread)
                self.main_window.stopGlowSignal.emit()
            time.sleep(0.5)
