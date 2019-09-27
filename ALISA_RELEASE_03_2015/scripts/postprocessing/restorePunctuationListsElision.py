#!/usr/bin/python
# -*- coding: utf-8 -*-

## Author: Adriana Stan - adriana.stan@com.utcluj.ro
## Project: Simple4All - May 2012 - www.simple4all.org 
## Edited January 2013


import os,sys
import string
from string import punctuation
from nltk.tokenize import wordpunct_tokenize

print punctuation
punctuation += "»".decode("utf-8")
punctuation += "«".decode("utf-8")
punctuation += "„".decode("utf-8")
punctuation += "”".decode("utf-8")
punctuation += "–".decode("utf-8") 
punctuation += "...".decode("utf-8") 
punctuation += "¿".decode("utf-8") 
punctuation += "¡".decode("utf-8")  
punctuation += "—".decode("utf-8")  
punctuation += "„".decode("utf-8")  



def contains(listOne, listTwo):
# returns the index of a list in another list

    for i in xrange(1+len(listTwo) - len(listOne)):
        if listOne == listTwo[i:i+len(listOne)]:
            return i, i+len(listOne)
    return False


def main(inDir, origTextFile, elisionNo, outDir):
# restores the punctuation in the speech transcript
    
    
    if elisionNo == 0:
        elision = '\''
    else:
        elision = '-'
    print ('STARTING PUNCTUATION RESTORATION!!')
    fOrig = open (origTextFile)
    #fout = open (outFile, 'w')
    listWithPct= []
    listStrip = []
    origText = fOrig.read().decode("utf-8").strip().replace('\n',' ').replace('  ', ' ')
    fOrig.close()
    aux = ''
    for word in origText.split():
        token = wordpunct_tokenize(word)

        if word in punctuation:
            aux = word
        else:
                if aux in punctuation:
                    if len(token)>2 and token[0] not in punctuation:
                        print token
                        outWord = aux+token[0]+token[1]
                        listWithPct.append(outWord)
                        wordStrip = outWord.lower().strip(punctuation)
                        listStrip.append(wordStrip)
                        print outWord.encode("utf-8"), '----', wordStrip.encode("utf-8")
                        outWord = token[2]
                        listWithPct.append(outWord)
                        wordStrip = outWord.lower().strip(punctuation)
                        listStrip.append(wordStrip)

                    else:
                        outWord = word
                        listWithPct.append(outWord)
                        wordStrip = outWord.lower().strip(punctuation)
                        listStrip.append(wordStrip)

                else:
                    if len(token)>2 and token[0] not in punctuation:
                        print token
                        outWord = token[0]+token[1]
                        listWithPct.append(outWord)
                        wordStrip = outWord.lower().strip(punctuation)
                        listStrip.append(wordStrip)
                        outWord = token[2]
                        listWithPct.append(outWord)
                        wordStrip = outWord.lower().strip(punctuation)
                        listStrip.append(wordStrip)

                    else:
                        outWord = word
                        listWithPct.append(outWord)
                        wordStrip = outWord.lower().strip(punctuation)
                        listStrip.append(wordStrip)
                print outWord.encode("utf-8"), '----', wordStrip.encode("utf-8")                 

                aux = word

    files = os.listdir(inDir)
    files.sort()
    i = count = 0
    unfound = []
    for fileN in files:
        if fileN.endswith(".txt"):
            #print fileN
            fin = open(inDir+'/'+fileN)
            text = fin.read()
            fin.close()
            textR = text.replace('.', '').decode("utf-8").strip()
            #print text.encode("utf-8")
            text = textR.split()
            index = contains(text, listStrip)
            if not index:
                fout = open(outDir+'/'+fileN ,'w')
                fout.write(textR.encode('utf-8'))
                fout.close()
                unfound.append(fileN)
                count +=1
            else:
                fout = open(outDir+'/'+fileN ,'w')
                fout.write(' '.join(listWithPct[index[0] : index[1]]).encode('utf-8').replace(elision+' ', elision))
                fout.close()
                #print ' '.join(listWithPct[index[0] : index[1]]).replace(elision+' ', elision)
           
    if unfound:
        print ("COULD NOT RESTORE PUNCTUATION FOR THE FOLLOWING %d UTTERANCES:\n" %count)
        for utt in unfound:
            print utt.encode("utf-8")
    
    print ('ALL DONE OK!')



if __name__ == '__main__':
    if len(sys.argv) == 5: 
        main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print "Usage: python restorePunctuation inDir origText elisionMark outDir"
