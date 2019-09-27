# -*- coding: utf-8 -*-

#################################################
## Author: Adriana STAN adriana.stan@com.utcluj.ro
## Project Simple4All - www.simple4all.org
## January 2013
#################################################

import sys

def main (speechTranscript, outDir):

    fS = open(speechTranscript)



    for line in fS:
        lab = line[line.find('(')+1: line.find(' ')]
        line = line.replace('!SENT_START ', '')
        line = line.replace(' !SENT_END ', '')
        fileName = outDir+'/'+lab+'.txt'
        fOut = open(fileName, 'w')
        fOut.write(line[line.find("\"")+1:-3]+'\n')        
        fOut.close()

    #print ('DONE!')
    fS.close()


if __name__ == '__main__':
    if len(sys.argv) == 3: 
        main(sys.argv[1], sys.argv[2])
    else:
        print "Usage: python createTxtFromSpeechTranscript speechTranscript, outDir"
