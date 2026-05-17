
from PySide6.QtWidgets import  QWidget, QPushButton, QVBoxLayout, QMessageBox
from PySide6.QtCore import QSize



class Widget(QWidget):
        def __init__(self):
                super().__init__()
                
                self.setWindowTitle("QMessageBox")
                
                button_hard = QPushButton("Hard")
                button_hard.clicked.connect(self.button_clicked_hard) 
                 
                button_critical = QPushButton("Critical")
                button_critical.clicked.connect(self.button_clicked_critical)
                
                button_question = QPushButton("Question")
                button_question.clicked.connect(self.button_clicked_question)
                
                button_information = QPushButton("Information")
                button_information.clicked.connect(self.button_clicked_information)
                
                button_warning = QPushButton("Warning")
                button_warning.clicked.connect(self.button_clicked_warning)
                
                button_about = QPushButton("About")
                button_about.clicked.connect(self.button_clicked_about)
                
                
                # Set up the layouts
                layout = QVBoxLayout()
                layout.addWidget(button_hard)
                layout.addWidget(button_critical)
                layout.addWidget(button_question)
                layout.addWidget(button_information)
                layout.addWidget(button_warning)
                layout.addWidget(button_about)
                self.setLayout(layout)
                
        def button_clicked_hard(self):
                #print("Hard")
                message = QMessageBox()
                message.setMinimumSize(QSize(700,200))
                message.setWindowTitle("Message Title")
                message.setText("Something happened")
                #message.setInformativeText("Informative text")
                message.setDetailedText("Do you want to do something about it?")
                message.setIcon(QMessageBox.Critical)
                message.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                message.setDefaultButton(QMessageBox.Ok)
                
                #Show the message box
                ret = message.exec()
                if ret == QMessageBox.Ok:
                        print("User clicked OK")
                else: 
                        print("User clicked Cancel")
        def button_clicked_critical(self):
                #print("Critical")
                ret = QMessageBox.critical(self, "Message Title",
                                           "Something critical happened",
                                           QMessageBox.Ok | QMessageBox.Cancel)
                if ret == QMessageBox.Ok:
                        print("User clicked OK")
                else: 
                        print("User clicked Cancel")
        def button_clicked_question(self):      
                #print("Question")
                ret = QMessageBox.question(self, "Message Title",
                                           "Something happened",
                                           QMessageBox.Ok | QMessageBox.Cancel)
                if ret == QMessageBox.Ok:
                        print("User clicked OK")
                else: 
                        print("User clicked Cancel")
        def button_clicked_information(self):
                #print("Information")
                ret = QMessageBox.information(self, "Message Title",
                                              "Something information happened",
                                              QMessageBox.Ok | QMessageBox.Cancel)
                if ret == QMessageBox.Ok:
                        print("User clicked OK")
                else: 
                        print("User clicked Cancel")
        def button_clicked_warning(self):
                #print("Warning")
                ret = QMessageBox.warning(self, "Message Title",
                                          "Something warning happened",
                                          QMessageBox.Ok | QMessageBox.Cancel)
                if ret == QMessageBox.Ok:
                        print("User clicked OK")
                else: 
                        print("User clicked Cancel")
        def button_clicked_about(self):
                #print("About")
                ret = QMessageBox.about(self, "Message Title",
                                          "Something about happened")
                if ret == QMessageBox.Ok:
                        print("User clicked OK")
                else: 
                        print("User clicked Cancel")
                
                
                
                """
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
                        
                         
                
                
                
                
                
        def button1_click(self): 
                print("Clicked on the button")
                  
                     
                
        def quit_app(self):
                self.app.quit()
                
        def toolbar_button_click(self):
                self.statusBar().showMessage("Message from my app", 3000)
                
                #print("action1 triggered")
                
                """