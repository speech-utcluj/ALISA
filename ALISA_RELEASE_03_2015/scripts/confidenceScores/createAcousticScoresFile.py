#!/usr/bin/python
# -*- coding: utf-8 -*-

#################################################
## Author: Adriana STAN adriana.stan@com.utcluj.ro
## Project Simple4All - www.simple4all.org
## January 2013
#################################################


import sys


def main(SKIP1File, SKIP3File, outFile):

    f1 = open(SKIP1File)
    print SKIP1File, SKIP3File
    f2 = open(SKIP3File)
    skip1={}
    skip3={}
    for line in f1.readlines():
        skip1[line.split()[0]]=line.strip().split()[1:]
    f1.close()
    
    for line2 in f2.readlines():
        skip3[line2.split()[0]]=line2.strip().split()[1:]
    f2.close()
    
    fout = open(outFile, 'w')
    
    for key in sorted(skip1.iterkeys()):

        
        if key in skip3.iterkeys():
            fout.write('%s %s %s\n' %(key, '\t'.join(skip1[key]), '\t'.join(skip3[key])))

if __name__ == '__main__':    
    if len(sys.argv) == 4: 
        main(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print "Usage: python createAcousticScoresFile.py <SKIP1file> <SKIP3file> <outFile>"
