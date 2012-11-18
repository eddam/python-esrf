import numpy as np
import os, os.path
from glob import glob

dirs = {'manip00':'/data/visitor/hd560/id19/glass_batch/290612/manip00-melange_mm_900/Manip',
        'manip01':'/data/visitor/hd560/id19/glass_batch/290612/manip01-melange_mm_820/Manip',
        'manip02':'/data/visitor/hd560/id19/glass_batch/290612/manip02-dilue_mm_900/Manip',
        'manip03':'/data/visitor/hd560/id19/glass_batch/290612/manip03-dilue_mm_900_noread/Manip/slice',
        'manip04':'/data/visitor/hd560/id19/glass_batch/290612/manip04-dilue_mm_800/Manip',
        'manip06':'/data/visitor/hd560/id19/glass_batch/300612/manip06-dilue_fm_820/Manip',
        'manip07':'/data/visitor/hd560/id19/glass_batch/300612/manip07-melange_mm_800/Manip',
        'manip08':'/data/visitor/hd560/id19/glass_batch/010712/manip08-dilue_mm_800/Manip',
        'manip09':'/data/visitor/hd560/id19/glass_batch/010712/manip09_dilue_mgp_800/Manip',
        'manip11':'/data/visitor/hd560/id19/glass_batch/010712/manip11-dilue_mm_750/Manip',
        'manip10':'/data/visitor/hd560/id19/glass_batch/010712/manip10-dilue_mgp_800_noread/manip/slice',
        'manip12':'/data/visitor/hd560/id19/glass_batch/010712/manip12-dilue_mgp_900/Manip/slice',
        'manip13':'/data/visitor/hd560/id19/glass_batch/010712/manip13-dilue_mm_720/Manip',
        'manip14':'/data/visitor/hd560/id19/glass_batch/010712/manip14-ternaire_mmg_900/Manip/slice'}

def check_exp(manip_name):
    dir_names = glob(os.path.join(manip_name, '*[0-9]'))
    dir_names.sort()
    for name in dir_names:
        if not os.path.isdir(name):
            dir_names.remove(name)
    h5_pag_names = glob(os.path.join(manip_name, 'volfloat/*pag0001.h5'))
    h5_pag_names.sort()
    h5_pag_names = [os.path.basename(name) for name in h5_pag_names]
    h5_pag_list = np.array([int(name[-13:-10]) for name in h5_pag_names])
    h5_names = glob(os.path.join(manip_name, 'volfloat/*[0-9]0001.h5'))
    h5_names.sort()
    h5_list = np.array([int(name[-10:-7]) for name in h5_names])
    h5_names = [os.path.basename(name) for name in h5_names]
    vol_names = glob(os.path.join(manip_name, 'volfloat/*.vol'))
    vol_names.sort()
    vol_names = [os.path.basename(name) for name in vol_names]
    dir_names = [os.path.basename(name) for name in dir_names]
    dir_list = np.array([int(name[-3:]) for name in dir_names])
    missing_h5 = np.setdiff1d(dir_list, h5_list)
    missing_h5_pag = np.setdiff1d(dir_list, h5_pag_list)
    print "dir: ", dir_list
    print "h5: ", h5_list
    print "h5_pag:", h5_pag_list
    print "vol: ", vol_names
    print "missing h5: ", missing_h5
    print "missing h5 pag: ", missing_h5_pag
