# commands.py
import os
import json
import requests
import subprocess
import keyboard
from dotenv import load_dotenv
from PyQt5.QtWidgets import (QApplication, QDialog, QVBoxLayout, QTextEdit,
                             QPushButton, QLabel, QMessageBox, QInputDialog)
from command_actions import (
    stop_music, start_music, translate_text, copy_neural_network_diagram,
    create_new_file, open_app, close_app, open_url, close_url
)
import pyautogui
import pytesseract
from rapidfuzz import fuzz
import re

# Load environment variables from .env file
load_dotenv()
API_KEY = os.getenv("NB_STUDIO_API_KEY")
if not API_KEY:
    raise ValueError("NB_STUDIO_API_KEY not found in environment variables. Please set it in your .env file.")

# Nebius API endpoint for chat completions (used as a fallback if needed)
NEBIUS_API_URL = "https://api.studio.nebius.ai/v1/chat/completions"

# Global variable to hold pending Nebius queries (for follow-up questions)
pending_nebius_context = None

def call_nebius_api(prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "meta-llama/Meta-Llama-3.1-70B-Instruct",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 1,
        "max_tokens": 150
    }
    try:
        response = requests.post(NEBIUS_API_URL, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            reply = result["choices"][0]["message"]["content"]
            return reply
        else:
            print("Nebius API Error:", response.text)
            return None
    except requests.exceptions.RequestException as e:
        print("Error calling Nebius API:", e)
        return None

def confirm_and_run_script(script, parent_window):
    dialog = QDialog(parent_window)
    dialog.setWindowTitle("Confirm Script Execution")
    layout = QVBoxLayout(dialog)
    label = QLabel("The following script will be executed:")
    layout.addWidget(label)
    text_edit = QTextEdit()
    text_edit.setPlainText(script)
    text_edit.setReadOnly(True)
    layout.addWidget(text_edit)
    button = QPushButton("good boy")
    layout.addWidget(button)
    button.clicked.connect(dialog.accept)
    dialog.exec_()
    import threading
    def run_script():
        try:
            exec(script, globals())
        except Exception as e:
            print("Error executing script:", e)
    threading.Thread(target=run_script, daemon=True).start()

def handle_nebius_choice_response(reply):
    """
    Handles a Nebius reply that contains a list of choices.
    It extracts numbered choices, prompts the user to pick one,
    shows a preview of the selected code, and if the user types 'go',
    writes the code to a temporary Python file and executes it.
    """
    import tempfile
    import subprocess

    # Extract numbered choices using a regex.
    pattern = re.compile(r"^\s*(\d+)\.\s*(.+)$", re.MULTILINE)
    choices = pattern.findall(reply)
    if not choices:
        return False

    # Build a display string for the choices.
    display_text = "Nebius returned multiple choices. Please choose one by entering its number:\n\n"
    for num, text in choices:
        display_text += f"{num}. {text}\n"

    parent = QApplication.activeWindow()
    choice_str, ok = QInputDialog.getText(parent, "Nebius Choices", display_text)
    if not ok or not choice_str.strip().isdigit():
        QMessageBox.information(parent, "Choice Selection", "Invalid choice entered.")
        return False

    choice_num = int(choice_str.strip())
    selected_choice = None
    for num, text in choices:
        if int(num) == choice_num:
            selected_choice = text
            break

    if selected_choice is None:
        QMessageBox.information(parent, "Choice Selection", "No matching choice found.")
        return False

    # Preview the code and ask for confirmation.
    preview, ok = QInputDialog.getMultiLineText(parent, "Preview Code",
                "The following code will be executed.\nType 'go' to run, or anything else to cancel:",
                selected_choice)
    if not ok or preview.strip().lower() != "go":
        QMessageBox.information(parent, "Cancelled", "Execution cancelled.")
        return False

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w", encoding="utf-8") as temp_file:
            temp_file.write(selected_choice)
            temp_path = temp_file.name
        subprocess.Popen(["python", temp_path])
        QMessageBox.information(parent, "Execution", f"Executing code from temporary file: {temp_path}")
    except Exception as e:
        QMessageBox.warning(parent, "Execution Error", f"Error executing code: {e}")
        return False

    return True

def load_command_config():
    config_path = os.path.join(os.path.dirname(__file__), "commands_config.json")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return json.load(f)
    return {}

command_config = load_command_config()

# Map action names to functions defined in command_actions.py
action_mapping = {
    "stop_music": stop_music,
    "start_music": start_music,
    "translate_text": translate_text,
    "copy_neural_network_diagram": copy_neural_network_diagram,
    "create_new_file": create_new_file,
    "open_app": open_app,
    "close_app": close_app,
    "open_url": open_url,
    "close_url": close_url
}

def execute_nebius_instructions(instructions):
    """
    Parses Nebius instructions for actionable keywords and executes them.
    This version improves the "click on" logic by grouping OCR data by line.
    """
    instructions_lower = instructions.lower()
    if "click on" in instructions_lower:
        target = instructions_lower.split("click on", 1)[1].strip()
        print("Attempting to click on element matching:", target)
        screenshot = pyautogui.screenshot()
        data = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT)
        lines = {}
        n = len(data["text"])
        for i in range(n):
            word = data["text"][i].strip()
            if not word:
                continue
            block = data["block_num"][i]
            line = data["line_num"][i]
            key = (block, line)
            if key not in lines:
                lines[key] = {
                    "words": [],
                    "left": data["left"][i],
                    "top": data["top"][i],
                    "right": data["left"][i] + data["width"][i],
                    "bottom": data["top"][i] + data["height"][i]
                }
            else:
                lines[key]["left"] = min(lines[key]["left"], data["left"][i])
                lines[key]["top"] = min(lines[key]["top"], data["top"][i])
                lines[key]["right"] = max(lines[key]["right"], data["left"][i] + data["width"][i])
                lines[key]["bottom"] = max(lines[key]["bottom"], data["top"][i] + data["height"][i])
            lines[key]["words"].append(word)
        best_line = None
        best_score = 0
        for key, line_data in lines.items():
            line_text = " ".join(line_data["words"])
            score = fuzz.ratio(line_text.lower(), target)
            if score > best_score:
                best_score = score
                best_line = line_data
        if best_line and best_score > 50:
            x = best_line["left"] + (best_line["right"] - best_line["left"]) // 2
            y = best_line["top"] + (best_line["bottom"] - best_line["top"]) // 2
            pyautogui.click(x, y)
            print(f"Clicked on element '{' '.join(best_line['words'])}' at ({x},{y}). (Score: {best_score})")
        else:
            print("Element not found on screen.")
    elif "type" in instructions_lower:
        idx = instructions_lower.find("type")
        text_to_type = instructions[idx + len("type"):].strip()
        print("Typing text:", text_to_type)
        keyboard.write(text_to_type)
    elif "press" in instructions_lower:
        idx = instructions_lower.find("press")
        key = instructions_lower[idx + len("press"):].strip().split()[0]
        print("Pressing key:", key)
        keyboard.send(key)
    else:
        print("No actionable instructions found in:", instructions)

