#!/usr/bin/python
# -*- coding: utf-8 -*-

#################################################
## Author: Adriana STAN adriana.stan@com.utcluj.ro
## Project Simple4All - www.simple4all.org
## January 2013
#################################################


import os
import sys

def main(transcripts, sentenceSegm, inWavDir, outWavDir, outTsc):
    print ('----------------------------------------------------------------')
    print ('STARTING TO CONCATENATE UTTERANCES WHICH FORM COMPLETE SENTENCES')
    print ('----------------------------------------------------------------')
    # read the sentence segmentation file
    sentences = []
    fSeg = open(sentenceSegm)
    concat = []
    for line in fSeg.readlines():
        sentences.append(line.strip('.\n').decode("utf-8"))
    fSeg.close()
    indexedTSC = {}
    transcript = []
    ft = open(transcripts)
    tot = 0
    for line in ft.readlines():
        lab = line[line.find('(')+1: line.find(' ')].decode("utf-8")
        line = line.replace(' .', '').strip().decode("utf-8")
        text = line[line.find("\"")+1:-3].strip()
        indexedTSC[tot] = lab
        transcript.append(text)
        tot += 1
    ft.close()
    ###########################################################              
    #count the number of utterances that are actual sentences
    unu = 0
    for i in range(len(transcript)):
        if transcript[i] in sentences:
            unu += 1
            
    ###########################################################            
    #check if two consecutive utterances combined are a sentence 
    print ('Checking for 2 consecutive utterances...')      
    doi = trei= 0
    newTranscript = []
    newIndex = {}
    i = j = 0
    while i < len(transcript)-1:
       
        if transcript[i]+' '+transcript[i+1] in sentences:
         #   print ('--- %s + %s' %(indexedTSC[i], indexedTSC[i+1]))
            concat.append(indexedTSC[i])
            concat.append(indexedTSC[i+1])

            newTranscript.append(transcript[i]+' '+transcript[i+1])
            newIndex[j] = indexedTSC[i]
            cmd = 'sox ' + inWavDir + '/'+indexedTSC[i]+'.wav ' +inWavDir + '/'+indexedTSC[i+1]+'.wav '+outWavDir+'/'  +indexedTSC[i]+ '.wav'
            print cmd
            os.system(cmd)
            doi += 1
            i += 1
        else:
            newTranscript.append(transcript[i])
            newIndex[j] = indexedTSC[i]
            
        i+=1    
        j +=1
        
    #add the last utterance    
    newTranscript.append(transcript[i])
    newIndex[j] = indexedTSC[i]
    
    ###########################################################
    #redo the above to get results for 3 consecutive utterances
    print ('Checking for 3 consecutive utterances...')    
    indexedTSC = {}
    transcript = []
    transcript = newTranscript
    indexedTSC = newIndex
    newTranscript = []
    newIndex = {}
    i = j = 0
    while i < len(transcript)-2:
        if transcript[i]+' '+transcript[i+1]+ ' '+transcript[i+2] in sentences:
        #    print transcript[i]+' / '+transcript[i+1] + ' / '+transcript[i+2]
        #    print ('--- %s + %s + %s' %(indexedTSC[i], indexedTSC[i+1], indexedTSC[i+2]))
            newTranscript.append(transcript[i]+' '+transcript[i+1]+' '+transcript[i+2])
            newIndex[j] = indexedTSC[i]
            cmd = 'sox ' + inWavDir + '/'+indexedTSC[i]+'.wav ' +inWavDir + '/'+indexedTSC[i+1]+'.wav '+inWavDir + '/'+indexedTSC[i+2]+'.wav '+outWavDir+'/'  +indexedTSC[i]+ '.wav'
            os.system(cmd)            
            trei += 1
            i += 1
        else:
            newTranscript.append(transcript[i])
            newIndex[j] = indexedTSC[i]
            if indexedTSC[i] not in concat:
                cmd = 'cp '+inWavDir+'/'+indexedTSC[i]+'.wav '+outWavDir+'/'+indexedTSC[i]+'.wav'
                os.system(cmd)
        i+=1    
        j+=1
        
    #add the last utterances
    newTranscript.append(transcript[i])
    newIndex[j] = indexedTSC[i]
    if indexedTSC[i] not in concat:
        cmd = 'cp '+inWavDir+'/'+indexedTSC[i]+'.wav '+outWavDir+'/'+indexedTSC[i]+'.wav'
        os.system(cmd)
    newTranscript.append(transcript[i+1])
    newIndex[j+1] = indexedTSC[i+1]    
    if indexedTSC[i+1] not in concat:
        cmd = 'cp '+inWavDir+'/'+indexedTSC[i+1]+'.wav '+outWavDir+'/'+indexedTSC[i+1]+'.wav'
        os.system(cmd)
    
    #write new transcript to file:
    fout = open(outTsc, 'w')        
    for i in range(len(newIndex)):
        fout.write ('(%s \"%s.")\n' %(newIndex[i].encode('utf-8'), newTranscript[i].encode("utf-8")))
    fout.close()     
         
    #print stats:
    print ('-------------------------------------------------') 
    print ('Total number of utts in the beginning: \t\t%d' %tot)           
    print ('No of utts already sentences: \t\t\t%d ' %unu)
    print ('No. of 2 consecutive utts which are sentences:\t %d' %doi)
    print ('No. of 3 consecutive utts which are sentences:\t %d' %trei)
    print ('Total number of utts after concatenation: \t%d' %(i+1))
    print ('\nALL DONE OK!!')

if __name__ == '__main__':    
    if len(sys.argv) == 6: 
        main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    else:
        print "Usage: python concatenateUtterances.py <transcripts> <sentenceSegm> <inWavDir> <outWavDir> <outTsc>"

