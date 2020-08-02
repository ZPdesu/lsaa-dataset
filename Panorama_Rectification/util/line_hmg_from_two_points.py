import numpy as np
def line_hmg_from_two_points(p1, p2):
    v1 = np.array([p1[0], p1[1], 1.0])
    v2 = np.array([p2[0], p2[1], 1.0])
    l = np.cross(v1, v2)
    l = l / np.sqrt(l[0] * l[0] + l[1] * l[1])
    return l