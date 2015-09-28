# -*- coding: UTF-8 -*-

import MySQLdb
from eventdriven import *
from datetime import datetime

class DataFetcher(object):
    '''
    DataFetcher is used to fetch market data, and save them to mysql database
    '''

    def __init__(self):
        self.__con = MySQLdb.connect('localhost', 'yaokai', '950808', 'Test')
        self.__cursor = self.__con.cursor()

    def __del__(self):
        self.__con.close()

    def registerListeners(self, engine):
        engine.registerListener(EVENT_MD_DATA, self.onMdData)

    def onMdData(self, event):
        data = event.data
        productName = data['InstrumentID']
        tableName = productName + (str(datetime.today()).split(' ')[0]).replace('-', '_')
        self.__cursor.execute("CREATE TABLE IF NOT EXISTS "
                              + tableName + " ("
                              + "InstrumentID char(20), "
                              + "LastPrice decimal, "
                              + "BidPrice1 decimal, "
                              + "BidVolume1 int, "
                              + "AskPrice1 decimal, "
                              + "AskVolume1 int, "
                              + "Volume int, "
                              + "UpdateTime char(20), "
                              + "UpdateMillisec int" + ");")
        self.__cursor.execute("INSERT INTO "
                              + tableName
                              + " (InstrumentID, LastPrice, BidPrice1, BidVolume1\
                              , AskPrice1, AskVolume1, Volume, UpdateTime, UpdateMillisec) "
                              + "VALUES"
                              + " ('%s', %s, %s, %s, %s, %s, %s, '%s', %s);"
                              % (data['InstrumentID'], data['LastPrice'], data['BidPrice1'], data['BidVolume1'],
                                 data['AskPrice1'], data['AskVolume1'], data['Volume'], data['UpdateTime'], data['UpdateMillisec']))

