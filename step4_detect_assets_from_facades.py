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
from options.asset_base_options import AssetBaseOptions
from util import filter_properties




def detect_assets(opt, asset_list, start_point, end_point, core):

    f_handler = open(os.path.join(opt.log_folder, str(core) + '.log'), 'w')
    std_f = sys.stdout
    sys.stdout = f_handler
    sys.stdout.write('start is {} number {}, end is {} number {}\n'.format(opt.asset_type, start_point, opt.asset_type,
                                                                                   min(end_point, len(asset_list)) -1))
    sys.stdout.flush()



    with open(opt.asset_detection_result) as f:
        asset_detection_result = json.load(f)


    for asset_name in asset_list[start_point:end_point]:


        facade_name = asset_detection_result[asset_name]['facade_name']

        facade_name_path = os.path.join(opt.facade_folder, facade_name)

        if os.path.exists(facade_name_path):

            asset_img_path = os.path.join(Asset_folder, asset_name)

            if not os.path.exists(asset_img_path):

                bbox = asset_detection_result[asset_name]['box']
                im = skimage.io.imread(facade_name_path)
                result_im = im[int(bbox[1]):int(bbox[1] + bbox[3]), int(bbox[0]):int(bbox[0] + bbox[2]), :]

                skimage.io.imsave(asset_img_path, result_im)

                print(asset_name + ' has been saved')
            else:
                print(asset_name + ' has already been saved before')

        else:
            print(asset_name + ' does not have corresponding facade image')

        sys.stdout.flush()
    sys.stdout.close()
    sys.stdout = std_f





if __name__=='__main__':


    opt = AssetBaseOptions().parse()


    Asset_folder = opt.asset_folder

    if not os.path.exists(Asset_folder):
        os.makedirs(Asset_folder)

    # Asset_img_folder = Asset_folder
    # if not os.path.exists(Asset_img_folder):
    #     os.makedirs(Asset_img_folder)

    Asset_log_folder = os.path.join('logs', os.path.basename(opt.asset_folder))
    if not os.path.exists(Asset_log_folder):
        os.makedirs(Asset_log_folder)


    # df_properties = pd.read_csv(opt.properties_file)
    df_properties = filter_properties(opt)

    asset_list = df_properties['name'].tolist()

    asset_list.sort()


    opt.log_folder = Asset_log_folder

    print('start')



    processing_list = []
    step_num = np.int(np.ceil(len(asset_list) / opt.cores))



    for i in range(opt.cores):
        processing_list.append(
            multiprocessing.Process(target=detect_assets,
                                    args=(opt, asset_list, i*step_num, (i+1)*step_num, i)))

    for i in range(opt.cores):
        processing_list[i].start()

    for i in range(opt.cores):
        processing_list[i].join()

    print('finished')