import multiprocessing
import argparse
import os


class FacadeBaseOptions():
    def __init__(self):
        self.initialized = False

    def initialize(self, parser):
        parser.add_argument("--properties_file", type=str, default='annotations/Properties23K.csv',
                            help="facade_properties file", metavar='FILE')
        parser.add_argument("--cores", type=int, default=multiprocessing.cpu_count(),
                       help="use multiple cores to download panoramas", metavar='NUM')
        parser.add_argument("--pano_folder", type=str, default='data/Panoramas', help="panorama folder", metavar='FOLDER')

        parser.add_argument("--projection_folder", type=str, default='data/Projection', help="projection folder", metavar='FOLDER')

        parser.add_argument("--facade_folder", type=str, default='data/Facades', help="facade folder", metavar='FOLDER')

        parser.add_argument("--facade_detection_result", type=str, default='annotations/facade_detection_result.json',
                            help="facade bounding boxes on projected images", metavar='FILE')

        parser.add_argument("--panorama_rectification", type=str, default='annotations/panorama_rectification.json',
                            help="rectification parameters of the panoramic images", metavar='FILE')

        parser.add_argument("--country", type=str, default=None,
                            help="country constrain")

        parser.add_argument("--city", type=str, default='Vienna',
                            help="city constrain")

        parser.add_argument("--min_height", type=int, default=None,
                            help="facade minimal height", metavar='PX')

        parser.add_argument("--min_width", type=int, default=None,
                            help="facade minimal width", metavar='PX')

        parser.add_argument("--max_height", type=int, default=None,
                            help="facade maximal height", metavar='PX')

        parser.add_argument("--max_width", type=int, default=None,
                            help="facade maximal width", metavar='PX')

        parser.add_argument("--max_occlusion", type=float, default=0.6,
                            help="facade max occlusion", metavar='NUM')



        parser.add_argument("--first", type=int, default=0, help="first facade number", metavar='NUM')
        parser.add_argument("--last", type=int, default=50, help="last facade number", metavar='NUM')

        parser.add_argument("--use_tqdm", type=bool, default=True, help="use tqdm", metavar='BOOL')

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