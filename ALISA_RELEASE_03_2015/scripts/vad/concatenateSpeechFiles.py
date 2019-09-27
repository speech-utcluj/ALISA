#!/usr/bin/python
# -*- coding: utf-8 -*-

#################################################
## Author: Adriana STAN adriana.stan@com.utcluj.ro
## Project Simple4All - www.simple4all.org
## January 2013
#################################################


import os
import sys
import wave

def main(inWavDir, minLength, outWavDir):
    print ('----------------------------------------------------------------')
    print ('STARTING TO CONCATENATE SHORT SPEECH FILES')
    print ('----------------------------------------------------------------')
    # read the speech segmentated files
    
    wavs = {}
    wavList = []
    files = os.listdir(inWavDir)
    files.sort()
    time = 0
    maxL = nextmaxL = 0
    maxLwav = nextmaxLwav =''
    for inFile in files:
        
        f1 = wave.open(inWavDir+'/'+inFile)
        time = (1.0 * f1.getnframes())/ f1.getframerate()
        if time > maxL:
            nextmaxL = maxL
            nextmaxLwav = maxLwav        
            maxL = time
            maxLwav = inFile

        wavs[inFile] = float(time)
        wavList.append(inFile)
        f1.close()
    i = 0    
    jTot = 0
    while i < len(wavList):

        if wavs[wavList[i]] > float(minLength):
            print ('Not concatenating %s , time %.2f' %(wavList[i], wavs[wavList[i]]))
            cmd = 'cp ' + inWavDir +'/'+wavList[i]+' '+outWavDir+'/'+wavList[i]
            os.system(cmd)
        else:
            newLength = wavs[wavList[i]]    
            j = 1
            print 'START FROM: %s - %.2f' %(wavList[i], wavs[wavList[i]])
            cmd = 'sox '+inWavDir+'/'+wavList[i]+' '
            while newLength < float(minLength) and ((i+j) < len(wavList)) and wavList[i][:-10] == wavList[i+j][:-10]:
                newLength = newLength + wavs[wavList[i+j]]
                print 'Adding %s %.2f  INT-TOT: %.2f' %(wavList[i+j], wavs[wavList[i+j]], newLength)                
                cmd = cmd +inWavDir+'/'+wavList[i+j]+' '
                j +=1
            print 'TOTAL: %.2f' %newLength
            cmd = cmd + outWavDir+'/'+wavList[i]
            print cmd
            os.system(cmd)
            i += j -1
            jTot += j-1
        i+=1
        
        print '---'
    print jTot
    
    print ('The maximum length of the files is: %.2f for %s' %(maxL, maxLwav))
    print ('The second maximum length of the files is: %.2f for %s' %(nextmaxL, nextmaxLwav))
    print ('\nALL DONE OK!!')

if __name__ == '__main__':	
    if len(sys.argv) == 4: 
        main(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print "Usage: python concatenateSpeechFiles.py <inWavDir> <minLength> <outWavDir>"

