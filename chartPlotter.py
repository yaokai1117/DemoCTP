# -*- coding: utf-8 -*-
"""
Created on Sat Sep 05 22:27:57 2015

@author: fanyang
"""

from PyQt4 import QtGui
from matplotlib.backends.backend_qt4agg import  FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
import matplotlib.dates
from matplotlib.dates import SecondLocator,MinuteLocator,HourLocator,DateFormatter
from matplotlib.ticker import MaxNLocator


class ChartPlotter(FigureCanvas):
    def __init__(self, timescale=1.0):
        self.fig = Figure()
        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        
        self.priceChart = self.fig.add_axes([0.05,0.278,0.9,0.672],axisbg = 'k')
        self.volumeChart = self.fig.add_axes([0.05,0.055,0.9,0.21],axisbg = 'k')
        self.priceChart.yaxis.set_major_locator(MaxNLocator(nbins=5,prune='lower'))
        self.volumeChart.yaxis.set_major_locator(MaxNLocator(nbins=2,prune='upper'))
        
        for tick in self.priceChart.xaxis.get_major_ticks():
            tick.label1On = False
        for tick in self.volumeChart.xaxis.get_major_ticks():
            tick.label1On = True
            tick.label1.set_fontsize(10)
        
        self.chartInit(self.priceChart,timescale)
        self.chartInit(self.volumeChart,timescale)
    
    def chartInit(self,chart,timescale=1.0):     
        #self.priceChart.set_ylabel('price', fontsize='small')
        chart.grid(color='w')
        
        for tick in chart.yaxis.get_major_ticks():
            tick.label1On = True
            tick.label2On = True
            tick.label1.set_fontsize(9)
            tick.label2.set_fontsize(9)
            
        # set_xlocator
        if timescale <= 10:
            chart.xaxis.set_major_locator(SecondLocator([0,30]))    
            chart.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
        elif timescale <= 60:
            chart.xaxis.set_major_locator(MinuteLocator([0,5,10,15,20,25,30,35,40,45,50,55]))    
            chart.xaxis.set_major_formatter(DateFormatter('%H:%M'))
        elif timescale <= 1800:
            chart.xaxis.set_major_locator(HourLocator([0,3,6,9,12,15,18,21]))    
            chart.xaxis.set_major_formatter(DateFormatter('%H:%M'))
        else :
            chart.xaxis.set_major_locator(HourLocator([0,12]))    
            chart.xaxis.set_major_formatter(DateFormatter('%H:%M'))
    
    def plotKLine(self, data, timescale=1.0,
                  width=0.9, colorup='r', colorflat = 'w', colordown='g', alpha=1.0):
        self.priceChart.set_xlim(data[0]-50*timescale/86400,data[0]+8*timescale/86400)
        
        t, open, close, high, low = data[:5]

        if close > open:
            color = colorup
        elif close == open:
            color = colorflat
        else:
            color = colordown
            
        if close == open:
            close = open + 0.005
        
        shadowline = Line2D(xdata=(t, t), ydata=(low, high),
            color=color,linewidth=0.5,antialiased=True,)

        rect = Rectangle(xy = (t-width*timescale/172800, open),
            width = width*timescale/86400,
            height = close-open, facecolor=color, edgecolor=color,)  
            
        rect.set_alpha(alpha)
        
        #self.priceChart.axhline(y=close,xmin=0.2,xmax=0.8)
        
        self.priceChart.add_line(shadowline)
        self.priceChart.add_patch(rect)
        self.priceChart.autoscale_view() 
    
    def adjustKLine(self, data, timescale=1.0, colorup='r', colorflat='w',colordown='g'): 
        open, close, high, low = data[1:5]
            
        if close > open:
            color = colorup
        elif close == open:
            color = colorflat
        else:
            color = colordown
            
        if close == open:
            close = open + 0.005
        
        (self.priceChart.patches[-1]).set(height=close-open, facecolor=color, edgecolor=color)
        (self.priceChart.lines[-1]).set(ydata=(low,high), color=color)
        
        self.priceChart.relim()
        self.priceChart.autoscale_view()
        
    def plotVolume(self, data, timescale=1.0,
                   width=0.9, colorup='r', colorflat='w',colordown='g', alpha=1.0):
        self.volumeChart.set_xlim(data[0]-50*timescale/86400,data[0]+8*timescale/86400)
        
        t, open, close= data[:3]
        volume = data[5]
        if close > open:
            color = colorup
        elif close == open:
            color = colorflat
        else:
            color = colordown
            
        rect = Rectangle(xy = (t-width*timescale/172800, 0),
            width = width*timescale/86400,
            height = volume, facecolor=color, edgecolor=color,)  
            
        self.volumeChart.add_patch(rect)
        self.volumeChart.autoscale_view()
        pass
    
    def adjustVolume(self, data, timescale=1.0, colorup='r', colorflat='w',colordown='g'):
        open, close = data[1:3]
        volume = data[5]
        
        if close > open:
            color = colorup
        elif close == open:
            color = colorflat
        else:
            color = colordown
            
        (self.volumeChart.patches[-1]).set(height=volume, facecolor=color, edgecolor=color)
        
        self.volumeChart.relim()
        self.volumeChart.autoscale_view()
        
        pass
        

