import datetime as dt
import time
from threading import Thread

import matplotlib.dates
import matplotlib.pyplot as plt
import matplotlib.dates as md
import matplotlib.animation as animation
import numpy as np

from coin_alarm.CoinInfo import CoinInfo
from coin_alarm.yaml_parser import YamlParser

# Create figure for plotting
fig = plt.figure(figsize=(14, 6))
SMALL_SIZE = 8
MEDIUM_SIZE = 10
BIGGER_SIZE = 12

plt.rc('font', size=MEDIUM_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=MEDIUM_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=MEDIUM_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
#plt.xticks(rotation=45, ha='right')

charts = [0] * 10

charts[0] = fig.add_subplot(1, 2, 1)
charts[1] = fig.add_subplot(1, 2, 2)

def animate(i, coin_list):
    #plt.xticks(rotation=45, ha='right')
    #plt.subplots_adjust(bottom=0.30)
    #plt.title('TMP102 Temperature over Time')
    #plt.ylabel('Temperature (deg C)')
    #plt.legend()
    #print(time)
    #plt.pause(5)

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
    #plt.pause(5)

def fetch_coin_price(coin_list):
    t = 1
    while True:
        t = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        #t = t + 1
        for coin in coin_list:
            coin.addPrice(t)
        time.sleep(5)
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


if __name__ == "__main__":
    coin_list = []
    coin_list.clear()
    configs = YamlParser("info.yaml").parse()

    for idx, config in enumerate(configs['Data']):
        coin_list.append(CoinInfo(config))

    #ani = animation.FuncAnimation(fig, animate, fargs=(coin_list,), repeat=True, repeat_delay=1000000)
    #plt.show()
    thread = Thread(target=fetch_coin_price, args=(coin_list,))
    thread.start()
    #plt.show()
    #realtime_chart(False)  # 175 fps
