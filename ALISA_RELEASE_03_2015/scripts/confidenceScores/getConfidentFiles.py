# -*- coding: utf-8 -*-

#################################################
## Author: Adriana STAN adriana.stan@com.utcluj.ro
## Project Simple4All - www.simple4all.org
## January 2013
#################################################

import sys,math
import os

def main(acousticScoresFile, mlfFile, outFile):
    
    old = []
    guessed = []
    noWords = {}
    lab = 'a'
    no = 0
    acScoresPerWord = {}
    acScoresPerWordFull = {}
    acScores = []
    acScores2 = []
    ## Read the number of words from each label to check if the utterance is not too short
    fl = open (mlfFile)
    for line in fl.readlines():

        if line[0] == "\"":
            noWords[lab] = no-1 #because of the point at the end
            acScoresPerWord[lab] = acScores
            acScoresPerWordFull[lab] = acScores2
            acScores = []
            acScores2 = []
            lab = line.strip().replace('"','')
            lab = os.path.basename(lab)
            lab = lab.replace('.rec', '')
            no = 0

        else:
            no += 1
            if line[0] != '.' and line[0]!='#'  :
                lineDecode = line.split()[0].decode('string-escape').decode('utf-8')
                if len(lineDecode) <=3:
                    acScores.append(float(line.split()[1].strip('\n'))/9/len(lineDecode))
                    acScores2.append(float(line.split()[1].strip('\n')))
                else:
                    acScores.append(float(line.split()[1].strip('\n'))/3/len(lineDecode))
                    acScores2.append(float(line.split()[1].strip('\n')))
            
    noWords[lab] = no-1
    acScoresPerWord[lab] = acScores
    acScoresPerWordFull[lab] = acScores2


    ## Get the old utterances for final results
#    fC = open (oldFiles)
#    for line1 in fC.readlines():
#        old.append(line1.strip())
#    fC.close()

    ## Read the acoustic scores file for confidence measures
    fA = open (acousticScoresFile)
    for line1 in fA.readlines():
        line = line1.strip().split()
        fA.close()
        
        ## An utterance is correctly recognised if the acoustic scores for all skip 
        ## models is the same and also in a descending order from HVite with word networks 
        ## to background models with forced alignment        
        bol = 1
        if (math.ceil(float(line[1])) == math.ceil(float(line[5]))) and (math.ceil(float(line[2])) == math.ceil(float(line[6]))) :
            if (float(line[1])>=float(line[2]))  and ((float(line[2])>=float(line[3]))) :
                if (noWords[line[0].replace('.mfcc', '')] >= 8):
                    # Check for audio insertions, if average acoustic score per word 
                    # is greater than 8 times the average acoustic score per utterance
                    # then there might be an audio insertion <=> text deletion
                    for score in acScoresPerWordFull[line[0].replace('.mfcc', '')]:
                        if score < -10000:
                            bol = 0
                            print ('%s - Ac score < -10000 ' %line[0])
                            break

                    for score in acScoresPerWord[line[0].replace('.mfcc', '')][1:-2]:
                        if score/float(line[1]) > 8:
                            bol = 0
                            print ('%s - Avg ac score > 8' %line[0])
                            break
#                    print acScoresPerWord[line[0].replace('.mfcc', '')][-1]
#                    print acScoresPerWordFull[line[0].replace('.mfcc', '')][-1]
                                                
                    if bol and (acScoresPerWordFull[line[0].replace('.mfcc', '')][0]<-10000 or acScoresPerWordFull[line[0].replace('.mfcc', '')][-1]<-10000):
                            bol = 0
                            print ('%s - SENT_END or SENT_START acoustic score < -10000' %line[0])         
                        
                    if bol:
                        guessed.append(line[0].replace('.mfcc', ''))
                        print ('%s - OK' %line[0])
                                    
                else:
                    print ('%s - Less than 5 words' %line[0])
                    
                                            
            else:
                print ('%s - Non descending acoustic scores' %line[0])                        
        else:
               print ('%s - Non-identical acoustic scores' %line[0])

    ## Print out the correct utterances which were not guessed using the confidence measure
#    print ("CORRECT BUT NOT GUESSED")
#    j = 0
#    for co in corr:
#        if co not in guess:
#            print co, noWords[co]
#            j = j+1

#    print ("============================================================")
#    print ("THERE ARE %d CORRECT UTTERANCES OF WHICH I GUESSED %d" %(len(corr), len(corr)-j))
#    print ("============================================================")

    fO = open (outFile, 'w')
    ## Print out the guessed utterances which were not correctly recognised    
    #print ("NEWLY GUESSED:")
    j = 0
    for co in guessed:
        #print co
#        if co not in old:
            #print co, noWords[co]
            j = j+1
            fO.write("%s\n" %co)

    print ("----------------------------------------")
    print ("I GUESSED: %d UTTERANCES IN THIS STAGE" %(len(guessed)))
    print ("----------------------------------------")
    

    fO.close()

if __name__ == '__main__':
    if len(sys.argv) == 4: 
        main(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print "Usage: python getConfidentFiles.py acousticScoresFile,  mlfFile, outFile"
