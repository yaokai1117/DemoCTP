# DemoCTP
-----------------------
一个量化交易平台，仍在完成中。

目前更新在https://github.com/yaokai1117/DemoCTP.git

目前已支持的功能：行情的实时显示和存储（MySQL），实时K线绘制，基本的手动交易，通联DataYes历史数据爬取和导入数据库。

还未支持的功能：事件驱动引擎中的多级队列和线程池，MySQL与Spark的对接， 与Spark相结合的程序化交易接口。

### 安装

系统环境：Linux，测试所用的发行版为Ubuntu 14.04，因为并没有使用太多系统的API，所以发行版的区别影响不的。

依赖的软件及版本：
 
* Boost 1.5以上   
* Python2.7   
* MySQL 5.6
* MySQL-python 1.2.5
* matplotlib 1.4.3
* PyQT4 

安装与使用：
    
在终端中切换到DemoCTP，运行install.sh脚本
    
    $ cd DemoCTP
    $ ./install.sh
    
会自动编译所需的动态链接库，并首次运行程序
    
之后直接用python运行ui.py即可启动程序
    
    $ python ui.py
登录需要CTP的帐号（或虚拟帐号），和交易前置机的地址，端口。我们测试使用的是SimNow的模拟交易服务器,建议不要在开发完成并进行足够测试之前使用实盘账户。
                

### 架构描述：
    
使用vn.py对原来的CTP的C++接口进行封装，从而接下来的工作可以基于python进行。前端使用PyQT4和maplotlib进行GUI的制作和K线图的绘制。中间层采用事件驱动引擎，对CTP接口进一步封装并对相关的动作产生对应的事件，送与事件驱动引擎，通过向事件驱动引擎注册对应的handler函数对事件进行处理。事件驱动引擎设想采用线程池和多级队列的技术。 

数据处理方面，设想是采用Spark进行数据的处理，MySQL承接Spark处理后的数据，也负责承接每天实时的原始数据和通联的DataYes历史数据。

程序化交易接口方面，设想通过Spark的python接口来封装出一些常用的数据处理功能，与交易方面的接口和事件驱动引擎结合，以形成一个程序化交易的接口。

### 目录结构

* chartPlotter.py       用于K线图绘制
* ctp_data_type         使用vn.py的TD接口需要包含此模块，主要是数据类型的定义，平常不必关心这个文件
* mdapi.py              对CTP行情（Market Data）接口的回调函数的实现与主动函数的初步封装，在回调函数中产生一个对应的事件交与事件驱动引擎进行处理
* tdapi.py              对CTP交易（Trade）接口的回调函数的实现与主动函数的初步封装，在回调函数中产生一个对应的事件交与事件驱动引擎
* ctp.py                对tdapi.py与mdapi.py中主动函数的进一步封装
* eventdriven.py        事件驱动引擎的实现及事件类型的定义
* listeners.py          用于测试的事件监听函数
* ui.py                 图形界面
* fetchdata.py          一个简易的向MySQL传递python数据的工具MyqlHandler，以及接受并保存行情数据的DataFetcher
* datayes.py            用于爬取通联datayes的历史行情数据，需要自行注册并获取token

