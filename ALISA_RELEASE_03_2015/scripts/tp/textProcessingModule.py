#!/usr/bin/python
# -*- coding: utf-8 -*-

#################################################
## Author: Adriana STAN adriana.stan@com.utcluj.ro
## Project Simple4All - www.simple4all.org
## May 2013
## Edited: January 2013
#################################################


## This module is used to process the text needed for 
## automatic segmentation and alignment of audiobooks
## It includes functions to segment the text into sentences, 
## to get the list of graphmes within the book,
## the hmmlist, to create an HTK compliant dictionary, and 
## some checking functions, such as notInDict,
## needed to check if all the words from the book are in the 
## dictionary, and also the characters. It also
## contains the functions to select the initial training data 
## and the one for finding the approximate text
## for the iterative retrain.

#The main function runs all the necessary steps in providing the required data for retraining.

import sys
import re
import os
import operator
from operator import itemgetter
import string


#TODO:add help to all functions and short descriptions

####################################
####################################

def prepareInitialTextData(inputTsc, wavDir, outFile):

    files = os.listdir(wavDir)
    files.sort()
    fin = open(inputTsc)
    fout = open(outFile, 'w')
    ind = 0
    for line in fin.readlines():
        line = line.decode('utf-8').lower().strip()
        pattern = re.compile(r'[^\w\s]', re.U) #pattern for unicode words
        newLine = re.sub(r'[_0-9]', ' ', re.sub(pattern, ' ', line)) 
        newLine = re.sub(' {1,}', ' ', newLine) #multiple succesive spaces
        newLine = re.sub('^ ', '', newLine) #spaces at beginning of lines
        fout.write('(%s "%s.")\n' %(files[ind][:-4], newLine.strip().encode("utf-8")))
        ind +=1
    fin.close()
    fout.close()
    
####################################
####################################


def punctuationAndLowercase (inFile, outFile):
#This function strips punctuation from an input file
    fin = open(inFile)
    fout = open(outFile, 'w')
    for line in fin.readlines():
        line = line.decode('utf-8').lower().strip()
        pattern = re.compile(r'[^\w\s]', re.U) #pattern for unicode words
#        pattern = re.compile(r'[^\w\s\']', re.U) #pattern for unicode words
        newLine = re.sub(r'[_0-9]', ' ', re.sub(pattern, ' ', line)) 
        newLine = re.sub(' {1,}', ' ', newLine) #multiple succesive spaces
        newLine = re.sub('^ ', '', newLine) #spaces at beginning of lines
        fout.write('%s.\n' %(newLine.strip().encode("utf-8")))
        
    fin.close()
    fout.close()
    
####################################
####################################    

def sentenceSplitNLTK (inFile, outFile):
#This function does a sentence split using NLTK.tokenizer
    import nltk.data
    print (">>> Tokenizing using NLTK... output: %s" %outFile)
    tokenizer = nltk.data.load('nltk:tokenizers/punkt/english.pickle')
    fin = open(inFile)
    fout = open(outFile, 'w')
    data = fin.read()
    data = data.decode("utf-8")
    fin.close()
    token = tokenizer.tokenize(data)
        
    for i in range(len(token)):
        fout.write('%s\n' %token[i].replace('\n', ' ').replace('  ', ' ').encode("utf-8"))
        
    fout.close()
    
####################################
####################################    

def sentenceSplitWithCommas (inFile, outFile):

