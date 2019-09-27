# -*- coding: utf-8 -*-

#################################################
## Author: Adriana STAN adriana.stan@com.utcluj.ro
## Project Simple4All - www.simple4all.org
## June 2012
#################################################

import sys, os

def main(guessedUttsFile, MLFFile, outFile):
    
    guess = []
    fG = open(guessedUttsFile)
    for line in fG.readlines():
        guess.append(line.strip())
    fG.close()
    fO = open(outFile, 'w')
    fM = open(MLFFile)
    ind = 1
    for line in fM.readlines():
        #line = line.decode('utf-8')
        #print line.split()[0].strip()
        if line[0] == "\"":

            lab = line.strip().replace('"','')
            lab = os.path.splitext(os.path.basename(lab))[0]
            #lab = lab.replace('.rec', '')            
            #lab = lab[:-5]
            print lab

            if (lab in guess):
                if ind!=1:
                    fO.write('. \")\n(%s \"' %lab)
                else:
                    fO.write('(%s \"' %lab)            
                ind +=1
    
                    
        elif line[0] != '.' and line[0] != '#' and (lab in guess) and (line.split()[0].strip() not in ['!SENT_END', '!SENT_START']):
            line = line.decode('string-escape', 'ignore').lower()
            fO.write('%s ' %line.split()[0].strip())

    if ind != 1:    
        fO.write('.\")\n')
    fO.close()


if __name__ == '__main__':
    if len(sys.argv) == 4: 
        main(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print "Usage: python createSpeechTranscriptFromMLF guessedUttsFile, MLFFile, outFile"
