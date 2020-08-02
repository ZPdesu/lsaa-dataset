import numpy as np

def calibrate(zvp, hvp, width, height):
    infty = 4
    accuracy = 2
    nt = pow(2, (5 + min(accuracy, np.log2(width) - 5)))
    step_h = width / nt
    Dt_h = np.arctan(step_h/width)
    u0 = width / 2
    v0 = height / 2
    manh_vps = []
    focal = -1
    confident = -1
    mht = []
    mht_count = 0
    mht_best = 0
    hvp_count = hvp.shape[0]
    if hvp_count > 1:
        for v in range(hvp_count):
            for v2 in range(v+1, hvp_count):
                x1 = hvp[v, 0] - u0
                y1 = hvp[v, 1] - v0
                x2 = hvp[v2, 0] - u0
                y2 = hvp[v2, 1] - v0
                ff = np.sqrt(-(x1 * x2 + y1 * y2))
                if ff*ff > 0 and ff > 0.28 * width and ff < 3.8 * width:
                    mht_count = mht_count + 1
                    vv1 = np.array([x1/ff, y1/ff, 1])
                    vv2 = np.array([x2/ff, y2/ff, 1])
                    vv3 = np.cross(vv1, vv2)
                    tmp1 = ff * vv3[0] / vv3[2] + u0
                    tmp2 = ff * vv3[1] / vv3[2] + v0
                    tmp3 = ff
                    tmp5 = v
                    tmp6 = v2
                    at_vz1 = np.arctan(tmp2 / height) / Dt_h
                    at_vz2 = np.arctan(zvp[1] / height) / Dt_h
                    tmp4 = np.min([np.abs(at_vz1 - at_vz2), np.abs(at_vz1 + at_vz2)])
                    mht.append(np.array([tmp1, tmp2, tmp3, tmp4, tmp5, tmp6]))

    mht = np.array(mht)
    if mht_count > 0:
        vvpc_min = np.min(mht[:, 3])
        mht_best = np.argmin(mht[:, 3])
        if vvpc_min < 2 or np.abs(zvp[1] - v0) >= infty * height:
            if vvpc_min < 2:
                confident = 3
            else:
                mht_best = np.argmax(np.abs(mht[:, 1] - v0))
                confident = 1
            id1 = mht[mht_best, 4]
            id2 = mht[mht_best, 5]
            x1 = hvp[int(id1), 0]
            x2 = hvp[int(id2), 0]
            y = mht[mht_best, 1]

            if (y > v0 and x1 > x2) or (y < v0 and x1 < x2):
                mht[mht_best, 4] = id2
                mht[mht_best, 5] = id1

            focal = mht[mht_best, 2]
            manh_vps = np.array([[hvp[int(mht[mht_best, 4]), 0], hvp[int(mht[mht_best, 4]), 1]],
                                 [hvp[int(mht[mht_best, 5]), 0], hvp[int(mht[mht_best, 5]), 1]],
                                 [zvp[0], zvp[1]]])

    if confident == -1 and hvp_count > 0 and np.abs(zvp[1] - v0) < infty * height:
        id_finite = np.where(np.abs(hvp[:, 0] - u0) < infty * width)[0]
        if len(id_finite) > 0:
            y1 = hvp[id_finite[0], 1] - v0
            y2 = zvp[1] - v0
            ff = np.sqrt(-y1 * y2)
            if ff*ff > 0 and ff > 0.28 * width and ff < 3.8 * width:
                focal = ff
                K = np.array([[focal, 0, u0], [0, focal, v0], [0, 0, 1]])
                r2 = np.array([hvp[id_finite[0], 0] - u0, hvp[id_finite[0], 1] - v0, focal])
                r2 = r2 / np.linalg.norm(r2)
                r3 = np.array([zvp[0] - u0, zvp[1] - v0, ff])
                r3 = r3 / np.linalg.norm(r3)
                vpx = K.dot(np.cross(r2, r3))
                vpx = vpx / vpx[2]
                manh_vps = np.array([[vpx[0] + u0, vpx[1] + v0], [hvp[id_finite[0], 0], hvp[id_finite[0], 1]], [zvp[0], zvp[1]]])
                confident = 2

    return focal, manh_vps, confident
