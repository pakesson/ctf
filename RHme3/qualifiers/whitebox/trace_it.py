#!/usr/bin/env python

import sys
# When running in an Orka container
sys.path.insert(0, '/root/Deadpool/')
from deadpool_dca import *

from binascii import unhexlify

def processinput(iblock, blocksize):
    hexblock = '%0*x' % (2*blocksize, iblock)
    return (unhexlify(hexblock), ['--stdin'])

def processoutput(output, blocksize):
    return int(''.join(output.replace('\r','').split(' ')), 16)

T=TracerGrind('./whitebox', processinput, processoutput, ARCH.amd64, 16)
T.run(100)
bin2daredevil(configs={'attack_sbox': {'algorithm':'AES', 'position':'LUT/AES_AFTER_SBOX'}})
