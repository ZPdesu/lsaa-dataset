
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import os.path
import skimage.io
import numpy as np
from default_params import default_params
from V import V

class todo:
    save_results_image = 1
    benchmark = 0
    calibrate = 1
    ortho_rectify = 1
    save_ortho_images = 1

# plot options (0 if not plotted, figure number otherwise)
class plots:
    hvps = 0 #1
    z = 0 #1
    hl = 0 #1
    gthl = 0 #1
    benchmark = 0 #2 display presision curve and AUC for each dataset (the figure number will be plots.benchmark*100+#dataset)
    manhattan = 0 #1
    orthorectify = 0


def simon_rectification(img, num, folder, root, tmp_count):

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

    # fake focal length
    focal = max(width, height) / 2

    # call V
    [hl, hvps, hvp_groups, z, z_group, ls, z_homo, hvp_homo, ls_homo] = V(im, width, height, focal, params, tmp_count)

    cmap = plt.cm.hsv(np.linspace(0, 1, 4))[:, :3]

    if plots.hvps:
        im_hvps = im
        draw = ImageDraw.Draw(im_hvps)
        for j in range(len(hvp_groups)):
            hg = hvp_groups[j]
            for k in range(len(hg)):
                pt1 = (ls[hg[k], 0], ls[hg[k], 1])
                pt2 = (ls[hg[k], 2], ls[hg[k], 3])
                draw.line((pt1, pt2), fill=tuple((cmap[j] * 255).astype(int)), width=5)
        # im4.show()
        hvps_name = os.path.join(folder,  str(num) + '_im_hvps.jpg')
        #im_hvps.save(hvps_name)

    if plots.z:
        im_z = im
        # if plots.hvps:
        #     im_z = im_hvps.copy()
        # else:
        #     im_z = im.copy()
        draw = ImageDraw.Draw(im_z)
        zg = z_group
        for k in range(len(zg)):
            pt1 = (ls[zg[k], 0], ls[zg[k], 1])
            pt2 = (ls[zg[k], 2], ls[zg[k], 3])
            draw.line((pt1, pt2), fill=tuple((cmap[2] * 255).astype(int)), width=5)
        z_name = os.path.join(folder,  str(num) + '_im_z.jpg')
        #im_z.save(z_name)

    if plots.hl:
        im_hl = im
        # if plots.hvps and plots.z:
        #     im_hl = im_z.copy()
        # else:
        #     im_hl = im.copy()
        draw = ImageDraw.Draw(im_hl)
        pt1 = (hl[0, 0], hl[0, 1])
        pt2 = (hl[1, 0], hl[1, 1])
        draw.line((pt1, pt2), fill=tuple([0, 255, 255]), width=7)
        hl_name = os.path.join(folder,  str(num) + '_im_hl.jpg')
        im_hl.save(hl_name)

        # SAVE HORIZON MASK
        # horizon_mask = np.zeros([height, width, 3], dtype=np.uint8)
        # horizon_mask = Image.fromarray(horizon_mask)
        # draw = ImageDraw.Draw(horizon_mask)
        # pt1 = (hl[0, 0], hl[0, 1])
        # pt2 = (hl[1, 0], hl[1, 1])
        # draw.line((pt1, pt2), fill=tuple([255, 255, 255]), width=8)
        # hl_mask = os.path.join(root, 'horizon_mask', str(num) + 'hl_msk.jpg')
        # horizon_mask.save(hl_mask)


    return [hl, hvps, hvp_groups, z, z_group, ls, z_homo, hvp_homo, ls_homo, params]