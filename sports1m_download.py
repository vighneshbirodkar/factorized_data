import hashlib
import os
import argparse
import pytube
import subprocess
import multiprocessing as mp
import pprint


parser = argparse.ArgumentParser()
parser.add_argument('--id_file', type=str, default='./train_partition.txt')
parser.add_argument('--outdir', type=str, default='./output')
parser.add_argument('--n_threads', type=int, default=8)
parser.add_argument('--start_index', type=int, default=0)
parser.add_argument('--end_index', type=int, default=None)


opt = parser.parse_args()
pprint.pprint(vars(opt), indent=2)


with open(opt.id_file) as f:
    video_urls = [line.split()[0] for line in f.readlines()]


video_urls = video_urls
preferred_resolutions = ['240p', '360p', '480p', '144p']


def get_hash(url):
    return hashlib.sha256(url.encode('utf-8')).hexdigest()[:10]


def download_vid(index):
    
    url = video_urls[index]

    try:
        yt = pytube.YouTube(url)
    except:
        print('Cannot find %s' % url)
        return 0

    videos = yt.filter(resolution='360p', extension='mp4')

    if len(videos) == 0:
        print('No suitable video for %s' % url)
        return 0
    else:
        video = videos[0]

    filename = 'video%05d' % index
    video.filename = filename
    try:
        video.download(opt.outdir)
    except:
        print('Download error')
        return 0

    print('Downloaded %s to %s' % (url, filename))
    return 1


pool = mp.Pool(opt.n_threads)
result = list(pool.map(download_vid, range(opt.start_index, opt.end_index)))

print('Downloaded %d videos' % sum(result))
