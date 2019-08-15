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
from options.facade_base_options import FacadeBaseOptions
from util import filter_properties


def download_panoramas(opt, pano_list, start_point, end_point, core):
    f_handler = open(os.path.join(opt.log_folder, str(core) + '.log'), 'w')
    std_f = sys.stdout
    sys.stdout = f_handler
    sys.stdout.write('start is PanoID number {}, end is PanoID number {}\n'.format(start_point,
                                                                                   min(end_point, len(pano_list)) -1))
    sys.stdout.flush()

    for panoid in pano_list[start_point:end_point]:

        if not os.path.exists(os.path.join(Pano_img_folder, panoid + '.jpg')):

            node_json_name = os.path.join(Pano_node_folder, panoid + '_node.json')
            if subprocess.call(['node', 'streetview/panodata.js', panoid, node_json_name]) == 0:
                with open(node_json_name) as data_file:
                    data = json.load(data_file)
                    width_num = int(int(data['Data']['image_width']) / 512)
                    height_num = int(int(data['Data']['image_height']) / 512)

                if width_num >= 26 and height_num >= 13:
                    if opt.use_tqdm:
                        progress = tqdm(desc='downloading {}'.format(panoid))

                        def progress_callback(i, total=None):
                            if total:
                                progress.total = total
                            progress.update(i - progress.n)
                    else:
                        progress_callback = None

                    pano_img_name = os.path.join(Pano_img_folder, panoid + '.jpg')
                    sv.download_panorama(panoid, Pano_folder, width_num, height_num, pano_img_name, cb=progress_callback)
                    if opt.use_tqdm:
                        progress.close()
                    print(panoid + ' has been saved')

            else:
                print(panoid + ' has been deleted by Google StreetView')
        else:
            print(panoid + ' has already been saved before')
        sys.stdout.flush()

    sys.stdout.close()
    sys.stdout = std_f




if __name__=='__main__':



    opt = FacadeBaseOptions().parse()

    Pano_folder = opt.pano_folder
    if not os.path.exists(Pano_folder):
        os.makedirs(Pano_folder)

    Pano_node_folder = os.path.join('nodes', 'Panoramas')
    if not os.path.exists(Pano_node_folder):
        os.makedirs(Pano_node_folder)


    Pano_img_folder = Pano_folder
    # if not os.path.exists(Pano_img_folder):
    #     os.makedirs(Pano_img_folder)

    Pano_log_folder = os.path.join('logs', 'Panoramas')
    if not os.path.exists(Pano_log_folder):
        os.makedirs(Pano_log_folder)

    df_properties = filter_properties(opt)

    # df_properties = pd.read_csv(opt.properties_file)
    #
    # if opt.country != None:
    #     df_properties = df_properties[(df_properties.country == opt.country)]
    #
    # if opt.city != None:
    #     df_properties = df_properties[(df_properties.city == opt.city)]
    #
    # if opt.min_height != None:
    #     df_properties = df_properties[(df_properties.height >= opt.min_height)]
    #
    # if opt.min_width != None:
    #     df_properties = df_properties[(df_properties.width >= opt.min_width)]
    #
    # if opt.max_height != None:
    #     df_properties = df_properties[(df_properties.height <= opt.max_height)]
    #
    # if opt.max_width != None:
    #     df_properties = df_properties[(df_properties.width <= opt.max_width)]
    #
    # if opt.max_occlusion != None:
    #     df_properties = df_properties[(df_properties.total_occlusion <= opt.max_occlusion)]



    facade_list = df_properties['name'].tolist()

    if opt.first == None:
        opt.first = 0
    if opt.last == None:
        opt.last = len(facade_list)

    # facade_list = facade_list[opt.first:opt.last]
    # facade_list.sort()






    pano_list = df_properties['panoID'].iloc[opt.first:opt.last].unique().tolist()
    # pano_list.sort()


    # pano_list = pano_list[:28]
    # opt.cores = 5


    opt.log_folder = Pano_log_folder

    print('start')

    processing_list = []
    step_num = np.int(np.ceil(len(pano_list)/ opt.cores))

    for i in range(opt.cores):
        processing_list.append(
            multiprocessing.Process(target=download_panoramas,
                                    args=(opt, pano_list, i*step_num, (i+1)*step_num, i)))

    for i in range(opt.cores):
        processing_list[i].start()

    for i in range(opt.cores):
        processing_list[i].join()

    print('finished')

