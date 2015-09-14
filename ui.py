# -*- coding: utf-8 -*-

import sys
import os
import shelve
from PyQt4 import QtGui, QtCore

from listeners import *
from eventdriven import *
from ctp import *


class LoginDialog(QtGui.QDialog):
    # login dialog

    def __init__(self, ctp):
        super(LoginDialog, self).__init__()

        self.__ctp = ctp

        self.setWindowTitle('Login')

        self.userid = QtGui.QLineEdit(self)
        self.userid.setPlaceholderText('UserID')
        self.passwd = QtGui.QLineEdit(self)
        self.passwd.setPlaceholderText('PassWord')
        self.mdAddress = QtGui.QLineEdit(self)
        self.mdAddress.setPlaceholderText('Md Server Address')
        self.tdAddress = QtGui.QLineEdit(self)
        self.tdAddress.setPlaceholderText('Td Server Address')
        self.brokerid = QtGui.QLineEdit(self)
        self.brokerid.setPlaceholderText('BrokerID')
        self.buttonLogin = QtGui.QPushButton('Login', self)
        self.buttonLogin.clicked.connect(self.handleLogin)

        self.statusBar = QtGui.QStatusBar()

        self.connect(self, QtCore.SIGNAL('successSignal'), self.accept)

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.userid)
        layout.addWidget(self.passwd)
        layout.addWidget(self.mdAddress)
        layout.addWidget(self.tdAddress)
        layout.addWidget(self.brokerid)
        layout.addWidget(self.buttonLogin)
        layout.addWidget(self.statusBar)

        self.readCache()

    def registerListeners(self, engine):
        engine.registerListener(EVENT_MD_LOGIN, self.onMdLogin)
        engine.registerListener(EVENT_TD_LOGIN, self.onTdLogin)

    def handleLogin(self):
        self.cache()
        self.__ctp.login(str(self.userid.text()), str(self.passwd.text()), str(self.mdAddress.text()), str(self.tdAddress.text()), str(self.brokerid.text()))
        #sleep(0.3)
        #self.emit(QtCore.SIGNAL('successSignal'))

    def cache(self):
        # remember the user config
        conf = shelve.open('login.conf')
        conf['userid'] = str(self.userid.text())
        conf['passwd'] = str(self.passwd.text())
        conf['mdAddress'] = str(self.mdAddress.text())
        conf['tdAddress'] = str(self.tdAddress.text())
        conf['brokerid'] = str(self.brokerid.text())
        conf.close()

    def readCache(self):
        # read the userconfig
        if os.path.exists(os.getcwd() + '/login.conf'):
            conf = shelve.open('login.conf', 'r')
            self.userid.setText(conf['userid'])
            self.passwd.setText(conf['passwd'])
            self.mdAddress.setText(conf['mdAddress'])
            self.tdAddress.setText(conf['tdAddress'])
            self.brokerid.setText(conf['brokerid'])
            conf.close()

    def onMdLogin(self, event):
        if event.error['ErrorID'] == 0:
            self.statusBar.showMessage('Md login succeed!')
        else:
            self.statusBar.showMessage('Md login failed, errorMsg: ' + event.error['ErrorMsg'].decode('gbk'))

    def onTdLogin(self, event):
        if event.error['ErrorID'] == 0:
            self.statusBar.showMessage('Td login succeed!')
            self.emit(QtCore.SIGNAL('successSignal'))
        else:
            self.statusBar.showMessage('Td login failed, errorMsg: ' + event.error['ErrorMsg'].decode('gbk'))


#class SettlementPane(QtGui.QWidget):
#    def __init__(self, parent=None):
#        super(SettlementPane, self).__init__(parent)




class OprationBox(QtGui.QWidget):
    def __init__(self, parent=None, ctp=None):
        super(OprationBox, self).__init__(parent)
        self.__ctp = ctp

        self.setGeometry(0, 0, 100, 270)

        self.instrument = QtGui.QLineEdit(self)
        self.instrument.setPlaceholderText('InstrumentID')
        self.mdSubButton = QtGui.QPushButton('MdSubscribe', self)
        self.mdSubButton.clicked.connect(lambda : self.__ctp.subMdData(str(self.instrument.text())))
        self.mdUnSubButton = QtGui.QPushButton('MdUnSubscribe', self)
        self.mdUnSubButton.clicked.connect(lambda : self.__ctp.unsubMdData(str(self.instrument.text())))

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.instrument)
        layout.addWidget(self.mdSubButton)
        layout.addWidget(self.mdUnSubButton)


