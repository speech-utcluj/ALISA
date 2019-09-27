#!/usr/bin/python
# -*- coding: utf-8 -*-

#################################################
## Author: Adriana STAN adriana.stan@com.utcluj.ro
## Project Simple4All - www.simple4all.org
## January 2013
#################################################


## This script outputs the file segmentation and their 
## text transcript into a single file, and it also
## outputs a ch_wave type file


import os
import sys
import wave


def main(rawWavsDir, segmentedDir, txtWithPctDir, outDir):

    filesRaw = [x for x in os.listdir(rawWavsDir) if x.find('wav')>0]
    filesRaw.sort()
    addTime=0
    # get the available text files
    textFiles = os.listdir(txtWithPctDir)
    textFiles.sort()
    #open the output files
    
    fout = open(outDir+'_segmentationAndTextData.txt', 'w')
    fchWaveOut = open(outDir+'_segmentationAndTextData_ch_wave_format.keylab', 'w')
    fchWaveOut.write('separator ;\n#\n')
    
    
    for fileRaw in filesRaw:
        time = addTime
        label = fileRaw[:-4]
        f2 = wave.open(rawWavsDir+'/'+fileRaw)
        lengthRaw = (1.0 * f2.getnframes())/ f2.getframerate()
        # get the segmented files for the corresponding raw speech file
        filesSeg = [x for x in os.listdir(segmentedDir) if x.find(label) ==0]
        filesSeg.sort()
        for fileS in filesSeg:
              f1 = wave.open(segmentedDir+'/'+fileS)
              length = (1.0 * f1.getnframes())/ f1.getframerate()
              fout.write('%s %.2f %.2f ' %(fileS, time, time+length))
#              time += float(length)
            
              f1.close()

              if fileS[:-4]+'.txt' in textFiles:
                fText = open(txtWithPctDir+'/'+fileS[:-4]+'.txt')
                line = fText.read().strip()
                #print line
                fout.write('\"'+line+'\"\n')
                fchWaveOut.write('%.2f 121 "%s" ; file %s\n' %(time+length, line, fileS))
                fText.close
              else:
                fout.write('\n')
                fchWaveOut.write('%.2f 121  ; file %s\n' %(time+length, fileS))
                
              time += float(length)  
        if int(time)>int(lengthRaw):
                    print ' '
                    print 'NOT OK FOR ' + fileRaw, time, lengthRaw, time-lengthRaw, ' the total segmented time is longer than the raw file'
                    addTime = time-lengthRaw
        else:
                    addTime = 0

    fout.close()            
    fchWaveOut.close()
    print ('ALL DONE OK!')
            

if __name__ == '__main__':    
    if len(sys.argv) == 5: 
        main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print "Usage: python getTimesAndTextForFiles.py rawWavsDir, segmentedDir, txtWithPctDir, outFile"



## OLD STUFF
#   cmd = 'sox '+rawWavsDir+'/'+ fileRaw +' '+outDir+'/'+fileS+' trim '+str(time)+' '+ str(length)
#  os.system(cmd)

