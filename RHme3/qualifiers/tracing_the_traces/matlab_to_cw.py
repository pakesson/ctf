#!/bin/env python

import numpy
import scipy.io as sio

# First load traces.mat in Octave and save as mat-binary
# > save -mat-binary binary.mat inout samples
# (-mat-binary sets the file format, binary.mat is the filename, inout and
# samples are the variables that will be saved)

mat = sio.loadmat("binary.mat")

textin = mat['inout'][:, 0:16]
textout = mat['inout'][:, 16:32]
traces = mat['samples']

numpy.save("textin", textin)
numpy.save("textout", textout)
numpy.save("traces", traces)
