import numpy as np

# convert lines or points from cartesian system (image frame) to homogenous system according to [Zhai et al., CVPR'2016]

def normalize(geometry_img, width, height, focal):
    center = np.array([width, height]) / 2
    if geometry_img.shape[1] == 2:
        geometry_normalized = (geometry_img - center) / focal
    else:
        geometry_normalized = (geometry_img - np.tile(center, 2)) / focal

    N = geometry_normalized.shape[0]
    if geometry_normalized.shape[1] == 2:
        geometry_homo = np.hstack([geometry_normalized, np.ones([N, 1])]).T
    else:
        x1 = normalize(geometry_img[:, [0, 1]], width, height, focal)
        x2 = normalize(geometry_img[:, [2, 3]], width, height, focal)
        geometry_homo = np.cross(x1.T, x2.T).T
        geometry_homo = geometry_homo * np.sign(geometry_homo[1,:] + np.finfo(float).eps)
    geometry_homo = geometry_homo / np.sqrt(np.sum(np.power(geometry_homo, 2), axis=0))
    return geometry_homo







