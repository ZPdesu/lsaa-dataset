import glob
from default_params import default_params
import skimage.io
import numpy as np
import cv2
from V import V
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
from util.calibrate import calibrate
import os.path
from util.line_hmg_from_two_points import line_hmg_from_two_points
import skimage.io
import time
from util.orthorectify_from_vps_and_lines import orthorectify_from_vps_and_lines
import json


class todo:
    save_results_image = 1
    benchmark = 0
    calibrate = 1
    ortho_rectify = 1
    save_ortho_images = 1

# plot options (0 if not plotted, figure number otherwise)
class plots:
    hvps = 1 #1
    z = 1 #1
    hl = 1 #1
    gthl = 1 #1
    benchmark = 0 #2 display presision curve and AUC for each dataset (the figure number will be plots.benchmark*100+#dataset)
    manhattan = 1 #1
    orthorectify = 1



def simon_rectification(img):

    if type(img) == str:
        im_path = img
        im = Image.open(im_path)
        im_useless = im.copy()
        im_array = skimage.io.imread(im_path)

    elif len(img.shape) == 3:
        im = Image.fromarray(img)
        im_useless = im.copy()
        im_array = img.copy()

    else:
        raise ValueError('input type is wrong')

    width = im.width
    height = im.height


    params = default_params()
    params.include_infinite_hvps = 1
    # fake focal length
    focal = max(width, height) / 2

    # call V
    [hl, hvps, hvp_groups, z, z_group, ls] = V(im, width, height, focal, params)
    if todo.calibrate:
        [focal, manh_vps, confident] = calibrate(z, hvps, width, height)

    if todo.ortho_rectify:
        K = np.array([])
        if focal > 0:
            K = np.array([[focal, 0.0, width / 2], [0.0, focal, height / 2], [0.0, 0.0, 1.0]])
        hl_homo = line_hmg_from_two_points(np.array([hl[0, 0], hl[0, 1]]), np.array([hl[1, 0], hl[1, 1]]))
        [imR, maskR, transform, crop_imR] = orthorectify_from_vps_and_lines(im_array, im_useless, hvps, hvp_groups, z,
                                                                            z_group, ls, 4, K, hl_homo, 0)
        return imR[0], maskR[0], transform[0], crop_imR[0]


# test\
# g = skimage.io.imread("/home/zhup/GitLab/Simon-py/test_images/0801.jpg")
# a,b,c,d = simon_rectification(g)
# skimage.io.imsave("tmp.jpg", a)