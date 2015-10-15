# -*- coding: utf-8 -*-

import sys
import os
import json
from collections import OrderedDict
from PyQt4 import QtGui, QtCore

from listeners import *
from eventdriven import *
from ctp import *

from fetchdata import DataFetcher

# fyabc
from chartPlotter import ChartWidget


class LoginDialog(QtGui.QDialog):
    """
    Loging dialog.
    User input his address, id, password and broker id here,
    if td account login successfully, this dialog is accepted.
    """

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

        # accept signal
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
        """ save the user config"""
        confFile = open('login.json', 'w')
        conf = dict()
        conf['userid'] = str(self.userid.text())
        conf['passwd'] = str(self.passwd.text())
        conf['mdAddress'] = str(self.mdAddress.text())
        conf['tdAddress'] = str(self.tdAddress.text())
        conf['brokerid'] = str(self.brokerid.text())
        json.dump(conf, confFile)
        confFile.close()

    def readCache(self):
        """ read the userconfig"""
        if os.path.exists(os.getcwd() + '/login.json'):
            confFile = open('login.json', 'r')
            conf = json.load(confFile)
            self.userid.setText(conf['userid'])
            self.passwd.setText(conf['passwd'])
            self.mdAddress.setText(conf['mdAddress'])
            self.tdAddress.setText(conf['tdAddress'])
            self.brokerid.setText(conf['brokerid'])
            confFile.close()

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


class OprationBox(QtGui.QWidget):
    """
    This box is for market data operations such as subscribing market data of a product
    """

    subSignal = QtCore.pyqtSignal(str, name='subSignal')
    unsubSignal = QtCore.pyqtSignal(str, name='unsubSignal')

    def __init__(self, parent=None, ctp=None):
        super(OprationBox, self).__init__(parent)
        self.__ctp = ctp

        self.setGeometry(0, 0, 100, 270)

        self.instrument = QtGui.QLineEdit(self)
        self.instrument.setPlaceholderText('InstrumentID')
        self.mdSubButton = QtGui.QPushButton('Subscribe', self)
        self.mdSubButton.clicked.connect(self.handleClickSub)
        self.mdUnSubButton = QtGui.QPushButton('UnSubscribe', self)
        self.mdUnSubButton.clicked.connect(self.handleClickUnsub)

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.instrument)
        layout.addWidget(self.mdSubButton)
        layout.addWidget(self.mdUnSubButton)


    def handleClickSub(self):
        self.__ctp.subMdData(str(self.instrument.text()))
        self.subSignal.emit(str(self.instrument.text()))

    def handleClickUnsub(self):
        self.__ctp.unsubMdData(str(self.instrument.text()))
        self.unsubSignal.emit(str(self.instrument.text()))


class MdTable(QtGui.QTableWidget):
    """
    A table showing market data, automatically updates when new market data comes
    """

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

    def removeProduct(self, product_name):
        name = str(product_name)
        if name not in self.products:
            return
        rowNum = self.products[name]
        newProducts = {}
        for key, value in self.products.items():
            if key == name:
                continue
            if value > rowNum:
                newProducts[key] = value - 1
            else:
                newProducts[key] = value
        self.products = newProducts
        self.removeRow(rowNum)
        self.insertRow(len(self.products))

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


################################################
# fyabc
################################################
class MdKLineChart(QtGui.QTabWidget):
    """
    This subwindow is used to draw K line graph
    """
    def __init__(self, parent=None, ctp=None):
        super(MdKLineChart, self).__init__(parent)
        
        self.__ctp = ctp
        
        self.setGeometry(10, 275, 970, 440)
        
        self.tabs = {}                  # a dict of tabs for Instruments


    def registerListeners(self, engine):
        engine.registerListener(EVENT_MD_DATA, self.onMdData)

    def addInstrument(self,InstrumentID):
        InstrumentID = str(InstrumentID)
        if InstrumentID not in self.tabs.keys():
            temptab = ChartWidget(InstrumentID)
            self.addTab(temptab,InstrumentID)
            self.tabs[InstrumentID] = temptab

    def removeInstrument(self,InstrumentID):
        InstrumentID = str(InstrumentID)
        if InstrumentID in self.tabs.keys():
            self.removeTab(self.indexOf(self.tabs[InstrumentID]))
            self.tabs.pop(InstrumentID)

    def refresh(self):
        pass

    def onMdData(self,event):
        ''' send data to chartWidgets'''
        if event.data['InstrumentID'] in self.tabs.keys():
            (self.tabs[event.data['InstrumentID']]).updateData(event.data)
            pass


