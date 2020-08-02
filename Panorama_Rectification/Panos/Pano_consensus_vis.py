import PIL
import numpy as np
from PIL import Image, ImageDraw
import os
from Panos.Pano_utils import line_intersection_homo
from numpy import linalg
import matplotlib.pyplot as plt
from qutip import Bloch, basis

from Panos.Pano_visualization import calculate_zenith_point_coordinate, calculate_horizon_coordinates, calculate_hvps, R_roll, R_pitch


def draw_consensus_zp_hvps(zenith_point, hv_points, im, root):
    cir_r = 80
    hori_coordinates = []
    draw = ImageDraw.Draw(im)
    cmap = plt.cm.hsv(np.linspace(0, 1, len(hv_points) + 1))[:, :3]


    tmp_coor = calculate_zenith_point_coordinate(zenith_point, im)
    draw.ellipse([tuple(np.array(tmp_coor) - cir_r), tuple(np.array(tmp_coor) + cir_r)], fill=tuple([0, 0, 0]))


    tmp_coor = calculate_zenith_point_coordinate(-zenith_point, im)
    draw.ellipse([tuple(np.array(tmp_coor) - cir_r), tuple(np.array(tmp_coor) + cir_r)], fill=tuple([0, 0, 0]))

    cir_r = 30
    tmp_coor = calculate_horizon_coordinates(zenith_point, im)
    hori_coordinates.append(tmp_coor)
    draw.line(tmp_coor, fill=tuple([255,255,255]), width=4)

    for i in range(len(hv_points)):

        # problems need to be fixed

        tmp_coor = calculate_hvps(hv_points[i], im)
        for j in range(len(tmp_coor)):
            draw.ellipse([tuple(np.array(tmp_coor[j]) - cir_r), tuple(np.array(tmp_coor[j]) + cir_r)],
                         fill=tuple((cmap[i] * 255).astype(int)))

    im.save(os.path.join(root, 'consensus_zp_hvps.jpg'))




def draw_consensus_rectified_sphere(hv_points, root):
    b = Bloch()
    b.point_color = ['m', 'k', 'g', 'b', 'w', 'c', 'y', 'r']
    b.zlabel = ['$z$', '']
    b.point_marker = ['o']
    b.point_size = [80]
    b.frame_width = 1.2
    fig = plt.figure(figsize=(20, 20))
    b.fig = fig

    x = (basis(2, 0) + (1 + 0j) * basis(2, 1)).unit()
    y = (basis(2, 0) + (0 + 1j) * basis(2, 1)).unit()
    z = (basis(2, 0) + (0 + 0j) * basis(2, 1)).unit()
    b.add_states([x, y, z])
    for i in range(len(hv_points)):
        # Transform xyz to zxy coordinates
        tmp2 = np.vstack([hv_points[i][:, 2], hv_points[i][:, 0], hv_points[i][:, 1]]).T
        tmp = tmp2.T
        b.add_points(tmp)

    # b.add_points([ 0.99619469809174555, 0.087155742747658166, 0])
    # b.add_points([0.99619469809174555, -0.087155742747658166, 0])
    # b.add_points(tmp)
    name = os.path.join(root, 'consensus_zenith_on_rectified_sphere.jpg')
    b.save(name=name)


def draw_center_hvps_rectified_sphere(hv_points, root):
    b = Bloch()
    b.point_color = ['m', 'k', 'g', 'b', 'w', 'c', 'y', 'r']
    b.zlabel = ['$z$', '']
    b.point_marker = ['o']
    b.point_size = [80]
    b.frame_width = 1.2
    fig = plt.figure(figsize=(20, 20))
    b.fig = fig

    x = (basis(2, 0) + (1 + 0j) * basis(2, 1)).unit()
    y = (basis(2, 0) + (0 + 1j) * basis(2, 1)).unit()
    z = (basis(2, 0) + (0 + 0j) * basis(2, 1)).unit()
    b.add_states([x, y, z])
    for i in range(len(hv_points)):
        # Transform xyz to zxy coordinates
        tmp1 = np.array([hv_points[i][2], hv_points[i][0], hv_points[i][1]])
        tmp2 = np.vstack([tmp1, -tmp1]).T
        tmp = tmp2
        b.add_points(tmp)

    name = os.path.join(root, 'consensus_hvps_center_on_rectified_sphere.jpg')
    b.save(name=name)



def draw_center_hvps_on_panorams(zenith_point, hv_points, im, pitch, roll, root):

    cir_r = 80
    hori_coordinates = []
    draw = ImageDraw.Draw(im)
    cmap = plt.cm.hsv(np.linspace(0, 1, len(hv_points) + 1))[:, :3]

    tmp_coor = calculate_zenith_point_coordinate(zenith_point, im)
    draw.ellipse([tuple(np.array(tmp_coor) - cir_r), tuple(np.array(tmp_coor) + cir_r)], fill=tuple([0, 0, 0]))

    tmp_coor = calculate_zenith_point_coordinate(-zenith_point, im)
    draw.ellipse([tuple(np.array(tmp_coor) - cir_r), tuple(np.array(tmp_coor) + cir_r)], fill=tuple([0, 0, 0]))

    tmp_coor = calculate_horizon_coordinates(zenith_point, im)
    hori_coordinates.append(tmp_coor)
    draw.line(tmp_coor, fill=tuple([255, 255, 0]), width=20)

    hv_points = [R_pitch(pitch).dot(R_roll(roll).dot(vp.T)).T for vp in hv_points]

    for i in range(len(hv_points)):
        # problems need to be fixed

        tmp_coor = calculate_hvps((hv_points[i].reshape(-1, 3)), im)
        for j in range(len(tmp_coor)):
            draw.ellipse([tuple(np.array(tmp_coor[j]) - cir_r), tuple(np.array(tmp_coor[j]) + cir_r)],
                         fill=tuple((cmap[i] * 255).astype(int)))

        tmp_coor = calculate_hvps(-hv_points[i].reshape(-1, 3), im)
        for j in range(len(tmp_coor)):
            draw.ellipse([tuple(np.array(tmp_coor[j]) - cir_r), tuple(np.array(tmp_coor[j]) + cir_r)],
                         fill=tuple((cmap[i] * 255).astype(int)))

    im.save(os.path.join(root, 'consensus_hvps_center_on_panoramas.jpg'))














if __name__ == "__main__":
   print(100)

