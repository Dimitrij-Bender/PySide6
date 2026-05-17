from PySide6.QtCore import QSize
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QMainWindow,QToolBar, QPushButton, QStatusBar



class MainWindow(QMainWindow):
        def __init__(self, app):
                super().__init__()
                self.app = app # declare an app member
                self.setWindowTitle("123 Custom MainWindow")
                
        def button_clicked_hard(self):
                message = QMessageBox()
                message.setMinimumSize(QSize(700,200))
                message.setWindowTitle("Message Title")
                message.setText("Something happened")
                message.setInformativeText("Informative text")
                message.setDetailedText("Do you want to do something about it?")
                message.setIcon(QMessageBox.Critical)
                message.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                message.setDefaultButton(QMessageBox.Ok)
                if ret == QMessageBox.Ok:
                        print("User clicked OK")
                else: 
                        print("User clicked Cancel")
                        
        def button_clicked_critical(self):
                ret = QMessageBox.critical(self, "Message Title",
                                           "Something critical happened",
                                           QMessageBox.Ok | QMessageBox.Cancel)  
                if ret == QMessageBox.Ok:
                        print("User clicked OK")
                else: 
                        print("User chose Cancel")   
                        
        button_hard = QPushButton("hard")
        button_hard.clicked.connect(self.button_clicked_hard)  
        button_critical = QPushButton("critical")
        button_critical.clicked.connect(self.button_clicked_critical)
        button_question = QPushButton("question")
        button_question.clicked.connect(self.button_clicked_question)
        button_warning = QPushButton("warning")
        button_warning.clicked.connect(self.button_clicked_warning)
        button_about = QPushButton("about")
        button_about.clicked.connect(self.button_clicked_about)                         
                
                
                
                
                
        def button1_click(self): 
                print("Clicked on the button")
                  
                     
                
        def quit_app(self):
                self.app.quit()
                
        def toolbar_button_click(self):
                self.statusBar().showMessage("Message from my app", 3000)
                
                #print("action1 triggered")