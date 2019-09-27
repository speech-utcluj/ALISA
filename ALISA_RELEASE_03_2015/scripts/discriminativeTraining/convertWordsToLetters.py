#!/usr/bin/python
# -*- coding: utf-8 -*-

#################################################
## Author: Adriana STAN adriana.stan@com.utcluj.ro
## Project Simple4All - www.simple4all.org
## January 2013
#################################################


import os
import sys

def main(inFile, dictionary, outFile):
    print ('Converting segmented data to letters...')
    dic = {}
    fdict = open(dictionary)
    for line in fdict.readlines():
        dic[line.strip().split()[0].lower().decode("utf-8")]= line.strip().split()[1:]
    fdict.close()    
    fin = open(inFile)
    fout = open(outFile, 'w')
    for line in fin.readlines():
        fout.write('!SENT_START ')
        for word in line.strip().split():
            if word not in  ['!SENT_START', '!SENT_END', '.']:
                for letter in dic[word.decode("utf-8")]:
                    fout.write('%s ' %letter.encode('utf-8'))
#            else:
 #               fout.write('%s ' %word)
        fout.write('!SENT_END\n')



if __name__ == '__main__':	
    if len(sys.argv) == 4: 
	    main(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print "Usage: python convertWordsToLetters.py <inFile> <dictionary> <outFile>"
