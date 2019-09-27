# -*- coding: utf-8 -*-

#################################################
## Author: Adriana STAN adriana.stan@com.utcluj.ro
## Project Simple4All - www.simple4all.org
## June 2012
#################################################

import sys

def main (speechTranscript, outFile):

    fS = open(speechTranscript)
    fOut = open(outFile, 'w')
    fOut.write("#!MLF!#\n")
    print ('Creating MLF file from the speech transcript!!')
    for line in fS:
        lab = line[line.find('(')+1: line.find(' ')]
        fOut.write('\"*/%s.lab\"\n' %lab)
        words = line[line.find('\"')+1: line.rfind('\"')]
        

        for word in words.split():
            #print word.strip('.')
            fOut.write('%s\n' %word.strip('.'))
        fOut.write('.\n')
    print ('DONE!')
    fS.close()
    fOut.close()

if __name__ == '__main__':
    if len(sys.argv) == 3: 
        main(sys.argv[1], sys.argv[2])
    else:
        print "Usage: python createMLFfromSpeechTranscript speechTsc, outFile"
