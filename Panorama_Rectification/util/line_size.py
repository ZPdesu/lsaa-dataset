import numpy as np

def line_size(seglines):
    if len(seglines.shape) == 2:
        return np.sqrt(np.power((seglines[:,0] - seglines[:,2]),2) + np.power((seglines[:,1] - seglines[:,3]),2))
    if len(seglines.shape) == 1:
        return np.sqrt(np.power((seglines[0] - seglines[2]),2) + np.power((seglines[1] - seglines[3]),2))