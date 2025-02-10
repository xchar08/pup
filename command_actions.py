# command_actions.py
import subprocess
import keyboard  # pip install keyboard
import os
import webbrowser
import requests
from dotenv import load_dotenv
from PyQt5.QtWidgets import QApplication, QMessageBox, QInputDialog
from rapidfuzz import fuzz

# Load environment variables
load_dotenv()
NB_STUDIO_API_KEY = os.getenv("NB_STUDIO_API_KEY")
if not NB_STUDIO_API_KEY:
    raise ValueError("NB_STUDIO_API_KEY not found in environment variables. Please set it in your .env file.")

# Nebius API endpoint for chat completions (fallback, if needed)
NEBIUS_API_URL = "https://api.studio.nebius.ai/v1/chat/completions"

# Global dictionaries to store opened process handles
opened_apps = {}
opened_urls = {}

def stop_music():
    keyboard.send("play/pause media")
    print("Toggled media playback (stop).")

def start_music():
    keyboard.send("play/pause media")
    print("Toggled media playback (start).")

# -------------------- LIVE TRANSLATION WINDOW --------------------
# This class implements a live translation mode that updates periodically.
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton
from PyQt5.QtCore import QTimer
import pyautogui
import pytesseract
import nltk
from langdetect import detect_langs

class LiveTranslationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Live Translation")
        self.resize(800, 400)
        self.layout = QVBoxLayout(self)
        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        self.layout.addWidget(self.text_edit)
        self.stop_button = QPushButton("Stop Live Translation", self)
        self.stop_button.clicked.connect(self.close)
        self.layout.addWidget(self.stop_button)

        # Set up a QTimer to update translation every second.
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_translation)
        self.timer.start(1000)  # update every 1000 milliseconds

    def update_translation(self):
        # Ensure NLTK resources are available.
        nltk.download('punkt', quiet=True)
        nltk.download('punkt_tab', quiet=True)

        # Capture a region centered on the current mouse pointer.
        region_width, region_height = 800, 600
        x, y = pyautogui.position()
        region_left = max(0, x - region_width // 2)
        region_top = max(0, y - region_height // 2)
        screenshot = pyautogui.screenshot(region=(region_left, region_top, region_width, region_height))
        extracted_text = pytesseract.image_to_string(screenshot)
        if not extracted_text.strip():
            self.text_edit.setPlainText("No text detected in the region.")
            return

        # Split the text into sentences.
        sentences = nltk.sent_tokenize(extracted_text)
        if not sentences:
            self.text_edit.setPlainText("Could not split text into sentences.")
            return

        translation_url = "https://api.mymemory.translated.net/get"
        translated_sentences = []
        english_threshold = 0.95  # Only translate if less than 95% confidence for English.

        for sentence in sentences:
            try:
                langs = detect_langs(sentence)
            except Exception as e:
                print("Error detecting language for sentence:", sentence, e)
                translated_sentences.append(sentence)
                continue

            # Determine the English probability (if available)
            english_prob = 0.0
            for lang in langs:
                if lang.lang == "en":
                    english_prob = lang.prob
                    break

            if english_prob >= english_threshold:
                # Sentence is confidently English; do not translate.
                translated_sentences.append(sentence)
            else:
                # Otherwise, translate this sentence.
                src_lang = langs[0].lang if langs else "auto"
                params = {
                    "q": sentence,
                    "langpair": f"{src_lang}|en"
                }
                try:
                    response = requests.get(translation_url, params=params, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        translation = data.get("responseData", {}).get("translatedText", "")
                        if translation and translation.lower() != sentence.lower():
                            translated_sentences.append(translation)
                        else:
                            translated_sentences.append(sentence)
                    else:
                        translated_sentences.append(sentence)
                except Exception as e:
                    print("Error translating sentence:", sentence, e)
                    translated_sentences.append(sentence)

        final_translation = " ".join(translated_sentences)
        if len(final_translation) > 1000:
            final_translation = final_translation[:1000] + "..."
        self.text_edit.setPlainText(final_translation)

    def closeEvent(self, event):
        self.timer.stop()
        event.accept()

def translate_text(command_str=None):
    """
    Launches the live translation window.
    The optional command_str parameter is ignored.
    """
    parent = QApplication.activeWindow()
    dialog = LiveTranslationDialog(parent)
    dialog.exec_()
# -------------------- END LIVE TRANSLATION --------------------

def copy_neural_network_diagram():
    print("Copying neural network diagram from screen... (feature not yet implemented)")

def create_new_file(command_str=None):
    import re
    default_file_type = "txt"  # default extension if nothing is specified
    default_file_name = "new_file"
    home = os.path.expanduser("~")
    default_directory = os.getcwd()  # default directory if none inferred

    # If no command string is provided, ask the user.
    if command_str is None or command_str.strip() == "":
        parent = QApplication.activeWindow()
        command_str, ok = QInputDialog.getText(parent, "Create New File", "Enter file creation command:")
        if not ok or not command_str.strip():
            print("No file creation command specified.")
            return
        command_str = command_str.strip()

    command_lower = command_str.lower()

    # --- Parse the file name ---
    file_name = None
    # Look for "named" followed by the desired name (up to "in" or end-of-string)
    import re
    match_name = re.search(r"named\s+([^\s].*?)(?:\s+in\s+|$)", command_lower)
    if match_name:
        file_name = match_name.group(1).strip()
        # Replace " dot " with "."
        file_name = file_name.replace(" dot ", ".").replace(" dot", ".").replace("dot ", ".")
    
    # --- Parse the directory ---
    directory = None
    match_dir = re.search(r"in\s+([^\s].*?)(?:\s+named|\s*$)", command_lower)
    if match_dir:
        dir_text = match_dir.group(1).strip()
        # Remove common filler words.
        dir_text = dir_text.replace("my ", "").replace("folder", "").strip()
        # If "document" is mentioned, assume the user's Documents folder.
        if "document" in dir_text:
            directory = os.path.join(home, "Documents")
        elif dir_text:
            # Otherwise, assume it's a subfolder of the home directory.
            directory = os.path.join(home, dir_text.capitalize())
    
    # --- Determine the file type (for default extension) ---
    default_extensions = {
        "text": "txt",
        "python": "py",
        "markdown": "md",
        "html": "html",
        "css": "css",
        "javascript": "js",
        "java": "java",
        "c++": "cpp",
        "c#": "cs",
    }
    file_type = None
    for key in default_extensions:
        if key in command_lower and "file" in command_lower:
            file_type = key
            break

    # --- Decide on the extension ---
    if file_name and "." in file_name:
        ext = file_name.split(".")[-1]
    else:
        ext = default_extensions.get(file_type, default_file_type)

    # --- Finalize the file name ---
    if not file_name:
        file_name = default_file_name + "." + ext
    else:
        if "." not in file_name:
            file_name = file_name + "." + ext

    # --- Finalize the directory ---
    if not directory:
        directory = default_directory

    full_path = os.path.join(directory, file_name)
    # Create the directory if it doesn't exist.
    os.makedirs(directory, exist_ok=True)

    # --- Default content based on file extension ---
    if ext == "py":
        content = "# New Python file generated by Hey Miso\n\nprint('Hello from Hey Miso!')\n"
    elif ext == "txt":
        content = "New text file created by Hey Miso.\n"
    else:
        content = ""

    try:
        with open(full_path, "w") as f:
            f.write(content)
        print(f"Created new file: {full_path}")
    except Exception as e:
        print("Error creating file:", e)

def open_app(app_name=None):
    if app_name is None or app_name.strip() == "":
        parent = QApplication.activeWindow()
        app_path, ok = QInputDialog.getText(parent, "Open App", "Enter application path or name:")
        if not ok or not app_path.strip():
            print("No application specified.")
            return
        app_name = app_path.strip()
    else:
        app_name = app_name.strip()
    
    known_apps = {
        "spotify": "spotify",
        "microsoft edge": "cmd /c start microsoft-edge:",
        "edge": "cmd /c start microsoft-edge:",
        "chrome": "chrome",
        "google chrome": "chrome",
        "notepad": "notepad",
        "calculator": "calc"
    }
    
    best_match = None
    best_score = 0
    lower_input = app_name.lower()
    for key in known_apps:
        score = fuzz.partial_ratio(lower_input, key)
        if score > best_score:
            best_score = score
            best_match = key
    
    if best_score > 50:
        command_to_run = known_apps[best_match]
        print(f"Interpreted '{app_name}' as '{best_match}'.")
    else:
        command_to_run = app_name

    try:
        subprocess.Popen(command_to_run, shell=True)
        opened_apps[app_name] = command_to_run
        print(f"Opened application: {app_name} using command: {command_to_run}")
    except Exception as e:
        print("Error opening application:", e)

def close_app(app_name=None):
    parent = QApplication.activeWindow()
    if app_name is None or app_name.strip() == "":
        app_name, ok = QInputDialog.getText(parent, "Close App", "Enter application name to close:")
        if not ok or not app_name.strip():
            print("No application specified.")
            return
        app_name = app_name.strip()
    else:
        app_name = app_name.strip()
    proc = opened_apps.get(app_name)
    if proc:
        try:
            proc.terminate()
            proc.wait()
            print(f"Closed application: {app_name}")
            del opened_apps[app_name]
        except Exception as e:
            print("Error closing application:", e)
    else:
        QMessageBox.information(parent, "Close App", "Application not found among open apps.")

def open_url(url_input=None):
    if url_input is None or url_input.strip() == "":
        parent = QApplication.activeWindow()
        url, ok = QInputDialog.getText(parent, "Open URL", "Enter URL to open:")
        if not ok or not url.strip():
            print("No URL specified.")
            return
        url_input = url.strip()
    else:
        url_input = url_input.strip()

    known_websites = {
        "google": "https://www.google.com",
        "wikipedia": "https://www.wikipedia.org",
        "youtube": "https://www.youtube.com",
        "facebook": "https://www.facebook.com",
        "twitter": "https://www.twitter.com",
        "reddit": "https://www.reddit.com"
    }

    lower_input = url_input.lower()
    final_url = None
    for key, website in known_websites.items():
        if key in lower_input:
            final_url = website
            break
    if final_url is None:
        final_url = url_input.replace(" ", "")
        if not (final_url.startswith("http://") or final_url.startswith("https://")):
            if "." not in final_url:
                final_url += ".com"
            final_url = "https://www." + final_url

    try:
        webbrowser.open(final_url)
        print(f"Opened URL: {final_url}")
    except Exception as e:
        print(f"Error opening URL: {e}")

def close_url(url_input=None):
    parent = QApplication.activeWindow()
    if url_input is None or url_input.strip() == "":
        url, ok = QInputDialog.getText(parent, "Close URL", "Enter URL to close:")
        if not ok or not url.strip():
            print("No URL specified.")
            return
        url_input = url.strip()
    else:
        url_input = url_input.strip()

    if not (url_input.startswith("http://") or url_input.startswith("https://")):
        url_input = url_input.replace(" ", "")
        if "." not in url_input:
            url_input += ".com"
        url_input = "https://www." + url_input
    proc = opened_urls.get(url_input)
    if proc:
        try:
            proc.terminate()
            proc.wait()
            print(f"Closed URL: {url_input}")
            del opened_urls[url_input]
        except Exception as e:
            print(f"Error closing URL: {e}")
    else:
        QMessageBox.information(parent, "Close URL", "URL process not found.")

# (Re)initialize the dictionaries for process handles.
opened_apps = {}
opened_urls = {}