def execute_system_command(command):
    """
    Processes a command. If it matches one of our locally mapped commands,
    it runs it. Otherwise, the command is forwarded to Nebius.
    If Nebius returns a follow-up question or a list of choices,
    this function handles the response accordingly.
    """
    global pending_nebius_context
    print("Processing command:", command)
    lower_command = command.lower()
    matched = False
    for key, config in command_config.items():
        pattern = config.get("pattern", "").lower()
        if lower_command.startswith(pattern):
            action_name = config.get("action")
            func = action_mapping.get(action_name)
            if func:
                if action_name in ["open_app", "open_url", "close_app", "close_url",
                                   "create_new_file", "translate_text"]:
                    arg = command[len(pattern):].strip()
                    func(arg)
                else:
                    func()
                matched = True
                break
    if not matched:
        # If there is a pending Nebius context, combine it with the new command.
        if pending_nebius_context is not None:
            full_query = pending_nebius_context + " " + command
            print("Processing follow-up query:", full_query)
            reply = call_nebius_api(full_query)
            pending_nebius_context = None
            if reply:
                if any(keyword in reply.lower() for keyword in ["click on", "type", "press"]):
                    execute_nebius_instructions(reply)
                elif "\n" in reply and (reply.lstrip().startswith("import") or 
                                         reply.lstrip().startswith("def") or 
                                         reply.lstrip().startswith("#")):
                    parent = QApplication.activeWindow()
                    confirm_and_run_script(reply, parent)
                else:
                    print("Nebius API response:", reply)
            else:
                print("No response from Nebius API.")
            return

        # Otherwise, forward the command to Nebius.
        print("Command not recognized locally. Forwarding to Nebius API...")
        reply = call_nebius_api(command)
        if reply:
            # Check if the reply contains multiple choices.
            if len(re.findall(r"^\s*\d+\.\s+", reply, re.MULTILINE)) > 1:
                if handle_nebius_choice_response(reply):
                    return
            if reply.strip().endswith("?"):
                pending_nebius_context = reply
                print("Nebius API asks:", reply)
                parent = QApplication.activeWindow()
                QMessageBox.information(parent, "Nebius Query", reply)
            elif any(keyword in reply.lower() for keyword in ["click on", "type", "press"]):
                execute_nebius_instructions(reply)
            elif "\n" in reply and (reply.lstrip().startswith("import") or 
                                     reply.lstrip().startswith("def") or 
                                     reply.lstrip().startswith("#")):
                parent = QApplication.activeWindow()
                confirm_and_run_script(reply, parent)
            else:
                print("Nebius API response:", reply)
        else:
            print("No response from Nebius API.")

def process_command(command):
    """
    Called with each recognized command. If there is a pending Nebius query awaiting
    an answer, this function combines the pending context with the new command and processes it.
    Otherwise, it processes the command normally (supporting chaining with " and ").
    """
    global pending_nebius_context
    if pending_nebius_context is not None:
        full_query = pending_nebius_context + " " + command
        print("Processing follow-up query:", full_query)
        reply = call_nebius_api(full_query)
        pending_nebius_context = None
        if reply:
            if any(keyword in reply.lower() for keyword in ["click on", "type", "press"]):
                execute_nebius_instructions(reply)
            elif "\n" in reply and (reply.lstrip().startswith("import") or 
                                     reply.lstrip().startswith("def") or 
                                     reply.lstrip().startswith("#")):
                parent = QApplication.activeWindow()
                confirm_and_run_script(reply, parent)
            else:
                print("Nebius API response:", reply)
        else:
            print("No response from Nebius API.")
        return

    print("Processing command:", command)
    if " and " in command.lower():
        sub_commands = command.split(" and ")
        for sub in sub_commands:
            sub = sub.strip()
            if sub:
                execute_system_command(sub)
    else:
        execute_system_command(command)
