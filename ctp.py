# encoding: UTF-8

from mdapi import *
from tdapi import *
from eventdriven import *


class Ctp(object):
    """
    a encapsuation of the active functions of CTP api,
    include tdapi and mdapi
    """

    def __init__(self):
        self.__md = TestMdApi()
        self.__td = TestTdApi()

    def registerEngine(self, engine):
        self.__md.registerEngine(engine)
        self.__td.registerEngine(engine)

    def login(self, username, password, mdAddress, tdAddress, brokerid):
        self.__md.login(username, password, mdAddress, brokerid)
        self.__td.login(username, password, tdAddress, brokerid)

    def subMdData(self, instrument):
        self.__md.subscribe(instrument)

    def unsubMdData(self, instrument):
        self.__md.unsubscribe(instrument)

    def qrySettleInfo(self):
        self.__td.qrySettlementInfo()

    def qryAccount(self):
        self.__td.qryAccount()

    def qryInvesor(self):
        self.__td.qryInvestor()

    ##########################
    # fyabc
    ##########################
    def sendOrder(self):
        #发单
        pass

    ##########################
    # end fyabc
    ##########################
