import numpy as np
from util.line_hmg_from_two_points import line_hmg_from_two_points
from util.normalize import normalize

def hl_sample(zenith_homo, modes_homo, modes_offset, modes_left, modes_right, H, u0, v0, width, height, focal, params):
    np.random.seed(1)
    samp_homo = modes_homo
    samp_left = modes_left
    samp_right = modes_right
    S = params.S

    tilt = np.arctan((zenith_homo[0] / zenith_homo[2]) / (zenith_homo[1] / zenith_homo[2]))

    if np.isnan(tilt):
        tilt = 0
    nsamp = np.ceil(S / modes_homo.shape[1])
    x = np.linspace(-2.0, 2.0, num=1e5)
    uniformrnd = np.arange(1, 1e5 + 1)
    for i in range(modes_homo.shape[1]):
        for j in range(int(nsamp) - 1):
            if H[i] <= 0:
                draw = np.random.rand() * uniformrnd[-1]
                id = np.min(np.where(uniformrnd >= draw)[0])
                orand = x[id] * height + modes_offset[i]
            else:
                orand = np.random.normal(0, params.sigma * height) + modes_offset[i]
            mnf_center = np.array([u0 + orand * np.cos(-tilt + np.pi / 2), v0 + orand * np.sin(-tilt + np.pi / 2)])
            hmnf = line_hmg_from_two_points(mnf_center, mnf_center + np.array([np.cos(-tilt), np.sin(-tilt)]))
            samp_left = np.append(samp_left, -hmnf[2] / hmnf[1])
            samp_right = np.append(samp_right, (-hmnf[0] * width - hmnf[2]) / hmnf[1])
            mode_seg = np.array([[0, samp_left[-1], width, samp_right[-1]]])
            tmp = normalize(mode_seg, width, height, focal)
            samp_homo = np.append(samp_homo, tmp, axis=1)

    return samp_homo, samp_left, samp_right

