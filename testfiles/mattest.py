import numpy as np, sqlite3 as sql, matplotlib.pyplot as plt

DISTANCES = {
    'gnx': 1.3750,  'gex': 0.0000,  'gtx': 0.0559,
    'gny': 0.0000,  'gey': 1.3750,  'gty': 0.3449,
    'gnz': 0.7528,  'gez': 0.7528,  'gtz': 3.2772,
}

db = sql.connect(r"d:\Documenten\Documents\GitHub\Active-Vibration-Stabilization\data\2023-03-08 - 165241.db")
cur = db.cursor()
data = {}

for col in np.transpose(cur.execute('PRAGMA table_info(guralp);').fetchall())[1]:
    data[col] = 0
res = np.array(cur.execute('SELECT * FROM guralp').fetchall())
t = np.transpose(res)[0]
mat = np.matrix([
                    [1,	0,	0,                 0,  DISTANCES['gez'],  DISTANCES['gey'],],
                    [1,	0,	0,                 0, -DISTANCES['gtz'],  DISTANCES['gty'],],
                    [0,	1,	0, -DISTANCES['gnz'],                 0, -DISTANCES['gnx'],],
                    [0,	1,	0,  DISTANCES['gtz'],	              0, -DISTANCES['gtx'],],
                    [0,	0,	1, -DISTANCES['gey'],  DISTANCES['gex'],                 0,],
                    [0,	0,	1, -DISTANCES['gny'],  DISTANCES['gnx'],                 0,],
                ])

inv = np.linalg.inv(mat)
x,y,z,rx,ry,rz = [np.array([]) for i in range(6)]
for ar in res:
    for i,k in enumerate(data.keys()):
        data[k] = ar[i]
    meas = np.matrix([[data['eastX']],[data['topX']],[data['northY']],[data['topY']],[data['northZ']],[data['eastZ']]])
    meas /= 1000

    X,Y,Z,RX,RY,RZ = inv*meas
    x = np.append(x, X)
    y = np.append(y, Y)
    z = np.append(z, Z)
    rx = np.append(rx, RX)
    ry = np.append(ry, RY)
    rz = np.append(rz, RZ)

plt.plot(t,x, label='x')
plt.plot(t,y,label='y')
plt.plot(t,z,label='z')
plt.plot(t,rx,label='rx')
plt.plot(t,ry,label='ry')
plt.plot(t,rz,label='rz')
plt.legend()
plt.show()

# fourierTransform = np.fft.fft(x)/len(x)
# fourierTransform = fourierTransform[range(int(len(x)/2))]
# tpCount = len(x)
# values = np.arange(int(tpCount/2))
# timePeriod = tpCount / 1000
# frequencies = values / timePeriod
# plt.plot(frequencies, np.abs(fourierTransform))
# plt.show()

# print(meas)
# print(mat)
# print(inv)
# print(data)