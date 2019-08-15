import multiprocessing
import argparse
import os


class FacadeBaseOptions():
    def __init__(self):
        self.initialized = False

    def initialize(self, parser):
        parser.add_argument("--properties_file", type=str, default='annotations/Properties23K.csv', help="properties file")
        parser.add_argument("--cores", type=int, default=max(multiprocessing.cpu_count() - 2, 1),
                       help="use multiple cores to download panoramas")
        parser.add_argument("--pano_folder", type=str, default='data/Panoramas', help="pano folder")

        parser.add_argument("--projection_folder", type=str, default='data/Projection', help="projection folder")

        parser.add_argument("--facade_folder", type=str, default='data/Facades', help="facade folder")

        parser.add_argument("--facade_detection_result", type=str, default='annotations/facade_detection_result.json',
                            help="facade_detection_result")

        parser.add_argument("--panorama_rectification", type=str, default='annotations/panorama_rectification.json',
                            help="panorama_rectification")

        parser.add_argument("--country", type=str, default=None,
                            help="country constrain")

        parser.add_argument("--city", type=str, default='Bern',
                            help="city constrain")

        parser.add_argument("--min_height", type=int, default=None,
                            help="minimal height")

        parser.add_argument("--min_width", type=int, default=None,
                            help="minimal width")

        parser.add_argument("--max_height", type=int, default=None,
                            help="maximal height")

        parser.add_argument("--max_width", type=int, default=None,
                            help="maximal width")

        parser.add_argument("--max_occlusion", type=float, default=0.5,
                            help="max occlusion")



        parser.add_argument("--first", type=int, default=0, help="first facade number")
        parser.add_argument("--last", type=int, default=200, help="last facade number")

        parser.add_argument("--use_tqdm", type=bool, default=True, help="use tqdm")

        self.initialized = True
        return parser

    def gather_options(self):
        # initialize parser with basic options
        if not self.initialized:
            parser = argparse.ArgumentParser(
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
            parser = self.initialize(parser)

        # get the basic options
        #opt, unknown = parser.parse_known_args()

        opt = parser.parse_args()
        self.parser = parser
        return opt


    def parse(self):

        opt = self.gather_options()
        self.opt = opt
        return self.opt