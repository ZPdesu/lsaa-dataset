from util import line_size
import numpy as np
def ls_filter(thres_aligned, length_t, lsd):
    seglines = lsd
    L0 = line_size.line_size(seglines)
    seglinesC = np.zeros([seglines.shape[0], 2])
    seglinesC[:, 0] = (seglines[:, 2] + seglines[:, 0]) / 2
    seglinesC[:, 1] = (seglines[:, 3] + seglines[:, 1]) / 2
    seglinesJ = np.zeros([seglines.shape[0], 2])
    seglinesJ[:, 0] = -(seglines[:, 3] - seglines[:, 1]) / L0
    seglinesJ[:, 1] = (seglines[:, 2] - seglines[:, 0]) / L0
    I = np.argsort(-L0)
    L0.sort()
    L0 = L0[::-1]
    seglines = seglines[I, :]
    seglinesC = seglinesC[I, :]
    seglinesJ = seglinesJ[I, :]
    i = 0

    while (i < seglines.shape[0] -1):
        C = seglinesC[i, 0:2]
        J = seglinesJ[i, :]
        X1 = np.abs(((seglines[i + 1:, 0:2]) - np.tile(C, [seglines.shape[0] - i - 1, 1])).dot(J.T))
        X2 = np.abs(((seglines[i + 1:, 2:4]) - np.tile(C, [seglines.shape[0] - i - 1, 1])).dot(J.T))

        I = np.intersect1d(np.where(X1 < thres_aligned)[0], np.where(X2 < thres_aligned)[0]) + i + 1
        seglines = np.delete(seglines, I, 0)
        L0 = np.delete(L0, I)
        seglinesC = np.delete(seglinesC, I, 0)
        seglinesJ = np.delete(seglinesJ, I, 0)
        i += 1

    i = 0
    while i < seglines.shape[0]:
        if L0[i] < length_t / 2:
            seglines = np.delete(seglines, i, 0)
            L0 = np.delete(L0, i)
            seglinesJ = np.delete(seglinesJ, i, 0)
            i -= 1
        i += 1
    return seglines