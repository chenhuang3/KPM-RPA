#!/usr/bin/python


#*****************************************
# How to use? 
#
# get_eigen_min <system_folder>
#
#*****************************************

import re
import sys
import os
from subprocess import call
from array import *


sys_dir = './'#raw_input("\nEnter the system folder in which we read the lowest eigenvalues ...\n")



# get number of freq 
cmd = "cat  "+sys_dir+"/rpa_kpm.ini  | head -n 7 | tail -n 1 | awk '{print $1}'"
retval = os.popen( cmd ).read().rstrip('\r\n')
nfreq = int(retval)

print "system to read: ",sys_dir

emin = []
j = 0;
while j < nfreq :
    cmd = "grep kpm_emin "+sys_dir+"/kpm.log."+str(j)+" | grep =";
    retstr1 = os.popen( cmd ).read().rstrip('\r\n')
    rs = retstr1.split();
    value1 = float( rs[2] )
    emin.append( value1  )
    j = j+1;




print '\nemin for ',nfreq,' frequencies\n'
j=0;
print "freq         emin "
while j<nfreq: 
    print "%4i   %16.8f" % (j,emin[j])
    j = j+1





