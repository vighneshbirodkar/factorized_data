import os
import argparse
import pytube
import subprocess
import multiprocessing as mp


parser = argparse.ArgumentParser()
parser.add_argument('--id_file', type=str, default='./train_partition.txt')
parser.add_argument('--outdir', type=str, default='./output')
parser.add_argument('--start_index', type=int, required=True)
parser.add_argument('--end_index', type=int, required=True)
parser.add_argument('--n_threads', type=int, default=8)

opt = parser.parse_args()


with open(opt.id_file) as f:
    video_urls = [line.split()[0] for line in f.readlines()]


video_urls = video_urls[opt.start_index:opt.end_index]
preferred_resolutions = ['240p', '360p', '480p', '144p']


def download_vid(url):

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

    video.download(opt.outdir)
    print('Downloaded ' + url)
    return 1


pool = mp.Pool(opt.n_threads)

result = list(pool.map(download_vid, video_urls))

print('Downloaded %d videos' % sum(result))