#This function is used to split a raw text into sentences and write them into an output file line-by-line, 
#but retains the commas. It is the same as sentenceSplit, but used for speech transcript files. 

        fin = open(inFile, 'r')
        fout = open(outFile, 'w')
        print (">>> Writing to file: %s" %outFile)
        text = fin.read()
        text = text.decode("utf-8")
        text = re.sub('\n{2,}', '. ', text)   #if there are multiple newlines, assume that it's a full sentence. For titles for example.
        text = text.replace('\'', '')        #make Stan's a single word not Stan s
        text = text.replace('\n', ' ')        #if a sentence continues on a newline, remove the newline character.  
        text = text.replace('\t', ' ')        #replace tabs
        text = text.replace(u'\xa0',u' ')     #replace no-line breaks
        sentenceEnders = re.compile('[.!?;] |--|\(|\)') #assume sentences end with . ? or ! followed by a space. 
                                          #This keeps from splitting at www.aaa.org for example
        sentenceList = sentenceEnders.split(text)

        for sentence in sentenceList:
            
            pattern = re.compile(r'[^\w\s,]', re.U) #pattern for unicode words
            newLine = re.sub(r'[_0-9]', ' ', re.sub(pattern, ' ', sentence)) #clear out numbers and underscores
            newLine = re.sub(' {1,}', ' ', newLine) #multiple succesive spaces
            newLine = re.sub('^ ', '', newLine) #spaces at beginning of lines
            newLine = re.sub('^\.', '', newLine) #empty lines
            newLine = re.sub(' $', '', newLine)
            newLine = newLine.replace (' ,', ',')
            fout.write(newLine.lower().encode("utf-8"))
            if (newLine == '\n') or (newLine == ' ') or (newLine == ''):
                      continue
            else:
                   fout.write('.\n') 
        fin.close()
        fout.close()

####################################
####################################

def sentenceSplit (inFile, outFile):

#This function is used to split a raw text into sentences and write them in to an output file line-by-line.
#It makes some naive assumptions about the sentence endings, as books may contain some strange formatting.

        fin = open(inFile, 'r')
        fout = open(outFile, 'w')
        print (">>> Writing to file: %s" %outFile)
        text = fin.read()
        text = text.decode("utf-8")
        text = re.sub('\n{2,}', '. ', text)   #if there are multiple newlines, assume that it's a full sentence. For titles for example.
        text = text.replace('\'', '')        #make Stan's a single word not Stan s
        text = text.replace('\n', ' ')        #if a sentence continues on a newline, remove the newline character.  
        text = text.replace('\t', ' ')        #replace tabs
        text = text.replace(u'\xa0',u' ')     #replace no-line breaks
        sentenceEnders = re.compile('[.!?;] |--|\(|\)') #assume sentences end with . ? or ! followed by a space. 
                                          #This keeps from splitting at www.aaa.org for example
        sentenceList = sentenceEnders.split(text)

        for sentence in sentenceList:
            
            pattern = re.compile(r'[^\w\s]', re.U) #pattern for unicode words
            newLine = re.sub(r'[_0-9]', ' ', re.sub(pattern, ' ', sentence)) #clear out numbers and underscores
            newLine = re.sub(' {1,}', ' ', newLine) #multiple succesive spaces
            newLine = re.sub('^ ', '', newLine) #spaces at beginning of lines
            newLine = re.sub('^\.', '', newLine) #empty lines
            newLine = re.sub(' $', '', newLine)
            fout.write(newLine.lower().encode("utf-8"))
            if (newLine == '\n') or (newLine == ' ') or (newLine == ''):
                      continue
            else:
                   fout.write('.\n') 
        fin.close()
        fout.close()




###################################
###################################

def getGraphemesAndHMMList (inFile, graphFile, hmmFile):

