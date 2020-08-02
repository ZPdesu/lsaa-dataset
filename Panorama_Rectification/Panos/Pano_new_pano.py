from Panos.Pano_visualization import R_roll, R_pitch
from scipy.ndimage.interpolation import map_coordinates
import numpy as np
from PIL import Image
import skimage.io
import os
from Panos.Pano_consensus_vis import calculate_zenith_point_coordinate, calculate_horizon_coordinates, calculate_hvps
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw


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
    return coordinates


def save_heading_pitch_json(point1, im, m, n):
    angle_x = np.degrees(np.arctan2(point1[:, 0], point1[:, 2]))
    angle_y = np.degrees(np.arctan2(point1[:, 1], np.hypot(point1[:, 2], point1[:, 0])))
    coordinates = np.vstack([angle_x, -angle_y])
    coordinates = coordinates.reshape(2, m, n)
    return coordinates






def create_new_panorama(im_path, pitch, roll, root):
    im = Image.open(im_path)

    height = im.height
    width = im.width

    u, v = np.mgrid[-np.pi / 2:np.pi / 2:height * 1j, -np.pi:np.pi:width * 1j]

    y = np.sin(u)
    x = np.cos(u) * np.sin(v)
    z = np.cos(u) * np.cos(v)

    coordinates = np.array([x, y, z]).transpose([1, 2, 0]).reshape(-1, 3)
    coordinates = R_pitch(pitch).dot(R_roll(roll).dot(coordinates.T)).T
    coordinates = calculate_new_pano(coordinates, im)

    coordinates = coordinates.reshape(2, height, width)

    img = skimage.io.imread(im_path)
    sub = np.dstack([
        map_coordinates(img[:, :, 0], coordinates, order=0),
        map_coordinates(img[:, :, 1], coordinates, order=0),
        map_coordinates(img[:, :, 2], coordinates, order=0)
    ])

    save_path = os.path.join(root, 'Pano_rectified/rectified_panorama.jpg')
    skimage.io.imsave(save_path, sub)
    return save_path


def draw_new_panorama(im_path, hv_points, root):
    zenith_point = np.array([0, 1, 0])

    im = Image.open(im_path)
    cir_r = 50
    hori_coordinates = []
    draw = ImageDraw.Draw(im)
    cmap = plt.cm.hsv(np.linspace(0, 1, len(hv_points) + 1))[:, :3]

    tmp_coor = calculate_zenith_point_coordinate(zenith_point, im)
    draw.ellipse([tuple(np.array(tmp_coor) - cir_r), tuple(np.array(tmp_coor) + cir_r)], fill=tuple([0, 0, 0]))

    tmp_coor = calculate_zenith_point_coordinate(-zenith_point, im)
    draw.ellipse([tuple(np.array(tmp_coor) - cir_r), tuple(np.array(tmp_coor) + cir_r)], fill=tuple([0, 0, 0]))

    tmp_coor = calculate_horizon_coordinates(zenith_point, im)
    hori_coordinates.append(tmp_coor)
    draw.line(tmp_coor, fill=tuple([255, 255, 255]), width=4)

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
    save_path = os.path.join(root, 'Pano_rectified/drawed_rectified_panorama.jpg')
    im.save(os.path.join(root, save_path))







# im_path = '/home/zhup/Desktop/Pano/consensus_hvps_center_on_panoramas.jpg'
# im = Image.open(im_path)
#
#
# height = 6656
# width = 13312
#
# u, v = np.mgrid[-np.pi/2:np.pi/2:height * 1j, -np.pi:np.pi:width * 1j]
#
#
# y = np.sin(u)
# x = np.cos(u) * np.sin(v)
# z = np.cos(u) * np.cos(v)
#
#
# pitch = 0.013090747086943225
# roll = -0.024310663703621463
# coordinates = np.array([x, y, z]).transpose([1, 2, 0]).reshape(-1, 3)
# coordinates = R_pitch(pitch).dot(R_roll(roll).dot(coordinates.T)).T
# coordinates = calculate_points(coordinates, im)
#
#
# coordinates = coordinates.reshape(2, height, width)
#
#
# img = skimage.io.imread(im_path)
# sub = np.dstack([
#             map_coordinates(img[:, :, 0], coordinates, order=0),
#             map_coordinates(img[:, :, 1], coordinates, order=0),
#             map_coordinates(img[:, :, 2], coordinates, order=0)
#             ])
# # sub = sub[::-1, :, :]
#
# save_path = 'uu.jpg'
# save_img = skimage.io.imsave(save_path, sub)
#
# print(100)


if __name__ == "__main__":
    print(100)