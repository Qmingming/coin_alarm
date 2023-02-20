import asyncio
import datetime as dt
import sys
import time
from threading import Thread

import pandas
from PyQt5.QtCore import pyqtSignal, QObject
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import telegram_api as tele

import matplotlib.dates
import matplotlib.dates as md
import matplotlib.pyplot as plt
from PyQt5 import uic
from PyQt5.QtWidgets import *

import pymysql

from coin_alarm.coin_info import CoinInfo
from coin_alarm.yaml_parser import YamlParser

conn = pymysql.connect(host='127.0.0.1', user='root', password='12345', db='coin_price', charset='utf8')
form_class = uic.loadUiType("gui.ui")[0]

SMALL_SIZE = 8
MEDIUM_SIZE = 10
BIGGER_SIZE = 12

plt.rc('font', size=SMALL_SIZE)  # controls default text sizes
plt.rc('axes', titlesize=SMALL_SIZE)  # fontsize of the axes title
plt.rc('axes', labelsize=SMALL_SIZE)  # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)  # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)  # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)  # legend fontsize
plt.rc('figure', titlesize=SMALL_SIZE)  # fontsize of the figure title
# plt.subplots_adjust(top=0.1, bottom=0.09, left=0.5, right=1, wspace=0.3, hspace=0.5)

class Worker(QObject):
    coin_list = []
    update_chart_signal = pyqtSignal(CoinInfo, pandas.core.series.Series, pandas.core.series.Series)

    def __init__(self, coin_list):
        super().__init__()
        self.coin_list = coin_list

    def draw_chart(self, coin_list):
        for idx, coin in enumerate(coin_list):
            msg = "SELECT date, %s FROM crypto ORDER BY date DESC LIMIT %d" % (coin.name, 2000)
            df = pandas.read_sql_query(msg, conn)

            if coin.chart_num != -1:
                self.update_chart_signal.emit(coin, df['date'], df[coin.name])

    def run(self):
        th = Thread(target=self.draw_chart, args=(self.coin_list,))
        th.name = 'fetch_coin_price'
        th.start()

class MyWindow(QMainWindow, form_class):
    coin_list = []

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.fig = plt.figure(figsize=(30, 30))
        self.canvas = FigureCanvas(self.fig)
        self.verticalLayout.addWidget(self.canvas)
        self.row = 3
        self.col = 2
        self.chart = self.canvas.figure.subplots(self.row, self.col, sharex=True)
        self.fig.subplots_adjust(left=0.05, bottom=0.05, right=0.93, top=0.95, hspace=0.05, wspace=0.2)

        # parse coin info. from Yaml
        configs = YamlParser("info.yaml").parse()
        for idx, config in enumerate(configs['Data']):
            # append coin yaml information to coin_list
            self.coin_list.append(CoinInfo(config))

        worker = Worker(self.coin_list)
        worker.update_chart_signal.connect(self.plot)
        worker.run()

    def plot(self, coin, x, y):
        row = int(coin.chart_num/self.col)
        col = int(coin.chart_num%self.col)
        ax1 = self.chart[row, col]

        print(row, col)

        if coin.series == 0:
            ax1.cla()
            ax1.plot(x, y, '-', label=coin.name, markersize=1, linewidth=0.8)
            ax1.grid(True)

            legend_h, legend_l = ax1.get_legend_handles_labels()
        else:
            ax2 = self.chart[row, col].twinx()
            ax2.cla()
            ax2.plot(x, y, '-', label=coin.name, markersize=1, linewidth=0.8, color='red')
            #ax1.get_legend().remove()
            legend_h, legend_l = ax1.get_legend_handles_labels()
            legend_h2, legend_l2 = ax2.get_legend_handles_labels()
            legend_h = legend_h + legend_h2
            legend_l = legend_l + legend_l2

        ax1.legend(legend_h, legend_l, loc=1)
        ax1.xaxis.set_major_locator(md.DayLocator(interval=1))
        ax1.xaxis.set_major_formatter(md.DateFormatter('%D'))
        #plt.subplots_adjust(left=0.1, bottom=0.05, right=0.93, top=0.95, hspace=0.5, wspace=0.4)
        self.canvas.draw()

    """
    chart.clear()
    dates = matplotlib.dates.datestr2num(coin.xs)
    chart.plot(dates, coin.ys, label=coin.name, linewidth=1)
    #chart.set_xticks(np.arange(min(coin.xs), max(coin.xs)+1, 10), rotation=45, ha='right')

    chart.xaxis.set_major_locator(md.MinuteLocator(interval=15))  # to get a tick every 15 minutes
    chart.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))  # optional formatting
    chart.set_xlabel('time')
    chart.set_ylabel(coin.name)
    #chart.set_legend()
    plt.subplots_adjust(bottom=0.30)
    #plt.set_title('TMP102 Temperature over Time')
    #plt.legend()
    fig.canvas.draw()
    """

def run_telegram_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(tele.main())
    loop.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # thread = threading.Thread(target=run_telegram_bot)
    # thread.name = 'thread_telegram'
    # thread.start()

    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
