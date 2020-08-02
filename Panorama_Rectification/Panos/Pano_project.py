import os
import numpy as np
from scipy.ndimage.interpolation import map_coordinates
import skimage.io
from math import acos, cos, degrees, radians, sin
import glob
from Panos.Pano_visualization import R_roll, R_pitch, R_heading
from Panos.Pano_new_pano import calculate_new_pano, save_heading_pitch_json
from Panos.Pano_refine_project import simon_refine
import json

# with open('/home/zhup/Desktop/GSV_Pano_val/Val/projections_views/useful_projections.json') as f:
#     useful_projections = json.load(f)

# with open('/home/zhup/Desktop/GSV_Pano_val/Val/projections_views/random_projections.json') as f:
#     useful_projections = json.load(f)

# with open('/home/zhup/Desktop/GSV_Pano_val/Val/projections_views/prior_projections.json') as f:
#     useful_projections = json.load(f)

# with open('/home/zhup/Desktop/GSV_Pano_val/Val/projections_views/12viewpoints_projections.json') as f:
#     useful_projections = json.load(f)

# with open('/home/zhup/Desktop/GSV_Pano_val/Val/projections_views/4viewpoints_projections.json') as f:
#     useful_projections = json.load(f)

# with open('/home/zhup/Desktop/GSV_Pano_val/Val/projections_views/16-inlier12viewpoints_projections.json') as f:
#     useful_projections = json.load(f)




def stitch_tiles(num, tiles, directory):
    test_img= skimage.io.imread(tiles[0])
    height = test_img.shape[0]
    width = test_img.shape[1]

    stiched_img = np.zeros([height, width * num, 3])
    for i, tile in enumerate(tiles):
        tmp = skimage.io.imread(tile)
        stiched_img[:, i * width: (i + 1) * width] = tmp

    skimage.io.imsave(os.path.join(directory, "hl_stiched.jpg"), stiched_img/255)


def rotation_matrix_Z(angle):
    # https://developers.google.com/streetview/spherical-metadata#euler_overview


    def R_Z(angle):
        return np.array([[cos(angle), -sin(angle), 0],
                         [sin(angle), cos(angle), 0], [0., 0., 1.]])

    def R_X(angle):
        return np.array([[1, 0, 0], [0, cos(angle), -sin(angle)],
                         [0, sin(angle), cos(angle)]])

    def R_Y(angle):
        return np.array([[cos(angle), 0, sin(angle)], [0, 1, 0],
                         [-sin(angle), 0, cos(angle)]])

    R = R_Z(radians(angle))

    return np.linalg.inv(R)


def rotation_matrix_X(angle):
    # https://developers.google.com/streetview/spherical-metadata#euler_overview


    def R_Z(angle):
        return np.array([[cos(angle), -sin(angle), 0],
                         [sin(angle), cos(angle), 0], [0., 0., 1.]])

    def R_X(angle):
        return np.array([[1, 0, 0], [0, cos(angle), -sin(angle)],
                         [0, sin(angle), cos(angle)]])

    def R_Y(angle):
        return np.array([[cos(angle), 0, sin(angle)], [0, 1, 0],
                         [-sin(angle), 0, cos(angle)]])

    R = R_X(radians(angle))
    return np.linalg.inv(R)

