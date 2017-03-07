# -*- coding: utf-8 -*-
"""
Created on Sat Sep 05 22:27:57 2015

@author: fanyang
"""

from PyQt4 import QtGui,QtCore
from matplotlib.backends.backend_qt4agg import  FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
import matplotlib.dates
from matplotlib.dates import SecondLocator,MinuteLocator,HourLocator,DateFormatter
from matplotlib.ticker import *


class ChartPlotter(FigureCanvas):
    u"""
    用于画一个特定品种的特定时间的K线图和成交量图，是对应ChartBar的实际绘图部分。

    self.priceChart： K线图
    self.volumeChart：成交量图
    self.trendlinesData：趋势线集合
    """

    def __init__(self, timescale=1.0):
        self.fig = Figure()
        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        
        self.priceChart = self.fig.add_axes([0.05,0.283,0.9,0.671],axisbg = 'k')
        self.volumeChart = self.fig.add_axes([0.05,0.048,0.9,0.209],axisbg = 'k')
        self.priceChart.yaxis.set_major_locator(LinearLocator(numticks=5))
        self.volumeChart.yaxis.set_major_locator(LinearLocator(numticks=3))

        for tick in self.priceChart.xaxis.get_major_ticks():
            tick.label1On = False
        for tick in self.volumeChart.xaxis.get_major_ticks():
            tick.label1On = True
            tick.label1.set_fontsize(10)
        
        self.chartInit(self.priceChart,timescale)
        self.chartInit(self.volumeChart,timescale)

        self.trendlinesData = {}
        self.lineColors = ['pink','red','green','purple','white','blue','yellow']
    
    def chartInit(self,chart,timescale=1.0):
        u"""根据timescale设置K线图和成交量图的label，xLocator等参数"""
        chart.grid(color='w')
        
        for tick in chart.yaxis.get_major_ticks():
            tick.label1On = True
            tick.label2On = True
            tick.label1.set_fontsize(9)
            tick.label2.set_fontsize(9)

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

    def adjustYLim(self,minPrice,maxPrice,maxVolume):
        u"""重新调整图的y轴上下界"""
        self.priceChart.set_ylim(minPrice,maxPrice)
        self.volumeChart.set_ylim(0,maxVolume)
    
    def plotKLine(self, data, timescale=1.0,
                  width=0.9, colorup='r', colorflat = 'w', colordown='g', alpha=1.0):
        u"""根据数据画一个新的K线"""
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
        
        self.priceChart.add_line(shadowline)
        self.priceChart.add_patch(rect)

        return shadowline, rect

    def adjustKLine(self, data, shadowLine, rect,
                    timescale=1.0, colorup='r', colorflat='w',colordown='g'):
        u"""调整一根K线shadowLine和rect的数据"""
        open, close, high, low = data[1:5]
            
        if close > open:
            color = colorup
        elif close == open:
            color = colorflat
        else:
            color = colordown
            
        if close == open:
            close = open + 0.005
        
        rect.set(height=close-open, facecolor=color, edgecolor=color)
        shadowLine.set(ydata=(low,high), color=color)
        
        self.priceChart.relim()
        
    def plotVolume(self, data, timescale=1.0,
                   width=0.9, colorup='r', colorflat='w',colordown='g', alpha=1.0):
        u"""根据数据画一个新的成交量rect"""
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
            height = volume, facecolor=color, edgecolor=color)

        rect.set_alpha(alpha)
            
        self.volumeChart.add_patch(rect)

        return rect
    
    def adjustVolume(self, data, rect, timescale=1.0, colorup='r', colorflat='w',colordown='g'):
        u"""调整成交量图rect的数据"""
        open, close = data[1:3]
        volume = data[5]
        
        if close > open:
            color = colorup
        elif close == open:
            color = colorflat
        else:
            color = colordown
            
        rect.set(height=volume, facecolor=color, edgecolor=color)
        
        self.volumeChart.relim()
        
        pass

    def addTrendline(self, trendline, isActive):
        u"""加入，隐藏或重新显示一条趋势线trendline
        isActive 是否显示该趋势线"""
        if isActive:
            if trendline not in self.trendlinesData:                #创建新线
                tempLine = Line2D(xdata=[],ydata=[])
                tempLine.set_label(trendline)
                tempLine.set_color(self.lineColors.pop())
                self.trendlinesData[trendline] = tempLine
                self.priceChart.add_line(tempLine)
            elif not self.trendlinesData[trendline].get_visible():  #不可见变为可见
                self.trendlinesData[trendline].set_visible(True)
                self.trendlinesData[trendline].set_color(self.lineColors.pop())
        else:
            if trendline in self.trendlinesData:
                if self.trendlinesData[trendline].get_visible():    #可见变为不可见
                    self.trendlinesData[trendline].set_visible(False)
                    self.lineColors.append(self.trendlinesData[trendline].get_color())

    def plotTrendline(self, data, trendline):
        """画一条趋势线的下一个点"""
        if trendline in self.trendlinesData:
            xdata = self.trendlinesData[trendline].get_xdata()
            ydata = self.trendlinesData[trendline].get_ydata()
            xdata.append(data[0])
            ydata.append(data[1])
            self.trendlinesData[trendline].set_xdata(xdata)
            self.trendlinesData[trendline].set_ydata(ydata)

    def adjustTrendline(self, newydata, trendline):
        """调整一条趋势线的y数据"""
        if trendline in self.trendlinesData:
            ydata = self.trendlinesData[trendline].get_ydata()
            ydata[-1] = newydata
            self.trendlinesData[trendline].set_ydata(ydata)