#This script is used to find all distinct letters, as used by Oliver's scripts, in a text already processed by sentenceSplit.py. 
#The output is a (sort of) alphabetically  ordered list and requires the user's input for ASCII - friendly characters. 
#Any characters which are not in the alphabet of the language should be replaced by the ones that are. 
#For example, replace ă and â with a for English, but replace ă with ah and â with aq for Romanian.

    fin = open(inFile, 'r')
    fout = open(graphFile, 'w')
    fhmm = open(hmmFile, 'w')
    graphemes = []
    hmms = []
    text = fin.read()
    text = text.decode("utf-8")
    fin.close()
    for char in text:
        if char.isalnum():
            if char in graphemes:
                continue
            else:
                graphemes.append(char)
                
    graphemesSorted = sorted(graphemes)
        
    print("Add an ASCII friendly description for each grapheme or an alternate for diacritics:")    
    
    orde = 1                                        
    for graph in graphemesSorted:

        if graph not in string.ascii_letters:
        
            tsc = raw_input(">> \"%s\": >> " %graph.encode("utf-8"))   
            if orde == 0:
                fout.write(str("\n%s\t%s" % (graph.encode("utf-8"),tsc)))
            else:
                fout.write(str("%s\t%s" % (graph.encode("utf-8"),tsc)))
                orde = 0
            if tsc not in hmms:
                hmms.append(tsc)
        else:
            if orde == 0:
                fout.write(str("\n%s\t%s" % (graph.encode("utf-8"),graph.decode('ascii'))))
            else:    
                fout.write(str("%s\t%s" % (graph.encode("utf-8"),graph.decode('ascii'))))
                orde=0
            hmms.append(graph.decode('ascii'))
        
                    
    print (">>> Writing list of graphemes to file: %s" %graphFile)
    print (">>> Writing hmmlist to file: %s" %hmmFile)
    hmms.append('skip')
    hmms.append('sil')
    orde = 1
    for hmm in hmms:
        if orde == 0:
            fhmm.write("\n%s" %hmm)
        else:
            fhmm.write("%s" %hmm)
            orde = 0
    
    fout.write("\n")
    fout.close()
    fhmm.close()

####################################
####################################

def createBigrams(segmentedFile, outFile):

    fS = open (segmentedFile)
    fout = open (outFile, 'w')
    bigrams = {}
    text = ''
    print ("CREATING BIGRAMS")
    for line in fS.readlines():
        text = text + line.replace("\n", '').replace(".", ' ')
    fS.close()

    aux = 's'
    for word in text.split():
        if bigrams.has_key(aux):
            if word not in bigrams[aux]:
                bigrams[aux].append(word)
        else:
            bigrams[aux] =[]
            bigrams[aux].append(word)
        aux = word
    if bigrams.has_key(word):
        bigrams[aux].append('end')
    else:
        bigrams[word] =[]
        bigrams[word].append('end')


    #print bigrams
    bigram_sorted = sorted(bigrams.iterkeys())
    print ("DONE!")
    for word in bigram_sorted:
        for first in bigrams[word]:
            fout.write('%s %s\n' %(word, first))
        
    fout.close()

#######################################
#######################################

def replaceWithASCII(inFile, graphFile, outFile):
#This function replaces the nonASCII characters which are not standard for that language with their substitutes.
#For example, in English, replace ă and â with a. 
#It is based on the assumption that standard letters are replaced with two letters for the dictionary and hmmlist

    fin = open(inFile)
    fgraph = open (graphFile)
    graphemes = {}
    print (">>> Replacing non ASCII characters in file with the ones you suggested")
    print (">>> except for diacritics which are kept")
    for line in fgraph.readlines():
        zz = line.decode("utf-8").split()
        graphemes[zz[0].strip()]= zz[1].strip()

    fout = open(outFile, 'w')
    for line in fin.readlines():
        line = line.decode("utf-8")
        for graph in graphemes:

            if len(graphemes[graph]) == 1 and graph.isalpha():
                line = line.replace(graph, graphemes[graph])

        fout.write(line.encode("utf-8"))            

    fin.close()
    fout.close()

###################################
###################################

def getWordList (inFile, outFile):

