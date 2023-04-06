import sqlite3 as sql, time
import numpy as np
import matplotlib.pyplot as plt

t0 = time.time()
db = sql.connect('Meetfiles/data/2023-04-04 - 100631.db')
cur = db.cursor()

print(time.time() - t0)
ret = cur.execute('SELECT * FROM guralp')
print(time.time() - t0)
ret = ret.fetchall()
print(time.time() - t0)
ret = np.transpose(ret)
print(time.time() - t0)
plt.plot(ret[0],ret[1])
plt.show()
