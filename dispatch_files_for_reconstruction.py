import numpy as np
import os, os.path
from glob import glob
import shutil

def dispatch_files(dir_name, flat_step=10, dark_step=-1):
    """
    Function to dispatch scans acquired in an experiment into individual
    directories, with the respective dark and ref files
    """
    if dir_name[-1] == os.sep:
        dir_name = dir_name[:-1]
        print "remove slash"
    base = os.path.basename(dir_name)
    print base
    proj_dir = os.path.join(dir_name, 'proj/')
    filelist = glob(os.path.join(proj_dir, base) + '*_0000.edf')
    filelist.sort()
    dark_list = glob(proj_dir + 'DARK*.edf')
    dark_list.sort()
    flat_list = glob(proj_dir + 'FLAT*.edf')
    flat_list.sort()
    for i, filename in enumerate(filelist):
        print filename
        filename_base = os.path.basename(filename)
        new_dir_name = os.path.join(dir_name, filename_base[:-9])
        dark_name = dark_list[max(0, i/dark_step)]
        flat_name_beg = flat_list[i/flat_step]
        flat_name_end = flat_list[min(i/flat_step + 1, len(flat_list) - 1)]
        if not os.path.exists(new_dir_name):
            os.mkdir(new_dir_name)
        if not os.path.exists(os.path.join(new_dir_name, filename_base)):
            shutil.move(filename, new_dir_name)
        if not os.path.exists(os.path.join(new_dir_name, 'darkend0000.edf')):
            shutil.copy(dark_name,
                        os.path.join(new_dir_name, 'darkend0000.edf'))
        if not os.path.exists(os.path.join(new_dir_name, 'refHST0000.edf')):
            shutil.copy(flat_name_beg,
                        os.path.join(new_dir_name, 'refHST0000.edf'))
    return filelist
