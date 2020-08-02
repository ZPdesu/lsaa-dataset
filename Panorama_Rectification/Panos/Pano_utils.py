import numpy as np
from qutip import Bloch

def line_intersection_2D(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1]) #Typo was here

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
       raise Exception('lines do not intersect')

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return np.array([x, y])



def line_intersection_homo(hl, z, center, focal):
    intersect_point = line_intersection_2D((hl[0], hl[1]), (center, z))
    intersect_homo = (intersect_point - center) / focal
    intersect_homo = np.hstack([intersect_homo, 1.0])
    intersect_homo = intersect_homo / np.sqrt(np.power(intersect_homo, 2).sum())
    return intersect_homo

def apply_mask(image, mask, color, alpha=0.5):
    """Apply the given mask to the image.
    """
    for c in range(3):
        image[:, :, c] = np.where(mask == 1,
                                  image[:, :, c] *
                                  (1 - alpha) + alpha * color[c] * 255,
                                  image[:, :, c])
    return image




if __name__ == "__main__":
    print('test')
    # b = Bloch()
    # b.point_color = ['y', 'm', 'c', 'r', 'g', 'b', 'w', 'k']
    # b.zlabel = ['$z$', '']
    # b.point_marker = ['o']
    # b.point_size = [10]
    #
    # pnt1 = np.array([[0, 0], [1, 0], [0, 1]])
    # pnt2 = np.array([[0, 1], [-1, 0], [0, 0]])
    # b.add_points(pnt1)
    # b.add_points(pnt2)
    # b.save('png')










# hl = np.array([[0., 774.0801861 ],[1600., 825.23757385], [np.nan, np.nan]])
# center = np.array([800, 800])
# focal = 800
#
# z = np.array([-3198.67797231, 125862.77267995])
#
# intersect_homo = line_intersection_homo(hl, z, center, focal)
# print(intersect_homo)



#####################################

#test real roll pitch
# point1 = np.array([-0.03195638, 0.00639339, 0.99946882])
# #point2 = np.array([0., 0., 1.])
#
# def R_roll(angle):
#     return np.array([[np.cos(angle), 0, np.sin(angle)], [0, 1, 0],
#                      [-np.sin(angle), 0, np.cos(angle)]])
# def R_pitch(angle):
#     return np.array([[1, 0, 0], [0, np.cos(angle), -np.sin(angle)],
#                      [0, np.sin(angle), np.cos(angle)]])
#
# pitch = -np.arctan(point1[1] / point1[2])
# roll = np.arctan(point1[0] / np.sign(point1[2]) * np.sqrt(np.power(point1[1], 2) + np.power(point1[2], 2)))

# print(R_roll(roll).dot(np.array([0, 0, 1])))
# print(R_pitch(pitch).dot(R_roll(roll).dot(np.array([0, 0, 1]))))
#
# print(roll, pitch)