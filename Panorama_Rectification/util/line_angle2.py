import math
def line_angle2(line):
    x1 = line[0]
    y1 = line[1]
    x2 = line[2]
    y2 = line[3]

    if x2 > x1:
        angle = math.atan2((y2 - y1), (x2 - x1))
    else:
        angle = math.atan2((y1 - y2), (x1 - x2))
    return angle
