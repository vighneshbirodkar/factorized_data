import argparse
import random
import os
import numpy as np
import time
import multiprocessing as mp

from suncg_wrapper import SceneObject

ELEVATIONS = np.linspace(-1, 2, num=5)

parser = argparse.ArgumentParser()
parser.add_argument('--data_root', type=str, default='.')
parser.add_argument('--outdir', type=str, default='./output')
parser.add_argument('--num', type=str, required=True)
parser.add_argument('--seed', type=str, default=0)
parser.add_argument('--img_size', type=int, default=256)


def safe_mkdir(path):
    if not os.path.exists(path):
        os.mkdir(path)


opt = parser.parse_args()

random.seed(opt.seed)
np.random.seed(opt.seed)

outdir = os.path.join(opt.outdir, opt.classname)
outdir = os.path.abspath(outdir)
safe_mkdir(outdir)


object_ids = os.lisdir(os.path.join(opt.data_root, 'object'))
object_pairs = []
