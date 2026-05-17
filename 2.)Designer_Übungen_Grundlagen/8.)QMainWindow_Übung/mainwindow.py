from PySide6.QtCore import Qt
from PySide6.QtWidgets import  QApplication, QMainWindow, QMessageBox, QWidget

#from ui_mainwindow import Ui_MainWindow
from ui_widget import Ui_Widget

#import resource_rc  #You need to manually import the compiled resource file

#class MainWindow(QMainWindow, Ui_MainWindow):
class MainWindow(QWidget, Ui_Widget):
        def __init__(self,app):
                super().__init__()
                self.setupUi(self)
                self.app = app
                
                #self.actionQuit.triggered.connect(self.quit)
                #self.actionCopy.triggered.connect(self.copy)
                #self.actionCut.triggered.connect(self.cut)
                #self.actionPaste.triggered.connect(self.paste)
                #self.actionUndo.triggered.connect(self.undo)
                #self.actionRedo.triggered.connect(self.redo)
                #self.actionAbout.triggered.connect(self.about)
                self.actionAboutQt.triggered.connect(self.aboutQt)
                
        def quit(self):
                self.app.quit()
        def copy(self):
                self.app.copy() 
        def cut(self):
                self.app.cut() 
        def paste(self):
                self.app.paste() 
        def undo(self):
                self.app.undo()
        def redo(self):
                self.app.redo() 
        def about(self):
                QMessageBox.information(self, "Going pro!", "QMainWidow, Qt Designer and Re")
        def aboutQt(self):
                QApplication.aboutQt()
                
                
                
                        
                
                
                