class MdTable(QtGui.QTableWidget):
    #a table showing marketdata

    def __init__(self, parent=None, ctp=None):
        super(MdTable, self).__init__(parent)
        self.__ctp = ctp

        self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.setGeometry(100, 0, 920, 270)

        self.setColumnCount(9)
        self.setRowCount(8)

        headers = [u'商品代码', u'最新价', u'买一价', u'买量', u'卖一价', u'卖量', u'仓量', u'更新时间', u'更新毫秒']
        self.setHorizontalHeaderLabels(headers)

        self.products = {}

    def registerListeners(self, engine):
        engine.registerListener(EVENT_MD_DATA, self.onMdData)

    def updateRow(self, data, rowNum):
        usefulHeaders = ['InstrumentID', 'LastPrice', 'BidPrice1', 'BidVolume1', 'AskPrice1', 'AskVolume1', 'Volume', 'UpdateTime', 'UpdateMillisec']
        for n, name in enumerate(usefulHeaders):
                newItem = QtGui.QTableWidgetItem(str(data[name]))
                self.setItem(rowNum, n, newItem)

    def refresh(self):
        pass

    def onMdData(self, event):
        usefulHeaders = ['InstrumentID', 'LastPrice', 'BidPrice1', 'BidVolume1', 'AskPrice1', 'AskVolume1', 'Volume', 'UpdateTime', 'UpdateMillisec']
        if event.data['InstrumentID'] in self.products.keys():
            self.updateRow(event.data, self.products[event.data['InstrumentID']])
        elif len(self.products) < 8:
            maxLen = len(self.products)
            self.products[event.data['InstrumentID']] = maxLen
            self.updateRow(event.data, maxLen)
        else:
            self.errorTooMuchMdSub(event.data['InstrumentID'])

    def errorTooMuchMdSub(self, instrument):
        print('Too much md sub!!')
        self.__ctp.unsubMdData(instrument)


class DemoGUI(QtGui.QMainWindow):

    def __init__(self, ctp):
        super(DemoGUI, self).__init__()
        self.__mainWidget = QtGui.QWidget()
        self.__ctp = ctp
        self.setCentralWidget(self.__mainWidget)
        self.initUI()

    def initUI(self):
        self.statusBar().showMessage('Ready')
        self.setGeometry(200, 200, 1020, 720)
        self.setWindowTitle('DemoGUI')

        # exit action in file menu
        exitAction = QtGui.QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit Application')
        exitAction.triggered.connect(QtGui.qApp.quit)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)

        self.opBox = OprationBox(self, self.__ctp)
        self.mdTable = MdTable(self, self.__ctp)

        grid = QtGui.QGridLayout(self.__mainWidget)

    def registerListeners(self, engine):
        self.mdTable.registerListeners(engine)



def main():
    app = QtGui.QApplication(sys.argv)


    engine = EventDispatcher()
    engine.start()
    engine.registerListener(EVENT_MD_LOGIN, onMdLogin)
    engine.registerListener(EVENT_MD_DATA, onMdData)
    engine.registerListener(EVENT_TD_LOGIN, onTdLogin)

    ctp = Ctp()
    ctp.registerEngine(engine)

    loginDialog = LoginDialog(ctp)
    loginDialog.registerListeners(engine)

    if loginDialog.exec_() == QtGui.QDialog.Accepted:
        window = DemoGUI(ctp)
        window.registerListeners(engine)
        window.show()
        ctp.qrySettleInfo()
        ctp.qryAccount()
        ctp.qryInvesor()

        #md.subscribe('CF509')
        #md.subscribe('CF511')
        #md.subscribe('IF1509')
        #md.subscribe('CF601')
        #md.subscribe('CF603')
        #md.subscribe('CF605')
        #md.subscribe('CF607')
        #md.subscribe('IF1510')
        #md.subscribe('IF1512')
        

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
