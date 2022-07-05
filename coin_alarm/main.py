import asyncio
import datetime
import os
import sys
import threading
import time
from threading import Thread

import matplotlib.dates as md
import matplotlib.pyplot as plt
import pandas
from PyQt5 import uic
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtGui import QBrush
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import telegram_api as telegram
from coin_alarm.coin_info import CoinInfo
from coin_alarm.yaml_parser import YamlParser

form_class = uic.loadUiType("gui.ui")[0]
# Create figure for plotting
SMALL_SIZE = 8
MEDIUM_SIZE = 9
BIGGER_SIZE = 12

plt.rc('font', size=MEDIUM_SIZE)  # controls default text sizes
plt.rc('axes', titlesize=MEDIUM_SIZE)  # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)  # fontsize of the x and y labels
plt.rc('xtick', labelsize=MEDIUM_SIZE)  # fontsize of the tick labels
plt.rc('ytick', labelsize=MEDIUM_SIZE)  # fontsize of the tick labels
plt.rc('legend', fontsize=MEDIUM_SIZE)  # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title


class ChartInfo():
    def __init__(self):
        self.ax1 = None
        self.ax2 = None


# plt.xticks(rotation=45, ha='right')
class Worker(QObject):
    coin_list = []
    update_price_signal = pyqtSignal(int, int, float)
    update_chart_signal = pyqtSignal(str)

    def __init__(self, coin_list):
        super().__init__()
        self.coin_list = coin_list

    def fetch_coin_price(self, coin_list):
        while True:
            t = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            row = 0
            for coin in coin_list:
                price = coin.addPrice(t)
                if price != -1:
                    self.update_price_signal.emit(row, 1, price)
                    if coin.checkMarkCondition(self.update_chart_signal):
                        self.update_price_signal.emit(row, 2, price)
                row = row + 1

                if coin.chart_num != -1:
                    df = coin.getChartData()
                    #self.update_chart_signal.emit(coin.name)

    def run(self):
        th = Thread(target=self.fetch_coin_price, args=(self.coin_list,))
        th.name = 'fetch_coin_price'
        th.start()


