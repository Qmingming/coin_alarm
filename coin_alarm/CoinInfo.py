from random import randint

import pandas as pd
import pymysql
import yaml

import chrome_selenium


class CoinInfo:
    webcrawler = chrome_selenium.ChromeSelenium()
    conn = pymysql.connect(host='127.0.0.1', user='root', password='12345', db='coin_price', charset='utf8')
    cur = conn.cursor()

    def __init__(self, yaml_info):
        self.xs = []
        self.ys = []

        # self.chart_num = int(yaml_info['chart_num'])
        self.name = yaml_info['name']
        self.url = yaml_info['url']
        self.xpath = yaml_info['xpath']

    def addPrice(self, t):
        print("searching price for coin", self.name)
        price = float(self.webcrawler.findElement(self.url, self.xpath))
        print(self.name, price)
        if price == -1:
            return
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
                print(msg)
                self.cur.execute(msg)

            #msg = "UPDATE %s SET %s WHERE date = %s" % (self.name, price, t)
            msg = "INSERT INTO crypto (date, %s) VALUES ('%s', '%s')" % (self.name, t, price)
            print(msg)
            self.cur.execute(msg)
        except Exception as e:
            #print(e)
            msg = "UPDATE crypto SET %s = %s WHERE date = '%s'" % (self.name, price, t)
            print(msg)
            self.cur.execute(msg)
        finally:
            self.conn.commit()