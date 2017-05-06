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

def process_vid(filename):

    basename, _ = os.path.splitext(filename)
    outdir = os.path.join(opt.outdir, basename)

    os.mkdir(outdir)
    inputfile = os.path.join(opt.indir, filename)

    command = ('ffmpeg -i {inp} -vf scale=-1:256 {out}/frame%05d.jpg'.
               format(inp=inputfile, out=outdir))
    try:
        subprocess.run(command, shell=True, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print('Error extracting video')
        print(e)
        return

    tarfilename = os.path.join(opt.outdir, '%s.tar' % basename)
    command = 'tar -cf {outtar} -C {folder} {name}'.format(outtar=tarfilename,
                                                           folder=opt.outdir,
                                                           name=basename)
    try:
        subprocess.run(command, shell=True, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print('Error tarring folder')
        print(e)
        return

    shutil.rmtree(outdir)
    print('Processed video %s' % filename)


list(map(process_vid, input_filenames[opt.start_index:opt.end_index]))
