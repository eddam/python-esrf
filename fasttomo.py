from EdfFile import EdfFile
import numpy as np
import os
from rotation_axis import _compute_proj_correlation

def string_scan_geometry(scan_name, nb_proj, dim1, dim2):
    s = """
MULTIFRAME = 2

FILE_PREFIX = %s
NUM_FIRST_IMAGE = 0 # No. of first projection file
NUM_LAST_IMAGE = %d # No. of last projection file
NUMBER_LENGTH_VARIES = NO
LENGTH_OF_NUMERICAL_PART = 4 # No. of characters
FILE_POSTFIX = .edf
FILE_INTERVAL = 1 # Interval between input files

# Parameters defining the projection file format
NUM_IMAGE_1 = %d # Number of pixels horizontally
NUM_IMAGE_2 = %d # Number of pixels vertically
IMAGE_PIXEL_SIZE_1 = 1.100000 # Pixel size horizontally (microns)
IMAGE_PIXEL_SIZE_2 = 1.100000 # Pixel size vertically

    """% (scan_name, nb_proj - 1, dim1, dim2)
    return s

def string_refs(med_dark_name, med_ref_name):
    s = """
# Parameters defining background treatment
SUBTRACT_BACKGROUND = YES # Subtract background from data
BACKGROUND_FILE = %s

# Parameters defining flat-field treatment
CORRECT_FLATFIELD = YES # Divide by flat-field image
FLATFIELD_CHANGING = NO # Series of flat-field files
FLATFIELD_FILE = %s

TAKE_LOGARITHM = YES # Take log of projection values
    """% (med_dark_name, med_ref_name)
    return s


def string_rotation(nb_proj, center):
    s = """
# Parameters defining experiment
ANGLE_BETWEEN_PROJECTIONS = %f # Increment angle in degrees
ROTATION_VERTICAL = YES
ROTATION_AXIS_POSITION = %f # Position in pixels
    """% (180./nb_proj, center)
    return s


def string_reconstruction(slice_nb, dim1):
    s = """
# Parameters defining reconstruction
OUTPUT_SINOGRAMS = NO # Output sinograms to files or not
OUTPUT_RECONSTRUCTION = YES # Reconstruct and save or not
START_VOXEL_1 =      1 # X-start of reconstruction volume
START_VOXEL_2 =      1 # Y-start of reconstruction volume
START_VOXEL_3 =    %d # Z-start of reconstruction volume
END_VOXEL_1 =   %d # X-end of reconstruction volume
END_VOXEL_2 =   %d # Y-end of reconstruction volume
END_VOXEL_3 =    %d # Z-end of reconstruction volume
OVERSAMPLING_FACTOR = 4 # 0 = Linear, 1 = Nearest pixel
ANGLE_OFFSET = 0.000000 # Reconstruction rotation offset angle in degrees
CACHE_KILOBYTES = 256 # Size of processor cache (L2) per processor (KBytes)
SINOGRAM_MEGABYTES = 400 # Maximum size of sinogram storage (megabytes)
    """% (slice_nb, dim1, dim1, slice_nb)
    return s


def string_output(output_file):
    s = """
# Parameters extra features PyHST
DO_CCD_FILTER = YES # CCD filter (spikes)
CCD_FILTER = "CCD_Filter"
CCD_FILTER_PARA = {"threshold": 0.040000 }
DO_SINO_FILTER = NO # Sinogram filter (rings)
SINO_FILTER = "SINO_Filter"
ar = Numeric.ones(2016,'f')
ar[0]=0.0
ar[2:18]=0.0
SINO_FILTER_PARA = {"FILTER": ar }
DO_AXIS_CORRECTION = NO # Axis correction
AXIS_CORRECTION_FILE = correct.txt
OPTIONS= { 'padding':'E' , 'axis_to_the_center':'Y'} # Padding and position axis

# Parameters defining output file / format
OUTPUT_FILE = %s

# Reconstruction program options
DISPLAY_GRAPHICS = NO # No images"""% (output_file)
    return s


def _process_ref(ref_name, med_name):
    if os.path.exists(med_name):
        print("ref already exists")
        return
    else:
        ref = EdfFile(ref_name)
        nb_ref = ref.GetNumImages()
        images = [ref.GetData(i) for i in range(nb_ref)]
        med_image = np.median(images, axis=0)
        header = ref.GetStaticHeader(0)
        header2 = ref.GetHeader(0)
        header.update(header2)
        med_edf = EdfFile(med_name)
        med_edf.WriteImage(header, med_image, DataType='UnsignedShort')

def reconstruction_slice(par_name):
    cmd = '/scisoft/ESRF_sw/opteron2/PACKAGES/PyHST_2_019/scripts/PyHST %s'\
                % par_name
    os.system(cmd)

def fast_tomo(scan_name, slice_nb=None, ref_name='bla', dark_name='blo',
              center=None, rec_slice=False, display=False):
    im = EdfFile(scan_name)
    nb_proj = im.GetNumImages()
    header = im.GetStaticHeader(0)
    dim1, dim2 = int(header['Dim_1']), int(header['Dim_2'])
    if slice_nb is None:
        slice_nb = dim2 / 2
    # Create dir
    dir_name = os.path.dirname(scan_name)
    root, ext = os.path.splitext(scan_name)
    base = os.path.basename(root)
    if not os.path.exists(root):
        os.mkdir(root)
    parfile_name = os.path.join(root, base + '.par')
    output_file = os.path.join(root, base+ '.vol')
    if os.path.dirname(ref_name) == '':
        ref_name = os.path.join(dir_name, ref_name)
        dark_name = os.path.join(dir_name, dark_name)
    med_ref_name = os.path.splitext(ref_name)[0] + '_med.edf'
    med_dark_name = os.path.splitext(dark_name)[0] + '_med.edf'
    _process_ref(ref_name, med_ref_name)
    _process_ref(dark_name, med_dark_name)
    if center is None:
        proj1 = im.GetData(0)
        proj2 = im.GetData(nb_proj - 1)
        ref = EdfFile(med_ref_name).GetData(0)
        center = _compute_proj_correlation(proj1, proj2, ref)
        print center

    # Now build par file
    parfile_string = string_scan_geometry(scan_name, nb_proj, dim1, dim2)
    # Background and flatfield
    parfile_string += string_refs(med_dark_name, med_ref_name)
    parfile_string += string_rotation(nb_proj, center)
    # Parameters defining reconstruction
    parfile_string += string_reconstruction(slice_nb, dim1)
    # Extra features
    parfile_string += string_output(output_file)
    # print(parfile_string)
    f = open(parfile_name, 'w')
    f.write(parfile_string)
    f.close()
    if rec_slice:
        reconstruction_slice(par_name)
