
import numpy as np
def line_to_segment(lines):
    segments = np.zeros([3,2])
    segments[0] = lines[0:2]
    segments[1] = lines[2:4]
    segments[2] = np.array([np.nan, np.nan])
    return segments