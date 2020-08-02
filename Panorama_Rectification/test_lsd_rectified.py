from pylsd.lsd import lsd
import numpy as np
import os
import skimage.io
import glob
from skimage.color import rgb2gray
import cv2

## first iteration
# a_threshold = 0.2
# l_threshold = 0.001

# folder = "output1/"
# #save_folder = "facade_output_simple"
# save_folder = "a1"


## second iteration
# a2
a_threshold = 0.3
l_threshold = 0.03
# a2-2
a_threshold = 0.5
l_threshold = 0.04
folder = "a1/"
#save_folder = "facade_output_simple"
save_folder = "a2-2"



imageList = glob.glob(folder + '*0.jpg')
imageList.sort()

for i_name in imageList:
    print(i_name)
    _, img_name = os.path.split(i_name)
    full_name = os.path.join(folder, img_name)

    # img = Image.open(full_name)
    # gray = np.asarray(img.convert('L'))
    # draw = ImageDraw.Draw(img)
    # width = img.width
    # height = img.height
    # img.show()

    img = cv2.imread(full_name, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    width = img.shape[1]
    height = img.shape[0]

    lines = lsd(gray)


    x_list = []
    y_list = []
    min_x = 0
    max_x = width
    min_y = 0
    max_y = height



    for i in range(lines.shape[0]):
        pt1 = (int(lines[i, 0]), int(lines[i, 1]))
        pt2 = (int(lines[i, 2]), int(lines[i, 3]))
        length = np.linalg.norm(lines[i, 0:2] - lines[i, 2:4])
        len_x = np.abs(lines[i, 0] - lines[i, 2])
        len_y = np.abs(lines[i, 1] - lines[i, 3])
        angle_x = np.arcsin(len_x / length) *180/np.pi
        angle_y = np.arcsin(len_y / length) *180/np.pi

        if (angle_x < a_threshold or angle_y < a_threshold) and (length/width > l_threshold and length/height > l_threshold):
            #draw.line((pt1, pt2), fill=(0, 0, 255))
            #cv2.line(img, pt1, pt2, (0, 0, 255))

            if angle_x < a_threshold:
                x_list.append(pt1[0])
            elif angle_y < a_threshold:
                y_list.append(pt1[1])

            # print(angle_x, angle_y, length/width, length/height)

    if len(x_list) > 2:
        min_x = np.min(x_list)
        max_x = np.max(x_list)

    if len(y_list) > 2:
        min_y = np.min(y_list)
        max_y = np.max(y_list)


    # arr = np.array(img)

    arr = img
    save_img_name = os.path.join(save_folder, img_name)

    #skimage.io.imsave(save_img_name, arr[min_y:max_y + 1, min_x:max_x + 1])
    cv2.imwrite(save_img_name, arr[min_y:max_y + 1, min_x:max_x + 1])

