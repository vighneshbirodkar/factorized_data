from __future__ import print_function
import subprocess
import shutil
import os
import re
import numpy as np
import errno
import pprint
import json
import uuid

from nibabel import eulerangles


float_re = r'([+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?)'
tuple_re = r'\(\s*{0}\s*{0}\s*{0}\s*\)'.format(float_re)
bbox_regex = re.compile(r'.*BBox\s*=\s*{0}\s*{0}.*'.format(tuple_re),
                        flags=re.DOTALL)

json_template = {
    "version": "suncg@1.0.0",
    "levels": [
        {
            "nodes": [
                {
                    "type": "Object",
                    "valid": 1,
                    "modelId": "",
                    "transform": []
                },
                {
                    "type": "Object",
                    "valid": 1,
                    "modelId": "",
                    "transform": []
                }
            ]
        }
    ]
}


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


class Interpolator(object):
    def interpolate_image(self, outfolder, n, **kwargs):

        prop_arrays = {}
        for prop in kwargs:

            if hasattr(kwargs[prop], '__iter__'):
                start, end = kwargs[prop]
            else:
                start = end = kwargs[prop]

            prop_arrays[prop] = np.linspace(start, end, num=n)

        camera = None
        for i in range(n):
            props = {}
            name = '%02d-' % i
            for key in sorted(kwargs.keys()):
                props[key] = prop_arrays[key][i]
                name += '%s-%.2f_' % (key, props[key])

            name = name.rstrip('_')
            name += '.jpg'
            imgname = os.path.join(outfolder, name)
            camera = self.transform_img(imgname, camera=camera, **props)


class SceneObject(Interpolator):
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
        return camera_str

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
                       elevation=1, camera=None):

        if elevation is not None:
            self._guess_good_cam(elevation)

        dst_obj = self._transform_inplace(tx, ty, tz, rx, ry, rz)
        camera_str = self.camera_str

        if camera is not None:
            camera_str = camera

        command = ('scnview {obj} -camera {cam}'.
                   format(obj=dst_obj, cam=camera_str))
        run_command(command)

    def transform_img(self, outfile, tx=0, ty=0, tz=0, rx=0, ry=0, rz=0,
                      elevation=1, light=None, camera=None):
        os.chdir(self.folder)

        if elevation is not None:
            self._guess_good_cam(elevation)

        dst_obj = self._transform_inplace(tx, ty, tz, rx, ry, rz)
        camera_str = self.camera_str
        if camera is not None:
            camera_str = camera

        with open('__cam', 'w') as f:
            cam = camera_str + ' 0.4 0.307065 1'
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


class DualObjectJSON(Interpolator):
    def __init__(self, folder1, folder2, root_dir, img_size=256,
                 mode='mesa'):

        self.object1 = SceneObject(folder1, mode=mode, img_size=img_size)
        self.object2 = SceneObject(folder2, mode=mode, img_size=img_size)
        self.mode = mode
        self.img_size = img_size

        unique_name = uuid.uuid4().hex
        self.folder = os.path.join(root_dir, 'tmp_house', unique_name)
        os.mkdir(self.folder)

    def _transform_inplace(self, tx1=0, ty1=0, tz1=0, tx2=0, ty2=0, tz2=0,
                           rx1=0, ry1=0, rz1=0, rx2=0, ry2=0, rz2=0):
        name1 = os.path.basename(self.object1.folder)
        name2 = os.path.basename(self.object2.folder)

        rx1, ry1, rz1, rx2, ry2, rz2 = np.deg2rad(
            [rx1, ry1, rz1, rx2, ry2, rz2])

        t1 = np.eye(4)
        t2 = np.eye(4)
        t1[:3, 3] = tx1, ty1, tz1
        t1[:3, :3] = eulerangles.euler2mat(rz1, ry1, rx1)
        t2[:3, 3] = tx2, ty2, tz2
        t2[:3, :3] = eulerangles.euler2mat(rz2, ry2, rx2)

        json_dict = dict(json_template)

        json_dict['levels'][0]['nodes'][0]['modelId'] = name1
        json_dict['levels'][0]['nodes'][1]['modelId'] = name2
        json_dict['levels'][0]['nodes'][0]['transform'] = list(t1.flatten('F'))
        json_dict['levels'][0]['nodes'][1]['transform'] = list(t2.flatten('F'))

        path = os.path.join(self.folder, 'house.json')
        with open(path, 'w') as f:
            json.dump(json_dict, f)
        return path

    def transform_view(self, tx1=0, ty1=0, tz1=0, tx2=0, ty2=0, tz2=0,
                       rx1=0, ry1=0, rz1=0, rx2=0, ry2=0, rz2=0,
                       elevation=1):

        self._transform_inplace(tx1, ty1, tz1, tx2, ty2, tz2,
                                rx1, ry1, rz1, rx2, ry2, rz2)
        sobj = SceneObject(self.folder)
        sobj.transform_view(elevation=elevation)

    def transform_img(self, outfile, tx1=0, ty1=0, tz1=0, tx2=0, ty2=0, tz2=0,
                      rx1=0, ry1=0, rz1=0, rx2=0, ry2=0, rz2=0, light=None,
                      elevation=1, camera=None):
        self._transform_inplace(tx1, ty1, tz1, tx2, ty2, tz2,
                                rx1, ry1, rz1, rx2, ry2, rz2)
        sobj = SceneObject(self.folder, mode=self.mode, img_size=self.img_size)

        if camera is None:
            camera = sobj._guess_good_cam(elevation=elevation)

        sobj.transform_img(outfile=outfile, elevation=elevation, light=light,
                           camera=camera)
        return camera

    def __del__(self):
        shutil.rmtree(self.folder, ignore_errors=True)


#dobj = DualObjectJSON('/home/vighnesh/data/suncg_data/object/41',
#                      '/home/vighnesh/data/suncg_data/object/42',
#                      '/home/vighnesh/data/suncg_data/', mode='glut')

#dobj.transform_img(outfile='/home/vighnesh/Desktop/test/image.jpg',
#                   tx1=1, tx2=-1, ry1=45, ry2=45, elevation=-1)

#dobj.interpolate_image('/home/vighnesh/Desktop/test/', n=10, tx1=-1, tx2=1,
#                       ry1=(0, 360))
