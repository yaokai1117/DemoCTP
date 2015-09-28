# coding: utf-8

# some listener functions for the event driven engine

def onMdLogin(event):
    if event.error['ErrorID'] == 0:
        print('md login succeed!')
    else:
        print('md login failed, errorID: ' + event.error['ErrorID'] + ', errorMsg:' + event.error['ErrorMsg'].decode('gbk'))


def onMdLogout(event):
    print('md logout!')


def onMdError(event):
    print('md error, errorID: ' + event.error['ErrorID'] + ', errorMsg:' + event.error['ErrorMsg'].decode('gbk'))


def onMdData(event):
    usefulHeaders = {'InstrumentID': u'商品代码', 'LastPrice' : u'最新价', 'BidPrice1' : u'买一价', 'BidVolume1' : u'买量', 'AskPrice1' : u'卖一价', 'AskVolume1' : u'卖量', 'Volume' : u'仓量', 'UpdateTime' : u'更新时间', 'UpdateMillisec' : u'更新毫秒' }
    #usefulData = {usefulHeaders[key].encode('utf-8') : event.data[key] for key in usefulHeaders.keys()}
    usefulData = {key.encode('utf-8') : event.data[key] for key in event.data.keys()}
    print('\t'.join(usefulData.keys()))
    print('\t'.join(str(value) + str(type(value)) for value in usefulData.values()))

def onTdLogin(event):
    pass





