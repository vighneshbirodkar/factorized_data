import argparse
import csv
import itertools
import os
import numpy as np
import time
import multiprocessing as mp

from gaps_wrapper import SceneObject

ELEVATIONS = np.linspace(-1, 2, num=5)

parser = argparse.ArgumentParser()
parser.add_argument('--data_root', type=str, default='.')
parser.add_argument('--outdir', type=str, default='./output')
parser.add_argument('--classname', type=str, required=True)
parser.add_argument('--img_size', type=int, default=256)


def safe_mkdir(path):
    if not os.path.exists(path):
        os.mkdir(path)


opt = parser.parse_args()

outdir = os.path.join(opt.outdir, opt.classname)
outdir = os.path.abspath(outdir)
safe_mkdir(outdir)

object_ids = []


# Fetched from
# https://github.com/shurans/SUNCGtoolbox/blob/master/metadata/ModelCategoryMapping.csv
with open(os.path.join(opt.data_root, 'ModelCategoryMapping.csv')) as f:
    first = True
    for row in csv.reader(f):
        if first:
            first = False
            continue

        if row[5] == opt.classname:
            object_ids.append(row[1])
            if row[1] is None:
                print(row)


def process_id(object_id):
    start_time = time.time()

    dir_id = os.path.join(outdir, object_id)
    safe_mkdir(dir_id)
    input_dir = os.path.join(*(opt.data_root, 'object', object_id))
    scene_object = SceneObject(input_dir, img_size=opt.img_size, mode='glut')

    for elevation in ELEVATIONS:
        dir_elevation = os.path.join(dir_id, 'elevation_%.2f' % elevation)
        safe_mkdir(dir_elevation)
        scene_object.interpolate_image(dir_elevation, elevation=elevation,
                                       ry=(-180, 180), n=36)

    time_taken = time.time() - start_time
    print('Processed ID %s in %.3f secs. ' % (object_id, time_taken))


pool = mp.Pool()
pool.map(process_id, object_ids)
