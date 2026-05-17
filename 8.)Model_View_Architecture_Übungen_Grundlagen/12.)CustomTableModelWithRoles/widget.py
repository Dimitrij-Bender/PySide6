from PySide6.QtCore import QDir, QModelIndex, QStringListModel, Qt
from PySide6.QtWidgets import QFileSystemModel, QTableWidgetItem, QTreeWidgetItem, QWidget, QFileDialog, QMessageBox
from PySide6.QtGui import QStandardItemModel, QStandardItem
from ui_widget import Ui_Widget
from tablemodel import TableModel


class Widget(QWidget, Ui_Widget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Custom TableModel") 
        
        self.model = TableModel()
        self.tableView.setModel(self.model)
        
        
        
        
            
    
        
    

        
        
        
        
            
    
        



    
        
        
