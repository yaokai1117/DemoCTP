# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FinanceKMainWindow.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
from financek1d import FinanceK1d,FinanceK2d

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(QtGui.QMainWindow):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(1034, 669)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.pushButton = QtGui.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(50, 20, 75, 23))
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.pushButton_2 = QtGui.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(140, 20, 75, 23))
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(10, 50, 1011, 581))
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab_1 = FinanceK1d()
        self.tab_1.setObjectName(_fromUtf8("financeK1d"))
        self.tabWidget.addTab(self.tab_1, _fromUtf8(""))
        self.tab_2 = FinanceK2d()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 934, 23))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.pushButton.setText(_translate("MainWindow", "开始", None))
        self.pushButton_2.setText(_translate("MainWindow", "暂停", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_1), _translate("MainWindow", "1 day", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "1 week", None))

