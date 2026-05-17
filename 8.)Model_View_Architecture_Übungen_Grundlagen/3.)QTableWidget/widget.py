from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidgetItem, QWidget, QFileDialog, QMessageBox
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from ui_widget import Ui_Widget


class Widget(QWidget, Ui_Widget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("QTableWidget") 
        
        self.list_items_button.clicked.connect(self.list_items)
        self.set_item_button.clicked.connect(self.set_items)
        
    def list_items(self):
        rows = self.tableWidget.rowCount()
        columns = self.tableWidget.columnCount()
        for r in range(rows):
            for c in range(columns):
                item = self.tableWidget.item(r, c)
                if (item):
                    data = item.data(Qt.DisplayRole)
                    print(data)
                else:
                    print("No data")
                    
    def set_items(self):
        self.tableWidget.insertRow(self.tableWidget.rowCount())
        self.tableWidget.insertColumn(self.tableWidget.columnCount())
        
        item = QTableWidgetItem("Hello")
        self.tableWidget.setItem(self.tableWidget.rowCount() - 1, self.tableWidget.columnCount() - 1, item)
        
        
        
        

            
    
        
    

        
        
        
        
            
    
        



    
        
        
