#!/usr/bin/python


###################################################################
#
#  How to use? 
#  get_ERPAs_v3  <root_dir_of_system>  <nRuns>   <nMoments>
#
###################################################################

import re
import sys
import os
import numpy as np
from subprocess import call
from array import *




def kernelJackson(n, nMoment):
    pi = np.pi;
    # Following Table I, in "The kernel polynomial method" vol 78, pp 275 
    # Review of Modern Physics (2006)
    g = 1.0/(nMoment+1)*( (nMoment-n+1)*np.cos(n*pi/(nMoment+1))    \
         + np.sin(n*pi/(nMoment+1))*(1.0/(np.tan(pi/(nMoment+1)))))
    return g





#>>>>>>>>>>>>>>>>>>>> main function begins <<<<<<<<<<<<<<<<<<<<



root_dir =  sys.argv[1]       # number of runs 
nRun     = int(sys.argv[2])   # number of runs 
nMoment  = int(sys.argv[3])   # number of moments to consider 


# get number of freq 
cmd = "cat  "+root_dir+"_1/rpa_kpm.ini  | head -n 5 | tail -n 1 | awk '{print $1}'"
retval = os.popen( cmd ).read().rstrip('\r\n')
nfreq = int(retval)


# echo inputs 
print '\nnumber of freq is:   ',nfreq
print   'root dir of system:  ',root_dir
print   'number of runs is:   ',nRun
print   'number of moments:   ',nMoment,' [ mu_0, ...,  mu_'+str(nMoment-1)+" ]"
raw_input("\nAll above are correct? \n\nPress Enter to continue...")



weight  = np.zeros(nfreq)
freq    = np.zeros(nfreq)
C_coeff = np.zeros((nfreq, nMoment))
gn      = np.zeros(nMoment)   # Kernel Jackson



#***********************************
# get freq_weight  
#***********************************

print "\n\nget freq_weight ...\n"
# grep the freq_weight
cmdWeight = "grep freq_weight: "+root_dir+"_"+str(1)+"/kpm.log.0"
retstr = os.popen( cmdWeight ).read().rstrip('\r\n')
rs = retstr.split('\n')
#print('rs = ', rs)
for i in range(nfreq):
    line = rs[i]
    arr_tmp = line.split()
    weight[i] = float(arr_tmp[4])
    freq[i]   = float(arr_tmp[2])
    print "f: %f   w: %f" % (freq[i],weight[i])

print ""



#***************************
# get C coefficients 
#***************************
print "\nget C coefficients\n"
for i in range(nfreq):
    # system 1
    cmdFreq1 = "grep \"c coeff:\"  system1_kpm_1/kpm.log."+str(i)
    retstrF1 = os.popen( cmdFreq1 ).read().rstrip('\r\n')
    rsF1 = retstrF1.split('\n')
    #print('rsF1 = ', rsF1)

    for j in range(nMoment):
        #C_coeff[i][j] = float(rsF1)
        line = rsF1[j]
        arr_tmp = line.split()
        C_coeff[i][j] = float(arr_tmp[3])
        #print 'Coeff = ', float(arr_tmp[3])



#***********************************
# compute kernel 
#***********************************
print "\nComputing Jackson kernel ......"
print "g kernels: "
# Jackson Kernel
for i in range(nMoment):
    gn[i] = kernelJackson(i, nMoment)
    print "g[%3d]: %12.6f" % (i,gn[i])



#***********************************************
# get number of random vectors for each run
#***********************************************
print  "\n\nGet # of sampling done by each run..."
minRandomVec = np.zeros(nRun)

for r in range(nRun):
    tmpRandomVec1 = np.zeros((nfreq, 1))
    tmpRandomVec2 = np.zeros((nfreq, 1))

    for i in range(nfreq):
        # grep the random vector from the system1_kpm
        cmd1 = "grep \"random vector \" "+root_dir+"_"+str(r+1)+"/kpm.log."+str(i)
        retstr1 = os.popen( cmd1 ).read().rstrip('\r\n')
        rs1 = retstr1.split()
        rsLeng1 = len(rs1)
        tmpRandomVec1[i] = int(rs1[rsLeng1-1])

    minRandomVec[r] = int(min(tmpRandomVec1))-1
    print '[Run ID:',r+1,']  min number of random vectors: ', int(minRandomVec[r])

