#!/usr/bin/python
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# collect RPA energies for each freq. and compute the total RPA energy
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import re
import sys
import os
import numpy as np
from subprocess import call
from array import *

#>>>>>>>>>>>>>>>>>>>> main function begins <<<<<<<<<<<<<<<<<<<<


cmd = "cat  rpa_kpm.ini  | head -n 7 | tail -n 1 | awk '{print $1}'"
retval = os.popen( cmd ).read().rstrip('\r\n')
nfreq = int(retval)
print "nfreq:", nfreq


rpa_u = np.zeros((nfreq,1))
for i in range(nfreq): 
   cmd = "grep \">>> RPA energy for this frequency\" kpm.log."+str(i)
   retval = os.popen( cmd ).read().rstrip('\r\n')
   arr_tmp = retval.split()
   rpa_u[i] = float(arr_tmp[-1])



weight = np.zeros((nfreq,1))
freq   = np.zeros((nfreq,1))

print "get freq_weight ...\n"
# grep the freq_weight
cmdWeight = "grep freq_weight: kpm.log.0"
retstr = os.popen( cmdWeight ).read().rstrip('\r\n')
rs = retstr.split('\n')
#print('rs = ', rs)
for i in range(nfreq):
    line = rs[i]
    arr_tmp = line.split()
    weight[i] = float(arr_tmp[4])
    freq[i]   = float(arr_tmp[2])
    print "f: %10.6e        w: %10.6e        rpa_u: %10.6f   " % (freq[i],weight[i],rpa_u[i])



RPA = 0.0
for j in range(nfreq): 
    RPA = RPA + weight[j,0]*rpa_u[j,0]


print ""
print 'RPA energy: ',RPA,' Hartree'
print '            ',RPA*27.2114,' eV\n\n'
