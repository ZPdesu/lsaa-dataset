from scipy import linalg
import numpy as np

# this function solve the homogeneous least squares prob
# A = line_homo', find x s.t. min(||Ax||)
# if b is given, then add a constraint: b'x = 0, which means x is forced to
# be orthogonal to b. [Zhai et al. 2016]

def lines_normal(line_homo, b=None):
    if b is None:
        [U,_,_] = linalg.svd(line_homo.dot(line_homo.T))
        vp_homo = U[:, 2]
    else:
        if len(b.shape) == 1:
            b = np.array([b]).T
        [U, _, _] = linalg.svd(b)
        p = U[:, 1]
        q = U[:, 2]
        Am = line_homo.T.dot(np.stack([p, q], axis=1))
        [U, _, _] = linalg.svd(Am.T.dot(Am))
        lambda_v = U[:, -1]
        vp_homo = np.stack([p, q]).T.dot(lambda_v)
        vp_homo = vp_homo / linalg.norm(vp_homo)

    # force to the z-positive semisphere
    vp_homo = vp_homo * np.sign(vp_homo[2] + np.finfo(float).eps)

    # [0 0 0] -> [0 1 0]
    if np.sum(vp_homo) == 0:
        vp_homo = np.array([0.0, 1.0, 0.0])

    return vp_homo