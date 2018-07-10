#!/usr/bin/python

import re
import sys
import os
import numpy as np
import readline
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

hartree2ev = 27.21138602;

nRun = int(raw_input("\nEnter the number of runs: \n"))
dir1 = raw_input("\nEnter the root name of directory #1: \n")
dir2 = raw_input("\nEnter the root name of directory #2: \n")

dir1 = dir1.strip()
dir2 = dir2.strip()

print "\nget other parameters from "+dir1+"_1/rpa_kpm.ini ..."

# get number of freq 
cmd = "cat  "+dir1+"_1/rpa_kpm.ini  | head -n 7 | tail -n 1 | awk '{print $1}'"
retval = os.popen( cmd ).read().rstrip('\r\n')
nfreq = int(retval)


cmd = "cat  "+dir1+"_1/rpa_kpm.ini  | head -n 3 | tail -n 1 | awk '{print $1}'"
retval = os.popen( cmd ).read().rstrip('\r\n')
nMoment = int(retval)

#nRun    = int(sys.argv[1])   # number of runs 
#nMoment = int(sys.argv[2])   # number of moments to consider 

# echo inputs 
print '\nnumber of freq:    ',nfreq
print   'number of runs:    ',nRun
print   'number of moments: ',nMoment,' [mu_0, ...,  mu_'+str(nMoment-1)+"]"
raw_input("\nAll above are correct? \n\nPress Enter to continue ...")


weight  = np.zeros(nfreq)
freq    = np.zeros(nfreq)
C_coeff = np.zeros((nfreq, nMoment))
gn      = np.zeros(nMoment)   # Kernel Jackson



#***********************************
# get freq_weight  
#***********************************

print "\n\nget freq_weight ...\n"
# grep the freq_weight
cmdWeight = "grep freq_weight: "+dir1+"_"+str(1)+"/kpm.log.0"
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
    cmdFreq1 = "grep \"c coeff:\"  "+dir1+"_1/kpm.log."+str(i)
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
print "kernels: "
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
        cmd1 = "grep \"random vector \" "+dir1+"_"+str(r+1)+"/kpm.log."+str(i)
        retstr1 = os.popen( cmd1 ).read().rstrip('\r\n')
        rs1 = retstr1.split()
        rsLeng1 = len(rs1)
        tmpRandomVec1[i] = int(rs1[rsLeng1-1])
        #print('Random Vector 1= ', tmpRandomVec1[i])

        # grep the random vector from the system2_kpm
        cmd2 = "grep \"random vector \" "+dir2+"_"+str(r+1)+"/kpm.log."+str(i)
        retstr2 = os.popen( cmd2 ).read().rstrip('\r\n')
        rs2 = retstr2.split()
        rsLeng2 = len(rs2)
        tmpRandomVec2[i] = int(rs2[rsLeng2-1])
        #print('Random Vector 2= ', tmpRandomVec2[i])

    #print('weight = ', weight)
    minRandomVec1 = int(min(tmpRandomVec1))-1
    #print 'min1 = ', minRandomVec1
    minRandomVec2 = int(min(tmpRandomVec2))-1
    #print 'min2 = ', minRandomVec2

    minRandomVec[r] = min(minRandomVec1, minRandomVec2)
    print 'run #',r+1,' =>  min number of random vectors: ', int(minRandomVec[r])


totRandomVec = int(sum(minRandomVec))
print '\nTotal number of random vector: ',totRandomVec



#************************
# grep moments
#************************

print "\n\nGet all moment sampling from all runs ..."

mo1 = np.zeros((nfreq,nMoment,totRandomVec))
mo2 = np.zeros((nfreq,nMoment,totRandomVec))

