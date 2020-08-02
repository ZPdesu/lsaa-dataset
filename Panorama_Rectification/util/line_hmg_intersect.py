import numpy as np

def line_hmg_intersect(l1_hmg,l2_hmg):

    p_hmg = np.cross(l1_hmg, l2_hmg)
    p = np.array([p_hmg[0] / p_hmg[2], p_hmg[1] / p_hmg[2]])
    return p