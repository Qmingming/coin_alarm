import datetime as dt
import sys
import time
from threading import Thread
import telegram_bot3 as tele

import matplotlib.dates
import matplotlib.dates as md
import matplotlib.pyplot as plt
from PyQt5 import uic
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtWidgets import *

from coin_alarm.coin_info import CoinInfo
from coin_alarm.yaml_parser import YamlParser

form_class = uic.loadUiType("gui.ui")[0]
# Create figure for plotting
fig = plt.figure(figsize=(14, 6))
SMALL_SIZE = 8
MEDIUM_SIZE = 10
BIGGER_SIZE = 12

plt.rc('font', size=MEDIUM_SIZE)  # controls default text sizes
plt.rc('axes', titlesize=MEDIUM_SIZE)  # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)  # fontsize of the x and y labels
plt.rc('xtick', labelsize=MEDIUM_SIZE)  # fontsize of the tick labels
plt.rc('ytick', labelsize=MEDIUM_SIZE)  # fontsize of the tick labels
plt.rc('legend', fontsize=MEDIUM_SIZE)  # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
# plt.xticks(rotation=45, ha='right')

charts = [0] * 10

charts[0] = fig.add_subplot(1, 2, 1)
charts[1] = fig.add_subplot(1, 2, 2)


class Worker(QObject):
    coin_list = []
    update_price_signal = pyqtSignal(int, int, float)

    def __init__(self, coin_list):
        super().__init__()
        self.coin_list = coin_list

    def fetch_coin_price(self, coin_list):
        while True:
            t = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            row = 0
            for coin in coin_list:
                price = coin.addPrice(t)
                if price != -1:
                    self.update_price_signal.emit(row, 1, price)
                    if coin.checkMarkCondition():
                        self.update_price_signal.emit(row, 2, price)
                row = row + 1
            time.sleep(5)

    def run(self):
        thread = Thread(target=self.fetch_coin_price, args=(self.coin_list,))
        thread.start()


class MyWindow(QMainWindow, form_class):
    coin_list = []

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        configs = YamlParser("info.yaml").parse()
        self.tableWidget.setRowCount(len(configs['Data']))

        self.coin_list.clear()
        for idx, config in enumerate(configs['Data']):
            self.coin_list.append(CoinInfo(config))
            self.setTableValue(idx, 0, config['name'])

        worker = Worker(self.coin_list)
        worker.update_price_signal.connect(self.setTableValue)
        worker.run()

    def setTableValue(self, row, column, value):
        if column == 0:
            item = QTableWidgetItem(value)
        else:
            price = "{:10.2f}".format(value)
            item = QTableWidgetItem(price)

        item.setTextAlignment(Qt.AlignCenter)
        self.tableWidget.setItem(row, column, item)

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


def animate(i, coin_list):
    # plt.xticks(rotation=45, ha='right')
    # plt.subplots_adjust(bottom=0.30)
    # plt.title('TMP102 Temperature over Time')
    # plt.ylabel('Temperature (deg C)')
    # plt.legend()
    # print(time)
    # plt.pause(5)

    t = dt.datetime.now().strftime("%H:%M:%S")
    # t = t + 1
    for (coin, chart) in zip(coin_list, charts):
        coin.addPrice(t)
        chart.clear()
        dates = matplotlib.dates.datestr2num(coin.xs)
        chart.plot(dates, coin.ys, label=coin.name, linewidth=1)
        # chart.set_xticks(np.arange(min(coin.xs), max(coin.xs)+1, 10), rotation=45, ha='right')

        chart.xaxis.set_major_locator(md.MinuteLocator(interval=15))  # to get a tick every 15 minutes
        chart.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))  # optional formatting
        chart.set_xlabel('time')
        chart.set_ylabel(coin.name)
        # chart.set_legend()
    plt.subplots_adjust(bottom=0.30)
    print(t)
    fig.canvas.draw()
    print("exit")
    # plt.set_title('TMP102 Temperature over Time')
    # plt.legend()
    # plt.pause(5)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    tele.init()
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()

    # plt.show()
    # realtime_chart(False)  # 175 fps
