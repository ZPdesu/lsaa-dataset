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
import multiprocessing
import argparse
import subprocess
import sys

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
save_directly = True

def job(t_start, t_end, thread_num, tmp_count):
    tmp_count = int(tmp_count)
    f_handler = open(os.path.join(logs_folder, str(thread_num) + '.log'), 'w')
    std_f = sys.stdout
    sys.stdout = f_handler
    print('start is Panorama{}, end is Panorama{}\n'.format(t_start + 1, t_end))

    ThreadImageList = TaskimageList[t_start:t_end]
    for im_path in ThreadImageList:


        im = Image.open(im_path)
        rendering_img_base = os.path.join(rendering_output_folder, os.path.splitext(os.path.basename(im_path))[0])

        thread = str(thread_num) + '/'
        tmp_folder = os.path.join(root, Country_city, 'tmp', task, thread)

        if not save_directly:
            if not os.path.exists(tmp_folder):
                os.makedirs(tmp_folder)
            removelist = glob.glob(tmp_folder + '*.jpg')
            for i in removelist:
                os.remove(i)


        render_num = 8
        start_angle = int(-render_num / 2) + 1
        end_angle = render_num + start_angle
        degree = 360 / render_num
        panorama_img = skimage.io.imread(im_path)
        coordinates_list = []

        tilelist = render_imgs(panorama_img, tmp_folder, save_directly)
        if not save_directly:
            tilelist = glob.glob(tmp_folder + '*.jpg')
            tilelist.sort()

        hl = []
        hvps = []
        hvp_groups = []
        z = []
        z_group = []
        ls = []
        z_homo = []
        hvp_homo = []
        ls_homo = []

        for i in range(len(tilelist)):
            [tmp_hl, tmp_hvps, tmp_hvp_groups, tmp_z, tmp_z_group, tmp_ls, tmp_z_homo, tmp_hvp_homo, tmp_ls_homo, params] = simon_rectification(tilelist[i], i, inter_Dir, root, tmp_count)
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

        if not save_directly:
            removelist = glob.glob(tmp_folder + '*.jpg')
            for i in removelist:
                os.remove(i)

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

        project_facade_for_refine(np.array(final_hvps_rectified), im.copy(), pitch, roll, im_path, root, tmp_folder, rendering_img_base, tmp_count)

    sys.stdout.write('finished')
    sys.stdout.close()
    sys.stdout = std_f

if __name__=='__main__':


    p = argparse.ArgumentParser()
    p.add_argument("--country_city",
                   help="Country and city of Panoramas")
    p.add_argument("--start", help="start buildings",
                   type=int)
    p.add_argument("--end", help="End buildings",
                   type=int)
    p.add_argument("--step_num", help="Step_num",
                   type=int)
    p.add_argument("--count_num", help="tmp_count",
                   type=int)


    args = p.parse_args()

    args.country_city = 'New'
    args.start = 0
    args.end = 1
    args.step_num = 1
    args.count_num = 2




    root = 'Pano_new'
    Country_city = args.country_city




    task = str(args.start) + '_' + str(args.end)
    Img_folder = os.path.join(root, Country_city, 'images/')
    inter_Dir = os.path.join(root, 'Pano_hl_z_vp/')
    imageList = glob.glob(Img_folder + '*.jpg')
    imageList.sort()
    TaskimageList = imageList[args.start: args.end]

    logs_folder = os.path.join('logs', args.country_city, str(args.start) + '_' + str(args.end))
    if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)

    rendering_output_folder = os.path.join(root, Country_city, 'Rendering')
    if not os.path.exists(rendering_output_folder):
        os.makedirs(rendering_output_folder)

    print('start')

    processing_list = []
    step_num = args.step_num
    # cores = multiprocessing.cpu_count()
    cores = int((args.end - args.start) / step_num)

    for i in range(cores):
        processing_list.append(
            multiprocessing.Process(target=job, args=(i * step_num + args.start, (i + 1) * step_num + args.start, i, args.count_num*50+i)))

    for i in range(cores):
        processing_list[i].start()

    for i in range(cores):
        processing_list[i].join()

    print('finished')