import numpy as np
import matplotlib.pyplot as plt

t = np.linspace(0, 6*np.pi, 3000)
sin = np.sin(t)
Fz1 = np.array([])
Fz2 = np.array([])
Fz3 = np.array([])

zMat = np.matrix([[-1.745,	0.727,	1.534],
                  [-0.712,	1.02 , -0.724],
                  [ 1.0  ,  1.0  ,  1.0  ]])
zMat_inv = np.linalg.inv(zMat)
Fz = np.matrix([[0],
                [0],
                [1]])
out = zMat_inv * Fz

Ft1 = out[0,0] * np.sin(t)
Ft2 = out[1,0] * np.sin(t)
Ft3 = out[2,0] * np.sin(t)


for i in sin:
    Fz = np.matrix([[0],
                    [0],
                    [i]])
    out = zMat_inv * Fz
    Fz1 = np.append(Fz1, out[0,0])
    Fz2 = np.append(Fz2, out[1,0])
    Fz3 = np.append(Fz3, out[2,0])


plt.plot(t,Fz1)
plt.plot(t,Fz2)
plt.plot(t,Fz3)
plt.plot(t, (Fz1 + Fz2 + Fz3))
plt.show()

print(Fz3-Ft3)