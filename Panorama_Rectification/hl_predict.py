import numpy as np
import numpy.linalg as linalg
import mnf_modes
from util.line_hmg_from_two_points import line_hmg_from_two_points
from util import normalize

def hl_predict(seglines, zenith_homo, u0, v0, width, height, focal, params):
    L = params.L_h
    x2 = zenith_homo[0] / zenith_homo[2]
    y2 = zenith_homo[1] / zenith_homo[2]
    tilt = np.arctan(x2 / y2)
    if np.isnan(tilt):
        tilt = 0
    offsets = []
    for i in range(seglines.shape[0]):
        v = np.array([seglines[i, 2] - seglines[i, 0], seglines[i, 3] - seglines[i, 1]])
        scal = np.dot(v/linalg.norm(v), np.array([np.cos(-tilt), np.sin(-tilt)]))
        ang = np.arccos(scal)
        if np.abs(ang) < params.theta_h * np.pi / 180:
            tmp = np.dot(np.array([(seglines[i, 2] + seglines[i, 0])/2 - u0, (seglines[i, 3] + seglines[i, 1])/2 - v0]),
                         np.array([np.cos(-tilt + np.pi / 2), np.sin(-tilt + np.pi/2)]))
            offsets.append(tmp)
    offsets = np.asarray(offsets)

    if len(offsets) == 0:
        offsets = np.arange(-height/2, (height+1)/2)
    [N, edges] = np.histogram(offsets, L)

    # import scipy.io as sio
    # tmp_mat = sio.loadmat('N_edges.mat')
    # [N, edges] = [tmp_mat['N'][0], tmp_mat['edges'][0]]


    max_modes = np.zeros([2 * len(N)])
    H = np.zeros([len(N)])
    Nout = mnf_modes.mnf(np.double(N), len(N), 1, max_modes, H)
    max_modes = max_modes[:Nout * 2]
    max_modes = max_modes.reshape(2, Nout).T
    H = H[:Nout]
    H = H.reshape(Nout)

    # Modification 1
    if Nout == 0:
        max_modes = np.array([[1, N.shape[0]]])
        H = np.array([-1])
    else:
        I = np.argsort(-H)
        H.sort()
        H = H[::-1]
        max_modes = max_modes[I, :]
    nmodes = max_modes.shape[0]
    modes_offset = []
    modes_left = []
    modes_right = []
    modes_homo = []
    for i in range(nmodes):
        Ni = np.zeros(N.shape[0])
        a = max_modes[i, 0]
        b = max_modes[i, 1]
        Ni[int(a)-1 : int(b)] = N[int(a)-1 : int(b)]
        bin = np.argmax(Ni)


        #modes_offset.append(edges[0] + (bin + 1) / L * (edges[L-1] - edges[0]))
        modes_offset.append(edges[0] + (bin + 1) / L * (edges[L] - edges[0]))
        mnf_center = np.array([u0 + modes_offset[-1] * np.cos(-tilt + np.pi/2), v0 + modes_offset[-1] * np.sin(-tilt + np.pi/2)])
        hmnf = line_hmg_from_two_points(mnf_center, mnf_center + np.array([np.cos(-tilt), np.sin(-tilt)]))
        modes_left.append(-hmnf[2] / hmnf[1])
        modes_right.append((-hmnf[0]*width -hmnf[2])/ hmnf[1])
        mode_seg = np.array([[0, modes_left[0], width, modes_right[0]]])
        modes_homo.append(np.squeeze(normalize.normalize(mode_seg, width, height, focal)))

    modes_offset = np.array(modes_offset)
    modes_left = np.array(modes_left)
    modes_right = np.array(modes_right)
    modes_homo = np.array(modes_homo).T

    return [modes_homo, modes_offset, modes_left, modes_right, H]




