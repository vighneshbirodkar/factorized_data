import sys
import shutil
import os
import random

folder = sys.argv[1]

train_folder = os.path.join(folder, 'train')
valid_folder = os.path.join(folder, 'valid')

os.mkdir(train_folder)
os.mkdir(valid_folder)

files = os.listdir(folder)
random.shuffle(files)

for i, file_ in enumerate(files[:250000]):
    src = os.path.join(folder, file_)
    dst = os.path.join(folder, 'train', file_, )

    print(i, file_)
    shutil.move(src, dst)
    
for i, file_ in enumerate(files[250000:]):
    src = os.path.join(folder, file_)
    dst = os.path.join(folder, 'valid', file_, )

    print(i, _file)
    shutil.move(src, dst)
