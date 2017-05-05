import hashlib
import os
import argparse
import pytube
import subprocess
import multiprocessing as mp
import random
import pprint


parser = argparse.ArgumentParser()
parser.add_argument('--id_file', type=str, default='./train_partition.txt')
parser.add_argument('--outdir', type=str, default='./output')
parser.add_argument('--n_threads', type=int, default=8)
parser.add_argument('--seed', type=int, default=None)


opt = parser.parse_args()
random.seed(opt.seed)

pprint.pprint(vars(opt), indent=2)


with open(opt.id_file) as f:
    video_urls = [line.split()[0] for line in f.readlines()]


video_urls = video_urls
preferred_resolutions = ['240p', '360p', '480p', '144p']


def get_hash(url):
    return hashlib.sha256(url.encode('utf-8')).hexdigest()[:10]


def download_random_vid(_):

    downloaded = set([name.split('.')[0] for name in os.listdir(opt.outdir)])
    
    url = random.choice(video_urls)

    while get_hash(url) in downloaded:
        print('Skipping %s as %s exists' % (url, get_hash(url)))
        url = random.choice(video_urls)

    try:
        yt = pytube.YouTube(url)
    except:
        print('Cannot find %s' % url)
        return 0

    video = None

    for res in preferred_resolutions:
        videos = yt.filter(resolution=res)
        if len(videos) > 0:
            video = videos[0]
            break

    if video is None:
        print('No suitable video for %s' % url)
        return 0

    filename = hashlib.sha256(url.encode('utf-8')).hexdigest()[:10]
    video.filename = filename
    try:
        video.download(opt.outdir)
    except:
        print('Download error')
        return 0

    print('Downloaded %s to %s' % (url, filename))
    return 1


pool = mp.Pool(opt.n_threads)
result = list(pool.map(download_random_vid, range(10**6)))

print('Downloaded %d videos' % sum(result))
