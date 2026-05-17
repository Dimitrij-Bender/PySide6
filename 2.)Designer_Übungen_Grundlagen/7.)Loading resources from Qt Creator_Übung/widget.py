from PySide6.QtCore import Qt
from PySide6.QtWidgets import  QWidget
from ui_widget import Ui_Widget
from PySide6.QtGui import QIcon

import resource_rc  #You need to manually import the compiled resource file

class Widget(QWidget, Ui_Widget):
        def __init__(self):
                super().__init__()
                
                self.setupUi(self)
                self.setWindowTitle("User data")
                self.spin_box.setValue(50)
                self.plus_button.clicked.connect(self.plus)     
                self.minus_button.clicked.connect(self.minus)
                
                #plus_icon = QIcon(":/plus.png")
                #minus_icon = QIcon(":/minus.png")
                
                #self.plus_button.setIcon(plus_icon)
                #self.minus_button.setIcon(minus_icon)
                
        def plus(self):
                value = self.spin_box.value()
                self.spin_box.setValue(value + 1)
                
        def minus(self):
                value = self.spin_box.value()
                self.spin_box.setValue(value - 1)
                
                
                
                        
                
                
                
