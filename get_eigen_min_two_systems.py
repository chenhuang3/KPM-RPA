#!/usr/bin/python


import re
import sys
import os
from subprocess import call
from array import *

j = 0;
dir1 = 'system1_emin'; #sys.argv[2];
dir2 = 'system2_emin'; #ys.argv[3];

# get number of freq 
cmd = "cat  system1_emin/rpa_kpm.ini  | head -n 7 | tail -n 1 | awk '{print $1}'"
retval = os.popen( cmd ).read().rstrip('\r\n')
nfreq = int(retval)


print "folder of system1: ",dir1
print "folder of system2: ",dir2
print "nfreq: ",nfreq


#print "system 1: ",dir1
#print "system 2: ",dir2,'\n'

emin = []


print '\n==> freq and freq_weight <==\n'
cmd = "grep freq_weight: "+dir1+"/kpm.log.0"
retstr1 = os.popen( cmd ).read().rstrip('\r\n')
print retstr1


# check the outputs from both system 1 and system 2, they shoudl be the same 
cmd = "grep freq_weight: "+dir1+"/kpm.log.0"
retstr2 = os.popen( cmd ).read().rstrip('\r\n')
if (retstr1 <> retstr2): 
    print "freq and freq_weight of systems 1 and 2 are different, check their rpa_kpm.ini files"
    stop
   


print '\n==> emin from system 1 and system 2 <==\n'
while j < nfreq :
    cmd = "grep kpm_emin "+dir1+"/kpm.log."+str(j)+" | grep =";
    retstr1 = os.popen( cmd ).read().rstrip('\r\n')
    rs = retstr1.split();
    value1 = float( rs[2] )

#    print('rs = ', rs)

    cmd = "grep kpm_emin "+dir2+"/kpm.log."+str(j)+" | grep =";
    retstr2 = os.popen( cmd ).read().rstrip('\r\n')
    rs = retstr2.split();
    value2 = float(rs[2])

    print 'freq_id: %2d     emin1= %18.12f   emin2= %18.12f' % (j,value1,value2)
    
    emin.append( min(value1,value2) )

    j = j+1;


# ===================================
print '\n>>> emin for ',nfreq,' frequencies <<<\n'

j=0;
while j<nfreq: 
    print "%18.12f" % emin[j]
    j = j+1