for i in range(nfreq):
    
    # show status 
    pt = float(i/float(nfreq-1)*100);
    print  "\rfinished %4.1f%%" % pt,
    sys.stdout.flush()

    for m in range(nMoment):
        shift = 0
         
        # loop over all sampling (runs)
        for r in range(nRun):
            nRV = int(minRandomVec[r]);

            # get the sampling for this moment 
            key = "moment #  {:4d}:".format(m) 
            cmd1 = "grep '"+key+"'   "+dir1+"_"+str(r+1)+"/kpm.log."+str(i)+" | awk '{print $8}'"
            cmd2 = "grep '"+key+"'   "+dir2+"_"+str(r+1)+"/kpm.log."+str(i)+" | awk '{print $8}'"
            #print cmd
            retval1 = os.popen(cmd1).read().rstrip('\r\n')
            retval2 = os.popen(cmd2).read().rstrip('\r\n')
            sp1 = retval1.split('\n')
            sp2 = retval2.split('\n')
            #print retval

            # assign it to the mo array 
            for q in range(nRV): 
                mo1[i][m][q+shift] = float(sp1[q])
                mo2[i][m][q+shift] = float(sp2[q])
                
                # check the length of mo1 and m2
                if r==nRun-1 and q==nRV-1: 
                    if q+shift != totRandomVec-1: 
                       print "q:",q," shift:",shift," nRV: ",nRV," totRandomVec:",totRandomVec
                       print "random vectors do not fit the mo1 and mo2 arrays"
                       stop

            shift = shift + nRV;



#**************************************
# Assemble the RPA energy w/ c and g
#**************************************

# Output format is 
#
# (# of number rand vector)     E1    E2     E1-E2
#   1                          xxx   xxx      xxx
#   2                          xxx   xxx      xxx
#   3                          xxx   xxx      xxx
#   4                          xxx   xxx      xxx

# E_RPA (final results)
rpaE1 = np.zeros(totRandomVec)
rpaE2 = np.zeros(totRandomVec)

rpaE1_f = np.zeros(nfreq)
rpaE2_f = np.zeros(nfreq)


print "\n\nComputing E_RPA for different number of random vectors. nRandVec: ",totRandomVec

# loop over all sampling  
for nRV in range(totRandomVec): 
##for nRV in range(totRandomVec-1,totRandomVec): 

    # show status 
    pt = float(nRV/float(totRandomVec-1)*100);
    print  "\rfinished %6.1f%%" % pt,
    sys.stdout.flush()


    eRPA1 = 0.0
    eRPA2 = 0.0

    for i in range(nfreq):
        eRPA1_f = 0.0;
        eRPA2_f = 0.0;

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

            mu1_avg = sum(mo1[i][m][0:nRV+1])/(nRV+1);
            mu2_avg = sum(mo2[i][m][0:nRV+1])/(nRV+1);
            #print "m:",m,"  mu1_avg: ",mu1_avg,"  gn:",gn[m],"  c:",C_coeff[i][m]
            
            if m==0: 
               eRPA1_f = eRPA1_f + mu1_avg*gn[m]*C_coeff[i][m]/2.0/np.pi
               eRPA2_f = eRPA2_f + mu2_avg*gn[m]*C_coeff[i][m]/2.0/np.pi
            else:
               eRPA1_f = eRPA1_f + 2.0*mu1_avg*gn[m]*C_coeff[i][m]/2.0/np.pi
               eRPA2_f = eRPA2_f + 2.0*mu2_avg*gn[m]*C_coeff[i][m]/2.0/np.pi

        
        # compute ERP(u) for largest number of random vectors 
        if nRV == totRandomVec-1: 
           rpaE1_f[i] = eRPA1_f
           rpaE2_f[i] = eRPA2_f

        eRPA1 = eRPA1 + weight[i]*eRPA1_f
        eRPA2 = eRPA2 + weight[i]*eRPA2_f
        ###break     # break the freq
    
    rpaE1[nRV] = eRPA1
    rpaE2[nRV] = eRPA2




#***************************************
#  compute RPA energy versus moments 
#***************************************

rpaE1_m = np.zeros(nMoment)  # RPA energy w.r.t. moments 
rpaE2_m = np.zeros(nMoment)  # RPA energy w.r.t. moments

mu1_avg = np.zeros((nfreq,nMoment))
mu2_avg = np.zeros((nfreq,nMoment))

nRV_moment = totRandomVec-1;    

# compute averaged moments for all freq
for i in range(nfreq): 
  for m in range(nMoment): 
     mu1_avg[i][m] = sum(mo1[i][m][0:nRV_moment+1])/(nRV_moment+1);
     mu2_avg[i][m] = sum(mo2[i][m][0:nRV_moment+1])/(nRV_moment+1);


