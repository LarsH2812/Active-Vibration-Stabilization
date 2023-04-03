import numpy as np, matplotlib.pyplot as plt
import control as c

convdB = lambda x: 20 * np.log10(x)

s = c.tf('s')
num1 = 1*s
den1 = .2*s**2 + .1*s + 0.4
sys1 = 50 * num1/den1


sys = sys1

bode = c.bode_plot(sys, plot=False, omega= np.linspace(10e-2,10e2,10000000))
amplitude:np.ndarray = bode[0]
phase:np.ndarray = bode[1]
freq:np.ndarray = bode[2]

maxAmp = amplitude.max()
_3db = maxAmp * 10**(-3/20)

arr_3db = _3db * np.ones_like(amplitude)
dif = amplitude - arr_3db
db3 = np.argsort(np.abs(dif))[0:2]

freq_res = freq[np.argmax(amplitude)]
freq_l_db3, freq_h_db3 = np.sort([freq[db3[0]],freq[db3[-1]]])

Q_fact = freq_res/ (freq_h_db3 - freq_l_db3)

print(Q_fact)
print(convdB(maxAmp))
print(convdB(amplitude[db3[0]]/maxAmp))
print(convdB(amplitude[db3[-1]]/maxAmp))
print(convdB(_3db))

top = _3db * np.ones_like(db3)

fig1, (mag,pha) = plt.subplots(2,1,sharex=True,label='bode plot')
mag.plot(freq,amplitude)
pha.plot(freq, np.rad2deg(phase))
mag.set_xscale('log'); mag.set_xlim(freq[0], freq[-1])
mag.set_yscale('log'); mag.set_ylim(10e-2,10e2)
mag.grid(True, 'both')
pha.grid(True, 'both')
mag.plot(freq[db3],top)
fig1.tight_layout()
plt.show()