#This script is used to find all distinct words in a text already processed by splitSentences.py
#The output is an alphabetically ordered list and it is used for the dictionary.

         fin = open(inFile, 'r')
         fout = open(outFile, 'w')
         print (">>> Writing contents to file<<<")
         words={}
         words_gen = (word.strip('.').lower() for line in open(inFile)
                                                      for word in line.split())
        
                                             
         for word in words_gen:
                words[word] = words.get(word, 0) + 1

        
         topWords = sorted(words.iteritems(), key=itemgetter(0), reverse=True)
         topWords.sort()

         for word, frequency in topWords:
             fout.write(str("%s\n" % (word)))
         fin.close()
         fout.close()



########################################
########################################

def createHTKDictionary (inFile, lettersFile, dictFile):
#This script is used to create a HTK dictionary from a segmented file

    fgraph = open (lettersFile)
    graphemes = {}
    #add to dictionary only words with valid graphemes
    for line in fgraph.readlines():
        zz = line.decode("utf-8").split()
        graphemes[zz[0].strip()]= zz[1].strip()
    fgraph.close()    
    fin = open(inFile, 'r')
    words={}
    print inFile
    words_gen = (word.strip('.').lower() for line in open(inFile) for word in line.split())
                                                    
    for word in words_gen:
                words[word] = words.get(word, 0) + 1
#    add background model to dictionary
    words['bghmm']=1
    topWords = sorted(words.iteritems(), key=itemgetter(0), reverse=True)
    topWords.sort()
    fin.close()
    
    fout = open(dictFile, 'w')
    fout.write('!SENT_END sil\n!SENT_START sil')
    print (">>> Writing dictionary to file: %s" %dictFile)
    for word, freq in topWords:
        word = word.decode("utf-8")
        fout.write('%s ' %word.upper().encode("utf-8"))
        if word == 'bghmm' :
            fout.write('bghmm')
        else:
            if word != '':
                for c in list(word):
                    fout.write('%s ' %graphemes[c].encode("utf-8"))
        fout.write('\n')
    
    fout.close()
###################################
###################################

def getInitialSentences (inFile, graphemeFile, N, steps, outFile):

## This script is used to write the first $steps utterances into a file and determine
## the number of occurences for each grapheme. It is an alternative to the selectTrainingText() 
## function

    fout = open(outFile, 'w')
    fGraph = open(graphemeFile, 'r')
    graphemeList = []
    print (">>>Reading grapheme list<<<")
    graphCount = {}
    for line in fGraph.readlines():
        if len(line.split()[1]) > 1:
            char = line.split()[0]
        else:
            char = line.split()[1]
        graphemeList.append(char.strip().decode("utf-8"))
        if not graphCount.has_key(char.strip().decode("utf-8")):
            graphCount[char.strip().decode("utf-8")] = int(N)
        #for key in graphCount:
    #           print key.encode("utf-8"), graphCount[key]
        print ("Found %s graphemes:" %len(graphemeList))
    for grapheme in graphemeList:
        print(grapheme.encode('utf-8'))
        fGraph.close()
     
        print (">>>Reading file contents<<<")
        fin = open(inFile, 'r') 
      
        print (">>>Selecting sentences<<<")
        done = 0
        step = 1
    
    while not done and step < int(steps)+1:


        line = fin.readline().decode("utf-8")
        
        count = {}
        for c in line.replace(' ','').strip():
            if count.has_key(c):
                count[c] += 1
            else:
                count[c] = 1
            
        count = {}
        for c in line.replace(' ','').strip():
            if count.has_key(c):
                if count[c] < int(N):
                    count[c] += 1
            else:
                count[c] = 1
                changed = 0
        for c in count:
            if graphCount.has_key(c):
                graphCount[c] = graphCount[c] - count[c]
                changed = 1
                if graphCount[c] <= 0:
                    del graphCount[c]
        print ('-------\nSTEP %d\n-------' %step)
        print ('STILL MISSING: ')
        for key in graphCount:
            print ('%s -- %d occ. out of %d' %(key.encode("utf-8"), graphCount[key], int(N)))        
        #if changed: 

        fout.write("(seg_%s \"%s\")\n" %(str(step).zfill(5),line.encode("utf-8").strip()))
        print ("Wrote to file!")
        
        done = 1
        for key in graphCount:
            if graphCount[key] > 0:
                done = 0

                
        step += 1


    for key in graphCount:
        if graphCount[key] == int(N):
            print ('Could not find any occurences of grapheme: \"%s\".' %key.encode("utf-8"))
            done = 1
    if done == 1:
        print ('\nPlease increase the number of steps!!')
    print ("---------------")
    print ("WROTE %d UTTERANCES TO %s" %(steps, outFile))
    fout.close()


