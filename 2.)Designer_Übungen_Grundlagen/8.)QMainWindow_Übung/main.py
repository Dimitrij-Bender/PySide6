import sys

from PySide6.QtWidgets import QApplication
#from PySide6.QtUiTools import QUiLoader
#from user_interface import UserInterface
from mainwindow import MainWindow

app = QApplication(sys.argv)


w = MainWindow(app)
#w = MainWindow()
w.show()
app.exec()