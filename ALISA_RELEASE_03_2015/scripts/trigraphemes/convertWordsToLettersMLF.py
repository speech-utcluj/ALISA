# -*- coding: utf-8 -*-

#################################################
## Author: Adriana STAN adriana.stan@com.utcluj.ro
## Project Simple4All - www.simple4all.org
## January 2013
#################################################


import sys

def main (MLF, dictionary, lettersMLF, stringEscape):

    dic = {}
    fdict = open(dictionary)
    for line in fdict.readlines():
        
        dic[line.strip().split()[0].decode("utf-8").upper()]= line.strip().split()[1:]
    fdict.close() 
   

    #graph = {}
    #fG = open(graphFile)
    #for line in fG.readlines():
    #    line = line.decode('utf-8')
    #    graph[line.split()[0].strip()] = line.split()[1].strip()
    fM = open(MLF)
    fout = open(lettersMLF, 'w')
    
    for line in fM.readlines():
        if line.strip() != '':
            if stringEscape:
                line = line.decode('string-escape')
            if line.strip() in ['#!MLF!#', '!SENT_START', '!SENT_END'] :
                fout.write(line.encode('utf-8'))
            elif line[0] == '\"' :
                fout.write('%ssil\n' %line.encode('utf-8'))
            elif line[0] == '.':
                fout.write('sil\n%s' %line.encode('utf-8'))
            else:
                for i in dic[line.strip().decode("utf-8").upper()]:
                    fout.write('%s\n' %i)
                #fout.write('skip\n')
               




if __name__ == '__main__':
    if len(sys.argv) == 5: 
        main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print "Usage: python convertWordsToLetters MLF, lettersMLF, stringEscape"
