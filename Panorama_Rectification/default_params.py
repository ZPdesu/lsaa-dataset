import numpy as np


class params:
    # parameters below are provided in the same order and with the same values as in [Simon rt al., ECCV' 2018] paper
    theta_v = np.pi / 8
    theta_z = 10
    L_z = 45
    theta_h = 1.5
    L_h = 64
    sigma = 0.2
    S = 300
    L_vp = 128

    # put the parameter below to 1 if you need to detect infinite horizontal VPs,
    # e.g.for ortho - rectification of fronto-parallel vertical planes
    include_infinite_hvps = 0

    # parameters below are used in the code provided by [Zhai et al., CVPR' 2016]

    theta_con = 1.5
    #score_function = lambda x: (params.theta_con - x) * (params.theta_con > x)
    theta_verline = 15
    # theta_horline = 2
    theta_horline = 1
    hvp_refinement = True
    refine_niters = 3

    def score_function(self, x):
        return (params.theta_con - x) * (params.theta_con > x)

def default_params():
    return params()