def get_the_top():
    height = 20
    width = 20
    mpp = 0.0125
    p0 = np.array([-10., 10., 0.])
    p1 = np.array([10., 10, 0.])
    middle = (p0 + p1) / 2

    up = np.array([0., 0., 1.])
    vec = p1 - p0
    dist = np.linalg.norm(vec)
    vec /= dist
    rot = rotation_matrix_X(-90)

    # if width is not None:
    #     center = (p0 + p1) / 2.
    #     dist = width
    #     p0 = center - 0.5 * vec * dist

    # m - Number of rows in the output image
    # n - Number of columns in the output image
    m = int(np.ceil(height / mpp))
    n = int(np.ceil((width) / mpp))

    # Generate barycentric coordinates for every point on the face-grid
    u, v = np.mgrid[-height / 2:height / 2:m * 1j, -width / 2:width / 2:n * 1j]

    # Generate enu-coordinates for each point on the face-grid
    xy = np.outer(u, up) + np.outer(v, vec) + middle
    xy = rot.dot(xy.T).T

    # Generate a m x n x 2 array of headings and pitches
    heading = (np.degrees(np.arctan2(xy[:, 0], xy[:, 1])))
    pitch = np.degrees(np.arctan2(xy[:, 2], np.hypot(xy[:, 0], xy[:, 1])))
    projected = np.column_stack((heading, pitch)).reshape(m, n, 2)

    root = '/home/zhup/Desktop/Pano'
    img_folder = os.path.join(root, 'Pano_img/')
    output_folder = os.path.join(root, 'Pano_render/')
    imageList = glob.glob(img_folder + '*.jpg')
    imageList.sort()

    panorama_img = imageList[0]
    render_num = 8
    start = int(-render_num / 2) + 1
    img = skimage.io.imread(panorama_img)

    coordinates = projected.transpose(2, 0, 1, )

    # I am getting 'heading, pitch', I want 'pitch, heading' since columns correspond to different headings
    coordinates = np.roll(coordinates, 1, axis=0)

    # Map heading from  -180 ..180 to  0...360
    coordinates[1] += 180.
    coordinates[0] = 90 - coordinates[0]  # 0 ->90 (horizontal), 90->0 (top/up)

    coordinates[0] *= img.shape[0] / 180.
    coordinates[1] *= img.shape[1] / 360.

    sub = np.dstack([
        map_coordinates(img[:, :, 0], coordinates, order=0),
        map_coordinates(img[:, :, 1], coordinates, order=0),
        map_coordinates(img[:, :, 2], coordinates, order=0)
    ])
    sub = sub[::-1, :, :]

    save_path = os.path.join(output_folder, 'top/Render_top.jpg')
    save_img = skimage.io.imsave(save_path, sub)





def project_face(num, degree):
    # enu = self.enu_matrix
    # rot = self.rotation_matrix_Z


    # p0 = (enu @ lla2xyz(lat=edge[0][1], lon=edge[0][0], alt=ground))[:3]
    # p1 = (enu @ lla2xyz(lat=edge[1][1], lon=edge[1][0], alt=ground))[:3]


    height = 20
    width = 20
    mpp = 0.0125
    p0 = np.array([-10., 10., 0.])
    p1 = np.array([10., 10, 0.])
    middle = (p0 + p1) / 2

    up = np.array([0., 0., 1.])
    vec = p1 - p0
    dist = np.linalg.norm(vec)
    vec /= dist
    rot = rotation_matrix_Z(degree * (num))


    # if width is not None:
    #     center = (p0 + p1) / 2.
    #     dist = width
    #     p0 = center - 0.5 * vec * dist

    # m - Number of rows in the output image
    # n - Number of columns in the output image
    m = int(np.ceil(height / mpp))
    n = int(np.ceil((width) / mpp))

    # Generate barycentric coordinates for every point on the face-grid
    u, v = np.mgrid[-height/2:height/2:m * 1j, -width/2:width/2:n * 1j]

    # Generate enu-coordinates for each point on the face-grid
    xy = np.outer(u, up) + np.outer(v, vec) + middle
    xy = rot.dot(xy.T).T

    # Generate a m x n x 2 array of headings and pitches
    heading = (np.degrees(np.arctan2(xy[:, 0], xy[:, 1])))
    pitch = np.degrees(np.arctan2(xy[:, 2], np.hypot(xy[:, 0], xy[:, 1])))
    projected = np.column_stack((heading, pitch)).reshape(m, n, 2)
    return projected




