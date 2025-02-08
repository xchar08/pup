# main.py
import sys
import threading
from PyQt5.QtWidgets import QApplication
from ui import MainWindow
from voice import VoiceListener

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    # Start voice recognition in a separate thread (non-blocking)
    voice_listener = VoiceListener(window)
    voice_thread = threading.Thread(target=voice_listener.start_listening, daemon=True)
    voice_thread.start()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
