# -*- coding: UTF-8 -*-

import MySQLdb
from eventdriven import *
from datetime import datetime


class MySqlHandler(object):
    """
    MySqlHandler is used to handle data transmission between our python application and mysql server.
    Some usually used operations are encapsulated in this class, such as insert, create table.
    """

    __metaclass__ = Singleton

    typeTransDict = {int: 'bigint', float: 'double', str: 'char(20)', unicode: 'char(60)'}

    def __init__(self, address, username, password, database):
        self.__con = MySQLdb.connect(address, username, password, database)
        self.__cursor = self.__con.cursor()
        self.__count = 0

    def __del__(self):
        self.__con.commit()
        self.__con.close()

    def createTable(self, tableName, header, types):
        """
        Create a table if it does not exist.
        :param header: a list of string, header of the table
        :param types: a list of type, data types correspond to header
        """

        self.__cursor.execute("CREATE TABLE IF NOT EXISTS "
                              + tableName
                              + " ("
                              + ", ".join(name + " " + self.typeTransDict[dataType] for name, dataType in zip(header, types))
                              + ");")
        self.__con.commit()

    def insert(self, tableName, data, fieldList=None):
        """
        Insert some value to a existing table.
        :param data: a dict to be insert into mysql database.
        :param fieldList: a list of str, if fieldList isn't none, a record will be insert only if its field is in fieldList
        """

        # transfer str to 'str'
        def toSqlStr(obj):
            if type(obj) == str:
                return "'" + str(obj) + "'"
            elif type(obj) == unicode:
                return "'" + obj.encode('utf-8') + "'"
            else:
                return str(obj)

        currentFieldList= data.keys()

        # check field
        if fieldList is not None:
            currentFieldList = fieldList

        self.__cursor.execute("INSERT INTO " +
                              tableName +
                              " (" + ", ".join(currentFieldList) + ") " +
                              "VALUE" +
                              " (" + ", ".join(toSqlStr(data[field]) for field in currentFieldList) + ");")

        self.__count += 1
        if self.__count == 50:
            self.__con.commit()
            self.__count = 0


class DataFetcher(object):
    """
    DataFetcher is used to fetch market data, and save them to mysql database
    """

    __metaclass__ = Singleton

    def __init__(self):
        """ Init a MySqlHandler"""
        self.__handler = MySqlHandler('localhost', 'yaokai', '123456', 'Test')

    def registerListeners(self, engine):
        """ register listener function to the event driven engine """
        engine.registerListener(EVENT_MD_DATA, self.onMdData)

    def onMdData(self, event):
        """
        Listener function to be registered to a event driven engine.
        This function save the market data to mysql
        """

        productName = event.data['InstrumentID']
        tableName = productName + '_' + (str(datetime.today()).split(' ')[0]).replace('-', '_')

        data = event.data
        fieldList = data.keys()

        self.__handler.createTable(tableName,
                                   fieldList,
                                   [type(data[field]) for field in fieldList])
        self.__handler.insert(tableName, data)


if __name__ == '__main__':
    dataFetcher = DataFetcher()
    data = {'InstrumentID' : 'FUCK666', 'Num' : 2333, 'Weight' : 88.88}
    transDict = {int : 'int', float : 'double', str : 'char(20)'}
    print(" (" + ", ".join(key + " " + transDict[type(value)] for key, value in data.items()) + ");")
    event = Event(data=data)
    dataFetcher.onMdData(event)




