import numpy as np
from util.lines_normal import lines_normal

def vp_refinement(lines_homo, vps_homo, horizon_homo, params):
    np.random.seed(1)
    niters = params.refine_niters
    inlier_thr = np.sin(params.theta_con * np.pi / 180)
    ngrps = len(vps_homo)
    for ig in range(ngrps):
        for it in range(niters):
            good_ids = np.where(np.abs(vps_homo[ig].dot(lines_homo)) < inlier_thr)[0]
            vps_homo[ig] = lines_normal(lines_homo[:, good_ids], horizon_homo)
    return vps_homo