class ChartBar(QtGui.QWidget):
    def __init__(self,InstrumentID, timescale=1.0, parent=None, initData=None):
        super(ChartBar, self).__init__(parent)
        
        self.__InstrumentID = InstrumentID
        self.__timescale = timescale
        self.plotter = ChartPlotter(self.__timescale)
        
        self.layout = QtGui.QVBoxLayout()
        self.toolbar = NavigationToolbar(self.plotter, parent)
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.plotter)
        self.setLayout(self.layout)
        self.data = []                    #time,open,close,high,low,volume
        #self.data.append([730000,4455,4494,4520,4397,714])       
        self.currtime = 0.0  
        pass
    
    def updateData(self,data):
        if data[0] - self.currtime > self.__timescale/86400:
            self.currtime = self.__timescale/86400*int(data[0]*86400/self.__timescale)
            self.data.append([self.currtime,data[1],data[1],data[1],data[1],data[2]])
            
            self.plotter.plotKLine(self.data[-1],timescale=self.__timescale)
            self.plotter.plotVolume(self.data[-1],timescale=self.__timescale)
            self.plotter.draw()
        else:
            self.data[-1][2] = data[1]
            if data[1] > self.data[-1][3]:
                self.data[-1][3] = data[1]
            if data[1] < self.data[-1][4]:
                self.data[-1][4] = data[1]
            self.data[-1][5] = self.data[-1][5] + data[2]
            self.plotter.adjustKLine(self.data[-1],timescale=self.__timescale)
            self.plotter.adjustVolume(self.data[-1],timescale=self.__timescale)
            self.plotter.draw()
            
        print self.__InstrumentID + ' ' + str(self.__timescale)
        print self.data[-1]
        print ''
        pass

    def initPlot(self):
	  pass
    
    
class ChartWidget(QtGui.QTabWidget):
    def __init__(self, InstrumentID, parent=None, initdata=None):
        super(ChartWidget, self).__init__(parent)
        
        self.__InstrumentID = InstrumentID  
        self.data = []
        
        self.tab_5s = ChartBar(self.__InstrumentID,timescale=5.0)
        self.addTab(self.tab_5s,'5s')
        
        self.tab_30s = ChartBar(self.__InstrumentID,timescale=30.0)
        self.addTab(self.tab_30s,'30s')
        
        #test
        data = {}
        data['TradingDay'] = '20111111'
        data['UpdateTime'] = '14:11:12'
        data['UpdateMillisec'] = 500
        data['LastPrice'] = 2230.0
        data['BidVolume1'] = 4
        data['AskVolume1'] = 7
        
        #self.updateData(data)
        #time.sleep(1)
        
        data['UpdateTime'] = '14:11:13'
        data['UpdateMillisec'] = 0
        data['LastPrice'] = 2230.4
        data['BidVolume1'] = 7
        data['AskVolume1'] = 11
        
        #self.updateData(data)
        #time.sleep(1)
        
        data['UpdateTime'] = '14:11:13'
        data['UpdateMillisec'] = 560
        data['LastPrice'] = 2229.6
        data['BidVolume1'] = 1
        data['AskVolume1'] = 9
        
        #self.updateData(data)
        #time.sleep(1)
        
        data['UpdateTime'] = '14:11:14'
        data['UpdateMillisec'] = 0
        data['LastPrice'] = 2230.0
        data['BidVolume1'] = 12
        data['AskVolume1'] = 14
        
        #self.updateData(data)
        #time.sleep(1)
        
        #data['UpdateTime'] = '14:11:14'
        #data['UpdateMillisec'] = 400
        #data['LastPrice'] = 229.6
        #data['BidVolume1'] = 12
        #data['AskVolume1'] = 14
        
        #self.updateData(data)
        #time.sleep(1)
        
        #data['UpdateTime'] = '14:11:15'
        #data['UpdateMillisec'] = 0
        #data['LastPrice'] = 221.1
        #data['BidVolume1'] = 12
        #data['AskVolume1'] = 14
        
        #self.updateData(data)
        #time.sleep(1)
        
        #data['UpdateTime'] = '14:11:15'
        #data['UpdateMillisec'] = 500
        #data['LastPrice'] = 225.6
        #data['BidVolume1'] = 12
        #data['AskVolume1'] = 14
        
        #self.updateData(data)
        #time.sleep(1)
        
        #data['UpdateTime'] = '14:11:15'
        #data['UpdateMillisec'] = 800
        #data['LastPrice'] = 224.7
        #data['BidVolume1'] = 12
        #data['AskVolume1'] = 14
        
        #self.updateData(data)
        #time.sleep(1)
        pass
    
    def updateData(self,data=None):
        timeData = (data['TradingDay'] + ' ' + data['UpdateTime'] + 
            '.' + str(data['UpdateMillisec']))
        priceData = data['LastPrice']
        volumeData = data['BidVolume1'] + data['AskVolume1']
        
        time0 = matplotlib.dates.datestr2num(timeData)
        
        self.data.append([time0,priceData,volumeData])
        self.tab_5s.updateData(self.data[-1])
        self.tab_30s.updateData(self.data[-1])
        
        print 'the data is updated!!!!!!!!!!!'
        print timeData,priceData,volumeData
        #for key in data.keys():
        #    print key,data[key],type(data[key])
        
        pass
       
def test():
    pass

if __name__ == '__main__':
    test()