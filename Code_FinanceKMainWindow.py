# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 23:10:18 2015

@author: fanyang
"""

from PyQt4 import QtCore, QtGui
from FinanceKMainWindow import Ui_MainWindow

class Code_MainWindow(Ui_MainWindow):
    def __init__(self, parent = None):
        super(Code_MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.startPlot)
        self.pushButton_2.clicked.connect(self.pausePlot)
    def startPlot(self):
        ''' begin to plot'''
        self.tab_1.startPlot()
        self.tab_2.startPlot()
        pass
    def pausePlot(self):
        ''' pause plot '''
        self.tab_1.pausePlot()
        self.tab_2.pausePlot()
        pass
    def releasePlot(self):
        ''' stop and release thread'''
        self.tab_1.releasePlot()
        self.tab_2.releasePlot()
    def closeEvent(self,event):
        result = QtGui.QMessageBox.question(self,
                                            "Confirm Exit...",
                                            "Are you sure you want to exit ?",
                                            QtGui.QMessageBox.Yes| QtGui.QMessageBox.No)
        event.ignore()
        if result == QtGui.QMessageBox.Yes:
            self.releasePlot()#release thread's resouce
            event.accept()
if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ui = Code_MainWindow()
    ui.show()
    sys.exit(app.exec_())
