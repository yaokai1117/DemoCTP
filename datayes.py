# -*- coding: utf-8 -*-

import requests
import json
from fetchdata import MySqlHandler
from collections import OrderedDict


class Downloader(object):
    """
    This class is used to download data from datayes,
    downloader needs to be initialed with an address and a token
    """

    def __init__(self, config=None, address=None, token=None):
        if config is not None:
            configFile = open(config, 'r')
            conf = json.load(configFile)
            self.__address = conf['address']
            self.__token = conf['token']
        elif address is not None and token is not None:
            self.__address = address
            self.__token = token
        else:
            print('Datayes downloader init failed!')
            return

        self.__headers = {'Authorization': 'Bearer ' + self.__token, 'Connection': 'keep-alive'}

        self.__session = requests.session()

    def getData(self, url, params):
        """
        This method gets data using datayes api.
        :param url: url specifies the kind of data, for example /api/market/getMktFutd.json means market data...
        :param params: params is a dict, include params specifying the data you want, such as tradeDate
        :return: a response from datayes
        """
        realUrl = 'https://' + self.__address+ url
        print(realUrl)

        req = requests.Request('GET', url=realUrl,
                               headers=self.__headers,
                               params=params)
        prepreq = self.__session.prepare_request(req)
        resp = self.__session.send(prepreq, stream=False, verify=True)

        if resp.status_code != 200:
            print('Request error, status code of the response is wrong')

        return resp


if __name__ == '__main__':
    downloader = Downloader(config='datayesconf.json')
    testData = downloader.getData(url='/api/market/getMktFutdVol.json',
                                  params={'ticker': 'CF601',
                                          'beginDate': '20150303',
                                          'endDate': '20150304',
                                          'field': ''})

    print(testData.text.encode('utf-8'))

    #handler = MySqlHandler('localhost', 'yaokai', '123456', 'Test')

    #tableName = 'YES_CF601'

    #originData = json.loads(testData.text.encode('utf-8'))
    #print(originData['data'])
    #print(str(originData['data'][0].keys()[0]))
    #example = originData['data'][0]
    #ordered = OrderedDict(example)

    #handler.createTable(tableName,
    #                    ordered.keys(),
    #                    [type(value) for value in ordered.values()])

    #for data in originData['data']:
    #    handler.insert(tableName, data)

    testData.close()