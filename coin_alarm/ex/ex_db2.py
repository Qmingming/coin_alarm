import pandas as pd
import pymysql
from matplotlib import pyplot as plt
import matplotlib.dates as md

conn = pymysql.connect(host='127.0.0.1', user='root', password='12345', db='coin_price', charset='utf8')
cur = conn.cursor()

#msg = "select * FROM crypto order by date limit 20000"
msg = "select * FROM crypto"

cur.execute(msg)
field_names = [i[0] for i in cur.description]
df = pd.DataFrame(cur, columns=field_names)
print(df)
msg = "ALTER TABLE crypto ADD %s text"
cur.execute(msg, (email, ))

msg = "ALTER TABLE crypto ADD %s text"

cur.execute(msg, email)

msg = "INSERT INTO crypto (date, name, email) VALUES (%s, %s, %s)"

#msg = "UPDATE %s SET %s WHERE date = %s"
with conn:
    with conn.cursor() as cur:
        cur.execute(msg, ('101110', 'Kyumin', 'jeongeun@example.com'))
        conn.commit()