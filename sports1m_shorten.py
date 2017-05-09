import os
import argparse
import subprocess
import pprint
import shutil


parser = argparse.ArgumentParser()
parser.add_argument('--indir', type=str, required=True)
parser.add_argument('--outdir', type=str, default='./output')
parser.add_argument('--start_index', type=int, default=0)
parser.add_argument('--end_index', type=int, default=None)


opt = parser.parse_args()
pprint.pprint(vars(opt), indent=2)


input_filenames = sorted(os.listdir(opt.indir))

def shorten_vid(filename):

    basename, _ = os.path.splitext(filename)
    inputfile = os.path.join(opt.indir, filename)

    command = ('ffmpeg -i {inp} -t 00:01:00.000 -c copy '
               '{out}/{name}'.
               format(inp=inputfile, out=opt.outdir, name=filename))
    try:
        subprocess.run(command, shell=True, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
        
    except subprocess.CalledProcessError as e:
        print('Error shortening video')
        print(e)
        return
    print('Shortened %s' % filename)


list(map(shorten_vid, input_filenames[opt.start_index:opt.end_index]))
