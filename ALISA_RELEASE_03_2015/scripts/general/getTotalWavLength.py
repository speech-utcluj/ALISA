# -*- coding: utf-8 -*-

#################################################
## Author: Adriana STAN adriana.stan@com.utcluj.ro
## Project Simple4All - www.simple4all.org
## January 2013
#################################################


import sys,wave, os

def main(inWavDir, totWavDir):
    
    files = os.listdir(inWavDir)
    files.sort()
    time = 0
    for inFile in files:
        f1 = wave.open(inWavDir+'/'+inFile)
        time = time + (1.0 * f1.getnframes())/ f1.getframerate()
        f1.close()
    sec = time%60
    mins = time//60
    hrs = mins//60
    mins = mins%60
    print ('I MANAGED TO ALIGN:\t%dh:%dmin:%dsec' %(int(hrs), int(mins), int(sec)))
    
    files = os.listdir(totWavDir)
    files.sort()
    time = 0
    for inFile in files:
        f1 = wave.open(totWavDir+'/'+inFile)
        time = time + (1.0 * f1.getnframes())/ f1.getframerate()
        f1.close()
    sec = time%60
    mins = time//60
    hrs = mins//60
    mins = mins%60
    print ('OUT OF A TOTAL OF:\t%dh:%dmin:%dsec' %(int(hrs), int(mins), int(sec)))

if __name__ == '__main__':    
    if len(sys.argv) == 3: 
        main(sys.argv[1], sys.argv[2])
    else:
        print "Usage: python getTotalWavLength.py <alignedWavDir> <totalWavDir>"
