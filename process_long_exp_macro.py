import numpy as np
import os, os.path
from glob import glob
import shutil
import matplotlib.pyplot as plt
from scipy import stats

def _remove_doubles(list_of_indices):
    li = np.array(list_of_indices)
    diff_li = np.concatenate(([10], np.diff(li)))
    inds = li[diff_li > 1]
    return inds

def process_series(pattern, dark_file='darkend0000.edf',
            ref_file='refHST0000.edf', remove_first=True, n_proj=None):
    """
    Parameters
    ----------

    pattern: string, 
    """
    file_list = glob(pattern)
    file_list.sort()
    if remove_first:
        file_size = os.path.getsize(file_list[0])
        n_trash = file_size / n_proj
    if dark_file == 'darkend0000.edf':
        base_name = os.path.dirname(file_list[0])
        dark_file = os.path.join(base_name, dark_file)
    if ref_file == 'refHST0000.edf':
        base_name = os.path.dirname(file_list[0])
        ref_file = os.path.join(base_name, ref_file)
    for file_name in file_list:
        dir_name = os.path.splitext(file_name)[0]
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
        if not remove_first:
            shutil.move(file_name, dir_name)
        else:
            f = open(file_name, 'r')
            fist_trash = f.read(n_trash)
            to_keep = f.read()
            f.close()
            new_f = open(os.path.join(dir_name, file_name), 'w')
            new_f.write(to_keep)
            new_f.close()
        shutil.copy(dark_file, dir_name)
        shutil.copy(ref_file, dir_name)
        shutil.copy(ref_file, os.path.join(dir_name,
                                    'refHST%04d.edf' %(n_proj - 1)))



def process_long_exp(pattern, dim_1, dim_2, n_proj, n_ref=21,
            dark_file='darkend0000.edf', remove_bad_darks=True):
    """
    Given a set of scans and intermediary refs, this function creates
    a directory for each scan, copies the closest ref (closest in time)
    as well ad a dark file, if given, in this directory.

    Parameters
    ----------
    pattern : str
        files to be processed, wildcard style (e.g. '/my_path/manip*.edf')

    dim_1 :  int
        width in pixels of the ROI

     dim_2 : int
        height in pixels of the ROI

    n_proj : int
        number of projections acquired for one scan

    n_ref : int
        how many pictures are taken during the refs

    dark_file : str, optional
        file with dark images to be copied in each subdirectory

    remove_bad_darks : bool, optional (default True)
        this is a dirty hack in order to get rid of additional images
        that were taken after the refs in the macro

    Examples
    --------

    >>> process_long_exp('manip*.edf', 1104, 800, 600, dark_file='dark.edf')

    Notes
    -----

    A possible improvement would be to detect automatically which files are
    scans and which one are refs, without providing the dimensions. At least
    this version is safe.
    """
    file_list = glob(pattern)
    file_list.sort()
    scan_size = (2 * dim_1 * dim_2 + 1024) * n_proj
    ref_size = (2 * dim_1 * dim_2 + 1024) * n_ref
    file_sizes = np.array([os.path.getsize(file_name) for file_name in file_list])
    scan_inds = np.nonzero(file_sizes == scan_size)[0]
    ref_inds = np.nonzero(file_sizes == ref_size)[0]
    print ref_inds
    if remove_bad_darks:
        ref_inds = _remove_doubles(ref_inds)
    print ref_inds
    if dark_file == 'darkend0000.edf':
        base_name = os.path.dirname(file_list[0])
        dark_file = os.path.join(base_name, dark_file)
    for ind in scan_inds:
        file_name = file_list[ind]
        dir_name = os.path.splitext(file_name)[0]
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
        shutil.move(file_name, dir_name)
        ref_ind = ref_inds[np.argmin(np.abs(ref_inds - ind))]
        print ind, ref_ind
        shutil.copy(file_list[ref_ind], os.path.join(dir_name, 'refHST0000.edf'))
        shutil.copy(file_list[ref_ind], os.path.join(dir_name,
                                            'refHST%04d.edf' %n_proj))
        if dark_file is not None:
            shutil.copy(dark_file, os.path.join(dir_name, 'darkend0000.edf'))

def get_bounds(input_name, dtype=np.float32):
    input_size = os.path.getsize(input_name)
    l = int(np.sqrt(input_size / 4.))
    dat = np.memmap(input_name, dtype=dtype, shape=(l, l), mode='r')
    vmin = stats.scoreatpercentile(dat.ravel(), 0.1)
    vmax = stats.scoreatpercentile(dat.ravel(), 99.9)
    print vmin, vmax
    return vmin, vmax


def vol_to_png(input_name, output_name, dtype=np.float32, vmin=None, vmax=None):
    input_size = os.path.getsize(input_name)
    l = int(np.sqrt(input_size / 4.))
    dat = np.memmap(input_name, dtype=dtype, shape=(l, l), mode='r')
    if vmin is not None:
        plt.imsave(output_name, dat, cmap='gray', vmin=vmin, vmax=vmax)
    else:
        plt.imsave(output_name, dat, cmap='gray')

def make_png(dir_name, exp=True):
    vmin, vmax = None, None
    if exp:
        pattern = os.path.join(dir_name, '*[0-9]*/*.vol')
    else:
        pattern = os.path.join(dir_name, '*.vol')
        print pattern
    vol_files = glob(pattern)
    vol_files.sort()
    png_dir_name = os.path.join(dir_name, 'pngs')
    if not os.path.exists(png_dir_name):
        os.mkdir(png_dir_name)
    for file_name in vol_files:
        if vmin is None:
            vmin, vmax = get_bounds(file_name)
        print file_name
        new_name = os.path.splitext(os.path.basename(file_name))[0] + '.png'
        new_name = os.path.join(png_dir_name, new_name)
        vol_to_png(file_name, new_name, vmin=vmin, vmax=vmax)
