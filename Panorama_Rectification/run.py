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



# todo options
class todo:
    save_results_image = 0
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
    orthorectify = 0 #3 rectified images (the figure number will be plots.orthorectify*100+#plane)

# path(s) to the image (set(s))
imgDir = 'Pano_new/New/images/'
tmp_count = 0

# the following datasets, as well as the ground truth horizon lines in a
# unified format can be obtained from our webpage:
# https://members.loria.fr/GSimon/software/v/

# imgDir{1,end+1} = '/home/gsimon/ownCloud/Matlab/fastvp2/YorkUrbanDB/'
# imgDir{1,end+1} = '/home/gsimon/ownCloud/Matlab/fastvp2/EurasianCitiesBase/'
# imgDir{1,end+1} = '/home/gsimon/Documents/MATLAB/HLW dataset/images/Tests/'

# for each image set...

for i_s in range(1):
    imageList = glob.glob(imgDir + '*.jpg')
    imageList.sort()
    nImages = len(imageList)

    zhupei_save = [[] for i in range(nImages)]

    params = default_params()
    # include the detection of infinite horizontal VPs
    params.include_infinite_hvps = 1
    params.return_z_homo = 0

    hl_error = []
    for i in range(nImages):
        print('%d/%d\n', i+1, nImages)
        im = Image.open(imageList[i])
        im_useless = im.copy()
        im_array = skimage.io.imread(imageList[i])

        width = im.width
        height = im.height
        # fake focal length
        focal = max(width, height) / 2

        # call V
        # V_result_list = V(im, width, height, focal, params)

        [hl, hvps, hvp_groups, z, z_group, ls] = V(im, width, height, focal, params, tmp_count)

        cmap = plt.cm.hsv(np.linspace(0, 1, 4))[:, :3]

        if plots.hvps:
            im_hvps = im
            draw = ImageDraw.Draw(im_hvps)
            for j in range(len(hvp_groups)):
                hg = hvp_groups[j]
                for k in range(len(hg)):
                    pt1 = (ls[hg[k], 0], ls[hg[k], 1])
                    pt2 = (ls[hg[k], 2], ls[hg[k], 3])
                    draw.line((pt1, pt2), fill=tuple((cmap[j] * 255).astype(int)), width=2)
            # im4.show()
            im_hvps.save('tmp/im_hvps.jpg')

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
                draw.line((pt1, pt2), fill=tuple((cmap[2] * 255).astype(int)), width=2)
            im_z.save('tmp/im_z.jpg')

        if plots.hl:
            im_hl = im
            # if plots.hvps and plots.z:
            #     im_hl = im_z.copy()
            # else:
            #     im_hl = im.copy()
            draw = ImageDraw.Draw(im_hl)
            pt1 = (hl[0, 0], hl[0, 1])
            pt2 = (hl[1, 0], hl[1, 1])
            draw.line((pt1, pt2), fill=tuple([0, 255, 255]), width=4)
            im_hl.save('tmp/im_hl.jpg')

        if plots.gthl or plots.benchmark:
            print("Not yet implemented, no xxxhor.mat data and not necessary")


        if todo.calibrate:
            [focal, manh_vps, confident] = calibrate(z, hvps, width, height)
            if plots.manhattan and confident >= 0:
                im_manhattan = im
                # if plots.hl:
                #     im_manhattan = im_hl.copy()
                # else:
                #     im_manhattan = im.copy()
                draw = ImageDraw.Draw(im_manhattan)
                u0 = width / 2
                v0 = height / 2
                if z[1] > v0:
                    posy = 0
                else:
                    posy = height

                if confident == 3:
                    pt1 = (u0, posy)
                    pt2 = (manh_vps[0, 0], manh_vps[0, 1])
                    draw.line((pt1, pt2), fill=tuple([255, 0, 0]), width=4)
                    pt2 = (manh_vps[1, 0], manh_vps[1, 1])
                    draw.line((pt1, pt2), fill=tuple([0, 255, 0]), width=4)
                    pt2 = (manh_vps[2, 0], manh_vps[2, 1])
                    draw.line((pt1, pt2), fill=tuple([0, 0, 255]), width=4)
                elif confident == 2:
                    pt1 = (u0, posy)
                    pt2 = (manh_vps[0, 0], manh_vps[0, 1])
                    draw.line((pt1, pt2), fill=tuple([255, 0, 0]), width=1)
                    pt2 = (manh_vps[1, 0], manh_vps[1, 1])
                    draw.line((pt1, pt2), fill=tuple([0, 255, 0]), width=4)
                    pt2 = (manh_vps[2, 0], manh_vps[2, 1])
                    draw.line((pt1, pt2), fill=tuple([0, 0, 255]), width=4)
                elif confident == 1:
                    pt1 = (u0, posy)
                    pt2 = (manh_vps[0, 0], manh_vps[0, 1])
                    draw.line((pt1, pt2), fill=tuple([255, 0, 0]), width=1)
                    pt2 = (manh_vps[1, 0], manh_vps[1, 1])
                    draw.line((pt1, pt2), fill=tuple([0, 255, 0]), width=1)
                    pt2 = (manh_vps[2, 0], manh_vps[2, 1])
                    draw.line((pt1, pt2), fill=tuple([0, 0, 255]), width=4)

                im_manhattan.save('tmp/im_manhattan.jpg')

        # save the results image

        if plots.hvps and todo.save_results_image:
            img_path = imageList[i]
            [pathstr, img_name] = os.path.split(img_path)
            name = os.path.splitext(img_name)[0]
            name = './intermediate/' + name + 'res.png'
            im.save(name)

        # ortho-rectify all vertical planes

        if todo.ortho_rectify:
            K = np.array([])
            if focal > 0:
                K = np.array([[focal, 0.0, width / 2], [0.0, focal, height / 2], [0.0, 0.0, 1.0]])
            hl_homo = line_hmg_from_two_points(np.array([hl[0, 0], hl[0, 1]]), np.array([hl[1, 0], hl[1, 1]]))


            [imR, maskR, transform, crop_imR] = orthorectify_from_vps_and_lines(im_array, im_useless, hvps, hvp_groups, z, z_group, ls, 4, K, hl_homo, 0)

            # imR = orthorectify_from_vps_and_lines(im_array, im_useless, hvps, hvp_groups, z, z_group, ls, 4, K, hl_homo, 0)


            # if len(imR) > 0:
            #     if len(imR[0]) != 0:
            #         zhupei_save[i].append(transform[0]["H"].tolist())
            # if len(imR) > 1:
            #     if len(imR[1]) != 0:
            #         zhupei_save[i].append(transform[1]["H"].tolist())
            # if len(imR) > 2:
            #     if len(imR[2]) != 0:
            #         zhupei_save[i].append(transform[2]["H"].tolist())


            if todo.save_ortho_images:
                img_path = imageList[i]
                [pathstr, img_name] = os.path.split(img_path)
                name = os.path.splitext(img_name)[0]
                black_percentage = []
                index_list = []

                for j in range(len(imR)):
                    if len(imR[j]) != 0:

                        if not os.path.exists('./output/'):
                            os.makedirs('./output/')
                        out_img_name = './output/' + name + '_R_' + str(j) + '.jpg'
                        skimage.io.imsave(out_img_name, maskR[j])



                # for j in range(len(imR)):
                #     if len(imR[j]) != 0:
                #         black_percentage.append(1 - maskR[j].mean())
                #         index_list.append(j)
                # if len(index_list) > 0:
                #     output_num = 0
                #     if np.array(black_percentage).min() < 0.5 * black_percentage[0] and black_percentage[0] > 0.15:
                #         output_num = index_list[np.argmin(black_percentage)]
                #         out_img_name = './output/manual_selection' + name + '_R_' + str(output_num) + '.jpg'
                #         skimage.io.imsave(out_img_name, imR[output_num])
                #         # break
                #         # mask_img_name = './mask/' + name + '_R_' + str(output_num) + '.jpg'
                #         # skimage.io.imsave(mask_img_name, maskR[output_num])
                #         # crop_img_name = './crop_output/' + name + '_R_' + str(output_num) + '.jpg'
                #         # skimage.io.imsave(crop_img_name, crop_imR[output_num])
                #
                #
                #     out_img_name = './output/' + name + '_R_' + str(0) + '.jpg'
                #     skimage.io.imsave(out_img_name, imR[0])
                #     # break
                #     # mask_img_name = './mask/' + name + '_R_' + str(0) + '.jpg'
                #     # skimage.io.imsave(mask_img_name, maskR[0])
                #     # crop_img_name = './crop_output/' + name + '_R_' + str(0) + '.jpg'
                #     # skimage.io.imsave(crop_img_name, crop_imR[0])






    # with open('simon_zenith.json', 'w') as f:
    #     json.dump(zhupei_save, f)



#print(todo.save_results_image)