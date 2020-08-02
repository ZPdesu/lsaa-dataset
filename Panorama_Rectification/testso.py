import mnf_modes
import numpy as np

histo = np.array([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,8,15,20,19,8,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], dtype=np.double)
N = 45
epsilon = 1
outArray1 = np.zeros([2*N])
outArray2 = np.zeros([N])

print(len(outArray1))

Nout = mnf_modes.mnf(histo, N, epsilon,outArray1, outArray2)
max_modes = outArray1[:Nout*2]
max_modes = max_modes.reshape(2, Nout).T
H = outArray2[:Nout]
H = H.reshape(1, Nout).T
print(max_modes)
print(H)