import PIL
import numpy as np
from PIL import Image, ImageDraw
import os
from Panos.Pano_utils import line_intersection_homo
from numpy import linalg
import matplotlib.pyplot as plt
from qutip import Bloch, basis

def R_roll(angle):
    return np.array([[np.cos(angle), -np.sin(angle), 0],
                     [np.sin(angle), np.cos(angle), 0], [0., 0., 1.]])

def R_pitch(angle):
    return np.array([[1, 0, 0], [0, np.cos(angle), -np.sin(angle)],
                     [0, np.sin(angle), np.cos(angle)]])

def R_heading(angle):
    return np.array([[np.cos(angle), 0, np.sin(angle)], [0, 1, 0],
                     [-np.sin(angle), 0, np.cos(angle)]])




############################################################



def calculate_venith_points(point1, im):


    # sample_points = sample_points / np.sqrt(np.power(sample_points, 2).sum(axis=1)).reshape([-1, 1])

    angle_x = np.degrees(np.arctan2(point1[:, 0], point1[:, 2]))
    angle_y = np.degrees(np.arctan2(point1[:, 1], np.hypot(point1[:, 2], point1[:, 0])))

    # print(sample_point[0])
    height = im.height
    width = im.width

    center = np.array([width, height]) / 2

    x_list = angle_x * (width / 360) + center[0]
    y_list = angle_y * (height / 180) + center[1]

    coordinates = [(x, y) for x, y in zip(x_list, y_list)]
    return coordinates


def calculate_hvps(point1, im):

    # sample_points = sample_points / np.sqrt(np.power(sample_points, 2).sum(axis=1)).reshape([-1, 1])

    angle_x = np.degrees(np.arctan2(point1[:, 0], point1[:, 2]))
    angle_y = np.degrees(np.arctan2(point1[:, 1], np.hypot(point1[:, 2], point1[:, 0])))

    # print(sample_point[0])
    height = im.height
    width = im.width

    center = np.array([width, height]) / 2

    x_list = angle_x * (width / 360) + center[0]
    y_list = angle_y * (height / 180) + center[1]

    coordinates = [(x, y) for x, y in zip(x_list, y_list)]
    return coordinates



def calculate_zenith_point_coordinate(point1, im):


    # sample_points = sample_points / np.sqrt(np.power(sample_points, 2).sum(axis=1)).reshape([-1, 1])

    angle_x = np.degrees(np.arctan2(point1[0], point1[2]))
    angle_y = np.degrees(np.arctan2(point1[1], np.hypot(point1[2], point1[0])))

    # print(sample_point[0])
    height = im.height
    width = im.width

    center = np.array([width, height]) / 2

    x = angle_x * (width / 360) + center[0]
    y = angle_y * (height / 180) + center[1]

    coordinates = (x, y)
    return coordinates






def calculate_horizon_coordinates(point1, im):
    pitch = np.arctan2(point1[2], point1[1])
    roll = - np.arctan(point1[0] / np.sign(point1[1]) * np.hypot(point1[1], point1[2]))
    x_homo = np.cos(np.linspace(0, 2 * np.pi, 2000))
    z_homo = np.sin(np.linspace(0, 2 * np.pi, 2000))

    horizon_samples = np.vstack([x_homo,  np.zeros(2000), z_homo])

    org_horizon_samples = (R_pitch(pitch).dot(R_roll(roll).dot(horizon_samples))).T

    angle_x = np.degrees(np.arctan2(org_horizon_samples[:, 0], org_horizon_samples[:, 2]))
    angle_y = np.degrees(np.arctan2(org_horizon_samples[:, 1], np.hypot(org_horizon_samples[:, 2], org_horizon_samples[:, 0])))

    height = im.height
    width = im.width

    center = np.array([width, height]) / 2

    x_list = angle_x * (width / 360) + center[0]
    y_list = angle_y * (height / 180) + center[1]

    coordinates = sorted(zip(x_list, y_list))

    return coordinates




