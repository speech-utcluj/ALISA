## This script convert the MLF files into simple text for the language model

import sys

def main(MLFFile, outFile, marker):
    
    fO = open(outFile, 'w')
    fM = open(MLFFile)
    ind = 1
    for line in fM.readlines():
        #line = line.decode('utf-8')
        if line[0] == "\"":
            lab = line[line.find(marker):].strip()
            lab = lab[:-5]
            if ind!=1:
                    fO.write('!SENT_END \n!SENT_START ')
            else:
                    fO.write('!SENT_START ' )            
            ind +=1
        elif line[0] != '.' and line[0] != '#':
            line = line.decode('string-escape', 'ignore')
            fO.write('%s ' %line.split()[0].strip().lower())
    if ind != 1:    
        fO.write('!SENT_END\n')
    fO.close()

if __name__ == '__main__':
    if len(sys.argv) == 4: 
        main(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print "Usage: python createTxtFromMLF MLFFile, outFile, marker"
