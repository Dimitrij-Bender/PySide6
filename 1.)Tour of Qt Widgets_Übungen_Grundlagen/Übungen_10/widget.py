
from PySide6.QtWidgets import  QWidget, QLabel, QHBoxLayout, QPushButton, QVBoxLayout, QMessageBox, QTextEdit
#from PySide6.QtCore import QSize
from PySide6.QtGui import QPixmap
from pathlib import Path

"""
class Widget(QWidget):
        def __init__(self):
                super().__init__()
                
                self.setWindowTitle("QLabel Image Demo")
                
                image_label = QLabel()
                #image_label.setPixmap(QPixmap("Desktop\\GUI_Oberfläche\\PySide6\\Übungen\\Übungen_10\\Images\\minions.png"))
                image_label.setPixmap(QPixmap("burster_logo.png"))
                
                
                layout = QVBoxLayout()
                layout.addWidget(image_label)
                
                self.setLayout(layout)
"""

class Widget(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("QLabel Image Demo")

        image_label = QLabel()

        image_path = Path(__file__).parent / "burster_logo.png"
        pixmap = QPixmap(str(image_path))

        print(image_path)
        print(pixmap.isNull())

        image_label.setPixmap(pixmap)

        layout = QVBoxLayout()
        layout.addWidget(image_label)

        self.setLayout(layout)
