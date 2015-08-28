# encoding: UTF-8

import os
import sys

from PyQt4 import QtGui
from time import sleep
from vnctpmd import *
from eventdriven import *
from listeners import *

class TestMdApi(MdApi):

    def __init__(self, engine):
        super(TestMdApi, self).__init__()
        self.__reqid = 0
        self.__engine = engine
        self.__engine.start()
        self.createFtdcMdApi(os.getcwd() + '\\mdconnection\\')

        #self.usefulHeaders = ['InstrumentID', 'LastPrice', 'BidPrice1', 'BidVolume1', 'AskPrice1', 'AskVolume1', 'Volume', 'UpdateTime', 'UpdateMillisec' ]

    def __del__(self):
        pass

    def onFrontConnected(self):
        print u'md已连接服务器'

    def onFrontDisconnected(self, n):
        print u'md服务器已断开：' + n

    def onRspError(self, error, n, last):
        state = {'n' : n, 'last' : last}
        event = Event(EVNET_MD_RSPERROR, error=error, state=state)
        self.__engine.put(event)
        #print u'错误'


    def onRspUserLogin(self, data, error, n, last):
        state = {'n' : n, 'last' : last}
        event = Event(EVENT_MD_LOGIN, data, error, state)
        self.__engine.put(event)
        #print u'用户登录'


    def onRspUserLogout(self, data, error, n, last):
        state = {'n' : n, 'last' : last}
        event = Event(EVENT_MD_LOGOUT, data, error, state)
        self.__engine.put(event)
        #print u'用户登出'

    def onRspSubMarketData(self, data,error, n, last):
        #print u'订阅行情应答'
        #print data
        #print error
        pass

    def onRspUnSubMarketData(self, data, error, n, last):
        #print u'退订行情应答'
        #print data
        #print error
        pass

    def onRtnDepthMarketData(self, data):
        event = Event(type=EVENT_MD_DATA, data=data)
        self.__engine.put(event)
        #print u'深度行情通知'


    # 以下为主动函数
    def login(self, username, password, address, brokerid):
        self.registerFront(address)         #self.registerFront('tcp://180.168.146.187:10010')
        self.init()
        sleep(0.5)
        loginReq = {}
        loginReq['UserID'] = username       #'020956'
        loginReq['Password'] = password     #'18936803910'
        loginReq['BrokerID'] = brokerid     #'9999'
        self.__reqid = self.__reqid + 1
        self.reqUserLogin(loginReq, 1)

    def subscribe(self, instrumentID):
        self.subscribeMarketData(instrumentID)

    def unsubscribe(self, instrumentID):
        self.unSubscribeMarketData(instrumentID)

    def registerListener(self, event_type, listener):
        self.__engine.registerListener(event_type, listener)

def main():

    app = QtGui.QApplication(sys.argv)
    engine = EventDispatcher()
    engine.registerListener(EVENT_MD_LOGIN, onMdLogin)
    engine.registerListener(EVNET_MD_RSPERROR, onMdError)
    engine.registerListener(EVENT_MD_LOGOUT, onMdLogout)
    engine.registerListener(EVENT_MD_DATA, onMdData)

    md = TestMdApi(engine)
    md.login('020956', '18936803910', 'tcp://180.168.146.187:10010','9999')
    md.subscribe('CF509')
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()



