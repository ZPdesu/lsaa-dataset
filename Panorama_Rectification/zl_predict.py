from util.line_angle2 import line_angle2
from util.line_hmg_from_two_points import line_hmg_from_two_points
import mnf_modes

import numpy as np

def zl_predict(ls, dist_max, u0, v0, width, height, params):
    hist = []
    ang = []
    for i in range(ls.shape[0]):
        ang.append(line_angle2(ls[i,:]))
        if ang[i] < -np.pi / 4:
            ang[i] = ang[i] + np.pi
        if np.abs(ang[i] - np.pi / 2) < params.theta_v:
            l = line_hmg_from_two_points(ls[i, 0:2], ls[i, 2:4])
            dist = np.abs(np.dot(l, np.array([width / 2, height / 2, 1])))
            if dist < dist_max:
                hist.append(ang[i])

    [N, edges0] = np.histogram(hist, np.arange(np.pi/2 - np.pi/8, np.pi/2 + np.pi/8 + np.pi/180, np.pi/180))
    N[np.where(N <= 5)[0]] = 0
    if np.sum(N) == 0:
        N[int(np.round(len(N) / 2 + 0.1)) - 1] = 1
    edges = (edges0[:-1] + edges0[1:]) / 2

    max_modes = np.zeros([2*len(N)])
    H = np.zeros([len(N)])
    Nout = mnf_modes.mnf(np.double(N), len(N), 1, max_modes, H)
    max_modes = max_modes[:Nout * 2]
    max_modes = max_modes.reshape(2, Nout).T
    H = H[:Nout]
    H = H.reshape(Nout)

    if len(max_modes) == 0 or max_modes.shape[1] == 0:
        max_modes = np.array([[1, N.shape[0]]])
        H = 0
    else:
        I = np.argsort(-H)
        H.sort()
        H = H[::-1]
        max_modes = max_modes[I, :]
    zl = []
    for i in range(max_modes.shape[0]):
        Ni = np.zeros(N.shape[0])
        a = max_modes[i, 0]
        b = max_modes[i, 1]
        Ni[int(a-1):int(b)] = N[int(a-1):int(b)]
        m = np.max(Ni)
        I = np.where(Ni == m)[0]
        j = I[0]
        a = edges[j]
        l = np.abs(v0 / np.sin(a))
        zl.append(u0+l*np.cos(np.pi-a))

    return zl




