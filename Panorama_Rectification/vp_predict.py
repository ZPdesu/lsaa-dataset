import numpy as np
import mnf_modes
from util.vp_refinement import vp_refinement


def vp_score(vp_homo, lines_homo, score_function):
    cos_mat = np.array(vp_homo).dot(lines_homo)
    theta_mat = np.abs(np.arcsin(cos_mat) * 180 / np.pi)
    score_mat = score_function(theta_mat)

    horgroup = []
    score = []
    for i in range(score_mat.shape[0]):
        horgroup.append(np.where(score_mat[i])[0])
        score.append(np.sum(score_mat[i]))

    #horgroup = np.array(horgroup, dtype=object)  # horgroup is a jagged array
    score = np.array(score)
    return score, horgroup




def vp_predict(lines_homo, initialIds, horizon_homo, params):
    # compute intersections between the line segments and the HL candidate

    inter_homo = np.cross(lines_homo[:, initialIds].T, horizon_homo).T
    inter_homo = inter_homo / np.sqrt(np.sum(np.power(inter_homo, 2), axis=0))
    inter_homo = inter_homo * np.sign(inter_homo[2, :] + np.finfo(float).eps)
    inter_homo[2, :] = np.where(inter_homo[2, :] != 0, inter_homo[2, :], np.finfo(float).eps)
    inter_pts = inter_homo[:2, :] / inter_homo[2, :]

    # compute the MMMs of the coordinate histogram
    max_modes = []
    a = horizon_homo[0]
    b = horizon_homo[1]
    c = horizon_homo[2]

    A_hmg = np.cross(horizon_homo, np.array([b, -a, 0]))
    A = np.array([A_hmg[0] / A_hmg[2], A_hmg[1] / A_hmg[2]])
    rho = np.abs(c) / np.sqrt(np.power(a, 2) + np.power(b, 2))
    rho2 = np.sqrt(inter_pts[0, :] * inter_pts[0, :] + inter_pts[1, :] * inter_pts[1, :])

    if rho > 1:
        p = np.arccos(rho / rho2) / np.pi
    else:
        p = np.zeros(rho2.shape)
        d = np.sqrt(np.abs(rho2**2 - rho**2))
        I, = np.where(rho2 <= 1)
        if len(I) != 0:
            p[I] = d[I] / np.pi
        I, = np.where(rho2 > 1)
        if len(I) != 0:
            d2 = np.sqrt(rho2[I] * rho2[I] - 1)
            beta = np.arctan(d2)
            p[I] = (beta + d[I] - d2) / np.pi

    tmp = inter_pts - np.array([A]).T.dot(np.ones([1, inter_pts.shape[1]]))
    dt = np.array([b, -a]).dot(tmp)
    I, = np.where(dt < 0)
    p[I] = -p[I]
    [N, edges] = np.histogram(p, params.L_vp)

    # import scipy.io as sio
    # tmp_mat = sio.loadmat('vp_Nedges.mat')
    # [N, edges] = [tmp_mat['N'][0], tmp_mat['edges'][0]]

    max_modes = np.zeros([2 * len(N)])
    H = np.zeros([len(N)])
    Nout = mnf_modes.mnf(np.double(N), len(N), 400, max_modes, H)
    max_modes = max_modes[:Nout * 2]
    max_modes = max_modes.reshape(2, Nout).T
    H = H[:Nout]
    H = H.reshape(Nout)

    if len(max_modes) == 0:
        max_modes = np.array([])
        H = 0
    else:
        I = np.argsort(-H)
        H.sort()
        H = H[::-1]
        max_modes = max_modes[I, :]

    horgroups = []
    scores = []
    horvps_homo = []

    for i in range(max_modes.shape[0]):
        Ni = np.zeros([N.shape[0]])
        a = max_modes[i, 0]
        b = max_modes[i, 1]
        Ni[int(a) - 1:int(b)] = N[int(a) - 1:int(b)]
        m = np.max(Ni)
        j = np.argmax(Ni)
        p_i = (edges[j] + edges[j+1]) / 2
        vpId = np.argmin(np.abs(p - p_i))
        horvps_homo.append(inter_homo[:,vpId])
        scores.append(m)
        edgesId = np.intersect1d(np.where(p >= edges[int(a)- 1])[0], np.where(p <= edges[int(b)])[0])
        horgroups.append(edgesId)

    if len(max_modes) == 0:
        scores = [0]
        sc = 0
        horvps_homo = np.array([])

    else:
        #refine the VPs according to [Zhai et al.] and/or compute the scores
        if params.hvp_refinement:
            horvps_homo = vp_refinement(lines_homo, horvps_homo, horizon_homo, params)

        [scores, horgroups] = vp_score(horvps_homo, lines_homo, params.score_function)

        #sorted by score
        sortIds = np.argsort(-scores)
        scores.sort()
        scores = scores[::-1]
        horvps_homo = np.array(horvps_homo)[sortIds]
        horgroups = [horgroups[i] for i in sortIds]
        nvps = np.min([len(horgroups), 2])
        sc = np.sum(scores[:nvps])

    return [sc, horvps_homo, horgroups]