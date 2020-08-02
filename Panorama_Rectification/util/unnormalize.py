# convert lines or points from homogeneous system to cartesian system (image frame)
# according to [Zhai et al., CVPR'2016]
import numpy as np
from util.line_to_segment import line_to_segment


def unnormalize(geometry_homo, width, height, focal, isline=None):
    if isline != None and not isline:
        p = geometry_homo
        if len(p.shape) == 1:
            geometry_img = p[0:2] / p[2]
            geometry_img = geometry_img * focal + np.array([width, height]) / 2
        elif len(p.shape) == 2 and p.shape[1] == 3:
            p = p.T
            geometry_img = p[0:2] / p[2]
            geometry_img = geometry_img.T
            geometry_img = geometry_img * focal + np.array([width, height]) / 2
            #print("each row a vector")
        else:
            print("order error")
    else:
        h = geometry_homo
        if len(h.shape) == 1:
            pl = (0 - width/2) / focal
            pr = (width - width/2) / focal
            ly = (height/2 - ((h[0]*pl + h[2]) / h[1]) * focal)
            ry = (height/2 - ((h[0]*pr + h[2]) / h[1]) * focal)
            geometry_img = np.array([0, ly, width, ry])
            geometry_img = line_to_segment(geometry_img)
        else:
            print("unnormalize error")
    return geometry_img