def draw_all_vp_and_hl_color(zenith_points, hv_points, im, root):
    cir_r = 30
    hori_coordinates = []
    draw = ImageDraw.Draw(im)
    cmap = plt.cm.hsv(np.linspace(0, 1, len(zenith_points)+1))[:, :3]

    tmp_coor = calculate_venith_points(zenith_points, im)
    # zeni_coordinates = tmp_coor
    for i in range(len(tmp_coor)):
        draw.ellipse([tuple(np.array(tmp_coor[i]) - cir_r), tuple(np.array(tmp_coor[i]) + cir_r)], fill=tuple((cmap[i] * 255).astype(int)))

    tmp_coor = calculate_venith_points(-zenith_points, im)
    for i in range(len(tmp_coor)):
        draw.ellipse([tuple(np.array(tmp_coor[i]) - cir_r), tuple(np.array(tmp_coor[i]) + cir_r)], fill=tuple((cmap[i] * 255).astype(int)))


    for i, point1  in enumerate(zenith_points):

        tmp_coor = calculate_horizon_coordinates(point1, im)
        hori_coordinates.append(tmp_coor)
        draw.line(tmp_coor, fill=tuple((cmap[i] * 255).astype(int)), width=4)

        tmp_coor = calculate_hvps(hv_points[i], im)
        for j in range(len(tmp_coor)):
            draw.ellipse([tuple(np.array(tmp_coor[j]) - cir_r), tuple(np.array(tmp_coor[j]) + cir_r)], fill=tuple((cmap[i] * 255).astype(int)))


    im.save(os.path.join(root, 'all_vp_and_hl_color.jpg'))




def draw_all_vp_and_hl_bi(zenith_points, hv_points, im, root):
    cir_r = 10
    hori_coordinates = []
    draw = ImageDraw.Draw(im)
    cmap = plt.cm.hsv(np.linspace(0, 1, len(zenith_points) + 1))[:, :3]

    for i in range(len(zenith_points)):
        tmp_coor = calculate_zenith_point_coordinate(zenith_points[i], im)
        draw.ellipse([tuple(np.array(tmp_coor) - cir_r), tuple(np.array(tmp_coor) + cir_r)], fill=tuple([255, 0, 0]))

    for i in range(len(zenith_points)):
        tmp_coor = calculate_zenith_point_coordinate(-zenith_points[i], im)
        draw.ellipse([tuple(np.array(tmp_coor) - cir_r), tuple(np.array(tmp_coor) + cir_r)], fill=tuple([0, 0, 0]))


    for i, point1  in enumerate(zenith_points):

        tmp_coor = calculate_horizon_coordinates(point1, im)
        hori_coordinates.append(tmp_coor)
        draw.line(tmp_coor, fill=tuple((cmap[i] * 255).astype(int)), width=4)

        tmp_coor = calculate_hvps(hv_points[i], im)
        for j in range(len(tmp_coor)):
            draw.ellipse([tuple(np.array(tmp_coor[j]) - cir_r), tuple(np.array(tmp_coor[j]) + cir_r)],
                         fill=tuple((cmap[i] * 255).astype(int)))

    im.save(os.path.join(root, 'all_vp_and_hl_bi.jpg'))



def draw_zenith_on_top_color(zenith_points, root):
    cir_r = 2
    im_path = os.path.join(root, 'Pano_render/top/Render_top.jpg')
    im = Image.open(im_path)
    draw = ImageDraw.Draw(im)
    cmap = plt.cm.hsv(np.linspace(0, 1, len(zenith_points) + 1))[:, :3]

    for i in range(len(zenith_points)):
        z_coordinates = zenith_points[i] / -zenith_points[i][1]
        tmp_coor = np.array([z_coordinates[0] * 800 + 800, z_coordinates[2] * 800 + 800])
        draw.ellipse([tuple(np.array(tmp_coor) - cir_r), tuple(np.array(tmp_coor) + cir_r)], fill=tuple((cmap[i] * 255).astype(int)))
    im.save(os.path.join(root, 'zenith_on_top_color.jpg'))


