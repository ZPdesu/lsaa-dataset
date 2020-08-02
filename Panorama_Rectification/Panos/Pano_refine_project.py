from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import os.path
import skimage.io
import numpy as np
from default_params import default_params
from util.filter_verhor_lines import filter_verhor_lines

import cv2
from pylsd.lsd import lsd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from PIL import Image, ImageDraw
from ls_filter import ls_filter
from util import normalize, unnormalize
from zl_predict import zl_predict
from z_predict import z_predict
from hl_predict import hl_predict
from hl_score import hl_score
from hl_sample import hl_sample
from vp_predict import vp_predict

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
    gthl = 0 #1
    benchmark = 0 #2 display presision curve and AUC for each dataset (the figure number will be plots.benchmark*100+#dataset)
    manhattan = 0 #1
    orthorectify = 0



def Refine(im, width, height, focal, params, tmp_count):

    # fix random seed
    np.random.seed(1)

    # principal point is assumed at image center
    u0 = width / 2
    v0 = height /2

    # line segment (LS) extraction based on the LSD algorithm
    # Reference https://github.com/primetang/pylsd

    gray = np.asarray(im.convert('L'))
    lines = lsd(gray, tmp_count)
    lsd_output = lines[:, :4]


    # LS filtering

    thres_aligned = max(width, height) / 128.
    length_t = np.sqrt(width + height) / 1.71
    ls = ls_filter(thres_aligned, length_t, lsd_output)
    ls_homo = normalize.normalize(ls, width, height, focal)


    # zenith refinement (based on Zhang et al. method)
    z_homo = np.array([0., 1., 0.])


    ############################
    ############################
    candidates = {}
    nhvps = []
    helpfulIds = filter_verhor_lines(ls_homo, z_homo, params)
    initialIds = np.arange(len(helpfulIds))
    if z_homo[1] > 0:
        candidates["horizon_homo"] = z_homo
    else:
        candidates["horizon_homo"] = -z_homo


    [candidates["sc"], candidates["hvp_homo"], hvp_groups] = vp_predict(ls_homo[:, helpfulIds], initialIds,
                                                                        candidates["horizon_homo"], params)
    candidates["hvp_groups"] = [helpfulIds[hvp_groups[k]] for k in range(len(hvp_groups))]
    #nhvps.append(candidates["hvp_homo"].shape[0])

    # output results

    results = candidates

    # verigy_vp = True
    # if verigy_vp:
    #     cmap = plt.cm.hsv(np.linspace(0, 1, 4))[:, :3]
    #     im_hvps = im.copy()
    #     draw = ImageDraw.Draw(im_hvps)
    #     for j in range(len(results["hvp_groups"])):
    #         hg = results["hvp_groups"][j]
    #         for k in range(len(hg)):
    #             pt1 = (ls[hg[k], 0], ls[hg[k], 1])
    #             pt2 = (ls[hg[k], 2], ls[hg[k], 3])
    #             draw.line((pt1, pt2), fill=tuple((cmap[j] * 255).astype(int)), width=2)
    #     # im4.show()
    #     im_hvps.save('refine_verify.jpg')

    return results



def simon_refine(img, focal, is_main_vp, tmp_count):

    if type(img) == str:
        im_path = img
        im = Image.open(im_path)
        im_useless = im.copy()
        im_array = skimage.io.imread(im_path)

    elif len(img.shape) == 3:
        im = Image.fromarray(img)
        im_useless = im.copy()
        im_array = img

    else:
        raise ValueError('input type is wrong')

    width = im.width
    height = im.height


    params = default_params()
    params.include_infinite_hvps = 1
    params.return_z_homo = 1


    results = Refine(im, width, height, focal, params, tmp_count)

    if is_main_vp == 0:
        consider_times = 3
    else:
        consider_times = 3

    hvps = results['hvp_homo'][:consider_times]

    refined_vp = np.array([])

    if len(hvps) > 0:

        # smaller value means more similar
        values = np.abs(hvps.dot(np.array([0, 0, 1])))
        vp_num = np.argmin(values)

        if np.min(values) < np.sin(np.radians(5)):
            refined_vp = hvps[vp_num]

    if len(refined_vp) > 0:
        refine_radians = np.arctan2(refined_vp[2], refined_vp[0])
        if refine_radians > np.pi / 2:
            refine_radians = refine_radians - np.pi
        elif refine_radians < -np.pi / 2:
            refine_radians = refine_radians + np.pi

    else:
        refine_radians = None
        #refine_radians = 0

    return refine_radians


if __name__ == "__main__":
    img = '/home/zhup/Desktop/Pano/Pano_refine/1.5463177385553142_0.jpg'
    #img = '/home/zhup/Desktop/Pano/Pano_refine/1.5463177385553142_1.jpg'


    img = '/home/zhup/Desktop/Pano/Pano_refine/VP_0_0_left.jpg'

    mpp = 0.0125
    focal = 10 / mpp
    num = 0
    folder = None
    root =None
    refined_vp = simon_refine(img, num, focal)
    if len(refined_vp) > 0:
        refine_radians = np.arctan2(refined_vp[2], refined_vp[0])
        print(refine_radians)

    else:
        print('no need this projection')






    print(100)