for i in range(nfreq): 
   for mMax in range(1,nMoment+1): 
      eRPA1_f = 0.0
      eRPA2_f = 0.0
      for m in range(mMax): 
          g = kernelJackson(m, mMax);
          if m==0: 
            eRPA1_f = eRPA1_f + mu1_avg[i][m]*g*C_coeff[i][m]/2.0/np.pi
            eRPA2_f = eRPA2_f + mu2_avg[i][m]*g*C_coeff[i][m]/2.0/np.pi
          else:
            eRPA1_f = eRPA1_f + 2.0*mu1_avg[i][m]*g*C_coeff[i][m]/2.0/np.pi
            eRPA2_f = eRPA2_f + 2.0*mu2_avg[i][m]*g*C_coeff[i][m]/2.0/np.pi

      rpaE1_m[mMax-1] = weight[i]*eRPA1_f + rpaE1_m[mMax-1] 
      rpaE2_m[mMax-1] = weight[i]*eRPA2_f + rpaE2_m[mMax-1] 
        


#****************************************************
# outputs 
#****************************************************

print "\n\n"
print "********************************"
print "*           Output             *"
print "********************************\n"



file = open("ERPA_vs_random_vectors.txt",'w') 
print "\n\n\n>>> RPA energy vs number of random vectors (nMoment: ",nMoment,")\n"
ss = " nRV          E1           E2          E1-E2 (Ha)   E1-E2 (eV) "
file.write("# "+ss+"\n")
print ss
print "--------------------------------------------------------------"
for j in range(totRandomVec): 
   de = rpaE1[j]-rpaE2[j];
   ss = "%4d  %12.5f  %12.5f  %12.5f  %12.5f" \
        % (j, rpaE1[j], rpaE2[j], de, de*hartree2ev );
   print ss
   file.write(ss+"\n")






file = open("ERPA_vs_moments.txt",'w') 
ss = "#   nMoment        E_RPA1        E_RPA2      E_RPA1-E_RPA2 (Ha)     E_RPA1-E_RPA2 (eV) "
file.write(ss+"\n")
print "\n\n\n>>> RPA energy vs moments (with ",nRV_moment," random vectors) <<<\n"
print "  nMoment        E_RPA1        E_RPA2      E_RPA1-E_RPA2 (Ha)     E_RPA1-E_RPA2 (eV)"
print "--------------------------------------------------------------------------------------"
for j in range(mMax): 
    de = rpaE1_m[j]-rpaE2_m[j]
    ss =  "%4d       %12.5f     %12.5f     %12.5f       %12.5f" %\
            (j, rpaE1_m[j], rpaE2_m[j], de, de*hartree2ev)
    print ss
    file.write(ss+"\n")






print "\n\n\n>>> RPA energy vs freq <<< \n"
print "RPA energy is calculated with moments: mu_0, mu_1, ..., mu_"+str(nMoment-1)," (with "+str(totRandomVec)+" random vectors)\n"
print "  index         u        E_RPA_1(u)      E_RPA_2(u)        delta_E_RPA(u)"
print "---------------------------------------------------------------------"
for i in range(nfreq): 
     print "%4d    %12.5f    %12.5f    %12.5f    %12.5f" %  \
        (i,freq[i],rpaE1_f[i],rpaE2_f[i],rpaE1_f[i]-rpaE2_f[i])
print "---------------------------------------------------------------------"
print "Integrated over freq:   %12.5f    %12.5f    %12.5f  (Ha)  %9.5f (eV)" % \
      (np.dot(rpaE1_f,weight),np.dot(rpaE2_f,weight), 
       np.dot(rpaE1_f-rpaE2_f,weight),
       np.dot(rpaE1_f-rpaE2_f,weight)*hartree2ev)


print "\n\n>>> Output files <<<"
print "\n ERPA_vs_random_vectors.txt   <= RPA energy versus number of random vectors"
print "\n ERPA_vs_moments.txt          <= RPA energy versus number of moments"


print ""
print ""
print ""





