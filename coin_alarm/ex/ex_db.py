import pandas as pd
import pymysql
from matplotlib import pyplot as plt
import matplotlib.dates as md

conn = pymysql.connect(host='127.0.0.1', user='root', password='12345', db='coin', charset='utf8')

cur = conn.cursor()

msg = "select * FROM kai_protocol order by date limit 20000"

cur.execute(msg)
field_names = [i[0] for i in cur.description]
df = pd.DataFrame(cur, columns=field_names)
print(df)

df = df[['btc', 'eth', 'date']]
print(df['date'])

fig = plt.figure(figsize=(14, 6))
ax1 = fig.add_subplot(1, 2, 1)
ax1.plot(df['date'], df['eth'], label='A', color='green')
ax1.set_xticks(rotation=90)
ax1.xaxis.set_major_locator(md.DayLocator(interval=4))
ax1.xaxis.set_major_formatter(md.DateFormatter('%D'))

ax2 = fig.add_subplot(1, 2, 2)
ax2.plot(df['date'], df['btc'], label='B', color='steelblue')
ax2.xaxis.set_major_locator(md.DayLocator(interval=4))
ax2.xaxis.set_major_formatter(md.DateFormatter('%H:%M'))

plt.show()