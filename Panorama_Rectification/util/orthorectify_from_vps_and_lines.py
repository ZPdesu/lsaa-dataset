import numpy as np
from util.line_hmg_from_two_points import line_hmg_from_two_points
from util.line_size import line_size
from PIL import Image, ImageDraw
from util.line_angle2 import line_angle2
from util.line_hmg_intersect import line_hmg_intersect
from util.poly2mask import poly2mask
import skimage.io
import skimage.transform
from util.orthorectify import orthorectify

def orthorectify_from_vps_and_lines(im_array, im, hvps, hvp_groups, zenith, z_group, lines, n_lines_min, K, horizon_line, PLOT):

    n_hvp = hvps.shape[0]
    width = im_array.shape[1]
    height = im_array.shape[0]
    n_imR = -1
    imR = [[] for i in range(n_hvp)]
    maskR = [[] for i in range(n_hvp)]
    # new item
    crop_imR = [[] for i in range(n_hvp)]

    transform = [{} for i in range(n_hvp)]

    vp_association = -1 * np.ones(len(lines))
    vp_association[z_group] = 0
    for i in range(len(hvp_groups)):
        vp_association[hvp_groups[i]] = i + 1
    if len(K) != 0:
        Ki = np.linalg.inv(K)
        pp = np.array([K[0, 2], K[1, 2]])
        pp_zen_line = line_hmg_from_two_points(pp, zenith)
        vp_zen = np.array([zenith[0], zenith[1], 1])
        y = Ki.dot(vp_zen)
        y = y / np.linalg.norm(y)
        if horizon_line.dot(vp_zen) < 0:
            y = -y

    idmax = np.array([-1.0, -1.0])
    idmin = np.array([-1.0, -1.0])

    for i in range(n_hvp):
        #if PLOT:
        im_bundle_line = im.copy()

        hvp = np.array([hvps[i, 0], hvps[i, 1]])
        vp_zen_line = line_hmg_from_two_points(hvp, zenith)
        if vp_zen_line[0] < 0:
            vp_zen_line = -vp_zen_line

        zen_line_normal = vp_zen_line[0:2]
        zen_line_normal = zen_line_normal / np.linalg.norm(zen_line_normal)
        proj_min = np.array([1.0, 1.0])
        proj_max = np.array([-1.0, -1.0])
        n_lines_zen = np.array([0.0, 0.0])

        centroid = np.zeros([lines.shape[0], 2])
        lines_dir = np.zeros([lines.shape[0], 2])


        for j in range(lines.shape[0]):
            centroid[j, 0] = (lines[j, 0] + lines[j, 2]) / 2
            centroid[j, 1] = (lines[j, 1] + lines[j, 3]) / 2
            lines_dir[j, 0] = lines[j, 0] - lines[j, 2]
            lines_dir[j, 1] = lines[j, 1] - lines[j, 3]
            lines_dir[j] = lines_dir[j] / np.linalg.norm(lines_dir[j])
            bundle_dir = centroid[j, :] - zenith
            bundle_dir = bundle_dir / np.linalg.norm(bundle_dir)
            proj = np.dot(zen_line_normal, bundle_dir)

            if vp_association[j] == 0:
                for s in range(2):
                    if np.dot(zen_line_normal, bundle_dir) * np.power(-1, s + 1) > 0:
                        n_lines_zen[s] = n_lines_zen[s] + 1
                        if proj > proj_max[s]:
                            proj_max[s] = proj
                            idmax[s] = j
                        if proj < proj_min[s]:
                            proj_min[s] = proj
                            idmin[s] = j
        for s in range(2):
            if n_lines_zen[s] >= n_lines_min:
                centroid_min = centroid[int(idmin[s]), 0:2]
                centroid_max = centroid[int(idmax[s]), 0:2]
                dist_min = line_size(np.array([hvp[0], hvp[1], centroid_min[0], centroid_min[1]]))
                dist_max = line_size(np.array([hvp[0], hvp[1], centroid_max[0], centroid_max[1]]))
                if dist_min < dist_max:
                    middle = np.zeros(2)
                    middle[0] = (hvp[0] + centroid_max[0]) / 2
                    middle[1] = (hvp[1] + centroid_max[1]) / 2
                    dist_middle = line_size(np.hstack([hvp, middle]))
                    if dist_min < dist_middle and dist_middle < dist_max:
                        centroid_min = middle.copy()
                else:
                    middle = np.zeros(2)
                    middle[0] = (hvp[0] + centroid_min[0]) / 2
                    middle[1] = (hvp[1] + centroid_min[1]) / 2
                    dist_middle = line_size(np.hstack([hvp, middle]))
                    if dist_max < dist_middle and dist_middle < dist_min:
                        centroid_max = middle.copy()

                lzmin = line_hmg_from_two_points(zenith, centroid_min)
                lzmax = line_hmg_from_two_points(zenith, centroid_max)
                lzmin_V = np.zeros(2)
                lzmin_V[0] = centroid_min[0] - zenith[0]
                lzmin_V[1] = centroid_min[1] - zenith[1]
                lzmin_V = lzmin_V / np.linalg.norm(lzmin_V)

                lzmax_V = np.zeros(2)
                lzmax_V[0] = centroid_max[0] - zenith[0]
                lzmax_V[1] = centroid_max[1] - zenith[1]
                lzmax_V = lzmax_V / np.linalg.norm(lzmax_V)
                hvp_amin = 2 * np.pi
                hvp_amax = -2 * np.pi
                n_lines_hvp = 0
                idmax2 = 0
                for j in range(lines.shape[0]):
                    if vp_association[j] == i + 1:
                        if np.dot(vp_zen_line, np.array([lines[j, 0], lines[j, 1], 1.0])) * np.power(-1, s + 1) > 0 and np.dot(
                                vp_zen_line, np.array([lines[j, 2], lines[j, 3], 1.0])) * np.power(-1, s + 1) > 0 and np.abs(
                            np.dot(lines_dir[j], lzmin_V)) < np.cos(np.pi / 8) and np.abs(np.dot(lines_dir[j], lzmax_V)) < np.cos(np.pi / 8):

                            n_lines_hvp = n_lines_hvp + 1
                            boundle_line = np.array([hvps[i, 0], hvps[i, 1], centroid[j, 0], centroid[j, 1]])

                            if PLOT:
                                draw = ImageDraw.Draw(im_bundle_line)
                                pt1 = (boundle_line[0], boundle_line[1])
                                pt2 = (boundle_line[2], boundle_line[3])
                                draw.line((pt1, pt2), fill=tuple([0, 255, 0]), width=2)

                                pt1 = (lines[j, 0], lines[j, 1])
                                pt2 = (lines[j, 2], lines[j, 3])
                                draw.line((pt1, pt2), fill=tuple([0, 0, 255]), width=2)

                            a = -line_angle2(boundle_line)
                            if a < hvp_amin:
                                hvp_amin = a
                                idmin2 = j
                            else:
                                if a > hvp_amax:
                                    hvp_amax = a
                                    idmax2 = j

                if n_lines_hvp >= n_lines_min:
                    n_imR = n_imR + 1
                    if n_imR > len(transform) - 1:
                        transform.append({})
                        imR.append([])
                        maskR.append([])
                        crop_imR.append([])
                    transform[n_imR]["K"] = K
                    if len(K) > 0:
                        vp = np.array([hvps[i, 0], hvps[i, 1], 1.0])
                        x = Ki.dot(vp)
                        x = x / np.linalg.norm(x)
                        if (np.dot(pp_zen_line, vp) < 0 and np.dot(horizon_line, vp_zen) < 0) or (np.dot(pp_zen_line, vp) > 0 and np.dot(horizon_line, vp_zen) > 0):
                            x = -x
                        if (np.dot(pp_zen_line, vp) < 0 and np.dot(horizon_line, vp_zen) < 0 and s == 0) or (np.dot(pp_zen_line, vp) > 0 and np.dot(horizon_line, vp_zen) < 0 and s ==1) or (np.dot(pp_zen_line, vp) > 0 and np.dot(horizon_line, vp_zen) > 0 and s ==0) or (np.dot(pp_zen_line, vp) < 0 and np.dot(horizon_line, vp_zen) > 0 and s ==1):
                            x = -x
                        z = np.cross(x, y)
                        transform[n_imR]["R"] = np.array([x, y, z]).T
                        transform[n_imR]["H"] = K.dot(np.linalg.inv(transform[n_imR]["R"])).dot(Ki)
                    else:
                        lhmin = line_hmg_from_two_points(hvps[i], centroid[idmin2])
                        lhmax = line_hmg_from_two_points(hvps[i], centroid[idmax2])
                        c = np.zeros([4,2])
                        c[0] = line_hmg_intersect(lhmin, lzmin)
                        c[1] = line_hmg_intersect(lhmax, lzmin)
                        c[2] = line_hmg_intersect(lhmax, lzmax)
                        c[3] = line_hmg_intersect(lhmin, lzmax)
                        sc = np.sort(c[:, 0])
                        id = np.argsort(c[:, 0])
                        idul = id[1 - int(c[id[0], 1] < c[id[1], 1])]
                        idll = id[1 - int(c[id[0], 1] > c[id[1], 1])]
                        up = ((idll + 1) == np.mod(idul + 1, 4) + 1)
                        idc = idul

                        corners = np.zeros([2, 4])
                        for j in range(4):
                            corners[:, j] = c[idc]
                            if up:
                                idc = np.mod(idc + 1, 4)
                            else:
                                idc = idc - 1
                                if idc == -1:
                                    idc = 3
                        if PLOT:
                            draw = ImageDraw.Draw(im_bundle_line)
                            pt1 = (zenith[0], zenith[1])
                            pt2 = (centroid_min[0], centroid_min[1])
                            draw.line((pt1, pt2), fill=tuple([255, 0, 0]), width=2)

                            pt1 = (zenith[0], zenith[1])
                            pt2 = (centroid_max[0], centroid_max[1])
                            draw.line((pt1, pt2), fill=tuple([255, 0, 0]), width=2)

                            pt1 = (hvps[i, 0], hvps[i, 1])
                            pt2 = (centroid[idmin2, 0], centroid[idmin2, 1])
                            draw.line((pt1, pt2), fill=tuple([255, 0, 0]), width=2)

                            pt1 = (hvps[i, 0], hvps[i, 1])
                            pt2 = (centroid[idmax2, 0], centroid[idmax2, 1])
                            draw.line((pt1, pt2), fill=tuple([255, 0, 0]), width=2)

                            # pt1 = (200, 200)
                            # pt2 = (800, 1400)
                            # draw.line((pt1, pt2), fill=tuple([0, 0, 0]), width=10)

                            lhmin = line_hmg_from_two_points(hvps[i], centroid[idmin2])
                            lhmax = line_hmg_from_two_points(hvps[i], centroid[idmax2])

                            draw.polygon(xy=[tuple(corners[:, 0]), tuple(corners[:, 1]), tuple(corners[:, 2]), tuple(corners[:, 3]), tuple(corners[:, 0])], outline=tuple([0, 0, 0]))
                            name = './tmp/im_bundle_line_' + str(i) + '.jpg'
                            im_bundle_line.save(name)
                        BW = poly2mask(corners[1], corners[0], [height, width])
                        # skimage.io.imsave('tmp/polygon.jpg', BW)
                        M = np.sum(corners, 1) / 4
                        A = np.sum(BW)
                        AR = (np.sqrt(np.sum(np.power((corners[:, 0] - corners[:, 1]), 2))) + np.sqrt(np.sum(np.power((corners[:, 2] - corners[:, 3]), 2)))) / (np.sqrt(np.sum(np.power((corners[:, 1] - corners[:, 2]), 2))) + np.sqrt(np.sum(np.power((corners[:, 3] - corners[:, 0]), 2))))
                        w = np.sqrt(A / AR)
                        h = AR * w
                        pointsR = np.array([[M[0] - w/2, M[0] - w/2, M[0] + w/2, M[0] + w/2], [M[1] - h/2, M[1] + h/2, M[1] + h/2, M[1] - h/2]]).T
                        points = corners[:, 0:4].T.copy()
                        tform = skimage.transform.estimate_transform('projective', points, pointsR)
                        transform[n_imR]['H'] = tform.params
                        transform[n_imR]['R'] = np.array([])

                    [imR[n_imR], transform[n_imR]['imref'], final_transform] = orthorectify(im_array, transform[n_imR]['H'], vp_zen_line, s)
                    transform[n_imR]['final_transform'] = final_transform
                    if len(transform[n_imR]['imref']) != 0:
                        imwhite = np.ones([im_array.shape[0], im_array.shape[1]])
                        maskR[n_imR] = skimage.transform.warp(imwhite, final_transform, output_shape=transform[n_imR]['imref'][0])

                    if len(K) > 0:
                        crop_imR[n_imR] = imR[n_imR]
                    else:
                        if len(final_transform) != 0:
                            inv_final_transform = np.linalg.inv(final_transform)
                            tmp1 = inv_final_transform.dot(np.array([points[0, 0], points[0, 1], 1.0]))
                            tmp1 = tmp1 / tmp1[2]

                            tmp2 = inv_final_transform.dot(np.array([points[2, 0], points[2, 1], 1.0]))
                            tmp2 = tmp2 / tmp2[2]

                            crop_imR[n_imR] = imR[n_imR][int(tmp1[1]): int(tmp2[1]), int(tmp1[0]): int(tmp2[0]), :]

        # if PLOT:
        #     name = './tmp/im_bundle_line_' + str(i) + '.jpg'
        #     im_bundle_line.save(name)


    return imR, maskR, transform, crop_imR
    #return imR