###################################
###################################

def selectTrainingText (inFile, graphemeFile, N, steps, outFile):

#This script is use select a minimum number of sentences that contain all graphemes in initial text at least N times and write them in the training file (outFile). 

    fout = open(outFile, 'w')
    fGraph = open(graphemeFile, 'r')
    graphemeList = []
    numberedSentences = {}
    outSentences = []
    print (">>>Reading grapheme list<<<")
    graphCount = {}
    for line in fGraph.readlines():
        if len(line.split()[1]) > 1:
            char = line.split()[0]
        else:
            char = line.split()[1]
        graphemeList.append(char.strip().decode("utf-8"))
        if not graphCount.has_key(char.strip().decode("utf-8")):
            graphCount[char.strip().decode("utf-8")] = int(N)
        #for key in graphCount:
    #           print key.encode("utf-8"), graphCount[key]
        print ("Found %s graphemes:" %len(graphemeList))
    for grapheme in graphemeList:
        print(grapheme)
        fGraph.close()
     
        print (">>>Reading file contents<<<")
        fin = open(inFile, 'r') 
        sentences = fin.readlines()
    fin.close()
    fin = open(inFile, 'r')  
    i = 0
    for line in fin.readlines():
        numberedSentences[line.decode("utf-8").strip()] = i
        i +=1
        fin.close()

        print (">>>Selecting sentences<<<")
        done = 0
        step = 1

    while not done and step < int(steps)+1 and sentences:
         
        print ("---------------")
        print ("ROUND %d" %step)
         
        score = {}
         
        for line in sentences:
            line = line.decode("utf-8")
            score[line] = 0
            count = {}
            for c in line.replace(' ','').strip():

                if count.has_key(c):
                    count[c] += 1
                else:
                    count[c] = 1
            
            for key in graphCount:
            
                if count.has_key(key) and count[key] >= graphCount[key]:
                    score[line] = score[line]+1
                elif count.has_key(key) and count[key] < graphCount[key]:
                    score[line] = score[line]+0.1
                                  
#        print score.values()
#        bestLocal =  max(score.values())
        bestLocal = max(score,key = lambda b: score.get(b))
        print ("---------------")
        print ("BEST SCORE IN ROUND %d: %.2f - FOR SENTENCE:  %s" %(step,score[bestLocal], bestLocal))
        print ("---------------")
         
        msg = 'Should I write the sentence to file or you think we can do better?'
        shall = True if raw_input("%s (y/N) " % msg).lower() == 'y' else False   
        #print graphCount
        if shall:
            print ("REINITIALIZING graphCount")
            sentences.remove(bestLocal.encode("utf-8"))
            #testSentences.remove(bestLocal.encode("utf-8"))
            count = {}
            for c in bestLocal.replace(' ','').strip():
                if count.has_key(c):
                    if count[c] < int(N):
                        count[c] += 1
                else:
                    count[c] = 1
                    changed = 0
            for c in count:
                if graphCount.has_key(c):
                    graphCount[c] = graphCount[c] - count[c]
                    changed = 1
                    if graphCount[c] <= 0:
                        del graphCount[c]
                
            if changed: 
                #fout.write("%s - SCORE: %.2f\n" %(bestLocal.encode("utf-8").strip(), score[bestLocal]))
                outSentences.append([bestLocal.strip(), numberedSentences[bestLocal.strip()]])
                #print outSentences
                #fout.write("(seg_%s \"%s\")\n" %(str(step).zfill(5),bestLocal.encode("utf-8").strip()))
                #print ("Wrote to file!")
                step = step+1

        else:
            sentences.remove(bestLocal.encode("utf-8"))        
        print ("STILL MISSING: ")
        for grapheme in graphCount:
            print ("%s - %d  " %(grapheme, graphCount[grapheme]))
    
                  
        print ("---------------")
        done = 1
        for key in graphCount:
            if graphCount[key] > 0:
                done = 0
    if done:
        print ("FOUND ALL GRAPHEMES!! Hooray!!")
    else:
        print ("There are still some missing graphemes :( -- try using more rounds or less occurences".upper())
    print ("\nWROTE %d UTTERANCES TO %s" %(steps, outFile))
    #a = sorted(outSentences, key=itemgetter(1))
    
    for  item, index in enumerate(sorted(outSentences, key=itemgetter(1))):
        fout.write("(seg_%s \"%s\")\n" %(str(step).zfill(5),index[0].encode("utf-8").strip()))
        
    print ("---------------")
    fout.close()

