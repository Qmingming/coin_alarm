import asyncio
import datetime
import sys
import threading
from threading import Thread

import matplotlib.dates as md
import matplotlib.pyplot as plt
import pymysql
from PyQt5 import uic
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtGui import QBrush, QScreen
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import telegram_api as telegram
from coin_info import CoinInfo
from yaml_parser import YamlParser

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


class ChartInfo:
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
                price = coin.add_price(t)
                if price != -1 and price != 0:
                    self.update_price_signal.emit(row, 1, price)
                    if coin.check_mark_condition(self.update_chart_signal):
                        self.update_price_signal.emit(row, 2, price)
                row = row + 1

                # df = coin.getChartData()

    def run(self):
        th = Thread(target=self.fetch_coin_price, args=(self.coin_list,))
        th.name = 'fetch_coin_price'
        th.start()


class MyWindow(QMainWindow, form_class):
    coin_list = []
    chart_list = [ChartInfo() for _ in range(6)]
    primary_screen = 0
    win_id = 0

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.primary_screen = app.primaryScreen()
        self.win_id = self.tableWidget.winId()

        self.fig = plt.Figure(figsize=(5, 5))
        self.fig.subplots_adjust(left=0.1, right=0.93, bottom=0.08, top=0.9)
        self.canvas = FigureCanvas(self.fig)
        self.verticalLayout.addWidget(self.canvas)
        self.chart = self.canvas.figure.subplots()

        # parse coin info. from Yaml
        configs = YamlParser("info.yaml").parse()
        # set number of coin info. as row count of tableWidget
        self.tableWidget.setRowCount(len(configs['Data']))
        self.tableWidget.doubleClicked.connect(self.table_double_clicked)
        self.pushButton.clicked.connect(self.test)

        # self.coin_list.clear()
        for idx, config in enumerate(configs['Data']):
            try:
                # append coin yaml information to coin_list
                self.coin_list.append(CoinInfo(config))
                # set coin name in tableWidget
                self.set_table_value(idx, 0, config['name'])
            except Exception as err:
                print(err)

        self.db_set_new_coin(configs['Data'])

    @staticmethod
    def db_set_new_coin(yaml_info):
        conn = pymysql.connect(host='127.0.0.1', user='root', password='12345', db='coin_price', charset='utf8')
        try:
            cur = conn.cursor()
            t = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            s = ", "
            msg = "SELECT * FROM crypto LIMIT 1"
            cur.execute(msg)
            field_names = [i[0] for i in cur.description]
            new_property_name = []
            new_property_value = []

            for idx, config in enumerate(yaml_info):
                if config['name'] not in field_names:
                    msg = "ALTER TABLE crypto ADD %s FLOAT" % config['name']
                    cur.execute(msg)

                    new_property_name.append(config['name'])
                    new_property_value.append('0')
            if len(new_property_name) > 0:
                msg = "INSERT INTO crypto (date, %s) VALUES ('%s', %s)" \
                      % (s.join(new_property_name), t, s.join(new_property_value))
                cur.execute(msg)
        except Exception as err:
            print(err)
        finally:
            conn.commit()

    def run_price_alarm(self):
        worker = Worker(self.coin_list)
        worker.update_price_signal.connect(self.set_table_value)
        worker.update_chart_signal.connect(self.plot)
        worker.run()

    def set_table_value(self, row, column, value):
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

        except Exception as err:
            print(err)

    def table_double_clicked(self):
        try:
            row = self.tableWidget.currentIndex().row()
            # column = self.tableWidget.currentIndex().column()
            selected_coin_name = self.tableWidget.item(row, 0).text()
            self.plot(selected_coin_name)
        except Exception as err:
            print(err)

    def plot(self, selected_coin_name):
        for coin in self.coin_list:
            if coin.name == selected_coin_name:
                try:
                    df = coin.get_chart_data()
                    x = df['date']
                    y = df[coin.name]
                    self.chart.cla()
                    # self.chart.plot(x, y, '-', label=coin.name, markersize=1, linewidth=0.8)
                    self.chart.plot(x, y, '-', label=coin.name)
                    self.chart.grid(True, which='both')
                    # self.chart.legend(loc='best')
                    # self.chart.set_ylabel(coin.name)
                    self.chart.set_title(coin.name, fontsize=25, pad=18)
                    self.chart.annotate(xytext=(0.1, 0.94), xy=(0.5, 0.5), text=coin.price,
                                        xycoords='subfigure fraction',
                                        bbox=dict(boxstyle="round,pad=0.3", fc="none"), size=11)

                    time_interval = 8
                    self.chart.xaxis.set_major_locator(md.DayLocator(interval=1))
                    self.chart.xaxis.set_major_formatter(md.DateFormatter('%m-%d'))
                    self.chart.xaxis.set_tick_params(which='major', pad=18)
                    self.chart.xaxis.set_minor_locator(md.MinuteLocator(interval=(time_interval * 60)))
                    self.chart.xaxis.set_minor_formatter(md.DateFormatter('%H'))
                    self.chart.xaxis.remove_overlapping_locs = False

                    now = datetime.datetime.now()
                    end_time = now + datetime.timedelta(hours=(time_interval - (now.hour % time_interval)))
                    start_time = end_time - datetime.timedelta(days=7)

                    self.chart.set_xlim([start_time, end_time])
                    # self.chart.set_ylim(y.mean() * 0.9, y.mean() * 1.1)

                    self.fig.savefig('plot.png')
                except Exception as err:
                    print(err)

                return

    def screenshot(self):
        p = QScreen.grabWindow(self.primary_screen, self.win_id)
        p.save('table.png', 'png')

    def test(self):
        try:
            p = QScreen.grabWindow(self.primary_screen, self.win_id)
            p.save('plot.png', 'png')
            telegram.send_pic('plot.png')
        except Exception as err:
            print(err)


def run_telegram_bot(my_window):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(telegram.main(my_window))
    loop.close()


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        # start_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        # logging.basicConfig(filename='start_time.log', encoding='utf-8', level=logging.DEBUG)
        # logging.info("logging started at %s" %start_time)

        myWindow = MyWindow()

        thread = threading.Thread(target=run_telegram_bot, args=(myWindow,))
        thread.name = 'thread_telegram'
        thread.start()

        myWindow.run_price_alarm()
        myWindow.show()
        app.exec_()
    except Exception as err:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(err).__name__, err.args)
        print(message)
        result = -1
