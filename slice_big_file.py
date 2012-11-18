import numpy as np
import os, os.path
import shutil

def slice_big_file(filename, size, nproj, dark_name=None, flat_name=None):
    """
    Parameters
    ----------

    filename : str
        name of multiedf files with several scans

    size : int
        size of one projection, 2 * dim1 * dim2

    nproj : int
        number of projections

    dark_name : str
        dark file copied in each subdirectory

    flat_name : str
        ref file to be copied in each subdirectory

    Examples
    --------
    >>> slice_big_file('/data/visitor/hd560/id19/glass_batch/290612/D1_mm_noread/Manip/D1_noread_0000.edf', 1104*600*2, 800, dark_name='/data/visitor/hd560/id19/glass_batch/290612/D1_mm_noread/Manip/darkend0000.edf', flat_name='/data/visitor/hd560/id19/glass_batch/290612/D1_mm_noread/Manip/refHST0000.edf')
    """
    strip_name = os.path.splitext(os.path.basename(filename))[0]
    print strip_name
    slice_dir = os.path.join(os.path.dirname(filename), 'slice')
    if not os.path.exists(slice_dir):
        os.mkdir(slice_dir)
    f = open(filename, 'r')
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
            if dark_name is not None:
                shutil.copy(dark_name, os.path.join(slice_dir_step, 'darkend0000.edf'))
            if flat_name is not None:
                shutil.copy(flat_name, os.path.join(slice_dir_step, 'refHST0000.edf')) 
                shutil.copy(flat_name, os.path.join(slice_dir_step, 'refHST%04d.edf' %nproj)) 
            i += 1
            print i
    f.close()
