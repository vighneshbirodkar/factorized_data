import argparse
import random
import os
import numpy as np
import time
import multiprocessing as mp

from suncg_wrapper import DualObjectJSON, SceneObject

ELEVATIONS = np.linspace(-1, 2, num=5)
SIZE_RATIO = 3.0

parser = argparse.ArgumentParser()
parser.add_argument('--data_root', type=str, default='.')
parser.add_argument('--outdir', type=str, default='./output')
parser.add_argument('--num', type=int, required=True)
parser.add_argument('--seed', type=int, default=0)
parser.add_argument('--img_size', type=int, default=256)


def safe_mkdir(path):
    if not os.path.exists(path):
        os.mkdir(path)


opt = parser.parse_args()
opt.outdir = os.path.abspath(opt.outdir)

random.seed(opt.seed)
np.random.seed(opt.seed)

safe_mkdir(opt.outdir)


object_dir = os.path.join(opt.data_root, 'object')
tmp_dir = os.path.join(opt.data_root, 'tmp_house')
object_ids = os.listdir(object_dir)
object_pairs = []


scanned = 0
while len(object_pairs) < opt.num:
    scanned += 1
    
    name1 = random.choice(object_ids)
    object1 = SceneObject(os.path.join(*[opt.data_root, 'object', name1]))

    name2 = random.choice(object_ids)
    object2 = SceneObject(os.path.join(*[opt.data_root, 'object', name2]))

    e1 = np.max(object1.get_extents())
    e2 = np.max(object2.get_extents())

    emax = np.max((e1, e2))
    emin = np.min((e1, e2))

    print(emax/emin)
    if emax/emin <= SIZE_RATIO:
        object_pairs.append((name1, name2))


print('Scanned %d pairs to find %d suitable pairs.' % (scanned, opt.num))

def process_pair(pair):

    object1, object2 = pair
    dir_pair = os.path.join(opt.outdir, '_and_'.join([object1, object2]))
    inp1 = os.path.join(object_dir, object1)
    inp2 = os.path.join(object_dir, object2)

    dual_object = DualObjectJSON(inp1, inp2, tmp_dir, img_size=opt.img_size)

    if os.path.exists(dir_pair):
        print('%s exists, skipping' % dir_pair)

    safe_mkdir(dir_pair)

    speed1 = random.randint(-5, 5)
    speed2 = random.randint(-5, 5)

    for elevation in ELEVATIONS:
        dir_elevation = os.path.join(dir_pair, 'elevation_%.2f' % elevation)
        safe_mkdir(dir_elevation)

        params = dual_object.guess_random_xz()
        dual_object.interpolate_image(dir_elevation, elevation=elevation,
                                      ry1=(0, speed1*72), ry2=(0, speed2*72),
                                      n=36, **params)

    print('Processed pair {}'.format(pair))

pool = mp.Pool()
pool.map(process_pair, object_pairs)
