# -*- coding: UTF-8 -*-

import MySQLdb
from eventdriven import *
from datetime import datetime
from collections import OrderedDict


class DataFetcher(object):
    """
    DataFetcher is used to fetch market data, and save them to mysql database
    """

    def __init__(self):
        """ Connect to mysql server, and generate a cursor """
        self.__con = MySQLdb.connect('localhost', 'yaokai', '123456', 'Test')
        self.__cursor = self.__con.cursor()

    def __del__(self):
        """ Remember to close the connection to mysql server """
        self.__con.close()

    def registerListeners(self, engine):
        """ register listener function to the event driven engine """
        engine.registerListener(EVENT_MD_DATA, self.onMdData)

    def onMdData(self, event):
        """
        Listener function to be registered to a event driven engine.
        This function save the market data to mysql
        """

        def toSqlStr(obj):
            if type(obj) == str:
                return "'" + str(obj) + "'"
            else:
                return str(obj)

        data = OrderedDict(event.data)
        productName = data['InstrumentID']
        tableName = productName + '_' + (str(datetime.today()).split(' ')[0]).replace('-', '_')
        transDict = {int : 'int', float : 'double', str : 'char(20)'}



        self.__cursor.execute("CREATE TABLE IF NOT EXISTS "
                              + tableName
                              + " ("
                              + ", ".join(key + " " + transDict[type(value)] for key, value in data.items())
                              + ");")
        self.__cursor.execute("INSERT INTO "
                              + tableName
                              + " (" + ", ".join(data.keys()) + ") "
                              + "VALUE"
                              + " (" + ", ".join(toSqlStr(value) for value in data.values()) + ");")

        self.__con.commit()


if __name__ == '__main__':
    dataFetcher = DataFetcher()
    data = {'InstrumentID' : 'FUCK666', 'Num' : 2333, 'Weight' : 88.88}
    transDict = {int : 'int', float : 'double', str : 'char(20)'}
    print(" (" + ", ".join(key + " " + transDict[type(value)] for key, value in data.items()) + ");")
    event = Event(data=data)
    dataFetcher.onMdData(event)




