from __future__ import print_function
import subprocess
import os
import re
import numpy as np
import errno


float_re = r'([+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?)'
tuple_re = r'\(\s*{0}\s*{0}\s*{0}\s*\)'.format(float_re)
bbox_regex = re.compile(r'.*BBox\s*=\s*{0}\s*{0}.*'.format(tuple_re),
                        flags=re.DOTALL)


def silentremove(filename):
    try:
        os.remove(filename)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise


def _parse_bbox_extents(string):
    result = bbox_regex.match(string)
    result = result.group(*range(1, 22, 4))
    result = list(map(float, result))
    return np.array(result[:3]), np.array(result[3:])


def run_command(command):
    result = subprocess.run(command, shell=True, check=True,
                            stdout=subprocess.PIPE)
    return result.stdout.decode()


class SceneObject(object):
    def __init__(self, folder, img_size=256, mode='mesa'):
        self.init_dir = os.getcwd()
        self.folder = folder.rstrip('/')
        self.filename = self._guess_filename()
        self.basename = os.path.splitext(self.filename)[0]
        self.mode = mode
        self.img_size = img_size

        self._fetch_info()
        self._guess_good_cam()

    def _guess_filename(self):

        name = os.path.basename(self.folder) + '.obj'
        filename = os.path.join(self.folder, name)
        if os.path.exists(filename):
            return name

        filename = os.path.join(self.folder, 'house.json')
        if os.path.exists(filename):
            return 'house.json'

    def _guess_good_cam(self, elevation=1.0):

        os.chdir(self.folder)
        extents = np.abs(self.bbox1 - self.bbox2)
        coords = np.zeros(3)
        coords[1] = extents[1]*elevation
        coords[2] = np.max(extents)*2
        ox, oy, oz = coords
        tx, ty, tz = -coords

        oy += extents[1]/2

        camera_str = ('{ox} {oy} {oz} {tx} {ty} {tz} 0 1 0'.
                      format(ox=ox, oy=oy, oz=oz, tx=tx, ty=ty, tz=tz))
        self.camera_str = camera_str

    def view(self):

        command = ('scnview {name} -camera {cam}'.
                   format(name=self.filename, cam=self.camera_str))
        run_command(command)

    def _fetch_info(self):
        os.chdir(self.folder)
        result = run_command('scninfo %s' % self.filename)
        self.bbox1, self.bbox2 = _parse_bbox_extents(result)

    def _transform_inplace(self, tx=0, ty=0, tz=0, rx=0, ry=0, rz=0):
        os.chdir(self.folder)
        src_obj = self.filename
        dst_obj = '__t__%s.obj' % self.basename
        command = ('scn2scn {src_path} {dst_path} -rx {rx} -ry {ry} -rz {rz} '
                   '-tx {tx} -ty {ty} -tz {tz}'
                   .format(src_path=src_obj, dst_path=dst_obj,
                           rx=rx, ry=ry, rz=rz, tx=tx, ty=ty, tz=tz))

        run_command(command)
        return dst_obj

    def transform_view(self, tx=0, ty=0, tz=0, rx=0, ry=0, rz=0,
                       elevation=None):

        if elevation is not None:
            self._guess_good_cam(elevation)

        dst_obj = self._transform_inplace(tx, ty, tz, rx, ry, rz)
        command = ('scnview {obj} -camera {cam}'.
                   format(obj=dst_obj, cam=self.camera_str))
        run_command(command)

    def transform_img(self, outfile, tx=0, ty=0, tz=0, rx=0, ry=0, rz=0,
                      elevation=None, light=None):
        os.chdir(self.folder)

        if elevation is not None:
            self._guess_good_cam(elevation)

        dst_obj = self._transform_inplace(tx, ty, tz, rx, ry, rz)
        with open('__cam', 'w') as f:
            cam = self.camera_str + ' 0.4 0.307065 1'
            f.write(cam.replace(' ', '\t'))

        outpath = os.path.dirname(outfile)

        command = ('scn2img -{mode} -capture_color_images {obj} __cam '
                   '{outpath} -width {size} -height {size} -background 1 1 1'
                   .format(mode=self.mode, obj=dst_obj, outpath=outpath,
                           size=self.img_size))
        if light is not None:

            # From R3Graphics/R3Scene.cpp in function CreateDirectionalLights
            with open('__light', 'w') as f:
                f.write('directional_light world {i} 1 1 1 3 2 3\n'.
                        format(i=light))
                f.write('directional_light world {i} 1 1 1 -3 -4 -5'.
                        format(i=light))
            command += ' -lights __light'

        run_command(command)
        os.rename(os.path.join(outpath, '000000_color.jpg'), outfile)

    def __del__(self):
        os.chdir(self.folder)
        silentremove('__t__%s.obj' % self.basename)
        silentremove('__t__%s.mtl' % self.basename)
        silentremove('__cam')
        silentremove('__light')

    def interpolate_image(self, outfolder, n, **kwargs):

        prop_arrays = {}
        for prop in kwargs:

            if hasattr(kwargs[prop], '__iter__'):
                start, end = kwargs[prop]
            else:
                start = end = kwargs[prop]

            prop_arrays[prop] = np.linspace(start, end, num=n)

        for i in range(n):
            props = {}
            name = '%02d-' % i
            for key in sorted(kwargs.keys()):
                props[key] = prop_arrays[key][i]
                name += '%s-%.2f_' % (key, props[key])

            name = name.rstrip('_')
            name += '.jpg'
            imgname = os.path.join(outfolder, name)
            self.transform_img(imgname, **props)


#obj = SceneObject('/home/vighnesh/data/suncg_data/object/42', mode='glut')
#obj = SceneObject('/home/vighnesh/data/suncg_data/house/0004d52d1aeeb8ae6de39d6bd993e992', mode='glut')

#obj.interpolate_image(n=10, outfolder='/home/vighnesh/Desktop/test',
#                      ry=(-90, 90))
