import numpy as np
import numpy.linalg as linalg

def calcdist(M, X):
    d = np.abs(M.dot(X))
    return d


def randIndex(lines_homo, maxIndex, len):
    # INDEX = RANDINDEX(MAXINDEX,LEN)
    # randomly, non-repeatedly select LEN integers from 1:MAXINDEX

    index = np.random.permutation(maxIndex)[:len]

    # normal of great circle consisting of 2 randomly sampled points.

    M = np.cross(lines_homo[:, index[0]], lines_homo[:, index[1]])
    M = M / linalg.norm(M)
    M = M * np.sign(M[1] + np.finfo(float).eps)  # stay in y-positive plane
    return M, index


def ransac_intersection(lines_homo, ransacCoef):
    np.random.seed(1)

    # sample 2 LSs to find the VP
    minPtNum = 2
    iterNum = ransacCoef["iterNum"]
    thInlrRatio = ransacCoef["thInlrRatio"]
    thDist = ransacCoef["thDist"]
    ptNum = lines_homo.shape[1]
    thInlr = np.round(thInlrRatio*ptNum)

    if ptNum < minPtNum:
        M = np.zeros([3,2])
        inlierIdx = []
        N = 0
        return M, inlierIdx

    inlrNum = np.zeros(iterNum)
    fLib = np.zeros([3, iterNum])

    for p in range(iterNum):
        # 1. fit using random points
        [M, _] = randIndex(lines_homo, ptNum, minPtNum)

        # 2. count the inliers, if more than thInlr, refit; else iterate
        dist = calcdist(M, lines_homo)

        inlier1 = np.where(dist < thDist)[0]
        inlrNum[p] = len(inlier1)

        if len(inlier1) < thInlr:
            continue
        fLib[:, p] = M

    # 3. choose the coef with the most inliers
    idx = np.argmax(inlrNum)
    if linalg.norm(fLib[:, idx]) != 0:
        M = fLib[:, idx]
        dist = calcdist(M, lines_homo)
        inlierIdx = np.where(dist < thDist)[0]
    else:
        print("no enough inliers")
        [M, _] = randIndex(lines_homo, ptNum, minPtNum)
        inlierIdx = np.array([])

    return M, inlierIdx

