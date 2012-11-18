import numpy as np
import tables as tb
from time import time
import os, os.path
import numexpr as ne
from glob import glob

def write_hdf(arrays):
    h5file = tb.openFile("out/test.h5",
                            mode = "w", title = "Test file")

    for index, array in enumerate(arrays):
        h5file.createArray(h5file.root, 'array%i' % index,
                            array)
    h5file.close()


def write_chdf(arrays, compress=0, complib='zlib', output_name='out.h5', 
        array_names=['data']):
    if compress == 0:
        return write_hdf(arrays)
    h5file = tb.openFile(output_name,
                            mode = "w", title = "Test file")
    filters = tb.Filters(complevel=compress,
                                complib=complib)

    for index, (array, array_name) in enumerate(zip(arrays, array_names)):
        shape = array.shape
        atom = tb.Atom.from_dtype(array.dtype)
        ca = h5file.createCArray(h5file.root, array_name,
                                    atom, shape, filters=filters)
        ca[...] = array
    h5file.close()

def recad_to_h5_chunk(file_name, vmin, vmax, shape):
    h5_name = os.path.splitext(file_name)[0] + '.h5'
    if not os.path.getsize(file_name) == 4 * np.prod(shape):
        print "the shape is not consistent with the size of the file!"
        return
    data = np.memmap(file_name, dtype=np.float32, shape=shape)
    data_uint8 = np.memmap('/tmp/recad.raw', dtype=np.uint8, shape=shape,
                           mode='w+')
    chunk_size = 50
    len_data = shape[0]
    for i in range((len_data - 1)/chunk_size + 1):
        #print i
        beg = i * chunk_size
        end = (i + 1) * chunk_size
        if end >= len_data:
            end = None
        dat = np.copy(data[beg:end])
        mask_inf = ne.evaluate("dat < vmin")
        dat = ne.evaluate("(1 - mask_inf) * dat + vmin * mask_inf")
        mask_sup = ne.evaluate("dat > vmax")
        dat = ne.evaluate("(1 - mask_sup) * dat + vmax * mask_sup")
        dat = ne.evaluate("255 * (dat - vmin) / (vmax - vmin)")
        data_uint8[beg:end] = dat.astype(np.uint8)[:]
        del dat
    write_chdf([data_uint8], compress=3, output_name=h5_name)


def recad_to_h5(file_name, vmin, vmax, shape):
    if not os.path.getsize(file_name) == 4 * np.prod(shape):
        print "the shape is not consistent with the size of the file!"
        return
    h5_name = os.path.splitext(file_name)[0] + '.h5'
    dat = np.fromfile(file_name, dtype=np.float32).reshape(shape)
    mask_inf = ne.evaluate("dat < vmin")
    dat = ne.evaluate("(1 - mask_inf) * dat + vmin * mask_inf")
    del mask_inf
    print "min ok"
    mask_sup = ne.evaluate("dat > vmax")
    dat = ne.evaluate("(1 - mask_sup) * dat + vmax * mask_sup")
    del mask_sup
    print "max ok"
    dat = ne.evaluate("255 * (dat - vmin) / (vmax - vmin)")
    print "recad ok"
    dat = dat.astype(np.uint8)
    write_chdf([dat], compress=3, output_name=h5_name)

def recad_dir(pattern, vmin, vmax, shape, discard_vol=False,
                        only_new=True):
    """
    Batch-transform float-32 .vol files into arrays of uint8 stored in
    hdf5 files, using zlib compression. vmin and vmax are used to clip
    the dynamics of the uint8 array.

    Parameters
    ----------

    pattern: str
        wildcard-style pattern ('*.vol') of files to be processed

    vmin: float
        minimum value (set to 0 in the uint8 array)

    vmax: float
        maximum value (set to 255 in the uint8 array)

    shape: tuple
        shape of the 3-D volumes

    discard_vol: bool
        if True, the .vol files are removed after they have been transformed
        to h5 files.

    only_new: bool
        if True, existing h5 files are not computed again

    Examples
    --------

    >>> recad_dir('*.vol', -50, 50, (600, 1104, 1104))

    Notes
    -----

    hdf5 files have the same name as vol files, with just the extension
    that is changed (.vol --> .h5). They are saved in the same directory.
    """
    file_list = glob(pattern)
    file_list.sort()
    for file_name in file_list:
        h5_name = os.path.splitext(file_name)[0] + '.h5'
        print file_name
        if only_new:
            if os.path.exists(h5_name):
                print "already exists"
                continue
        recad_to_h5_chunk(file_name, vmin, vmax, shape)
        if discard_vol and os.path.exists(h5_name):
            os.remove(file_name)
            os.remove(file_name + '.info')
            os.remove(file_name + '.xml')
