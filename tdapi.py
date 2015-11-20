# encoding: UTF-8

import sys
import os
from PyQt4 import QtGui
from time import sleep

from vnctptd import *
from eventdriven import *
from ctp_data_type import defineDict


class TestTdApi(TdApi):
    """
    TestTdApi is a encapsuation of CTP td api.
    It has two main part,
    call back functions which work with event driven engine,
    and active functions such as login, logout
    """

    def __init__(self):
        """
        Initialization.
        userid, password... is saved for sending an order
        """
        super(TestTdApi, self).__init__()
        self.__reqid = 0
        self.__orderref = 0     #报单编号
        self.__engine = None

        self.__userid = ''
        self.__passwd = ''
        self.__address = ''
        self.__brokerid = ''

        self.createFtdcTraderApi(os.getcwd() + '/tdconnection/')


    def registerEngine(self, engine):
        """ register a event driven engine, so that call back functions can put different event in """
        self.__engine = engine

    # call back functions here
    # this functions usually put an event to the event engine
    def onFrontConnected(self):
        print u'td服务器连接'

    def onFrontDisConnected(self, n):
        print u'td服务器断开'

    def onRspError(self, error, n, last):   # debug
        print(error)

    def onRspUserLogin(self, data, error, n, last):
        state = {'n' : n, 'last' : last}
        event = Event(EVENT_TD_LOGIN, data, error, state)
        self.__engine.put(event)
        print(data)
        print(error['ErrorMsg'])
        #print u'用户登录'

    def onRspQrySettlementInfo(self, data, error, n, last):
        for key, value in data.items():
            print(str(key).decode('gbk') + ':' + str(value).decode('gbk'))
        for key, value in error.items():
            print(str(key).decode('gbk') + ':' + str(value).decode('gbk'))
        state = {'n' : n, 'last' : last}
        event = Event(EVENT_TD_SETTLEINFO, data, error, state)
        self.__engine.put(event)

    def onRspSettlementInfoConfirm(self, data, error, n, last):
        for key, value in data.items():
            print(str(key).decode('gbk') + ':' + str(value).decode('gbk'))
        for key, value in error.items():
            print(str(key).decode('gbk') + ':' + str(value).decode('gbk'))
        state = {'n' : n, 'last' : last}
        event = Event(EVENT_TD_SETTLECONFIRM, data, error, state)
        self.__engine.put(event)

    def onRspOrderInsert(self, data, error, n, last):
        print(u'报单错误')
        print('ErrorID:' + str(error['ErrorID']) + ' ' + 'ErrorMsg:' + error['ErrorMsg'].decode('gbk'))

    def onRspOrderAction(self, data, error, n, last):
        print(u'撤单错误')
        print('ErrorID:' + str(error['ErrorID']) + ' ' + 'ErrorMsg:' + error['ErrorMsg'].decode('gbk'))

    def onRspQryInvestor(self, data, error, n, last):
        print(u'投资者回报')
        if error['ErrorID'] == 0:
            for key, value in data.items():
                print(str(key).decode('gbk') + ':' + str(value).decode('gbk'))
        else:
            print('ErrorID' + error['ErrorID'] + 'ErrorMsg' + error['ErrorMsg'])

    def onRspQryInvestorPosition(self, data, error, n, last):
        print(u'持仓回报')
        if error['ErrorID'] == 0:
            for key, value in data.items():
                print(str(key).decode('gbk') + ':' + str(value).decode('gbk'))
        else:
            print('ErrorID' + error['ErrorID'] + 'ErrorMsg' + error['ErrorMsg'])

    def onRspQryTradingAccount(self, data, error, n, last):
        print(u'账户查询回报')
        for key, value in data.items():
            print(str(key).decode('gbk') + ':' + str(value).decode('gbk'))
        for key, value in error.items():
            print(str(key).decode('gbk') + ':' + str(value).decode('gbk'))

    # active functions here
    # these functions can be called by user
    def login(self, userid, passwd, address, brokerid):
        """ login the td server """
        self.__address = address
        self.registerFront(address)
        self.init()
        sleep(0.5)

        self.subscribePrivateTopic(0)   # 数据重传模式设为从本日开始
        self.subscribePublicTopic(0)

        loginReq = {}
        loginReq['UserID'] = self.__userid = userid
        loginReq['Password'] = self.__passwd = passwd
        loginReq['BrokerID'] = self.__brokerid = brokerid
        self.__reqid += 1
        self.reqUserLogin(loginReq, self.__reqid)


    def qrySettlementInfo(self):
        """ do confirming automatically after query """
        req = {}
        req['BrokerID'] = self.__brokerid
        req['InvestorID'] = self.__userid

        self.__reqid += 1
        self.reqQrySettlementInfo(req, self.__reqid)

        self.__reqid += 1
        self.reqSettlementInfoConfirm(req, self.__reqid)

    def qryAccount(self):
        """ query account massage """
        self.__reqid += 1
        loginReq = {}
        loginReq['UserID'] = self.__userid
        loginReq['Password'] = self.__passwd
        loginReq['BrokerID'] = self.__brokerid
        self.reqQryTradingAccount(loginReq, self.__reqid)

    def qryInvestor(self):
        """ quety investor message """
        self.__reqid += 1
        self.reqQryInvestor({}, self.__reqid)

    def sendOrder(self, instrumentId, exchangeId, price, priceType, volume, direction, offset):
        """发单"""
        self.__reqid += 1
        req = {}

        req['InstrumentID'] = instrumentId
        req['OrderPriceType'] = priceType
        req['LimitPrice'] = price
        req['VolumeTotalOriginal'] = volume
        req['Direction'] = direction
        req['CombOffsetFlag'] = offset

        self.__orderref += 1
        req['OrderRef'] = str(self.__orderref)

        req['InvestorID'] = self.__userid
        req['UserID'] = self.__userid
        req['BrokerID'] = self.__brokerid
        req['CombHedgeFlag'] = defineDict['THOST_FTDC_HF_Speculation']       # 投机单
        req['ContingentCondition'] = defineDict['THOST_FTDC_CC_Immediately'] # 立即发单
        req['ForceCloseReason'] = defineDict['THOST_FTDC_FCC_NotForceClose'] # 非强平
        req['IsAutoSuspend'] = 0                                             # 非自动挂起
        req['TimeCondition'] = defineDict['THOST_FTDC_TC_GFD']               # 今日有效
        req['VolumeCondition'] = defineDict['THOST_FTDC_VC_AV']              # 任意成交量
        req['MinVolume'] = 1                                                 # 最小成交量为1

        self.reqOrderInsert(req, self.__reqid)

        # 返回订单号，便于某些算法进行动态管理
        return self.__orderref