totRandomVec = int(sum(minRandomVec))
print '\nTotal number of random vectors: ',totRandomVec




#************************
# grep moments
#************************

print "\n\nGet all moment sampling from all runs ..."

mo = np.zeros((nfreq,nMoment,totRandomVec))

for i in range(nfreq):

    print "doing freq: ",i
    for m in range(nMoment):
        shift = 0
         
        # loop over all sampling (runs)
        for r in range(nRun):
            nRV = int(minRandomVec[r]);

            # get the sampling for this moment 
            key = "moment #  {:4d}:".format(m) 
            cmd1 = "grep '"+key+"'   "+root_dir+"_"+str(r+1)+"/kpm.log."+str(i)+" | awk '{print $8}'"
            #print cmd
            retval1 = os.popen(cmd1).read().rstrip('\r\n')
            sp1 = retval1.split('\n')
            #print retval

            # assign it to the mo array 
            for q in range(nRV): 
                mo[i][m][q+shift] = float(sp1[q])
                
                # check the length of mo1 and m2
                if r==nRun-1 and q==nRV-1: 
                   if q+shift != totRandomVec-1: 
                      print "q:",q," shift:",shift," nRV: ",nRV," totRandomVec:",totRandomVec
                      print "random vectors do not fit the mo1 and mo2 arrays"
                      stop

            shift = shift + nRV;



#**************************************
# assemble the RPA energy w/ c and g
#**************************************
# Output format is 
#
# (# of number rand vector)     E1  
#   1                          xxx  
#   2                          xxx  
#   3                          xxx  
#   4                          xxx  

# E_RPA (final results)
rpaE   = np.zeros(totRandomVec)
rpaE_f = np.zeros(nfreq)


print "\ncomputing E_RPA for different number of random vectors ......\n"

# loop over all sampling  
for nRV in range(totRandomVec): 
##for nRV in range(totRandomVec-1,totRandomVec): 

    if nRV%10==0: 
       print "doing nRV: ",nRV,' ...'

    eRPA = 0.0

    for i in range(nfreq):
        eRPA_f = 0.0;

        for m in range(nMoment): 
            # compute moments by taking averages over nRV samplings 
            #
            # Note: It is tricky with python with the definition of a[start:end]
            #
            #           a[start:end] 
            #
            #   Above scans items start through end-1
            #   the key point to remember is that the :end value represents 
            #   the first value that is not in the selected slice

            mu_avg = sum(mo[i][m][0:nRV+1])/(nRV+1);
            #print "m:",m,"  mu1_avg: ",mu1_avg,"  gn:",gn[m],"  c:",C_coeff[i][m]
            
            if m==0: 
               eRPA_f = eRPA_f + mu_avg*gn[m]*C_coeff[i][m]/2.0/np.pi
            else:
               eRPA_f = eRPA_f + 2.0*mu_avg*gn[m]*C_coeff[i][m]/2.0/np.pi

        
        # compute ERP(u) for largest number of random vectors 
        if nRV == totRandomVec-1: 
           rpaE_f[i] = eRPA_f

        eRPA = eRPA + weight[i]*eRPA_f
        ###break     # break the freq
    
    rpaE[nRV] = eRPA




#****************************************************
# outputs 
#****************************************************

print " nRV          RPA energy "
print "----------------------------------------------"
for j in range(totRandomVec): 
     print "%4d  %12.5f " % (j, rpaE[j])


print "\n\n\n>>> Computing RPA energy versus freq <<< "
print "RPA energy is calculated with moments: mu_0, mu_1, ..., mu_"+str(nMoment-1)
print "with "+str(totRandomVec)+" random vectors\n"
print "  index         u            E_RPA(u) "
print "---------------------------------------------------------------------"
for i in range(nfreq): 
     print "%4d    %12.5f    %12.5f   " % (i,freq[i],rpaE_f[i])
print "---------------------------------------------------------------------"
print "Integrated over freq:   %12.5f   (Ha)" % (np.dot(rpaE_f,weight))


