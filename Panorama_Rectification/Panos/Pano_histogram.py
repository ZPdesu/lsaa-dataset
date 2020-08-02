
import numpy as np
import matplotlib.pyplot as plt
import os
from Panos.Pano_zp_hvp import calculate_consensus_vps
import mnf_modes


def calculate_histogram(hvps_consensus_rectified, root, plot_redundant):
    hvp_cum = np.vstack(hvps_consensus_rectified)
    hvp_cum_pos = np.array([z_i if z_i[0] >= 0 else -z_i for z_i in hvp_cum])

    hvp_degrees = np.degrees(np.arctan2(hvp_cum_pos[:, 0], hvp_cum_pos[:, 2]))
    # hvp_periodic = np.where(hvp_degrees > 0, hvp_degrees, hvp_degrees+180)
    hvp_periodic = hvp_degrees

    hvp_periodic_2x = np.hstack([hvp_periodic, hvp_periodic + 180])
    hvp_periodic_3x = np.hstack([hvp_periodic - 180, hvp_periodic, hvp_periodic + 180])

    his_edge = 1

    if plot_redundant:
        plt.figure()
        plt.hist(hvp_periodic, np.arange(181))
        plt.title('histogram of angles (0-180)')
        plt.xlabel('degree')
        plt.ylabel('number')
        plt.savefig(os.path.join(root, 'histogram.jpg'))

        plt.figure()
        plt.hist(hvp_periodic_2x, np.arange(361))
        plt.title('histogram of angles (0-360)')
        plt.xlabel('degree')
        plt.ylabel('number')
        plt.savefig(os.path.join(root, 'histogram_2x.jpg'))

        plt.figure()
        plt.hist(hvp_periodic_3x, np.arange(-181, 362))
        plt.title('histogram of angles (-180-360)')
        plt.xlabel('degree')
        plt.ylabel('number')
        plt.savefig(os.path.join(root, 'histogram_3x.jpg'))


    if his_edge == 1:
        hvp_histogram = np.histogram(hvp_periodic_3x, np.arange(-180, 361))
    elif his_edge == 2:
        hvp_histogram = np.histogram(hvp_periodic_3x, np.arange(-180, 361, 2))
    elif his_edge == 3:
        hvp_histogram = np.histogram(hvp_periodic_3x, np.arange(-180, 361, 3))
    elif his_edge == 'auto':
        hvp_histogram = np.histogram(hvp_periodic_3x, 'auto')


    [N, edges] = hvp_histogram


    max_modes = np.zeros([2 * len(N)])
    H = np.zeros([len(N)])

    his_epsilon = 1
    Nout = mnf_modes.mnf(np.double(N), len(N), his_epsilon, max_modes, H)
    max_modes = max_modes[:Nout * 2]
    max_modes = max_modes.reshape(2, Nout).T
    H = H[:Nout]
    H = H.reshape(Nout)

    if len(max_modes) == 0:
        max_modes = np.array([])
        H = 0
    else:
        I = np.argsort(-H)
        H.sort()
        H = H[::-1]
        max_modes = max_modes[I, :]


    horgroups = []
    # scores = []
    # horvps_homo = []


    three_x_list = []
    three_y_list = []

    one_x_list = []
    one_y_list = []

    two_x_list = []
    two_y_list = []


    for i in range(max_modes.shape[0]):
        Ni = np.zeros([N.shape[0]])
        a = max_modes[i, 0]
        b = max_modes[i, 1]
        Ni[int(a) - 1:int(b)] = N[int(a) - 1:int(b)]
        m = np.max(Ni)
        j = np.argmax(Ni)

        three_x_list.append(j-180)
        three_y_list.append(m)


        # p_i = (edges[j] + edges[j+1]) / 2
        # vpId = np.argmin(np.abs(p - p_i))
        # horvps_homo.append(inter_homo[:,vpId])
        # scores.append(m)


        if 0 <= j - 180 /his_edge < 180/ his_edge:

            #print('range{}-{}'.format(j - 180/his_edge, j - 180/his_edge + 1))
            one_x_list.append(j-180)
            one_y_list.append(m)

            two_x_list.append(j-180)
            two_y_list.append(m)
            two_x_list.append(j - 180 + 180)
            two_y_list.append(m)


        ############## Wrong shouldn't be a and b (fixed)

            edgesId = np.intersect1d(np.where(hvp_periodic >= edges[j]), np.where(hvp_periodic < edges[j+1]))
            horgroups.append(edgesId)

    final_hvps_rectified = []
    for i in range(len(horgroups)):
        tmp = calculate_consensus_vps(hvp_cum_pos[horgroups[i]], 'svd')
        # at most two vanishing points will be chosen
        if i < 2:
            final_hvps_rectified.append(tmp)

    if plot_redundant:
        # plot peaks on -180-360
        plt.figure()
        plt.hist(hvp_periodic_3x, np.arange(-181, 362))
        plt.title('histogram of angles (-180-360)')
        plt.scatter(three_x_list, three_y_list, s=20, c='r')
        plt.xlabel('degree')
        plt.ylabel('number')
        plt.savefig(os.path.join(root, 'peaks_on_histogram_3x.jpg'))

        # plot peaks on 0-180
        plt.figure()
        plt.hist(hvp_periodic, np.arange(181))
        plt.title('histogram of angles (0-180)')
        plt.scatter(one_x_list, one_y_list, s=20, c='r')
        plt.xlabel('degree')
        plt.ylabel('number')
        plt.savefig(os.path.join(root, 'peaks_on_histogram.jpg'))

        # plot peaks on 0-180
        plt.figure()
        plt.hist(hvp_periodic_2x, np.arange(361))
        plt.title('histogram of angles (0-360)')
        plt.scatter(two_x_list, two_y_list, s=20, c='r')
        plt.xlabel('degree')
        plt.ylabel('number')
        plt.savefig(os.path.join(root, 'peaks_on_histogram_2x.jpg'))

    return final_hvps_rectified