class ChartBar(QtGui.QWidget):
    u"""
    界面中的一个timescale对应的一个标签页，存储画图需要的数据

    self.plotter：专门画图的对象
    self.trendlineBox：更改趋势线的按钮
    self.currShadowLine，self.currRect，self.currVolumeBar：保存当前图中正在操作的K线和成交量线等
    self.data：存储数据，每个元素格式为（time，open，close，high，low，volume）
    self.curTime：数据中最新的时间
    self.trendlineNames：趋势线名称列表
    """
    def __init__(self,InstrumentID, timescale=1.0, parent=None, initData=None):
        super(ChartBar, self).__init__(parent)
        
        self.__InstrumentID = InstrumentID
        self.__timescale = timescale
        self.plotter = ChartPlotter(self.__timescale)
        
        self.layout = QtGui.QVBoxLayout()
        self.subLayout = QtGui.QHBoxLayout()
        self.toolbar = NavigationToolbar(self.plotter, parent)
        self.trendlineBox = QtGui.QPushButton(u'添加趋势线..')
        self.trendlineMenu = QtGui.QMenu()
        self.trendlineBox.setMenu(self.trendlineMenu)
        self.subLayout.addWidget(self.toolbar)
        self.subLayout.addWidget(self.trendlineBox)
        self.layout.addLayout(self.subLayout)
        self.layout.addWidget(self.plotter)
        self.setLayout(self.layout)
        self.data = []
        self.curTime = 0.0

        self.currShadowLine = None
        self.currRect = None
        self.currVolumeBar = None

        self.trendlineNames = ['MA3','MA5','MA10','MA20','MA25']

        for i,trendline in enumerate(self.trendlineNames):
            self.plotter.addTrendline(trendline,True)
            self.plotter.addTrendline(trendline,False)
            tmp = self.trendlineMenu.addAction(trendline)
            tmp.setCheckable(True)
            tmp.triggered.connect(self.triggerMenu)

    def triggerMenu(self):
        u"""按下趋势线菜单，修改趋势线显示状态"""
        for action in self.trendlineMenu.actions():
            self.plotter.addTrendline(str(action.text()),action.isChecked())
        self.plotter.draw()
    
    def updateData(self,data):
        u"""data为从ChartWidget传来的tick数据，
        根据timescale更新该ChartBar存储的数据，并且画一个新的K线或者调整当前K线"""
        if data[0] - self.curTime > self.__timescale/86400:
            self.curTime = self.__timescale/86400*int(data[0]*86400/self.__timescale)
            self.data.append([self.curTime,data[1],data[1],data[1],data[1],data[2]])
            
            self.currShadowLine,self.currRect = self.plotter.plotKLine(self.data[-1],timescale=self.__timescale)
            self.currVolumeBar = self.plotter.plotVolume(self.data[-1],timescale=self.__timescale)
            for i in self.trendlineNames:
                self.calTrendlineAndPlot(i)
        else:
            self.data[-1][2] = data[1]
            if data[1] > self.data[-1][3]:
                self.data[-1][3] = data[1]
            if data[1] < self.data[-1][4]:
                self.data[-1][4] = data[1]
            self.data[-1][5] = self.data[-1][5] + data[2]
            self.plotter.adjustKLine(self.data[-1],self.currShadowLine,self.currRect,timescale=self.__timescale)
            self.plotter.adjustVolume(self.data[-1],self.currVolumeBar,timescale=self.__timescale)
            for i in self.trendlineNames:
                self.calTrendlineAndAdjust(i)

        self.plotter.adjustYLim(0.999*min([i[4] for i in self.data[max(-len(self.data),-50):]]),
                                1.001*max([i[3] for i in self.data[max(-len(self.data),-50):]]),
                                1*max([i[5] for i in self.data[max(-len(self.data),-50):]]))

        self.plotter.draw()

    def calTrendlineAndPlot(self,name):
        """计算各趋势线的值并画图"""
        avr = int(name[2:])                         #目前只有 'MAxxx' 均线
        if len(self.data) >= avr:
            tempPrice = 0.0
            for i in range(-avr,0):
                tempPrice += self.data[i][2]
            tempPrice /= avr
            self.plotter.plotTrendline((self.data[-1][0],tempPrice),name)

    def calTrendlineAndAdjust(self,name):
        """计算各趋势线的值并调整图"""
        avr = int(name[2:])
        if len(self.data) >= avr:
            tempPrice = 0.0
            for i in range(-avr,0):
                tempPrice += self.data[i][2]
            tempPrice /= avr
            self.plotter.adjustTrendline(tempPrice,name)

    def initPlot(self):
        u"""登录后，获取历史数据并画图，待实现"""
        pass


class ChartWidget(QtGui.QTabWidget):
    u"""
    包含一个品种的所有timescale的K线图，负责从engine接收tick数据，存储并分发给每个ChartBar
    """
    def __init__(self, InstrumentID, parent=None, initdata=None):
        super(ChartWidget, self).__init__(parent)
        
        self.__InstrumentID = InstrumentID  
        self.data = []
        
        self.tab_5s = ChartBar(self.__InstrumentID,timescale=5.0)
        self.addTab(self.tab_5s,'5s')
        
        self.tab_30s = ChartBar(self.__InstrumentID,timescale=30.0)
        self.addTab(self.tab_30s,'30s')
    
    def updateData(self,data=None):
        timeData = (data['TradingDay'] + ' ' + data['UpdateTime'] + 
            '.' + str(data['UpdateMillisec']))
        priceData = data['LastPrice']
        volumeData = data['BidVolume1'] + data['AskVolume1']
        
        time0 = matplotlib.dates.datestr2num(timeData)
        
        self.data.append([time0,priceData,volumeData])
        self.tab_5s.updateData(self.data[-1])
        self.tab_30s.updateData(self.data[-1])
