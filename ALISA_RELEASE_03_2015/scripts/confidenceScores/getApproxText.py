# -*- coding: utf-8 -*-

#################################################
## Author: Adriana STAN adriana.stan@com.utcluj.ro
## Project Simple4All - www.simple4all.org
## May 2012
#################################################

import sys
import wave
import os, os.path

def main(wavList, textFiles, Nwin, outFile):
    """Outputs the estimated word rate from training data
    """#wavFiles must be named as the corresponding text header in speech transcription file
    print ("==========================================")
    print ("CREATING APPROXIMATE TEXT TRANSCRIPTIONS")
    N = int(Nwin)
    fin = open(textFiles, 'r')
    fout = open (outFile, 'w')
    text = ''
    duration = 0
    j = 0

    # get a list of in words to generate approximate sentences:
    for line in fin.readlines():
        text = text + line.replace("\n", '').replace(".", ' ')
    text = text.split()
    fwavs = open(wavList, 'r')
    duration = 0
#    get the duration of wav files to estimate the word duration
    for wavFile in fwavs.readlines():
        wavFile = wavFile.replace('\n', '')
        wav = wave.open(wavFile)
        duration = duration+(1.0 * wav.getnframes ()) / wav.getframerate ()
    
    avgDuration = duration/len(text)
    print ('AVERAGE WORD DURATION: %f' %avgDuration)

#    get the approximate text
    duration = 0
    fwavs = open(wavList, 'r')
#    dirs = sorted([d for d in os.listdir(wavDir) if os.path.isdir(wavDir + os.path.sep + d)]) # files need to be alphabetically ordered
#       dirs.extend(sorted([f for f in os.listdir(wavDir) if os.path.isfile(wavDir + os.path.sep + f)]))
    for wavFile in fwavs.readlines():
        utt = ''
        wavFile = wavFile.replace('\n', '')
        wav = wave.open(wavFile)
#        wav = wave.open(wavDir+wavFile)
        sentStart = int(round(duration/float(avgDuration)))
        duration = duration+(1.0 * wav.getnframes ()) / wav.getframerate ()
        sentEnd = int(round(duration/float(avgDuration)))
        wav.close()
        
        if sentEnd > len(text):
            sentEnd = len(text)
        if sentStart > len(text):
            print "\n!!![ERROR] -- Word duration might be too low. Please adjust and try again!!\n"
            sys.exit(0)
        if sentStart-N < 0:
            sentStart = N
        if sentEnd+N >len(text):
            sentEnd = len(text)-N
        utt = ' '.join(text[sentStart-N:sentEnd+N])
            #for i in range(sentStart-N, sentEnd+N):
            #utt = utt + ' '+text[i]

        marker = wavFile[wavFile.rfind('/')+1:]
        fout.write ('(%s \"%s\")\n' %(marker[0:-4],utt))
        j +=1
    if sentEnd+N < len(text):
        print ("I ONLY USED: %d WORDS OUT OF %d!! ADJUST WORD LENGTH!!!" %(sentEnd,len(text)))
        print ("I WOULD SUGGEST AN AVERAGE WORD LENGTH OF %f!! " %(duration/len(text)))
        sys.exit(0)
    print ("WROTE %d UTTERANCES!!!" %j)
    print ("USED %d WORDS!!!" %len(text))
    
    print ("=============================")
    print ("DONE!")
    print ("=============================")        

    fin.close()
    fout.close()


if __name__ == '__main__':
    if len(sys.argv) == 5: 
        main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print "Usage: python getApproxText.py  wavList textFiles Nwin outFile "