# def project_facade_output(final_hvps_rectified, im, pitch, roll, im_path, root):
#
#     y = 100
#     h_fov = 120  # -60~60
#     v_fov1 = -20
#     v_fov2 = 70
#
#     x1 = np.tan(np.radians(-h_fov / 2)) * y
#     x2 = np.tan(np.radians(h_fov / 2)) * y
#     width = x2 - x1
#
#     z1 = np.tan(np.radians(v_fov1)) * y
#     z2 = np.tan(np.radians(v_fov2)) * y
#     height = z2 - z1
#
#
#     m = int(np.ceil(6656 / 180 * (v_fov2 - v_fov1)))
#     n = int(np.ceil(6656 / 180 * h_fov))
#
#
#     p0 = np.array([x1, y, 0.])
#     p1 = np.array([x2, y, 0.])
#     middle = (p0 + p1) / 2
#
#
#     up = np.array([0., 0., 1.])
#     vec = p1 - p0
#     dist = np.linalg.norm(vec)
#     vec /= dist
#
#
#     # Generate barycentric coordinates for every point on the face-grid
#     u, v = np.mgrid[-z2:-z1:m * 1j, x1:x2:n * 1j]
#
#     # Generate enu-coordinates for each point on the face-grid
#     xy = np.outer(u, up) + np.outer(v, vec) + middle
#
#     new_xy = np.vstack([xy[:, 0], xy[:, 2], xy[:, 1]])
#
#     for i in range(len(final_hvps_rectified)):
#         hvp = final_hvps_rectified[i]
#
#         heading = np.arctan2(hvp[2], hvp[0])
#         headings = [heading, heading + np.pi]
#
#         for j in range(2):
#
#             coordinates = (R_pitch(pitch).dot(R_roll(roll).dot(R_heading(-headings[j])))).dot(new_xy).T
#             coordinates = calculate_new_pano(coordinates, im)
#
#             coordinates = coordinates.reshape(2, m, n)
#
#             img = skimage.io.imread(im_path)
#             sub = np.dstack([
#                 map_coordinates(img[:, :, 0], coordinates, order=0),
#                 map_coordinates(img[:, :, 1], coordinates, order=0),
#                 map_coordinates(img[:, :, 2], coordinates, order=0)
#             ])
#
#             save_path = os.path.join(root, 'Pano_facades', '{}_{}.jpg'.format(heading, j))
#             skimage.io.imsave(save_path, sub)


def calculate_adaptive_coor():
    y = 10
    h_fov = 160  # -60~60
    v_fov1 = -70
    v_fov2 = 70

    h_fov_main = 140
    mpp = 0.0125

    x1 = np.tan(np.radians(-h_fov / 2)) * y
    x2 = np.tan(np.radians(h_fov / 2)) * y
    width = x2 - x1

    z1 = np.tan(np.radians(v_fov1)) * y
    z2 = np.tan(np.radians(v_fov2)) * y
    height = z2 - z1

    x1_main = np.tan(np.radians(-h_fov_main / 2)) * y
    x2_main = np.tan(np.radians(h_fov_main / 2)) * y
    width_main = x2_main - x1_main


    m = int(np.ceil(height / mpp))
    n = int(np.ceil((width) / mpp))
    n_main = int(np.ceil((width_main) / mpp))

    if m % 2 == 1:
        m = m + 1
    if n % 2 == 1:
        n = n + 1
    if n_main == 1:
        n_main = n_main + 1


    # m = int(np.ceil(6656 / 180 * (v_fov2 - v_fov1)))
    # n = int(np.ceil(6656 / 180 * h_fov))

    p0 = np.array([x1, y, 0.])
    p1 = np.array([x2, y, 0.])
    middle = (p0 + p1) / 2

    up = np.array([0., 0., 1.])
    vec = p1 - p0
    dist = np.linalg.norm(vec)
    vec /= dist

    # Generate barycentric coordinates for every point on the face-grid
    u, v = np.mgrid[-z2:-z1:m * 1j, x1:x2:n * 1j]

    # Generate enu-coordinates for each point on the face-grid
    xy = np.outer(u, up) + np.outer(v, vec) + middle

    new_xy = np.vstack([xy[:, 0], xy[:, 2], xy[:, 1]])

    return new_xy, m, n, n_main



