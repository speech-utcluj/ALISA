#!/usr/bin/python
# -*- coding: utf-8 -*-

#################################################
## Author: Adriana STAN adriana.stan@com.utcluj.ro
## Project Simple4All - www.simple4all.org
## September 2014
#################################################
## This script creates a full list of triphones
## both from the book text, as well as from the
## alignment.

import sys

def main(triph_align, triph_book, outputFile):

    fin = open(triph_align)
    fout = open(outputFile, 'w')
    triph_al = []
    for line in fin.readlines():
        triph_al.append(line.strip())
        fout.write('%s' %line)
    fin.close()

    fb = open(triph_book)
    for line in fb.readlines():
        if line.strip() not in triph_al:
            fout.write('%s' %line)
    fb.close()
    fout.close()
                    


if __name__ == '__main__':    
    if len(sys.argv) == 4: 
        main(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print "Usage: python getFullListOfTriphones <triphone1> <triphone2> <outputTriphone>"
