# ui.py
from PyQt5.QtWidgets import QMainWindow, QWidget
from PyQt5.QtGui import QPainter, QPixmap, QPen, QColor
from PyQt5.QtCore import Qt, QTimer, QRectF, pyqtSlot, pyqtSignal

class CircularWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.active = False
        self.setFixedSize(200, 200)  # Set widget size
        self.pixmap = QPixmap("assets/shiba_inu.png")
        self.glow_alpha = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_glow)

    def update_glow(self):
        if self.active:
            # Increase glow intensity (cycling for a pulsing effect)
            self.glow_alpha = (self.glow_alpha + 10) % 255
        else:
            self.glow_alpha = 0
            self.timer.stop()
        self.update()

    def start_glow(self):
        self.active = True
        self.timer.start(50)

    def stop_glow(self):
        self.active = False
        self.timer.stop()
        self.glow_alpha = 0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # Draw circular background
        rect = QRectF(0, 0, self.width(), self.height())
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(30, 30, 30))
        painter.drawEllipse(rect)
        # Draw glow effect when active
        if self.active:
            pen = QPen(QColor(255, 215, 0, self.glow_alpha))  # Golden glow
            pen.setWidth(15)
            painter.setPen(pen)
            painter.drawEllipse(rect.adjusted(5, 5, -5, -5))
        # Draw the Shiba Inu logo centered within the circle
        if not self.pixmap.isNull():
            pix_size = min(self.width() - 40, self.height() - 40)
            scaled = self.pixmap.scaled(pix_size, pix_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            x = (self.width() - scaled.width()) / 2
            y = (self.height() - scaled.height()) / 2
            painter.drawPixmap(int(x), int(y), scaled)

class MainWindow(QMainWindow):
    # Define signals to communicate with the main thread.
    commandReceived = pyqtSignal(str)
    startGlowSignal = pyqtSignal()
    stopGlowSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hey Miso Assistant")
        self.widget = CircularWidget(self)
        self.setCentralWidget(self.widget)
        self.resize(220, 220)

        # Connect the signals to their respective slots.
        self.commandReceived.connect(self.handle_command)
        self.startGlowSignal.connect(self.startGlow)
        self.stopGlowSignal.connect(self.stopGlow)

    @pyqtSlot(str)
    def handle_command(self, command):
        # Import here to avoid circular dependency issues.
        from commands import process_command
        process_command(command)

    @pyqtSlot()
    def startGlow(self):
        self.widget.start_glow()

    @pyqtSlot()
    def stopGlow(self):
        self.widget.stop_glow()
