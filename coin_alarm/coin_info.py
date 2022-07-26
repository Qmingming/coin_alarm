import os
import threading
import time

import pandas
import pymysql
from sqlalchemy import create_engine

import telegram_api as telegram

import chrome_selenium


class CoinInfo:
    webcrawler = chrome_selenium.ChromeSelenium()
    engine = create_engine('mysql+pymysql://root:12345@127.0.0.1:3306/coin_price')
    conn = pymysql.connect(host='127.0.0.1', user='root', password='12345', db='coin_price', charset='utf8')
    cur = conn.cursor()
    alarm_stop = 0

    def __init__(self, yaml_info):
        self.price = None
        self.mark_price = None

        self.chart_num = int(yaml_info['chart_num'])
        self.series = int(yaml_info['series'])
        self.name = yaml_info['name']
        self.url = yaml_info['url']
        self.xpath = yaml_info['xpath']
        self.xpath2 = yaml_info['xpath2']
        self.alarm_percentage = yaml_info['alarm_percentage']
        self.ax = None

    def addPrice(self, t):
        try:
            print("%s searching price for coin %s" % (t, self.name), end=" - ")
            price = float(self.webcrawler.findElement(self))
            print(price)

            if price == -1:
                return -1
            else:
                if price > 1:
                    price = float("{:.2f}".format(price))
                else:
                    price = float("{:.4f}".format(price))
        except Exception as e:
            print(e)

        # self.ys.append(price)
        # self.ys.append(randint(0, 100))
        # self.ys = self.ys[-80000:]
        # self.xs.append(t)
        # self.xs = self.xs[-80000:]

        try:
            msg = "SELECT * FROM crypto LIMIT 1"
            self.cur.execute(msg)
            field_names = [i[0] for i in self.cur.description]
            if self.name not in field_names:
                msg = "ALTER TABLE crypto ADD %s FLOAT" % self.name
                # print(msg)
                self.cur.execute(msg)

            msg = "INSERT INTO crypto (date, %s) VALUES ('%s', '%s')" % (self.name, t, price)
            # print(msg)
            self.cur.execute(msg)
        except Exception as e:
            # print(e)
            msg = "UPDATE crypto SET %s = %s WHERE date = '%s'" % (self.name, price, t)
            # print(msg)
            self.cur.execute(msg)
        finally:
            self.conn.commit()
            self.price = price
            return price

    def checkMarkCondition(self, chart_signal):
        EMOTICON_GREEN = "\U0001F7E2"
        EMOTICON_RED = "\U0001F534"

        try:
            self.alarm_stop = 0
            if self.mark_price is None or self.price == 0:
                # for initial
                self.mark_price = self.price
                return True
            else:
                if self.alarm_percentage == "n/a":
                    return False
                backup_mark_price = self.mark_price
                top_band = self.mark_price * (100 + self.alarm_percentage) / 100;
                bot_band = self.mark_price * (100 - self.alarm_percentage) / 100;

                if self.price > top_band or self.price < bot_band:
                    # send chart
                    chart_signal.emit(self.name)
                    time.sleep(1)
                    telegram.send_pic('plot.png', self.price)

                    # send message
                    emoticon = EMOTICON_GREEN if self.price > self.mark_price else EMOTICON_RED
                    increase_percent = (self.price / self.mark_price - 1) * 100
                    repeat_cnt = 7 if increase_percent < -20 else 1

                    for x in range(repeat_cnt):
                        telegram.send_msg("%s [%s] %s -> %s (%.2f%%)"
                                          % (emoticon, self.name, self.mark_price, self.price, increase_percent))
                        if self.alarm_stop == 1:
                            break
                    self.alarm_stop = 0
                    self.mark_price = self.price
                    return True
                else:
                    return False
        except Exception as e:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(e).__name__, e.args)
            return False

    def getChartData(self):
        msg = "SELECT date, %s FROM crypto ORDER BY date DESC LIMIT %d" % (self.name, 7000)
        # day = 3
        # time_interval = 3 * 24
        # msg = "SELECT date, %s FROM crypto WHERE date >= NOW() - INTERVAL %s day_hour GROUP BY FLOOR(UNIX_TIMESTAMP(date)/ ( %s * 60))" % (self.name, day, time_interval)
        df = pandas.read_sql_query(msg, self.engine)
        return df
