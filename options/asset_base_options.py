import multiprocessing
import argparse
import os



class AssetBaseOptions():
    def __init__(self):
        self.initialized = False

    def initialize(self, parser):



        parser.add_argument("--asset_type", type=str, default='window',choices=['window', 'balcony', 'door'],
                            help="asset type", metavar='TYPE')

        parser.add_argument("--filtered", type=bool, default=True,
                            help="if filtered use asset_filtered.csv, otherwise use asset_all.csv",  metavar='BOOL')


        parser.add_argument("--cores", type=int, default=multiprocessing.cpu_count(),
                       help="use multiple cores to download panoramas")
        parser.add_argument("--pano_folder", type=str, default='data/Panoramas', help="pano folder", metavar='FOLDER')

        parser.add_argument("--projection_folder", type=str, default='data/Projection', help="projection folder", metavar='FOLDER')

        parser.add_argument("--facade_folder", type=str, default='data/Facades', help="facade folder", metavar='FOLDER')

        parser.add_argument("--country", type=str, default=None,
                            help="country constrain")

        parser.add_argument("--city", type=str, default=None,
                            help="city constrain")

        parser.add_argument("--min_height", type=int, default=None,
                            help="asset minimal height", metavar='PX')

        parser.add_argument("--min_width", type=int, default=None,
                            help="asset minimal width", metavar='PX')

        parser.add_argument("--max_height", type=int, default=None,
                            help="asset maximal height", metavar='PX')

        parser.add_argument("--max_width", type=int, default=None,
                            help="asset maximal width", metavar='PX')

        parser.add_argument("--max_occlusion", type=float, default=None,
                            help="max occlusion", metavar='NUM')


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

        if opt.asset_type == 'window':
            opt.asset_folder = 'data/Windows'
        elif opt.asset_type == 'balcony':
            opt.asset_folder = 'data/Balconies'
        elif opt.asset_type == 'door':
            opt.asset_folder = 'data/Doors'



        if opt.filtered:
            opt.properties_file = os.path.join('annotations', opt.asset_type, opt.asset_type + '_filtered.csv')
        else:
            opt.properties_file = os.path.join('annotations', opt.asset_type, opt.asset_type + '_all.csv')

        opt.asset_detection_result = os.path.join('annotations', opt.asset_type, opt.asset_type + '_detection.json')

        return opt


    def parse(self):

        opt = self.gather_options()
        self.opt = opt
        return self.opt
