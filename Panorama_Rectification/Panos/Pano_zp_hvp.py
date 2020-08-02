import numpy as np
from scipy import linalg


# zenith_points= np.array([[-0.01586766, -0.9997433, -0.01617225],
#  [-0.00602033, -0.99995133, -0.00781664],
#  [-0.02363735, -0.99971256, -0.00400828],
#  [ 0.0230112, 0.99972355, 0.00482845],
#  [ 0.02890784, 0.99947202, 0.01483323],
#  [ 0.02950107, 0.99942838, 0.01651059],
#  [ 0.02785873, 0.99939872, 0.02064201],
#  [-0.0197328, -0.99950401, -0.02454273]])
#
# zenith_points_pos = np.array([z_i if z_i[1] > 0 else -z_i for z_i in zenith_points])



def calculate_mean_zp(zenith_points_pos):
    mean_zenith = zenith_points_pos.mean(axis=0)
    similarity = zenith_points_pos.dot(mean_zenith)
    # k = 4
    k = 4

    top_k = np.argsort(-similarity)[:k]
    top_k_zenith = zenith_points_pos[top_k]
    mean_zenith = top_k_zenith.mean(axis=0)
    return mean_zenith


def calculate_max_eigenvec_zp(zenith_points_pos):
    # k = 4
    k = 4
    data = zenith_points_pos.T

    [U, _, _] = linalg.svd(data.dot(data.T))
    best_zenith = U[:, 0]
    if best_zenith[1] < 0:
        best_zenith = -best_zenith

    for i in range(1):
        similarity = zenith_points_pos.dot(best_zenith)
        top_k = np.argsort(-similarity)[:k]
        top_k_zenith = zenith_points_pos[top_k]

        data = top_k_zenith.T
        [U, _, _] = linalg.svd(data.dot(data.T))
        best_zenith = U[:, 0]
        if best_zenith[1] < 0:
            best_zenith = -best_zenith

    return best_zenith




def calculate_consensus_zp(zenith_points, method):
    zenith_points_pos = np.array([z_i if z_i[1] > 0 else -z_i for z_i in zenith_points])
    if method == 'mean':
        best_zenith = calculate_mean_zp(zenith_points_pos)
    elif method == 'svd':
        best_zenith = calculate_max_eigenvec_zp(zenith_points_pos)



    # #  no zenith point estimation
    # best_zenith = np.array([0.,1.,0.])


    zenith_consensus = np.sign(zenith_points[:, 1]).reshape(-1, 1) * best_zenith

    return [zenith_consensus, best_zenith]




def calculate_mean_vp(vp_points):
    num = len(vp_points)
    if num >= 4:
        mean_vp = vp_points.mean(axis=0)
        similarity = vp_points.dot(mean_vp)
        k = int(np.ceil(num / 2))

        top_k = np.argsort(-similarity)[:k]
        top_k_vp = vp_points[top_k]
        mean_vp = top_k_vp.mean(axis=0)
    else:
        mean_vp = vp_points.mean(axis=0)
    return mean_vp


def calculate_max_eigenvec_vp(vp_points):
    num = len(vp_points)
    if num >= 4:

        k = int(np.ceil(num / 2))
        data = vp_points.T

        [U, _, _] = linalg.svd(data.dot(data.T))
        best_vp = U[:, 0]

        if best_vp[0] < 0:
            best_vp = -best_vp

        for i in range(1):
            similarity = vp_points.dot(best_vp)
            top_k = np.argsort(-similarity)[:k]
            top_k_vp = vp_points[top_k]

            data = top_k_vp.T
            [U, _, _] = linalg.svd(data.dot(data.T))
            best_vp = U[:, 0]
            if best_vp[0] < 0:
                best_vp = -best_vp
    else:
        data = vp_points.T
        [U, _, _] = linalg.svd(data.dot(data.T))
        best_vp = U[:, 0]
        if best_vp[0] < 0:
            best_vp = -best_vp
    return best_vp





def calculate_consensus_vps(vp_points, method):
    if method == 'mean':
        best_vp = calculate_mean_vp(vp_points)
    elif method == 'svd':
        best_vp = calculate_max_eigenvec_vp(vp_points)
    return best_vp










# calculate_consensus_zp(zenith_points, 'svd')


#
# output1 = calculate_mean_zp(zenith_points_pos)
# output2 = calculate_max_eigenvec_zp(zenith_points_pos)
#
# print(100)




