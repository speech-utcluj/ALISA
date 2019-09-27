# -*- coding: utf-8 -*-

#################################################
## Author: Adriana STAN adriana.stan@com.utcluj.ro
## Project Simple4All - www.simple4all.org
## January 2013
#################################################

import sys, os

def main(guessedUTTS, guessedMLF, outFile):
    print ('CREATING MLF FILE FOR THE GUESSED UTTERANCES!')
    guessed = []
    fG = open(guessedUTTS)
    for line in fG.readlines():
        guessed.append(line.strip())
    fG.close()
   # print len(guessed)
    
    fMLF = open(guessedMLF)

    fOut = open (outFile, 'w')
    fOut.write('#!MLF!#\n')
    line = fMLF.readline()

    while True:
        
        if len(line) ==0:
                break # EOF
    
        line = fMLF.readline()
        #print line
        lineAux = line.strip().replace('"','')
        lineAux = os.path.basename(lineAux)
        lineAux = lineAux.replace('.rec', '')
        #print lineAux, '   -   ', lineAux in guessed
#        lineAux = line.replace(outputM, '').strip()
#        lineAux = lineAux.replace('\"', '')
#        lineAux = lineAux.replace('.rec', '')
        #print lineAux

        if lineAux in guessed:
            print lineAux
            fOut.write(line)
            lineText=fMLF.readline()
            
            while lineText[0]!= '.':
                fOut.write(lineText)
                lineText = fMLF.readline()
            fOut.write('.\n')    
            line = lineText
        
    fOut.close()
    print ('DONE!')



if __name__ == '__main__':
    if len(sys.argv) == 4: 
        main(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print "Usage: python getMLFForGuessedUTTS guessedUTTS  guessedMLF outFile"
