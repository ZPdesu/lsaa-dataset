import numpy as np
import skimage.transform
import skimage.io

def orthorectify(im, H, line, s):
    max_stretch = 16
    step = np.round(im.shape[1] / 64)
    width = im.shape[1]
    height = im.shape[0]
    umin = 1e10
    umax = -1e10
    vmin = 1e10
    vmax = -1e10
    imR = np.array([])
    imref = np.array([])

    for i in np.arange(1, width + 1, step):
        for j in np.arange(1, height + 1, step):
            if np.dot(line, np.array([i, j, 1])) * np.power(-1, s + 1) > 0:
                pix = np.array([[i, i + 1], [j, j + 1], [1., 1.]])
                Tpix = H.dot(pix)
                Tpix[:, 0] = Tpix[:, 0] / Tpix[2, 0]
                Tpix[:, 1] = Tpix[:, 1] / Tpix[2, 1]
                u = Tpix[0, 0]
                v = Tpix[1, 0]
                u2 = Tpix[0, 1]
                v2 = Tpix[1, 1]
                if np.abs(u2 - u) < max_stretch and np.abs(v2 - v) < max_stretch:
                    if u < umin:
                        umin = u
                    elif u > umax:
                        umax = u
                    if v < vmin:
                        vmin = v
                    elif v > vmax:
                        vmax = v

    heightT = np.floor(vmax - vmin)
    widthT = np.floor(umax - umin)

    final_transform = np.array([])
    if heightT > 0 and widthT > 0:
        tmp_trans = np.array([[1, 0, umin], [0, 1, vmin], [0, 0, 1]])
        imref = np.array([[heightT, widthT], [umin, umax], [vmin, vmax]])

        final_transform = np.linalg.inv(H).dot(tmp_trans)

        #final_transform = np.linalg.inv(H)
        imR = skimage.transform.warp(im, final_transform, output_shape=[heightT, widthT])

        #skimage.io.imsave('tmp_out.jpg', imR)

    return imR, imref, final_transform

