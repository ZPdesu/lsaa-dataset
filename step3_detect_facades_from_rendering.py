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
import skimage.io
from options.facade_base_options import FacadeBaseOptions
from util import filter_properties


def detect_facades(opt, facade_list, start_point, end_point, core):
    f_handler = open(os.path.join(opt.log_folder, str(core) + '.log'), 'w')
    std_f = sys.stdout
    sys.stdout = f_handler
    sys.stdout.write('start is Facades number {}, end is Facades number {}\n'.format(start_point,
                                                                                   min(end_point, len(facade_list)) -1))
    sys.stdout.flush()


    with open(opt.facade_detection_result) as f:
        facade_detection_results = json.load(f)


    for facade_name in facade_list[start_point:end_point]:

        #projection_name = facade_detection_results[facade_name]['simplified_name']
        projection_name = facade_detection_results[facade_name]['complete_name']

        projection_name_path = os.path.join(opt.projection_folder, projection_name)

        if os.path.exists(projection_name_path):
            facade_img_path = os.path.join(Facades_folder, facade_name)
            if not os.path.exists(facade_img_path):
                bbox = facade_detection_results[facade_name]['box']
                im = skimage.io.imread(projection_name_path)
                result_im = im[int(bbox[1]):int(bbox[1] + bbox[3]), int(bbox[0]):int(bbox[0] + bbox[2]), :]

                skimage.io.imsave(facade_img_path, result_im)

                print(facade_name + ' has been saved')
            else:
                print(facade_name + ' has already been saved before')

        else:
            print(facade_name + ' does not have corresponding projection image')

        sys.stdout.flush()
    sys.stdout.close()
    sys.stdout = std_f





if __name__=='__main__':


    opt = FacadeBaseOptions().parse()
    Facades_folder = opt.facade_folder
    if not os.path.exists(Facades_folder):
        os.makedirs(Facades_folder)

    # Facade_img_folder = Facades_folder
    # if not os.path.exists(Facade_img_folder):
    #     os.makedirs(Facade_img_folder)

    Facade_log_folder = os.path.join('logs', 'Facades')
    if not os.path.exists(Facade_log_folder):
        os.makedirs(Facade_log_folder)

    # df_properties = pd.read_csv(opt.properties_file)
    df_properties = filter_properties(opt)

    facade_list = df_properties['name'].tolist()

    if opt.first == None:
        opt.first = 0
    if opt.last == None:
        opt.last = len(facade_list)


    facade_list = facade_list[opt.first:opt.last]
    facade_list.sort()


    # facade_list = facade_list[: 6000]
    # opt.cores = 5


    opt.log_folder = Facade_log_folder

    print('start')


    processing_list = []
    step_num = np.int(np.ceil(len(facade_list) / opt.cores))



    for i in range(opt.cores):
        processing_list.append(
            multiprocessing.Process(target=detect_facades,
                                    args=(opt, facade_list, i*step_num, (i+1)*step_num, i)))

    for i in range(opt.cores):
        processing_list[i].start()

    for i in range(opt.cores):
        processing_list[i].join()

    print('finished')