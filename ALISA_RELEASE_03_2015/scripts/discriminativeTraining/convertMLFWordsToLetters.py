#!/usr/bin/python
# -*- coding: utf-8 -*-

#################################################
## Author: Adriana STAN adriana.stan@com.utcluj.ro
## Project Simple4All - www.simple4all.org
## January 2013
#################################################


import sys

def main(inFile, dictionary, outFile):
        
    dic = {}
    fdict = open(dictionary)
    for line in fdict.readlines():
        dic[line.strip().split()[0].lower().decode("utf-8")]= line.strip().split()[1:]
    
    fin = open(inFile)
    fout = open(outFile, 'w')
    for line in fin.readlines():
        line = line.decode('string-escape', 'ignore')
        if line[0] not in ['"','#', '.', '!']:
             word = line.strip().split()[0].lower()
             word = word.decode('utf-8')

             for letter in dic[word]:
                      fout.write('%s\n' %letter.encode('utf-8'))
        else:
                 fout.write('%s' %line)




if __name__ == '__main__':	
    if len(sys.argv) == 4: 
	    main(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print "Usage: python convertMLFWordsToLetters.py <inFile> <dictionary> <outFile>"
