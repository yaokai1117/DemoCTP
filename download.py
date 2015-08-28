# encoding: UTF-8
import sys
import csv

from PyQt4 import QtGui
from time import sleep
from datetime import datetime
from threading import Lock
from vnctpmd import *


class TestMdApi(MdApi):

    def __init__(self):
        super(TestMdApi, self).__init__()
        self.usefulHeaders = ['InstrumentID', 'LastPrice', 'BidPrice1', 'BidVolume1', 'AskPrice1', 'AskVolume1', 'Volume', 'UpdateTime', 'UpdateMillisec' ]
        self.names = {'CF601', 'IF1508'}
        self.files = { name : open(name+'-'+str(datetime.today()).split(' ')[0]+'.csv', mode='a', buffering=1) for name in self.names }
        self.f_csvs = { name : csv.DictWriter(file, self.usefulHeaders) for name, file in self.files.items() }
        self.csv_locks = { name : Lock() for name in self.names }
        for f_csv in self.f_csvs.values():
            f_csv.writeheader()

    def __del__(self):
        for file in self.files.values():
            file.close()

    def onFrontConnected(self):
        print u'已连接服务器'

    def onFrontDisconnected(self, n):
        print u'服务器已断开：' + n

    def onRspError(self, error, n, last):
        print u'错误'
        print error
        print n

    def onRspUserLogin(self, data, error, n, last):
        print u'用户登录'
        print data
        print error

    def onRspUserLogout(self, data, error, n, last):
        print u'用户登出'
        print data
        print error

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
        print u'深度行情通知'
        useful_dict = { key:value for key, value in data.items() if key in self.usefulHeaders}
        self.csv_locks[useful_dict['InstrumentID']].acquire()
        self.f_csvs[useful_dict['InstrumentID']].writerow(useful_dict)
        self.csv_locks[useful_dict['InstrumentID']].release()


def main():
    reqid = 0

    app = QtGui.QApplication(sys.argv)

    md = TestMdApi()

    md.createFtdcMdApi('')

    md.registerFront('tcp://180.168.146.187:10010')

    md.init()
    sleep(0.5)

    loginReq = {}
    loginReq['UserID'] = '020956'
    loginReq['Password'] = '18936803910'
    loginReq['BrokerID'] = '9999'
    reqid = reqid + 1
    i = md.reqUserLogin(loginReq, 1)
    sleep(0.5)

    day = md.getTradingDay()
    print day

    md.subscribeMarketData('CF601')
    sleep(0.5)
    #md.subscribeMarketData('FG601')
    #sleep(0.5)
    #md.subscribeMarketData('IC1508')
    #sleep(0.5)
    md.subscribeMarketData('IF1508')
    #sleep(0.5)
    #md.subscribeMarketData('JR511')
    #sleep(0.5)
    #md.subscribeMarketData('LR605')
    #sleep(0.5)
    #md.subscribeMarketData('MA601')
    #sleep(0.5)
    #md.subscribeMarketData('OI601')
    #sleep(0.5)

   # i = md.subscribeForQuoteRsp('IF1508')
    #sleep(1)
    #i = md.unSubscribeForQuoteRsp('IO1504-C-3900')

    #md.reqUserLogout(loginReq, 1)
    app.exec_()

if __name__ == '__main__':
    main()