class MyWindow(QMainWindow, form_class):
    coin_list = []
    chart_list = [ChartInfo() for _ in range(6)]

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.fig = plt.Figure(figsize=(5, 5))
        self.canvas = FigureCanvas(self.fig)
        self.verticalLayout.addWidget(self.canvas)
        self.chart = self.canvas.figure.subplots()
        # self.row = 3
        # self.col = 2
        # self.chart = self.canvas.figure.subplots(self.row, self.col, sharex=True)
        # self.fig.subplots_adjust(left=0.1, bottom=0.05, right=0.93, top=0.95, hspace=0.3, wspace=0.4)

        # parse coin info. from Yaml
        configs = YamlParser("info.yaml").parse()
        # set number of coin info. as row count of tableWidget
        self.tableWidget.setRowCount(len(configs['Data']))
        self.tableWidget.doubleClicked.connect(self.table_double_clicked)
        self.pushButton.clicked.connect(self.test)

        # self.coin_list.clear()
        for idx, config in enumerate(configs['Data']):
            # append coin yaml information to coin_list
            self.coin_list.append(CoinInfo(config))
            # set coin name in tableWidget
            self.setTableValue(idx, 0, config['name'])
        '''
        for coin in self.coin_list:
            row = int(coin.chart_num / self.col)
            col = int(coin.chart_num % self.col)
            chart = self.chart_list[coin.chart_num]

            if coin.series == 1:
                chart.ax2 = self.chart[row, col].twinx()
            elif coin.series == 0:
                chart.ax1 = self.chart[row, col]
            else:
                continue
        '''
        worker = Worker(self.coin_list)
        worker.update_price_signal.connect(self.setTableValue)
        worker.update_chart_signal.connect(self.plot)

        worker.run()

    def setTableValue(self, row, column, value):
        try:
            if column == 0:
                item = QTableWidgetItem(value)
            else:
                item = QTableWidgetItem(str(value))

            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget.setItem(row, column, item)

            if column == 1:
                mark_value = self.tableWidget.item(row, 2)
                if mark_value is not None:
                    mark_value = mark_value.text()
                    if value > float(mark_value):
                        item.setForeground(QBrush(Qt.blue))
                    elif value < float(mark_value):
                        item.setForeground(QBrush(Qt.red))
                    else:
                        item.setForeground(QBrush(Qt.black))

        except Exception as e:
            print(e)

    '''
    def plot(self, coin, x, y):
        # row = int(coin.chart_num / self.col)
        # col = int(coin.chart_num % self.col)
        # ax1 = self.chart[row, col]
        chart = self.chart_list[coin.chart_num]

        if coin.series == 0:
            chart.ax1.cla()
            chart.ax1.plot(x, y, '-', label=coin.name, markersize=1, linewidth=0.8)
            chart.ax1.grid(True)
            chart.ax1.set_ylabel(coin.name)

            legend_h, legend_l = chart.ax1.get_legend_handles_labels()
        else:
            # ax2 = self.chart[row, col].twinx()
            chart.ax2.cla()
            chart.ax2.plot(x, y, '-', label=coin.name, markersize=1, linewidth=0.8, color='red')
            chart.ax2.set_ylabel(coin.name)
            chart.ax1.get_legend().remove()
            legend_h, legend_l = chart.ax1.get_legend_handles_labels()
            legend_h2, legend_l2 = chart.ax2.get_legend_handles_labels()
            legend_h = legend_h + legend_h2
            legend_l = legend_l + legend_l2

        chart.ax1.legend(legend_h, legend_l, loc=1)
        chart.ax1.xaxis.set_major_locator(md.DayLocator(interval=1))
        chart.ax1.xaxis.set_major_formatter(md.DateFormatter('%D'))
        # plt.subplots_adjust(left=0.1, bottom=0.05, right=0.93, top=0.95, hspace=0.5, wspace=0.4)
        self.canvas.draw()
        # self.save_plt_image()
    '''

    def table_double_clicked(self):
        try:
            row = self.tableWidget.currentIndex().row()
            # column = self.tableWidget.currentIndex().column()
            selected_coin_name = self.tableWidget.item(row, 0).text()
            self.plot(selected_coin_name)
        except Exception as e:
            print(e)

    def plot(self, selected_coin_name):
        for coin in self.coin_list:
            if coin.name == selected_coin_name:
                try:
                    df = coin.getChartData()
                    x = df['date']
                    y = df[coin.name]
                    self.chart.cla()
                    # self.chart.plot(x, y, '-', label=coin.name, markersize=1, linewidth=0.8)
                    self.chart.plot(x, y, '-', label=coin.name)
                    self.chart.grid(True, which='both')
                    #self.chart.set_ylabel(coin.name)
                    self.chart.set_title(coin.name, fontsize=30, pad=20)
                    #plt.subplots_adjust(left=0.1, bottom=0.05, right=0.93, top=0.95, hspace=0.5, wspace=0.4)
                    self.fig.subplots_adjust(left=0.1, right=0.93, bottom=0.1, top=0.85)

                    time_interval = 12
                    self.chart.xaxis.set_major_locator(md.DayLocator(interval=1))
                    self.chart.xaxis.set_major_formatter(md.DateFormatter('%m-%d'))
                    self.chart.xaxis.set_tick_params(which='major', pad=15)
                    self.chart.xaxis.set_minor_locator(md.MinuteLocator(interval=(12*60)))
                    self.chart.xaxis.set_minor_formatter(md.DateFormatter('%H:%M'))

                    self.chart.xaxis.remove_overlapping_locs = False

                    year = int(datetime.datetime.now().strftime("%Y"))
                    month = int(datetime.datetime.now().strftime("%m"))
                    day = int(datetime.datetime.now().strftime("%d"))
                    hour = int(datetime.datetime.now().strftime("%H"))
                    hour_modified = hour + (time_interval - (hour % time_interval))
                    if hour_modified >= 24:
                        day = day + 1
                        hour_modified = 0
                    end_time = datetime.datetime(year, month, day, hour_modified, 0)
                    start_time = end_time - datetime.timedelta(days=7)

                    self.chart.set_xlim([start_time, end_time])
                    # self.chart.set_ylim(y.mean() * 0.9, y.mean() * 1.1)
                    self.canvas.draw()
                    self.fig.savefig('capture.png')
                    #time.sleep(5)

                except Exception as e:
                    print(e)

                return

    def test(self):
        print("save photo")
        self.fig.savefig('capture.png')
        telegram.send_pic('capture.png')
        telegram.send_msg('test')


def run_telegram_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(telegram.main())
    loop.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    thread = threading.Thread(target=run_telegram_bot)
    thread.name = 'thread_telegram'
    thread.start()

    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
