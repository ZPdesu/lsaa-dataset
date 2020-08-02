
import numpy as np
from util.filter_verhor_lines import filter_verhor_lines
from vp_predict import vp_predict

def hvp_from_zenith(ls_homo, z_homo, params):

    candidates = {}
    nhvps = []
    helpfulIds = filter_verhor_lines(ls_homo, z_homo, params)
    initialIds = np.arange(len(helpfulIds))
    if z_homo[1] > 0:
        candidates["horizon_homo"] = z_homo
    else:
        candidates["horizon_homo"] = -z_homo
    # if i == 18:
    #     print(0)
    [candidates["sc"], candidates["hvp_homo"], hvp_groups] = vp_predict(ls_homo[:, helpfulIds], initialIds, candidates["horizon_homo"], params)
    candidates["hvp_groups"] = [helpfulIds[hvp_groups[k]] for k in range(len(hvp_groups))]
    nhvps.append(candidates["hvp_homo"].shape[0])

    # output results

    results = {}
    results["hvp_groups"] = candidates["hvp_groups"]
    results["hvp_homo"] = candidates["hvp_homo"]
    results["score"] = candidates["sc"]
    return results





def get_all_hvps(ls_homo, z_homo, params):
    candidates = {}
    helpfulIds = filter_verhor_lines(ls_homo, z_homo, params)
    initialIds = np.arange(len(helpfulIds))
    if z_homo[1] > 0:
        candidates["horizon_homo"] = z_homo
    else:
        candidates["horizon_homo"] = -z_homo

    inter_homo = vp_intersection(ls_homo[:, helpfulIds], initialIds, candidates["horizon_homo"])

    return inter_homo





def vp_intersection(lines_homo, initialIds, horizon_homo):
    # compute intersections between the line segments and the HL candidate

    inter_homo = np.cross(lines_homo[:, initialIds].T, horizon_homo).T
    inter_homo = inter_homo / np.sqrt(np.sum(np.power(inter_homo, 2), axis=0))
    inter_homo = inter_homo * np.sign(inter_homo[2, :] + np.finfo(float).eps)
    # inter_pts = inter_homo[:2, :] / inter_homo[2, :]

    return inter_homo.T






# import mnf_modes
# N = np.array([0,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
#
# max_modes = np.zeros([2 * len(N)])
# H = np.zeros([len(N)])
# Nout = mnf_modes.mnf(np.double(N), len(N), 400, max_modes, H)
# max_modes = max_modes[:Nout * 2]
# max_modes = max_modes.reshape(2, Nout).T
# H = H[:Nout]
# H = H.reshape(Nout)
# print(100)
