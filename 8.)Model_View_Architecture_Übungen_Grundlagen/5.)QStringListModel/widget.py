from PySide6.QtCore import QModelIndex, QStringListModel, Qt
from PySide6.QtWidgets import QTableWidgetItem, QTreeWidgetItem, QWidget, QFileDialog, QMessageBox
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from ui_widget import Ui_Widget


class Widget(QWidget, Ui_Widget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("QStringListModel - ListView") 
        
        self.model = QStringListModel(self)
        list = ["Cow", "Rooster", "Hyena", "Lion", "Wild Dog"]
        self.model.setStringList(list)
        
        self.listView.setModel(self.model)
        
        self.show_data_button.clicked.connect(self.show_data_button_clicked)
        
    def show_data_button_clicked(self):
        """
        #Read the data using QStringList API
        list = self.model.stringList()
        for s in list:
            print(s)
        """

        #Read the data using QAbstractItemModel API
        for i in range(self.model.rowCount(QModelIndex())):
            index = self.model.index(i, 0, QModelIndex())
            #data = index.data()
            #data = index.data(Qt.DisplayRole)
            #data = self.model.data(index)
            data = self.model.data(index, Qt.DisplayRole)
            print(data)
        
        

            
    
        
    

        
        
        
        
            
    
        



    
        
        
