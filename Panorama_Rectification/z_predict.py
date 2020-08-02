import numpy as np
from util.lines_normal import lines_normal
from util.vp_ransac_refinement import vp_ransac_refinement

def vp_score(vp_homo, lines_homo, score_function):
    cos_mat = vp_homo.dot(lines_homo)
    theta_mat = np.abs(np.arcsin(cos_mat)*180/np.pi)

    score_mat = score_function(theta_mat)
    horgroup = np.where(score_mat)[0]
    score = np.sum(score_mat)
    return score, horgroup





def z_predict(lines_homo, zenith_line_homo, params, refine):
    # threshold zenith LSs ids
    lines_tilt_ortho = np.arctan(-lines_homo[1,:] / lines_homo[0,:])*180 / np.pi
    zenith_tilt = np.arctan(-zenith_line_homo[1, 0] / zenith_line_homo[0, 0])*180 / np.pi
    verticalInd = np.where(np.abs(lines_tilt_ortho - zenith_tilt) < params.theta_z)[0]
    zenith_homo_pred = lines_normal(lines_homo[:, verticalInd])

    # refinement
    if refine:
        [zenith_homo, _] = vp_ransac_refinement(lines_homo[:, verticalInd], params)
    else:
        zenith_homo = zenith_homo_pred

    # LS grouping

    [_, groups] = vp_score(zenith_homo, lines_homo, params.score_function)
    zengroupIds = groups
    return zenith_homo, zengroupIds



