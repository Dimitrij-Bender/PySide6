import sys

from PySide6 import QtWidgets
#from PySide6.QtUiTools import QUiLoader
#from user_interface import UserInterface
from widget import Widget

app = QtWidgets.QApplication(sys.argv)


window = Widget()
window.show()
app.exec()