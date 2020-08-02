import numpy as np
from util.filter_verhor_lines import filter_verhor_lines
from vp_predict import vp_predict

def hl_score(hl_samp, ls_homo, z_homo, params):

    candidates = [{} for i in range(hl_samp.shape[1])]
    nhvps = []
    for i in range(hl_samp.shape[1]):
        helpfulIds = filter_verhor_lines(ls_homo, z_homo, params)
        initialIds = np.arange(len(helpfulIds))
        candidates[i]["horizon_homo"] = hl_samp[:, i]
        # if i == 18:
        #     print(0)
        [candidates[i]["sc"], candidates[i]["hvp_homo"], hvp_groups] = vp_predict(ls_homo[:, helpfulIds], initialIds, candidates[i]["horizon_homo"], params)
        candidates[i]["hvp_groups"] = [helpfulIds[hvp_groups[k]] for k in range(len(hvp_groups))]
        nhvps.append(candidates[i]["hvp_homo"].shape[0])

    # decide the horizon line

    horCandidateScores = np.array([candidates[i]["sc"] for i in range(hl_samp.shape[1])])
    maxHorCandidateId = np.argmax(horCandidateScores)
    hl_homo = candidates[maxHorCandidateId]["horizon_homo"]

    # output results

    results = {}
    results["hvp_groups"] = candidates[maxHorCandidateId]["hvp_groups"]
    results["hvp_homo"] = candidates[maxHorCandidateId]["hvp_homo"]
    results["score"] = candidates[maxHorCandidateId]["sc"]

    return hl_homo, results