def calculate_no_adaptive_coor(h_fov, v_fov1, v_fov2, mpp=0.0125):
    y = 10

    x1 = np.tan(np.radians(-h_fov / 2)) * y
    x2 = np.tan(np.radians(h_fov / 2)) * y
    width = x2 - x1

    z1 = np.tan(np.radians(v_fov1)) * y
    z2 = np.tan(np.radians(v_fov2)) * y
    height = z2 - z1


    m = int(np.ceil(height / mpp))
    n = int(np.ceil((width) / mpp))

    if m % 2 == 1:
        m = m + 1
    if n % 2 == 1:
        n = n + 1


    # m = int(np.ceil(6656 / 180 * (v_fov2 - v_fov1)))
    # n = int(np.ceil(6656 / 180 * (h_fov2 - h_fov1)))

    p0 = np.array([x1, y, 0.])
    p1 = np.array([x2, y, 0.])
    middle = (p0 + p1) / 2

    up = np.array([0., 0., 1.])
    vec = p1 - p0
    dist = np.linalg.norm(vec)
    vec /= dist

    # Generate barycentric coordinates for every point on the face-grid
    u, v = np.mgrid[-z2:-z1:m * 1j, x1:x2:n * 1j]

    # Generate enu-coordinates for each point on the face-grid
    xy = np.outer(u, up) + np.outer(v, vec) + middle

    new_xy = np.vstack([xy[:, 0], xy[:, 2], xy[:, 1]])
    focal = y / mpp

    return new_xy, m, n, focal






def project_facade_for_refine(final_hvps_rectified, im, pitch, roll, im_path, root, tmp_folder, rendering_img_base, tmp_count):

    no_adaptive = True
    if no_adaptive:
        [new_xy, m, n, focal] = calculate_no_adaptive_coor(h_fov=140, v_fov1=-70, v_fov2=70)
    else:
        [new_xy, m, n, n_main] = calculate_adaptive_coor()
        adat_1 = int((n - n_main) / 2)
        adat_2 = int(n - (n - n_main) / 2)


    for i in range(len(final_hvps_rectified)):
        hvp = final_hvps_rectified[i]

        heading = np.arctan2(hvp[2], hvp[0])

        #tmp
        #heading = heading + 0.0139
        headings = [heading, heading + np.pi]

        for j in range(2):

            headings_tmp = headings[j]
            coordinates = (R_pitch(pitch).dot(R_roll(roll).dot(R_heading(-headings_tmp)))).dot(new_xy).T
            coordinates = calculate_new_pano(coordinates, im)

            coordinates = coordinates.reshape(2, m, n)

            img = skimage.io.imread(im_path)
            sub = np.dstack([
                map_coordinates(img[:, :, 0], coordinates, order=0),
                map_coordinates(img[:, :, 1], coordinates, order=0),
                map_coordinates(img[:, :, 2], coordinates, order=0)
            ])

            # If we save the refine images


            if no_adaptive:
                # save_path_main = os.path.join(root, 'Pano_refine', 'VP_{}_{}.jpg'.format(i, j))
                # skimage.io.imsave(save_path_main, sub)

                # sub_im_path = os.path.join(tmp_folder, 'tmp.jpg')
                # skimage.io.imsave(sub_im_path, sub)

                refine_radians = simon_refine(sub.copy(), focal=focal, is_main_vp=i, tmp_count=tmp_count)
                # os.remove(sub_im_path)





                if refine_radians != None:

                    save_path_main = rendering_img_base + '_VP_{}_{}.jpg'.format(i, j)


                    headings_tmp += refine_radians

                    #[tmp_xy, m_tmp, n_tmp, _] = calculate_no_adaptive_coor(h_fov=160, v_fov1=-45, v_fov2=80, mpp=0.0125*2)

                    #  relax requirements
                    # [tmp_xy, m_tmp, n_tmp, _] = calculate_no_adaptive_coor(h_fov=146, v_fov1=-40, v_fov2=75,
                    #                                                        mpp=0.0125 * 2)

                    [tmp_xy, m_tmp, n_tmp, _] = calculate_no_adaptive_coor(h_fov=154, v_fov1=-44, v_fov2=83,
                                                                           mpp=0.0125 * 2)
                    super_R = R_pitch(pitch).dot(R_roll(roll).dot(R_heading(-headings_tmp)))
                    tmp_coordinates = super_R.dot(tmp_xy).T


                    ########### add a special part recording
                    # ttttt_heading_pitch = save_heading_pitch_json(tmp_coordinates, im, m_tmp, n_tmp)
                    # ttttt_heading_pitch_json_path = rendering_img_base + '_VP_{}_{}_heading_pitch.npy'.format(i, j)
                    # # with open(ttttt_heading_pitch_json_path, 'w') as f:
                    # #     json.dump(ttttt_heading_pitch.tolist(), f)
                    # np.save(ttttt_heading_pitch_json_path, ttttt_heading_pitch)
                    #########################################


                    tmp_coordinates = calculate_new_pano(tmp_coordinates, im)

                    tmp_coordinates = tmp_coordinates.reshape(2, m_tmp, n_tmp)

                    #img = skimage.io.imread(im_path)
                    tmp_sub = np.dstack([
                        map_coordinates(img[:, :, 0], tmp_coordinates, order=0),
                        map_coordinates(img[:, :, 1], tmp_coordinates, order=0),
                        map_coordinates(img[:, :, 2], tmp_coordinates, order=0)
                    ])

                    skimage.io.imsave(save_path_main, tmp_sub)
                    json_path = rendering_img_base + '_VP_{}_{}.json'.format(i, j)

                    with open(json_path, 'w') as f:
                        json.dump(super_R.tolist(), f)

                else:
                    pass
                    # print('no vp')


            else:
                assert no_adaptive == True
                # not implement
                sub_main =  sub[:, adat_1:adat_2, :]
                sub_left = sub[:, 0:int(n/2), :]
                sub_right = sub[:, int(n / 2):n, :]

                # save_path_main = os.path.join(root, 'Pano_refine', 'VP_{}_{}_main.jpg'.format(i, j))
                # save_path_left = os.path.join(root, 'Pano_refine', 'VP_{}_{}_left.jpg'.format(i, j))
                # save_path_right = os.path.join(root, 'Pano_refine', 'VP_{}_{}_right.jpg'.format(i, j))
                # skimage.io.imsave(save_path_main, sub_main)
                # skimage.io.imsave(save_path_left, sub_left)
                # skimage.io.imsave(save_path_right, sub_right)