###################################
###################################

def notInDictionary(inFile, dictFile):

#This script checks if all the words in the input file are in the HTK dictionary and prints the ones that are not in the terminal
    
    dicto = []
    print ("Checking all words from input file in the dictionary!")
    fd = open(dictFile)
    for line in fd.readlines():
        wd = line.split()
        if wd[0].strip() not in dicto:
            dicto.append(wd[0].strip())
            #print wd[0]
    print ("The following words could not be found in the provided dictionary")
    fin = open (inFile)
    for line in fin.readlines():
        for wd in line.split():
            if wd.strip('.') not in dicto:
                print wd.strip('.')
    print ("DONE!")
    fin.close()
    fd.close()



########################################
########################################

def checkCharacters(inFile, hmmList, out):

#This function checks if all the characters in the text file are in the hmmlist
#TODO: do I need out?

    chars = []
    nonch = []
    fin = open(inFile)
    fhmm = open(hmmList)
    for line in fhmm.readlines():
        if line.strip() not in chars:
            chars.append(line.strip())
    print chars
    chars.append('.')
    chars.append(',')

    for line in fin.readlines():
        line = line.decode('utf-8')
        for ch in line:
            if ch.strip() not in chars and ch.strip() not in nonch:
                
                nonch.append(ch.strip())

    print nonch
    fo = open (out, 'w')
    for non in nonch:
        fo.write('%s\n' %non.encode('utf-8'))

    fo.close()
    fin.close()
    fhmm.close()


#######################################
#             MAIN                    #
#######################################

