# encoding: UTF-8

import sys
from PyQt4 import QtGui
from time import sleep

from vnctptd import *
from eventdriven import *


class TestTdApi(TdApi):

    def __init(self):
        super(TestTdApi, self).__init__()
        self.__reqid = 0
        self.__engine = engine
        self.__engine.start()

    def onFrontConnected(self):
        print u'td服务器连接'

    def onFrontDisConnected(self, n):
        print u'td服务器断开'

    def onRspUserLogin(self, data, error, n, last):
        state = {'n' : n, 'last' : last}
        event = Event(EVENT_TD_LOGIN, data, error, state)
        self.__engine.put(event)
        #print u'用户登录'

    def onRspUserLogout(self, data, error, n, last):
        state = {'n' : n, 'last' : last}
        event = Event(EVENT_TD_LOGOUT, data, error, state)
        self.__engine.put(event)
        #print u'用户登出'

    def onRspQrySettlementInfo(self, data, error, n, last):
        f = open('testcoding', mode='a', buffering=1)
        for key, value in data.items():
            f.write(str(key).decode('gbk').encode('utf-8') + ':' + str(value).decode('gbk').encode('utf-8') + '\n')
        f.write(str(error))

    def onRspSettlementInfoConfirm(self, data, error, n, last):
        pass

    def onRspQryInstrument(self, data, error, n, last):
        f = open('instruments', mode='a', buffering=1)
        for key, value in data.items():
            f.write(str(key).decode('gbk').encode('utf-8') + ':' + str(value).decode('gbk').encode('utf-8') + '\n')
        f.write(str(error))


def main():

    reqid = 0

    app = QtGui.QApplication(sys.argv)

    td = TestTdApi()

    td.createFtdcTraderApi('')

    td.subscribePrivateTopic(1)
    td.subscribePublicTopic(1)

    td.registerFront("tcp://180.168.146.187:10000")

    td.init()
    sleep(0.5)

    loginReq = {}
    loginReq['UserID'] = '020956'
    loginReq['Password'] = '18936803910'
    loginReq['BrokerID'] = '9999'
    reqid += 1
    td.reqUserLogin(loginReq, reqid)
    sleep(0.5)

    #reqid += 1
    #td.reqQryInstrument({}, reqid)

    req = {}
    req['BrokerID'] = '9999'
    req['InvestorID'] = '020956'

    reqid += 1
    td.reqQrySettlementInfo(req, reqid)
    sleep(0.5)

    reqid += 1
    td.reqSettlementInfoConfirm(req, reqid)
    sleep(0.5)

    app.exec_()

if __name__ == '__main__':
    main()

