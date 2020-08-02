# %%-------------------------------------------------------------------------
# %
# % >V<
# %
# % Copyright 2018 Gilles Simon <gsimon@loria.fr> Université de Lorraine
# %
# % Version 1.0 - September 5, 2018
# %
# % >V< is an implementation of the vanishing point detector described in the
# % paper:
# %
# %   "A-Contrario Horizon-First Vanishing Point Detection Using Second-Order
# %   Grouping Laws" by Gilles Simon, Antoine Fond, and Marie-Odile Berger,
# %   European Conference on Computer Vision, Sep 2018, Munich, Germany."
# %
# % available on our website, along with a few example results:
# % https://members.loria.fr/GSimon/software/v/
# %
# % If you use the code, please cite the paper.
# %
# % This program is free software: you can redistribute it and/or modify
# % it under the terms of the GNU Affero General Public License as
# % published by the Free Software Foundation, either version 3 of the
# % License, or (at your option) any later version.
# %
# % This program is distributed in the hope that it will be useful,
# % but WITHOUT ANY WARRANTY; without even the implied warranty of
# % MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# % GNU Affero General Public License for more details.
# %
# % You should have received a copy of the GNU Affero General Public License
# % along with this program. If not, see <http://www.gnu.org/licenses/>.
# %%-------------------------------------------------------------------------

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
import os

# plot options (0 if not plotted, figure number otherwise)
class plots:
    lsd = 0 # 10
    ls_filter = 0 #11
    zl = 0 #12
    hl_modes = 0 #12
    hl_samples = 0 #12

