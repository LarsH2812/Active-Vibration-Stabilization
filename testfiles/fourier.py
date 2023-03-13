import sqlite3, sys
import numpy as np
import matplotlib.pyplot as plt
print(sys.version)

fig1 = plt.figure()

db = sqlite3.connect("data/2023-03-08 - 103041.db")
cur = db.cursor()

lines = {}

res = np.transpose(cur.execute('SELECT * FROM fourier').fetchall())[0]
des = 1.4 * np.ones_like(res)
out = res-des

print(res[np.argmin(np.abs(out))])

# print(lines)