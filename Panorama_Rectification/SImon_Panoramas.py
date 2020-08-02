import glob
from default_params import default_params
import skimage.io
import numpy as np
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import os.path
import skimage.io
import time
import json

import skimage.io
from Panos.Pano_rectification import simon_rectification
from Panos.Pano_project import project_face, stitch_tiles, render_imgs
import matplotlib.pyplot as plt

from Panos.Pano_visualization import R_heading, draw_all_vp_and_hl_color, draw_all_vp_and_hl_bi, \
    draw_zenith_on_top_color, draw_zenith_on_top_bi, draw_sphere_zenith, R_roll, R_pitch
from Panos.Pano_zp_hvp import calculate_consensus_zp
from Panos.Pano_consensus_vis import draw_consensus_zp_hvps, draw_consensus_rectified_sphere, \
    draw_center_hvps_rectified_sphere, draw_center_hvps_on_panorams
import Pano_hvp
from Panos.Pano_histogram import calculate_histogram
from Panos.Pano_project import project_facade_for_refine


plot_redundant = False


# test\
# g = skimage.io.imread("/home/zhup/GitLab/Simon-py/test_images/0801.jpg")
# a,b,c,d = simon_rectification(g)
# skimage.io.imsave("tmp.jpg", a)



#render_imgs()


root = '/home/zhup/Desktop/Panoramas'
inter_Dir = os.path.join(root, 'Pano_hl_z_vp/')
imgDir = os.path.join(root, 'Pano_render/')
Pano_img_Dir = os.path.join(root,'Pano_img/')



Pano_List = glob.glob(Pano_img_Dir + '*.jpg')
Pano_List.sort()
render_num = 8
start = int(-render_num / 2) + 1
end = render_num + start
degree = 360 / render_num
im_path = Pano_List[0]
panorama_img = skimage.io.imread(im_path)
coordinates_list = []
im = Image.open(im_path)

# for i in range(start, end):
#     coordinates = project_face(i, degree)
#     coordinates = coordinates.transpose(2, 0, 1, )
#
#     # I am getting 'heading, pitch', I want 'pitch, heading' since columns correspond to different headings
#     coordinates = np.roll(coordinates, 1, axis=0)
#
#     # Map heading from  -180 ..180 to  0...360
#     coordinates[1] += 180.
#     coordinates[0] = coordinates[0] + 90  # 0 ->90 (horizontal), 90->0 (top/up)
#
#     coordinates[0] *= panorama_img.shape[0] / 180.
#     coordinates[1] *= panorama_img.shape[1] / 360.
#
#     coordinates_list.append(coordinates)



imageList = glob.glob(imgDir + '*.jpg')
imageList.sort()

hl = []
hvps = []
hvp_groups = []
z = []
z_group = []
ls = []
z_homo = []
hvp_homo = []
ls_homo = []
for i in range(len(imageList)):
    [tmp_hl, tmp_hvps, tmp_hvp_groups, tmp_z, tmp_z_group, tmp_ls, tmp_z_homo, tmp_hvp_homo, tmp_ls_homo, params] = simon_rectification(imageList[i], i, inter_Dir, root)
    hl.append(tmp_hl)
    hvps.append(tmp_hvps)
    hvp_groups.append(tmp_hvp_groups)
    z.append(tmp_z)
    z_group.append(tmp_z_group)
    ls.append(tmp_ls)
    z_homo.append(tmp_z_homo)
    hvp_homo.append(tmp_hvp_homo)
    ls_homo.append(tmp_ls_homo)

# print('get all the zenith points')



#z_homo_pos = [z_i if z_i[1] > 0 else -z_i for z_i in z_homo]
#z_homo_neg = [z_i if z_i[1] < 0 else -z_i for z_i in z_homo]



####################### Get all the zenith points from all the (8) viewpoints

zenith_points = np.array([R_heading(np.pi / 4 * (i - 3)).dot(zenith) for i, zenith in enumerate(z_homo)])
points2 = np.array([R_heading(np.pi / 4 * (i - 3)).dot(np.array([0., 0., 1.])) for i in range(len(z_homo))])
hv_points = [(R_heading(np.pi / 4 * (i - 3)).dot(hv_p.T)).T for i, hv_p in enumerate(hvp_homo)]


if plot_redundant:
    draw_all_vp_and_hl_color(zenith_points, hv_points, im.copy(), root)
    draw_all_vp_and_hl_bi(zenith_points, hv_points, im.copy(), root)
    draw_zenith_on_top_color(zenith_points, root)
    draw_zenith_on_top_bi(zenith_points, root)
    draw_sphere_zenith(zenith_points, hv_points, root)



####################### Calculate the consensus zenith point

[zenith_consensus, best_zenith] = calculate_consensus_zp(zenith_points, method='svd')

# Transform the zenith points back to original homogeneous coordinates
zenith_consensus_org = np.array([R_heading(-np.pi / 4 * (i - 3)).dot(zenith) for i, zenith in enumerate(zenith_consensus)])


result_list = []
for i in range(len(zenith_consensus_org)):

    #result = Pano_hvp.hvp_from_zenith(ls_homo[i], zenith_consensus_org[i], params)

    result = Pano_hvp.get_all_hvps(ls_homo[i], zenith_consensus_org[i], params)
    result_list.append(result)

hvps_consensus_org = []
for i in range(len(result_list)):
    # hvps_consensus_org.append(result_list[i]['hvp_homo'])
    hvps_consensus_org.append(result_list[i])

hvps_consensus_uni = [(R_heading(np.pi / 4 * (i - 3)).dot(hv_p.T)).T for i, hv_p in enumerate(hvps_consensus_org)]

if plot_redundant:
    draw_consensus_zp_hvps(best_zenith, hvps_consensus_uni, im.copy(), root)


####################### Calculate pitch and roll
pitch = np.arctan(best_zenith[2] / best_zenith[1])
roll = - np.arctan(best_zenith[0] / np.sign(best_zenith[1]) * np.hypot(best_zenith[1], best_zenith[2]))


hvps_consensus_rectified = [R_roll(-roll).dot(R_pitch(-pitch).dot(vp.T)).T for vp in hvps_consensus_uni]

if plot_redundant:
    draw_consensus_rectified_sphere(hvps_consensus_rectified, root)



###################### Calculate horizontal VP histogram

final_hvps_rectified = calculate_histogram(hvps_consensus_rectified, root, plot_redundant)


# Test whether the main vanishing point is near 90 degrees to the second vanishing point

if len(final_hvps_rectified) == 2:
    hvp1 = final_hvps_rectified[0]
    hvp2 = final_hvps_rectified[1]
    if np.abs(hvp1.dot(hvp2)) > np.sin(np.radians(10)):
        final_hvps_rectified = [final_hvps_rectified[0]]

if plot_redundant:
    draw_center_hvps_rectified_sphere(np.array(final_hvps_rectified), root)
    draw_center_hvps_on_panorams(best_zenith, np.array(final_hvps_rectified), im.copy(), pitch, roll, root)



# Draw rectified panorama

# from Panos.Pano_new_pano import create_new_panorama, draw_new_panorama
# if plot_redundant:
#     new_pano_path = create_new_panorama(im_path, pitch, roll, root)
#     draw_new_panorama(new_pano_path, np.array(final_hvps_rectified), root)



###################### Rendering images from panoramas

project_facade_for_refine(np.array(final_hvps_rectified), im.copy(), pitch, roll, im_path, root)

print(100)

