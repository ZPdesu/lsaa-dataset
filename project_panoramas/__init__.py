import numpy as np

def calculate_no_adaptive_coor(h_fov, v_fov1, v_fov2, mpp=0.0125):
    y = 10

    x1 = np.tan(np.radians(-h_fov / 2)) * y
    x2 = np.tan(np.radians(h_fov / 2)) * y
    width = x2 - x1

    z1 = np.tan(np.radians(v_fov1)) * y
    z2 = np.tan(np.radians(v_fov2)) * y
    height = z2 - z1


    m = int(np.ceil(height / mpp))
    n = int(np.ceil((width) / mpp))

    if m % 2 == 1:
        m = m + 1
    if n % 2 == 1:
        n = n + 1


    # m = int(np.ceil(6656 / 180 * (v_fov2 - v_fov1)))
    # n = int(np.ceil(6656 / 180 * (h_fov2 - h_fov1)))

    p0 = np.array([x1, y, 0.])
    p1 = np.array([x2, y, 0.])
    middle = (p0 + p1) / 2

    up = np.array([0., 0., 1.])
    vec = p1 - p0
    dist = np.linalg.norm(vec)
    vec /= dist

    # Generate barycentric coordinates for every point on the face-grid
    u, v = np.mgrid[-z2:-z1:m * 1j, x1:x2:n * 1j]

    # Generate enu-coordinates for each point on the face-grid
    xy = np.outer(u, up) + np.outer(v, vec) + middle

    new_xy = np.vstack([xy[:, 0], xy[:, 2], xy[:, 1]])
    focal = y / mpp

    return new_xy, m, n, focal


def calculate_new_pano(point1, im):

    # sample_points = sample_points / np.sqrt(np.power(sample_points, 2).sum(axis=1)).reshape([-1, 1])

    angle_x = np.degrees(np.arctan2(point1[:, 0], point1[:, 2]))
    angle_y = np.degrees(np.arctan2(point1[:, 1], np.hypot(point1[:, 2], point1[:, 0])))

    # print(sample_point[0])
    height = im.height
    width = im.width

    center = np.array([width, height]) / 2

    x_list = angle_x * (width / 360) + center[0]
    y_list = angle_y * (height / 180) + center[1]
    coordinates = np.vstack([y_list, x_list])
    del im
    return coordinates



def R_roll(angle):
    return np.array([[np.cos(angle), -np.sin(angle), 0],
                     [np.sin(angle), np.cos(angle), 0], [0., 0., 1.]])

def R_pitch(angle):
    return np.array([[1, 0, 0], [0, np.cos(angle), -np.sin(angle)],
                     [0, np.sin(angle), np.cos(angle)]])

def R_heading(angle):
    return np.array([[np.cos(angle), 0, np.sin(angle)], [0, 1, 0],
                     [-np.sin(angle), 0, np.cos(angle)]])
