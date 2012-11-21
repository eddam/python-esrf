import numpy as np
import os
from scipy.fftpack import fft2, ifft2
from scipy import optimize
from scipy import fftpack
from scipy import ndimage


def _parab(params, dat, X, Y):
    a, b, c, d, x0, x1 = params
    return dat - (a * (X - x0)**2 + b * (Y - x1)**2 + c + d*X*Y)

def cost_function(s, im1, im2):
    return - np.corrcoef([im1[3:-3, 3:-3].ravel(),
                        ndimage.shift(im2, (0, s))[3:-3, 3:-3].ravel()])[0, 1]

def _fit_parab(data):
    X, Y = np.mgrid[-2:3, -2:3]
    params, cov = optimize.leastsq(_parab, (1, 1, 1, 0., 0.5, 0.5),
                    args=(data.ravel(), X.ravel(), Y.ravel()))
    return params[-1]


def _correlate_images(im1, im2, method='brent'):
    shape = im1.shape
    f1 = fft2(im1)
    f1[0, 0] = 0
    f2 = fft2(im2)
    f2[0, 0] = 0
    ir = np.real(ifft2((f1 * f2.conjugate())))
    t0, t1 = np.unravel_index(np.argmax(ir), shape)
    if t0 >= shape[0]/2:
        t0 -= shape[0]
    if t1 >= shape[1]/2:
        t1 -= shape[1]
    if method == 'brent':
        newim2 = ndimage.shift(im2, (t0, t1))
        refine = optimize.brent(cost_function, args=(im1, newim2),
                        brack=[-1, 1], tol=1.e-2) 
    return t1 + refine

def _compute_proj_correlation(proj1, proj2, ref):
    proj1 /= ref.astype(np.float)
    proj2 /= ref.astype(np.float)
    proj2 = proj2[:, ::-1]
    shift = _correlate_images(proj1, proj2)
    center = proj1.shape[1] / 2. + 0.5 + shift / 2.
    return center