def render_imgs(panorama_img, tmp_dir, save_directly):

    #render_num = 16
    render_num = 4

    start = int(-render_num/2) + 1
    end = render_num + start
    degree = 360 / render_num
    img = panorama_img.copy()
    output_tiles = []

    for i in range(start, end):
        # interleaved -> planar representation of the coordinates
        coordinates = project_face(i, degree)
        coordinates = coordinates.transpose(2, 0, 1,)

        # I am getting 'heading, pitch', I want 'pitch, heading' since columns correspond to different headings
        coordinates = np.roll(coordinates, 1, axis=0)

        # Map heading from  -180 ..180 to  0...360
        coordinates[1] += 180.
        coordinates[0] = 90 - coordinates[0]  # 0 ->90 (horizontal), 90->0 (top/up)

        coordinates[0] *= img.shape[0] / 180.
        coordinates[1] *= img.shape[1] / 360.

        sub = np.dstack([
            map_coordinates(img[:, :, 0], coordinates, order=0),
            map_coordinates(img[:, :, 1], coordinates, order=0),
            map_coordinates(img[:, :, 2], coordinates, order=0)
        ])
        sub = sub[::-1, :, :]
        output_tiles.append(sub)
        if not save_directly:
            save_path = os.path.join(tmp_dir, 'Render_' + str(i - start) + '.jpg')
            skimage.io.imsave(save_path, sub)

    # Get the top images
    #get_the_top()
    return output_tiles

if __name__ == "__main__":
    # render_imgs()
    # project_facade_output()
    print(100)
    calculate_adaptive_coor()
