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

# Nebius API endpoint for chat completions
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

def translate_text():
    """
    Capture the screen, perform OCR to extract text, detect its language,
    and if non-English, use Nebius to translate it into English.
    """
    from PyQt5.QtWidgets import QApplication, QMessageBox
    import pyautogui  # pip install pyautogui
    import pytesseract  # pip install pytesseract (requires Tesseract OCR installed)
    from langdetect import detect, DetectorFactory  # pip install langdetect

    DetectorFactory.seed = 0
    parent = QApplication.activeWindow()
    screenshot = pyautogui.screenshot()
    extracted_text = pytesseract.image_to_string(screenshot)
    if not extracted_text.strip():
        QMessageBox.information(parent, "Translation", "No text found on screen.")
        return

    try:
        detected_lang = detect(extracted_text)
        print(f"Detected language: {detected_lang}")
    except Exception as e:
        detected_lang = "unknown"
        print("Error detecting language:", e)

    if detected_lang == "en":
        QMessageBox.information(parent, "Translation", "The screen text appears to be in English.")
        return

    prompt = f"Translate the following text into English: {extracted_text.strip()}"
    headers = {
        "Authorization": f"Bearer {NB_STUDIO_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "meta-llama/Meta-Llama-3.1-70B-Instruct",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 1,
        "max_tokens": 500
    }
    try:
        response = requests.post(NEBIUS_API_URL, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            translation = result["choices"][0]["message"]["content"]
            QMessageBox.information(parent, "Translation", translation)
        else:
            QMessageBox.warning(parent, "Translation Error", f"API Error: {response.text}")
    except requests.exceptions.RequestException as e:
        QMessageBox.warning(parent, "Translation Error", f"Error calling Nebius API: {e}")

def copy_neural_network_diagram():
    print("Copying neural network diagram from screen... (feature not yet implemented)")

def create_new_file(command_str=None):
    """
    Creates a new file based on specifications in the command.
    The command can specify the file type, the name, and the location.
    For example:
      "create a new python file named armor dot py in my Documents folder"
      "create a new text file named notes dot txt"
      "create a new markdown file in the Github folder in my Documents folder named readme dot md"
    Specifications can be given in any order.
    """
    import re
    # Default values
    default_file_type = "txt"  # default extension if nothing is specified
    default_file_name = "new_file"
    home = os.path.expanduser("~")
    default_directory = os.getcwd()  # default directory if none inferred

    # If no command string is provided, fall back to asking the user.
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
    # Look for the keyword "named" and capture what follows until "in" or end-of-string.
    match_name = re.search(r"named\s+([^\s].*?)(?:\s+in\s+|$)", command_lower)
    if match_name:
        file_name = match_name.group(1).strip()
        # Replace occurrences of " dot " with "."
        file_name = file_name.replace(" dot ", ".").replace(" dot", ".").replace("dot ", ".")
    
    # --- Parse the directory ---
    directory = None
    # Look for "in" followed by a directory specification.
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

    # --- Determine default file content based on extension ---
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
        # Optionally, you can automatically open the file in an editor:
        # subprocess.run(["code", full_path], check=True)
    except Exception as e:
        print("Error creating file:", e)

def open_app(app_name=None):
    """
    Opens an application based on the provided name.
    If no name is provided, falls back to asking the user.
    Uses fuzzy matching against a dictionary of known apps.
    """
    if app_name is None or app_name.strip() == "":
        parent = QApplication.activeWindow()
        app_path, ok = QInputDialog.getText(parent, "Open App", "Enter application path or name:")
        if not ok or not app_path.strip():
            print("No application specified.")
            return
        app_name = app_path.strip()
    else:
        app_name = app_name.strip()
    
    # Define a dictionary of known apps.
    # For Windows, using "cmd /c start ..." lets you launch many registered apps.
    known_apps = {
        "spotify": "spotify",
        "microsoft edge": "cmd /c start microsoft-edge:",
        "edge": "cmd /c start microsoft-edge:",
        "chrome": "chrome",
        "google chrome": "chrome",
        "notepad": "notepad",
        "calculator": "calc"
        # Add more known apps as needed.
    }
    
    # Use fuzzy matching to find the best match.
    best_match = None
    best_score = 0
    lower_input = app_name.lower()
    for key in known_apps:
        score = fuzz.partial_ratio(lower_input, key)
        if score > best_score:
            best_score = score
            best_match = key
    
    # If a good match is found (adjust threshold as needed), use that command.
    if best_score > 50:
        command_to_run = known_apps[best_match]
        print(f"Interpreted '{app_name}' as '{best_match}'.")
    else:
        command_to_run = app_name  # fallback: try using the raw input

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
    """
    Opens a URL based on the provided string.
    If the string matches a known website (like 'wikipedia' or 'google'),
    it opens the corresponding homepage. Otherwise, it attempts to build a URL.
    """
    if url_input is None or url_input.strip() == "":
        parent = QApplication.activeWindow()
        url, ok = QInputDialog.getText(parent, "Open URL", "Enter URL to open:")
        if not ok or not url.strip():
            print("No URL specified.")
            return
        url_input = url.strip()
    else:
        url_input = url_input.strip()

    # Define a dictionary of known websites.
    known_websites = {
        "google": "https://www.google.com",
        "wikipedia": "https://www.wikipedia.org",
        "youtube": "https://www.youtube.com",
        "facebook": "https://www.facebook.com",
        "twitter": "https://www.twitter.com",
        "reddit": "https://www.reddit.com",
        # Add more as needed.
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
