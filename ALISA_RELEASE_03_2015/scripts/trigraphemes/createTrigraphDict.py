# -*- coding: utf-8 -*-

#################################################
## Author: Adriana STAN adriana.stan@com.utcluj.ro
## Project Simple4All - www.simple4all.org
## January 2013
#################################################


import sys

def main (dictionary, outDict):

    fdict = open(dictionary)
    fout = open(outDict, 'w')
    for line in fdict.readlines():
        if line.strip() not in ['!SENT_START', '!SENT_END']:
            fout.write('%s\n' %(line.strip()+' skip'))
        else:
            fout.write('%s\n' %(line.strip()))   

if __name__ == '__main__':
    if len(sys.argv) == 3: 
        main(sys.argv[1], sys.argv[2])
    else:
        print "Usage: python createTrigraphDict inDict outDict"
