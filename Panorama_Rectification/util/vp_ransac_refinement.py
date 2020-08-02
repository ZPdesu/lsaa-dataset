import numpy as np
from util.ransac_intersection import ransac_intersection
from util.lines_normal import lines_normal

def vp_ransac_refinement(lines_homo, opt):
    option = {}
    option["iterNum"] = 50
    option["thInlrRatio"] = 0.02
    option["thDist"] = np.sin(opt.theta_con * np.pi / 180)

    [_, inlierId] = ransac_intersection(lines_homo, option)
    zenith_homo = lines_normal(lines_homo[:, inlierId])

    return zenith_homo, inlierId



