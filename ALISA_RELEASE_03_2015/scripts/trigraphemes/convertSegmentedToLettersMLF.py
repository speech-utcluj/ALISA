# -*- coding: utf-8 -*-

#################################################
## Author: Adriana STAN adriana.stan@com.utcluj.ro
## Project Simple4All - www.simple4all.org
## January 2013
#################################################

import sys

def main (MLF, lettersMLF):

    fM = open(MLF)
    fout = open(lettersMLF, 'w')
    fout.write ('#!MLF!#\n')
    i = 1
    for line in fM.readlines():
        line = line.decode('string-escape').decode('utf-8')
    
        fout.write ('\"data/mfcc/chp01_%s.rec\"\n' %str(i).zfill(4))

        for word in line.strip().split():
            #word = word.encode('utf-8').encode('string-escape')
            if word[-1] == '.':
                #fout.write('%s\nsil\n.\n' %word[:-1].strip())
                fout.write('%s\n.\n' %word[:-1].strip().encode('utf-8'))
            else:
                #fout.write('%s\nskip\n' %word.strip())
                fout.write('%s\n' %word.strip().encode('utf-8'))
#        fout.write('sil\n')
        i +=1


if __name__ == '__main__':
    if len(sys.argv) == 3: 
        main(sys.argv[1], sys.argv[2])
    else:
        print "Usage: python convertSegmentedToLetters segmentedNLTK, lettersMLF"
