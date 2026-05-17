from PySide6.QtCore import Qt, QTextStream, QFile, QIODevice, QIODevice, QByteArray, QUrl
from PySide6.QtWidgets import QWidget, QFileDialog, QMessageBox
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from ui_widget import Ui_Widget


class Widget(QWidget, Ui_Widget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("QNetworkAccessManager") 
        
        self.manager = QNetworkAccessManager(self)
        self.m_data_buffer = QByteArray() #The buffer where you will be the data you get 
        self.request = QNetworkRequest() #The request object that will be used to make the request
        self.request.setUrl(QUrl("https://www.iq.io"))
        #self.request.setUrl(QUrl("https://www.github.com/"))
        #self.request.setUrl(QUrl("https://www.twitter.com/"))
        
        self.net_reply = self.manager.get(self.request) #Make the request and get the reply object
        
        self.net_reply.readyRead.connect(self.data_ready_to_read) #Connect the readyRead signal to the data_ready_to_read slot
        self.net_reply.finished.connect(self.data_read_finished) #Connect the finished signal to the data_read_finished slot
        
    def data_ready_to_read(self):
        print("Some data available")
        self.m_data_buffer.append(self.net_reply.readAll()) #Read the data and append it
            
    def data_read_finished(self):
        print("Data read finished")
        if( self.net_reply.error()):
            print("Some error occurred")
        else:
            self.testEdit.setText(str(self.m_data_buffer)) #Set the text of the text edit to the data buffer
                
        
        
        
            
    
        



    
        
        