class TdBox(QtGui.QWidget):
    """
    A box for trading operations, such as sending an order
    """

    directionDict = OrderedDict()
    directionDict['0'] = u'买'
    directionDict['1'] = u'卖'

    offsetDict = OrderedDict()
    offsetDict['0'] = u'开仓'
    offsetDict['1'] = u'平仓'
    offsetDict['3'] = u'平今'

    priceTypeDict = OrderedDict()
    priceTypeDict['1'] = u'任意价'
    priceTypeDict['2'] = u'限价'
    priceTypeDict['3'] = u'最优价'
    priceTypeDict['4'] = u'最新价'

    directionReverseDict = {value:key for key,value in directionDict.items()}
    offsetReverseDict = {value:key for key, value in offsetDict.items()}
    priceTypeReverseDict = {value:key for key, value in priceTypeDict.items()}

    def __init__(self, parent=None, ctp=None):
        super(TdBox, self).__init__(parent)
        self.__ctp = ctp

        self.setGeometry(1020, 0, 275, 280)

        #Info of the order to be sent and editor
        labelID = QtGui.QLabel(u'合约代码')
        labelDirection = QtGui.QLabel(u'委托类型')
        labelOffset = QtGui.QLabel(u'开平')
        labelPrice = QtGui.QLabel(u'价格')
        labelVolume = QtGui.QLabel(u'手数')
        labelPriceType = QtGui.QLabel(u'价格类型')

        self.EditID = QtGui.QLineEdit()

        self.EditDirection = QtGui.QComboBox()
        self.EditDirection.addItems(self.directionDict.values())
        self.EditOffset = QtGui.QComboBox()
        self.EditOffset.addItems(self.offsetDict.values())

        self.EditPrice = QtGui.QDoubleSpinBox()
        self.EditPrice.setDecimals(2)
        self.EditPrice.setMinimum(0)
        self.EditPrice.setMaximum(1000000)

        self.EditVolume = QtGui.QSpinBox()
        self.EditVolume.setMinimum(0)
        self.EditVolume.setMaximum(1000000)

        self.EditPriceType = QtGui.QComboBox()
        self.EditPriceType.addItems(self.priceTypeDict.values())

        # Info Layout
        tdInfo = QtGui.QGridLayout()
        tdInfo.setColumnStretch(0,100)
        tdInfo.addWidget(labelID, 0, 0)
        tdInfo.addWidget(labelDirection, 1, 0)
        tdInfo.addWidget(labelOffset, 2, 0)
        tdInfo.addWidget(labelPrice, 3, 0)
        tdInfo.addWidget(labelVolume, 4, 0)
        tdInfo.addWidget(labelPriceType, 5, 0)
        tdInfo.addWidget(self.EditID, 0, 1)
        tdInfo.addWidget(self.EditDirection, 1, 1)
        tdInfo.addWidget(self.EditOffset, 2, 1)
        tdInfo.addWidget(self.EditPrice, 3, 1)
        tdInfo.addWidget(self.EditVolume, 4, 1)
        tdInfo.addWidget(self.EditPriceType, 5, 1)

        # button for sending order
        self.tdSendOrderButton = QtGui.QPushButton(u'发单', self)

        tdBoxLayout = QtGui.QVBoxLayout(self)
        tdBoxLayout.addLayout(tdInfo)
        tdBoxLayout.addWidget(self.tdSendOrderButton)

        self.tdSendOrderButton.clicked.connect(self.sendOrder)

    def registerListeners(self, engine):
        pass

    def sendOrder(self):
        instrumentId = str(self.EditID.text())

        exchangeId = 0
        direction = self.directionReverseDict[unicode(self.EditDirection.currentText())]
        offset = self.offsetReverseDict[unicode(self.EditOffset.currentText())]
        price = float(self.EditPrice.value())
        volume = int(self.EditVolume.value())
        priceType = self.priceTypeReverseDict[unicode(self.EditPriceType.currentText())]

        self.__ctp.sendOrder(instrumentId, exchangeId, price, priceType, volume, direction, offset)
        pass

###########################################################
# end fyabc
###########################################################


class DemoGUI(QtGui.QMainWindow):
    """
    Main window
    """

    def __init__(self, ctp):
        super(DemoGUI, self).__init__()

        self.__mainWidget = QtGui.QWidget()
        self.__ctp = ctp
        self.setCentralWidget(self.__mainWidget)

        self.bar = self.statusBar()

        self.opBox = OprationBox(self, self.__ctp)
        self.mdTable = MdTable(self, self.__ctp)
        self.mdKLineChart = MdKLineChart(self, self.__ctp)
        self.tdBox = TdBox(self, self.__ctp)

        self.initUI()

    def initUI(self):
        self.bar.showMessage('Ready')
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

        # connect the subcribe and unsubcribe button to the Chart Tab
        # fyabc
        self.opBox.subSignal.connect(self.mdKLineChart.addInstrument)
        self.opBox.unsubSignal.connect(self.mdKLineChart.removeInstrument)
        self.opBox.unsubSignal.connect(self.mdTable.removeProduct)

        grid = QtGui.QGridLayout(self.__mainWidget)

    def registerListeners(self, engine):
        self.mdTable.registerListeners(engine)
        self.mdKLineChart.registerListeners(engine)

    # def updateLog(self, event):
    #     log = event.error['log']
    #     self.bar.showMessage(log)


def main():
    app = QtGui.QApplication(sys.argv)

    engine = EventDispatcher()
    engine.start()
    engine.registerListener(EVENT_MD_LOGIN, onMdLogin)
    engine.registerListener(EVENT_MD_DATA, onMdData)
    engine.registerListener(EVENT_TD_LOGIN, onTdLogin)

    ctp = Ctp()
    ctp.registerEngine(engine)

    dataFetcher = DataFetcher()
    dataFetcher.registerListeners(engine)

    loginDialog = LoginDialog(ctp)
    loginDialog.registerListeners(engine)

    if loginDialog.exec_() == QtGui.QDialog.Accepted:
        window = DemoGUI(ctp)
        window.registerListeners(engine)
        window.show()
        window.showMaximized()
        ctp.qrySettleInfo()
        #ctp.qryAccount()
        #ctp.qryInvesor()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
