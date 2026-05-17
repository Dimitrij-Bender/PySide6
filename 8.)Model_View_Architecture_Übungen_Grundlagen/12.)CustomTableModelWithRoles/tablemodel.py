from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import  Qt, QTime, QTimer
from PySide6.QtGui import QFont, QBrush

class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, *args, **kwargs):
        super(TableModel, self).__init__(*args, **kwargs)
        
        self.timer = QTimer(self)
        self.timer.setInterval(1000)  # Update every second
        self.timer.timeout.connect(self.timer_timeout)
        self.timer.start()
        
    def timer_timeout(self):
        top_left = self.index(0, 0)
        self.dataChanged.emit(top_left, top_left)  # Emit dataChanged for the top-left cell to update the time display
        
    def data(self, index, role):
        row = index.row()
        col = index.column()
        
        if role == Qt.DisplayRole:
            if(row == 0 and col == 1):
                return "<---left"
            if(row == 1 and col == 1):
                return "right--->"
            if(row == 0 and col == 0):
                return QTime.currentTime().toString()
            value = " [ Row : " + str(index.row()) + " , Column : " + str(index.column()) + " ] "
            return value
        #Font role
        if( role == Qt.FontRole):
            font = QFont()
            font.setBold(True)
            return font
        #Background role
        if( role == Qt.BackgroundRole):
            if( row == 1 and col == 2):
                background = QBrush(Qt.yellow)
                return background
        #Text alignment role
        if( role == Qt.TextAlignmentRole):
            if( row == 1 and col == 1):
                return Qt.AlignRight

        
    def rowCount(self, parent):  #How many rows do we have under index as parent?
        return 2
    
    def columnCount(self, parent):
        return 3