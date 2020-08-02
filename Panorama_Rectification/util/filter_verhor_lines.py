import numpy as np
def filter_verhor_lines(ls_homo, z_homo,  params):

    # filter vertical line segments
    cos_val = np.abs(ls_homo.T.dot(z_homo))
    inlier_id = cos_val > np.sin(np.pi /180 *params.theta_verline)
    lines_id = np.where(inlier_id)[0]

    # filter horizontal line segments
    if not params.include_infinite_hvps:
        ortho_thres = np.sin(np.pi /180 *params.theta_horline)
        lhomo = ls_homo[:, lines_id]
        cos_val = np.abs(lhomo.T.dot(np.array([-z_homo[1], z_homo[0], 0])))
        inlier_id = cos_val > ortho_thres
        lines_id = lines_id[inlier_id]

    return lines_id