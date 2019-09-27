# -*- coding: utf-8 -*-

#################################################
## Author: Adriana STAN adriana.stan@com.utcluj.ro
## Project Simple4All - www.simple4all.org
## August 2014
#################################################
## This script creates the tree.hed file used in
## the triphone state tying

import sys, os

def main(phoneList,  outPath, iteration , outFile):
    
    fin = open(phoneList)
    data = [line.strip() for line in fin.readlines()]
#    data.remove('skip')
    fin.close()
    fout = open(outFile, 'w')
    fout.write ('RO 100 %s/temp/trihmm-%i/stats\n\nTR 0\n' %(outPath, iteration))
    
    fout.write('TR 2\n')
    fstats = open(outPath+'data/models/stats-1')
    stat = {}
    for line in fstats.readlines():
        data2 = line.split()
        stat[data2[1].replace('"','')] = int(data2[2])
    fstats.close()
    for phone in data:
        if stat.has_key(phone):
            if stat[phone] > 0 or phone == 'skip':
                fout.write('QS \"R_%s\"\t{*+%s}\n' %(phone, phone))
                fout.write('QS \"L_%s\"\t{%s-*}\n' %(phone, phone))    
    for i in range(2,5):
        for phone in data:
            if stat[phone] >0:
                fout.write('TB 350 \"ST_%s_%i_\" {(\"%s\",\"*-%s+*\",\"%s+*\",\"*-%s\").state[%i]}\n' %(phone, i, phone, phone, phone, phone, i))

    
    fout.write('TR 1\nAU \"%s/temp/fulllist2\"\nCO \"%s/temp/tiedlist\"\nST \"%s/temp/trees\"\n' %(outPath, outPath, outPath)) 
    
    

if __name__ == '__main__':
    if len(sys.argv) == 5: 
        main(sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4])
    else:
        print "Usage: python createTreeHED phoneList outPath  outTreeHED"