def main(inFile, NoUTTS, N, iniRnd, inputTsc, outDir, supervised, fromStep, toStep):

    #creating a step list to run
    steps = range(int(fromStep), int(toStep)+1)

    print ("========================================\n")
    print ("STARTING TO PROCESS THE INPUT TEXT FILE\n")
    print ("========================================\n")
    print ("RUNNING STEPS FROM %s TO %s" %(fromStep, toStep))

    ## Check if newline is UNIX style:    
    fin = open(inFile, 'U')
    fin.readline()
    
    if fin.newlines == None or '\n' not in fin.newlines:
        print ("\n[ERROR +0001]: Your file does not use the Unix newline character.\n")
        sys.exit(1)
    
    audioBookName = os.path.split(inFile)[1]
    print ('PROCESSING FILE: %s' %audioBookName)
    if inFile.find('.'):
        audioBookName = audioBookName[0:audioBookName.find('.')]# assuming it has a txt extension

    if 1 in steps:
        print ("\n## STEP 1. SEGMENTING THE TEXT INTO SENTENCES")
        segmentedOut  = outDir+'data/' + audioBookName + '-segmented'
        segmentedOutCommas  = outDir+'data/' + audioBookName + '-segmentedWithCommas'
        segmentedOutNLTK  = outDir+'data/' + audioBookName + '-segmentedNLTK'
        segmentedOutNLTKStrip = segmentedOutNLTK+'-strip'
        sentenceSplit(inFile, segmentedOut)
        sentenceSplitWithCommas(inFile, segmentedOutCommas)
        sentenceSplitNLTK(inFile, segmentedOutNLTK)
        punctuationAndLowercase (segmentedOutNLTK, segmentedOutNLTKStrip)
        print ("##")

    if 2 in steps:
        print ("\n## STEP 2. CREATING GRAPHEME LIST")
        segmentedOut  = outDir+'data/' + audioBookName + '-segmented'
        graphFile = outDir+'data/' + audioBookName + '-graphemes'
        hmmlist = outDir+'data/' + audioBookName + '-hmmlist'
        getGraphemesAndHMMList (segmentedOut, graphFile, hmmlist)
        print ("##")

    if 3 in steps:
        print ("\n## STEP 3. REPLACING NON STANDARD CHARACTERS IN TEXT AND CREATING BIGRAM LIST")
        segmentedOut  = outDir+'data/' + audioBookName + '-segmentedNLTK-strip'
        graphFile = outDir+'data/' + audioBookName + '-graphemes'
        segmentedASCII = outDir+'data/' + audioBookName + '-segmentedASCII'
        bigramFile = outDir+'data/' + audioBookName + '-bigrams'
        if (int(supervised)==0):
            replaceWithASCII(segmentedOut, graphFile, segmentedASCII)
        createBigrams(segmentedOut, bigramFile)
        print ("##")

    if 4 in steps:
        if  int(supervised)>0:
            print("\nSkipping STEP 4 due to the supervised lexicon")
        else:    
            print ("\n## STEP 4. CREATING HTK DICTIONARY")
            graphFile = outDir+'data/' + audioBookName + '-graphemes'
            segmentedASCII = outDir+'data/' + audioBookName + '-segmentedASCII'
            segmentedOut  = outDir+'data/' + audioBookName + '-segmentedNLTK-strip'
            dictFile = outDir+'data/' + audioBookName + '-dict'
            createHTKDictionary (segmentedOut, graphFile, dictFile)        
        print ("##")

    if 5 in steps:
        print ("\n## STEP 5. PREPARING INITIAL TRAINING TEXT")
        #convert the raw initial text data into the one needed for model building
        prepareInitialTextData(inputTsc, outDir+'/initialWav16/', outDir+'data/' + audioBookName + '-initialTextData')
        
#        graphFile = 'data/' + audioBookName + '-graphemes'
#        segmentedASCII = 'data/' + audioBookName + '-segmentedASCII'
#        initialText = 'data/' + audioBookName + '-initialTextData'
#        utts = int(NoUTTS)
#        if int(iniRnd) == 0:
#            selectTrainingText (segmentedASCII, graphFile, int(N), utts, initialText)
#        else:
#            getInitialSentences (segmentedASCII, graphFile, int(N), utts, initialText)
        
    print ("ALL DONE!\n")
    

if __name__ == '__main__':    
    if len(sys.argv) == 8: 
        main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6],sys.argv[7], 1, 5)
    elif len(sys.argv) == 9:
        main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8], 5)
    elif len(sys.argv) == 10:
        main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4],  sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8], sys.argv[9])
    else:
        print "Usage: python textProcessingModule.py  <audiobook textFile> <NoUTTS> <NoOfGraphemes> <initialOrRandom> <initialTextFile> <outDir> <supervised> <fromSTEP> <toSTEP>"
        print "Usage: python textProcessingModule.py  <audiobook textFile> <NoUTTS> <NoOfGraphemes> <initialOrRandom> <initialTextFile> <outDir> <supervised> <fromSTEP>"


