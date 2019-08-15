import pandas as pd
import argparse
import os
import subprocess
import streetview as sv
import sys
from tqdm import tqdm
import json
import multiprocessing
import numpy as np
from project_panoramas import calculate_new_pano, calculate_no_adaptive_coor,R_heading, R_pitch, R_roll
import skimage.io
from scipy.ndimage.interpolation import map_coordinates
from PIL import Image
from options.facade_base_options import FacadeBaseOptions
from util import filter_properties

def project_panoramas(opt, projection_list, start_point, end_point, core):
    f_handler = open(os.path.join(opt.log_folder, str(core) + '.log'), 'w')
    std_f = sys.stdout
    sys.stdout = f_handler
    sys.stdout.write('start is Projection number {}, end is Projection number {}\n'.format(start_point,
                                                                                   min(end_point, len(projection_list)) -1))
    sys.stdout.flush()

    [tmp_xy1, m_tmp, n_tmp, _] = calculate_no_adaptive_coor(h_fov=160, v_fov1=-45, v_fov2=80, mpp=0.0125*2)
    with open(opt.panorama_rectification) as f:
        rectification_results = json.load(f)


    for projection_name in projection_list[start_point:end_point]:

        tmp_xy = tmp_xy1.copy()

        if projection_name in rectification_results:
            panorama_img_name = os.path.join(opt.pano_folder, rectification_results[projection_name]['panoID'] + '.jpg')

            projection_img_path = os.path.join(Projection_folder, projection_name)
            if os.path.exists(panorama_img_name):
                if not os.path.exists(projection_img_path):
                    super_R = R_pitch(rectification_results[projection_name]['pitch']).dot(
                        R_roll(rectification_results[projection_name]['roll']).dot(
                            R_heading(rectification_results[projection_name]['heading'])))

                    tmp_coordinates = super_R.dot(tmp_xy).T

                    tmp_coordinates = calculate_new_pano(tmp_coordinates, Image.open(panorama_img_name))

                    tmp_coordinates = tmp_coordinates.reshape(2, m_tmp, n_tmp)

                    img = skimage.io.imread(panorama_img_name)
                    tmp_sub = np.dstack([
                        map_coordinates(img[:, :, 0], tmp_coordinates, order=0),
                        map_coordinates(img[:, :, 1], tmp_coordinates, order=0),
                        map_coordinates(img[:, :, 2], tmp_coordinates, order=0)
                    ])

                    skimage.io.imsave(projection_img_path, tmp_sub)
                    print(projection_name + ' has been saved')
                else:
                    print(projection_name + ' has already been saved before')
            else:
                print(projection_name + ' does not have corresponding panorama image')
        else:
            print(projection_name + ' rectification parameters are not saved before')
        sys.stdout.flush()


    sys.stdout.close()
    sys.stdout = std_f





if __name__=='__main__':


    opt = FacadeBaseOptions().parse()

    Projection_folder = opt.projection_folder
    if not os.path.exists(Projection_folder):
        os.makedirs(Projection_folder)

    # Projection_img_folder = Projection_folder
    # if not os.path.exists(Projection_img_folder):
    #     os.makedirs(Projection_img_folder)

    Projection_log_folder = os.path.join('logs', 'Projection')
    if not os.path.exists(Projection_log_folder):
        os.makedirs(Projection_log_folder)

    # df_properties = pd.read_csv(opt.properties_file)
    df_properties = filter_properties(opt)

    facade_list = df_properties['name'].tolist()


    if opt.first == None:
        opt.first = 0
    if opt.last == None:
        opt.last = len(facade_list)


    facade_list = facade_list[opt.first:opt.last]
    facade_list.sort()


    projection_list = []

    with open(opt.facade_detection_result) as f:
        facade_detection_results = json.load(f)


    for i in facade_list:
        projection_name = facade_detection_results[i]['complete_name']
        if projection_name not in projection_list:
            projection_list.append(projection_name)


    # facade_list = facade_list[: 6000]
    # opt.cores = 5


    opt.log_folder = Projection_log_folder

    print('start')


    processing_list = []
    step_num = np.int(np.ceil(len(projection_list) / opt.cores))



    for i in range(opt.cores):
        processing_list.append(
            multiprocessing.Process(target=project_panoramas,
                                    args=(opt, projection_list, i*step_num, (i+1)*step_num, i)))

    for i in range(opt.cores):
        processing_list[i].start()

    for i in range(opt.cores):
        processing_list[i].join()

    print('finished')