import numpy as np
import os, os.path

def slice_big_file(filename, size, nproj):
    # Remove .edf
    strip_name = os.path.splitext(os.path.basename(filename))[0]
    print strip_name
    slice_dir = os.path.join(os.path.dirname(filename), 'slice')
    if not os.path.exists(slice_dir):
        os.mkdir(slice_dir)
    f = open(filename)
    i = 0
    new = 'starting'
    while len(new)>0:
        new = f.read(nproj * (size + 1024))
        if len(new) > 0:
            slice_dir_step = os.path.join(slice_dir, strip_name + '_%03d' %i)
            if not os.path.exists(slice_dir_step):
                os.mkdir(slice_dir_step)
            newfile_name = os.path.join(slice_dir_step,
                                    strip_name + '_%03d.edf' %i)
            newfile = open(newfile_name, 'w')
            newfile.write(new)
            newfile.close()
            i += 1
            print i
    f.close()
