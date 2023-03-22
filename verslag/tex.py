import matplotlib
import matplotlib.pyplot as plt
import numpy as np

v1 = np.array([1,2])
v2 = np.array([5,1])

v3 = v2 - v1

plt.quiver(0,0,v1[0],v1[1],angles='xy',scale_units='xy',scale=1)
plt.quiver(0,0,v2[0],v2[1],angles='xy',scale_units='xy',scale=1)
plt.quiver(v1[0],v1[1],v3[0],v3[1],angles='xy',scale_units='xy',scale=1)
plt.show()