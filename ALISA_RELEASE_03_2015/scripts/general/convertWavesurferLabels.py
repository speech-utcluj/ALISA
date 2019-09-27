#!/usr/bin/python
# -*- coding: utf-8 -*-

#################################################
## Author: Adriana STAN adriana.stan@com.utcluj.ro
## Project Simple4All - www.simple4all.org
## January 2013
#################################################


## This script converts wavesurfer labels into the format needed for GMM-VAD

import os
import sys


def main(inputFile, marker, outputFile):
        fIn = open(inputFile)
        fOut = open(outputFile, 'w')
        foundMark = 0
        err = 0
        print ('Starting to write the label...')
        firstLine = fIn.readline().strip().split()
        # I'm assuming the first line should always be a silence line 
        fOut.write('#\n%s sil' %(firstLine[1]))
        for line in fIn.readlines():
            if line.find(marker) > 0:
                foundMark = 1
                times = line.strip().split()
                fOut.write('\n%s\n%s sil' %(times[0], times[1]))
        if not foundMark:
            err = 1
            print ('[ERROR]:You suggested a wrong marker that you used in the file: \'%s\'. \n\tReconsider?!' %marker)
            
        fIn.close()
        fOut.close()
        if not err:
            print ('All done OK!!')




if __name__ == '__main__':    
    if len(sys.argv) == 4: 
        main(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print "Usage: python convertSilenceLabels <inputLabel> <marker> <outputLabel>"
