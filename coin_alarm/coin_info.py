import threading

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

    def __init__(self, yaml_info):
        self.price = None
        self.mark_price = None

        self.chart_num = int(yaml_info['chart_num'])
        self.series = int(yaml_info['series'])
        self.name = yaml_info['name']
        self.url = yaml_info['url']
        self.xpath = yaml_info['xpath']
        self.alarm_percentage = yaml_info['alarm_percentage']

        self.ax = None

    def addPrice(self, t):
        print("searching price for coin", self.name, end=" - ")
        price = float(self.webcrawler.findElement(self.url, self.xpath))
        print(price)

        if price == -1:
            return -1
        else:
            if price > 1:
                price = float("{:.2f}".format(price))
            else:
                price = float("{:.4f}".format(price))

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

    def checkMarkCondition(self):
        EMOTICON_GREEN = "\U0001F7E2"
        EMOTICON_RED = "\U0001F534"

        if self.mark_price is None:
            # for initial
            self.mark_price = self.price
            return True
        else:
            backup_mark_price = self.mark_price
            top_band = self.mark_price * (100 + self.alarm_percentage) / 100;
            bot_band = self.mark_price * (100 - self.alarm_percentage) / 100;

            if self.price > top_band or self.price < bot_band:
                if self.price > self.mark_price:
                    emoticon = EMOTICON_GREEN
                else:
                    emoticon = EMOTICON_RED
                telegram.send_msg("%s [%s] %s -> %s (%.2f%%)"
                                  % (emoticon, self.name, self.mark_price, self.price, (self.price/self.mark_price-1)*100))
                self.mark_price = self.price
                return True
            else:
                return False

    def getChartData(self):
        msg = "SELECT date, %s FROM crypto ORDER BY date DESC LIMIT %d" % (self.name, 7000)
        #day = 3
        #time_interval = 3 * 24
        #msg = "SELECT date, %s FROM crypto WHERE date >= NOW() - INTERVAL %s day_hour GROUP BY FLOOR(UNIX_TIMESTAMP(date)/ ( %s * 60))" % (self.name, day, time_interval)
        df = pandas.read_sql_query(msg, self.engine)
        return df
