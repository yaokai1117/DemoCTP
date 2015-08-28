# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 23:24:19 2015

@author: fanyang
"""
import matplotlib.pyplot as plt
from PyQt4 import  QtGui
from matplotlib.backends.backend_qt4agg import  FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

import time
import random
import threading
from datetime import datetime
from matplotlib.dates import  date2num, MinuteLocator, SecondLocator, DateFormatter
import matplotlib.ticker

X_MINUTES = 1
Y_MAX = 100
Y_MIN = 1
VOL_MAX = 1000
VOL_MIN = 0
INTERVAL = 1
MAXCOUNTER = 30000
class MplCanvas(FigureCanvas):
    def __init__(self):
        self.fig = Figure()
        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        
        self.ax = self.fig.add_axes([0.06,0.3,0.92,0.65],axisbg = 'k')
        self.ax.set_ylabel('price')
        self.ax.legend()
        self.ax.grid(color='w')
        self.ax.xaxis.set_major_formatter( DateFormatter('%H:%M:%S') ) #tick label formatter
        
        self.ax2 = self.fig.add_axes([0.06,0.05,0.92,0.2],axisbg = 'k')
        self.ax2.set_ylabel('volume')
        self.ax2.legend()
        self.ax2.grid(color='w')
        self.ax2.xaxis.set_major_formatter( DateFormatter('%H:%M:%S') ) #tick label formatter        
        
    def plot(self, data, timetick=1.0/86400, width=0.9, colorup='r', colordown='g', alpha=1.0):
        if len(data) >= 2 :
            if len(data) >= 30  :
                left = -30
            else                :
                left = 0
            delta = data[-1][0]-data[left][0]  #delta是左右距离，用来空出两边空隙
            self.ax.set_xlim(data[left][0] - delta*0.05,data[-1][0] + delta*0.05)
        
        t, open, close, high, low = data[-1][:5]
        if close>=open :
            color = colorup
            lower = open
            height = close-open
        else           :
            color = colordown
            lower = close
            height = open-close

        vline = Line2D(
            xdata=(t, t), ydata=(low, high),
            color=color,
            linewidth=0.5,
            antialiased=True,
            )

        rect = Rectangle(
            xy    = (t-width*timetick/2, lower),
            width = width*timetick,
            height = height,
            facecolor = color,
            edgecolor = color,
            )
        rect.set_alpha(alpha)

        self.ax.add_line(vline)
        self.ax.add_patch(rect)
        self.ax.autoscale_view()
        pass
    
    def plotMA(self,data,period=10,color='y'):
        if len(data) > period+1:
            price1 = 0.0
            price2 = 0.0
            for i in range(-period,0):
                price1 += data[i-1][2]
                price2 += data[i][2]
            price1 /= period
            price2 /= period
        
            self.ax.plot([data[-2][0],data[-1][0]],[price1,price2],color=color)
            self.ax.autoscale_view()
        pass
    
    def plotVolume(self, data, timetick=1.0/86400, width=0.9, colorup='r', colordown='g', alpha=1.0):
        if len(data) >= 2 :
            if len(data) >= 30  :
                left = -30
            else                :
                left = 0
            delta = data[-1][0]-data[left][0]  #delta是左右距离，用来空出两边空隙
            self.ax2.set_xlim(data[left][0] - delta*0.05,data[-1][0] + delta*0.05)
        
        t , open, close = data[-1][:3]
        volume = data[-1][5]
        
        if close>=open  :
            color = colorup
        else            :
            color = colordown

        self.ax2.bar(left=t-width*timetick/2,height=volume,width=width*timetick,color=color)
        self.ax2.autoscale_view()
        pass
                
class  FinanceK1d(QtGui.QWidget):
    def __init__(self , parent =None):
        QtGui.QWidget.__init__(self, parent)
        self.canvas = MplCanvas()
        self.canvas.ax.xaxis.set_major_locator(SecondLocator([0,5,10,15,20,25,30,35,40,45,50,55])) # every 5 second is a major locator
        self.canvas.ax2.xaxis.set_major_locator(SecondLocator([0,5,10,15,20,25,30,35,40,45,50,55])) # every 5 second is a major locator
        self.vbl = QtGui.QVBoxLayout()
        self.ntb = NavigationToolbar(self.canvas, parent)
        self.vbl.addWidget(self.ntb)
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)
        self.data= []
        self.initDataGenerator()
    def startPlot(self):
        self.__generating = True
    def pausePlot(self):
        self.__generating = False
        pass
    def initDataGenerator(self):
        self.__generating=False
        self.__exit = False
        self.tData = threading.Thread(name = "dataGenerator",target = self.generateData)
        self.tData.start()
    def releasePlot(self):
        self.__exit  = True
        self.tData.join()
    def generateData(self):
        counter=0
        while(True):
            if self.__exit:
                break
            if self.__generating:
                newOpen = random.uniform(Y_MIN+10, Y_MAX-10)
                newHigh = random.uniform(newOpen,newOpen+10)
                newLow = random.uniform(newOpen-10,newOpen)
                newClose = random.uniform(newLow,newHigh)
                newTime = date2num(datetime.now())
                newVolume = random.uniform(VOL_MIN,VOL_MAX)
                self.data.append((newTime,newOpen,newClose,newHigh,newLow,newVolume))
                self.canvas.plotMA(self.data)
                self.canvas.plotMA(self.data,period=5,color='m')
                self.canvas.plot(self.data)
                self.canvas.plotVolume(self.data)
                self.canvas.draw()
                if counter >= MAXCOUNTER:
                    self.data.pop(0)
                else:
                    counter+=1
                time.sleep(INTERVAL)
                
class  FinanceK2d(QtGui.QWidget):
    def __init__(self , parent =None):
        QtGui.QWidget.__init__(self, parent)
        self.canvas = MplCanvas()
        self.canvas.ax.xaxis.set_major_locator(SecondLocator([0,30])) # every 30 second is a major locator
        self.canvas.ax2.xaxis.set_major_locator(SecondLocator([0,30])) # every 30 second is a major locator
        self.vbl = QtGui.QVBoxLayout()
        self.ntb = NavigationToolbar(self.canvas, parent)
        self.vbl.addWidget(self.ntb)
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)
        self.data= []
        self.initDataGenerator()
    def startPlot(self):
        self.__generating = True
    def pausePlot(self):
        self.__generating = False
        pass
    def initDataGenerator(self):
        self.__generating=False
        self.__exit = False
        self.tData = threading.Thread(name = "dataGenerator",target = self.generateData)
        self.tData.start()
    def releasePlot(self):
        self.__exit  = True
        self.tData.join()
    def generateData(self):
        counter=0
        while(True):
            if self.__exit:
                break
            if self.__generating:
                newOpen = random.uniform(Y_MIN+10, Y_MAX-10)
                newHigh = random.uniform(newOpen,newOpen+10)
                newLow = random.uniform(newOpen-10,newOpen)
                newClose = random.uniform(newLow,newHigh)
                newTime= date2num(datetime.now())
                newVolume = random.uniform(VOL_MIN,VOL_MAX)
                self.data.append((newTime,newOpen,newClose,newHigh,newLow,newVolume))
                self.canvas.plotMA(self.data)
                self.canvas.plot(self.data,timetick=5.0/86400)
                self.canvas.plotVolume(self.data,timetick=5.0/86400)
                self.canvas.draw()
                if counter >= MAXCOUNTER:
                    self.data.pop(0)
                else:
                    counter+=1
                time.sleep(5*INTERVAL)