def draw_zenith_on_top_bi(zenith_points, root):
    cir_r = 2
    im_path = os.path.join(root, 'Pano_render/top/Render_top.jpg')
    im = Image.open(im_path)
    draw = ImageDraw.Draw(im)

    for i in range(len(zenith_points)):
        z_coordinates = zenith_points[i] / -zenith_points[i][1]
        tmp_coor = np.array([z_coordinates[0] * 800 + 800, z_coordinates[2] * 800 + 800])
        if zenith_points[i][1] < 0:
            draw.ellipse([tuple(np.array(tmp_coor) - cir_r), tuple(np.array(tmp_coor) + cir_r)], fill=tuple([255, 0, 0]))
        else:
            draw.ellipse([tuple(np.array(tmp_coor) - cir_r), tuple(np.array(tmp_coor) + cir_r)],
                         fill=tuple([0, 0, 0]))
    im.save(os.path.join(root, 'zenith_on_top_bi.jpg'))



def draw_sphere_zenith(zenith_points, hv_points, root):
    b = Bloch()
    b.point_color = ['m', 'k', 'g', 'b', 'w', 'c', 'y','r']
    b.zlabel = ['$z$', '']
    b.point_marker = ['o']
    b.point_size = [30]
    b.frame_width = 1.2
    fig = plt.figure(figsize=(20, 20))
    b.fig = fig

    x = (basis(2, 0) + (1 + 0j) * basis(2, 1)).unit()
    y = (basis(2, 0) + (0 + 1j) * basis(2, 1)).unit()
    z = (basis(2, 0) + (0 + 0j) * basis(2, 1)).unit()
    b.add_states([x, y, z])

    for i in range(len(zenith_points)):
        # Transform xyz to zxy coordinates
        tmp1 = np.array([zenith_points[i][2], zenith_points[i][0], zenith_points[i][1]])
        tmp2 = np.vstack([hv_points[i][:, 2], hv_points[i][:, 0], hv_points[i][:, 1]]).T
        tmp = np.vstack([tmp1, -tmp1, tmp2]).T
        b.add_points(tmp)

    # tmp1 = np.array([zenith_points[-1][2], zenith_points[-1][0], zenith_points[-1][1]])
    # tmp = np.array([tmp1, -tmp1]).T
    # b.add_points(tmp)
    name = os.path.join(root, 'zenith_on_sphere.jpg')
    b.save(name=name)




if __name__ == "__main__":
    # print(R_roll(-np.pi / 2).dot(np.array([0,1,0])))
    # print(100)
    #
    #
    # root = '/home/zhup/Desktop/Pano'
    # im_path = '/home/zhup/Desktop/Pano/Pano_img/DsK88fpAYl9NpNsM2yKMMA.jpg'
    # im = Image.open(im_path)
    #
    # point1 = np.array([-0.03195638, 0.99946882, 0.00639339])
    # point2 = np.array([0., 0., 1.])
    #
    #
    # # pitch = np.arctan(point1[2] / point1[1])
    # # roll = - np.arctan(point1[0] / np.sign(point1[1]) * np.hypot(point1[1], point1[2]))
    #
    #
    # ## print(R_pitch(pitch).dot(R_roll(roll).dot(np.array([0, 1, 0]))))
    #
    #
    # hl = np.array([[0., 774.0801861], [1600., 825.23757385], [np.nan, np.nan]])
    # hl_homo = np.array([np.hstack([hl[0] - 800, 800]), np.hstack([hl[1] - 800, 800])])
    #
    #
    # hvps = np.array([[830.73055179,800.6414392],[1158.09074533, 811.10824692]])
    # img = Image.open('/home/zhup/Desktop/Pano/Pano_hl_z_vp/3_im_hl.jpg')
    # draw = ImageDraw.Draw(img)
    # draw.line([tuple(hvps[0]), tuple(hvps[1])], width=6, fill='yellow')
    # img.save(os.path.join(root, 'render_part3.jpg'))

    b = Bloch()
    b.point_color = ['m', 'k', 'g', 'b', 'w', 'c', 'y', 'r']
    b.zlabel = ['$z$', '']
    b.point_marker = ['o']
    b.point_size = [3]
    b.frame_width = 0.5
    fig = plt.figure(figsize=(20, 20))
    b.fig = fig
    name = os.path.join('zenith_on_sphere.jpg')
    b.save(name=name)

