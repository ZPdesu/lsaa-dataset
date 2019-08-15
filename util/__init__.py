
import pandas as pd

def filter_properties(opt):
    df_properties = pd.read_csv(opt.properties_file)

    if opt.country != None:
        df_properties = df_properties[(df_properties.country == opt.country)]

    if opt.city != None:
        df_properties = df_properties[(df_properties.city == opt.city)]

    if opt.min_height != None:
        df_properties = df_properties[(df_properties.height >= opt.min_height)]

    if opt.min_width != None:
        df_properties = df_properties[(df_properties.width >= opt.min_width)]

    if opt.max_height != None:
        df_properties = df_properties[(df_properties.height <= opt.max_height)]

    if opt.max_width != None:
        df_properties = df_properties[(df_properties.width <= opt.max_width)]

    if opt.max_occlusion != None:
        df_properties = df_properties[(df_properties.total_occlusion <= opt.max_occlusion)]

    return df_properties