def V(im, width, height, focal, params, tmp_count):

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

    # import scipy.io as sio
    # mat_lsd = sio.loadmat('lsd.mat')
    # lsd_output = mat_lsd['lsd']


    # plot the results
    if plots.lsd:
        im1 = im.copy()
        cmap = plt.cm.hsv(np.linspace(0, 1, lsd_output.shape[0]))[:, :3]
        draw = ImageDraw.Draw(im1)
        for j in range(lsd_output.shape[0]):
            pt1 = (lsd_output[j, 0], lsd_output[j, 1])
            pt2 = (lsd_output[j, 2], lsd_output[j, 3])
            draw.line((pt1, pt2), fill=tuple((cmap[j]*255).astype(int)), width=2)
        #im1.show()
        im1.save('tmp/tmp1.jpg')

    # LS filtering

    thres_aligned = max(width, height) / 128.
    length_t = np.sqrt(width + height) / 1.71
    ls = ls_filter(thres_aligned, length_t, lsd_output)
    ls_homo = normalize.normalize(ls, width, height, focal)


    # plot the results
    if plots.ls_filter:
        im2 = im.copy()
        cmap = plt.cm.hsv(np.linspace(0, 1, ls.shape[0]))[:, :3]
        draw = ImageDraw.Draw(im2)
        for j in range(ls.shape[0]):
            pt1 = (ls[j, 0], ls[j, 1])
            pt2 = (ls[j, 2], ls[j, 3])
            draw.line((pt1, pt2), fill=tuple((cmap[j] * 255).astype(int)), width=4)
        #im2.show()
        im2.save('tmp/tmp2.jpg')


    # ZL and zenith rough predictions

    # prediction of the zenith line
    dist_max = width / 8
    zl = zl_predict(lsd_output, dist_max, u0, v0, width, height, params)
    zl_homo = []
    z_homo_cand = []
    z_group_cand = []
    for i in range(len(zl)):
        zl_homo.append(normalize.normalize(np.array([[zl[i], 0, u0, v0]]), width, height, focal))
        [tmp_z_homo_cand, tmp_z_group_cand] = z_predict(ls_homo, zl_homo[i], params, 0)
        z_homo_cand.append(tmp_z_homo_cand)
        z_group_cand.append(tmp_z_group_cand)

    # plot the results
    if plots.zl:
        im3 = im.copy()
        cmap = plt.cm.hsv(np.linspace(0, 1, len(z_homo_cand)))[:, :3]
        draw = ImageDraw.Draw(im3)
        for j in range(len(z_homo_cand)):
            # tmp = np.array([-0.0578, -0.9965, 0.0597])
            # z = unnormalize.unnormalize(tmp, width, height, focal, 0)
            z = unnormalize.unnormalize(z_homo_cand[j], width, height, focal, 0)
            pt1 = (width / 2, height / 2)
            pt2 = (z[0], z[1])
            draw.line((pt1, pt2), fill=tuple((cmap[j] * 255).astype(int)), width=4)
        # im3.show()
        im3.save('tmp/tmp3.jpg')


    # choose the best zenith candidate based on the relevance of the predicted HLs

    best_z_cand = 0
    best_z_score = 0
    for i in range(len(zl_homo)):

        # HL prediction
        [modes_homo, _, _, _, _] = hl_predict(lsd_output, z_homo_cand[i], u0, v0, width, height, focal, params)

        # HL scoring (for performance optimization, each zenith candidate is assessed based only on the meaningful
        # HLs (no sampling is performed at that step))

        [_, results] = hl_score(modes_homo, ls_homo, z_homo_cand[i], params)

        # keep the zenith candidate with highest score
        if results["score"] > best_z_score:
            best_z_cand = i
            best_z_score = results["score"]

    # zenith refinement (based on Zhang et al. method)
    [z_homo_cand[best_z_cand], z_group_cand[best_z_cand]] = z_predict(ls_homo, zl_homo[best_z_cand], params, 1)


    # HL prediction
    [modes_homo, modes_offset, modes_left, modes_right, H] = hl_predict(lsd_output, z_homo_cand[best_z_cand], u0, v0, width, height, focal, params)


    # HL sampling
    [samp_homo, samp_left, samp_right] = hl_sample(z_homo_cand[best_z_cand], modes_homo, modes_offset, modes_left, modes_right, H, u0, v0, width, height, focal, params)

    # plot the results
    if plots.hl_samples:
        if plots.hl_samples:
            im4 = im3.copy()
        else:
            im4 = im.copy()
        cmap = plt.cm.hsv(np.linspace(0, 1, len(zl_homo)))[:, :3]
        draw = ImageDraw.Draw(im4)
        for j in range(samp_homo.shape[1]):

            pt1 = (0, samp_left[j])
            pt2 = (width, samp_right[j])
            draw.line((pt1, pt2), fill=tuple((cmap[i] * 255).astype(int)), width=1)
        # im4.show()
        im4.save('tmp/tmp4.jpg')


    if plots.hl_modes:
        if plots.hl_samples and plots.hl_samples:
            im5 = im4.copy()
        else:
            im5 = im.copy()
        draw = ImageDraw.Draw(im5)
        for j in range(modes_homo.shape[1]):
            if H[j] > 0:
                pt1 = (0, modes_left[j])
                pt2 = (width, modes_right[j])
                draw.line((pt1, pt2), fill=tuple([0, 0, 255]), width=4)
        # im5.show()
        im5.save('tmp/tmp5.jpg')


    # HL scoring

    # import scipy.io as sio
    # tmp_samp_homo = sio.loadmat('samp_homo.mat')
    # samp_homo = tmp_samp_homo['samp_homo']


    [hl_homo, results] = hl_score(samp_homo, ls_homo, z_homo_cand[best_z_cand], params)

    # import scipy.io as sio
    # tmp_hl_homo = sio.loadmat('hl_homo.mat')
    # hl_homo = tmp_hl_homo['hl_homo']
    # hl_homo = np.squeeze(hl_homo)

    hl = unnormalize.unnormalize(hl_homo, width, height, focal, 1)
    hvps = unnormalize.unnormalize(results["hvp_homo"], width, height, focal, 0)
    hvp_groups = results["hvp_groups"]
    z = unnormalize.unnormalize(z_homo_cand[best_z_cand], width, height, focal, 0)
    z_group = z_group_cand[best_z_cand]

    if params.return_z_homo:
        return hl, hvps, hvp_groups, z, z_group, ls, z_homo_cand[best_z_cand], results["hvp_homo"], ls_homo

    #print(0)
    return hl, hvps, hvp_groups, z, z_group, ls




