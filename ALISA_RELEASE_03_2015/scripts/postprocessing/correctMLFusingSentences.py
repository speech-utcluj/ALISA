# -*- coding: utf-8 -*-

#################################################
## Author: Adriana STAN adriana.stan@com.utcluj.ro
## Project Simple4All - www.simple4all.org
## May 2012
#################################################


import sys

def main (segmentedASCII, MLF, outMLF):

    sentences = []
    fSeg = open(segmentedASCII)
    for line in fSeg.readlines():
        sentences.append(line.strip('.\n'))
    fSeg.close()

    
    fMLF = open(MLF)
    fout = open(outMLF, 'w')
    aux = ''
    line = fMLF.readline() # get rif of #!MLF!#
    fout.write(line)
    mlfsent = []
    line = fMLF.readline() # get rif of first label
    fout.write(line)
    print line

    i = 0
    bol = 0
    found = 0
    for line in fMLF.readlines():
        line = line.decode('string-escape')
        
        if line[0] == '\"':
            
            #if not bol:        
            #    fout.write(line)
            #    mlfsent = []
            if len(mlfsent)>4 :
                
                sent = ' '.join(mlfsent[1:-1])
                sent = sent.strip()
                #print ('%s' %sent)
                found = 0
                #print sent
                for sen in sentences:

                    if sent.strip() in sen:
                    
                        found = 1
                        zaone = sen
                        break
                
                
                if found and len(zaone.split()) <= len(mlfsent)+2:
                    outsent = mlfsent
                    #check if first word is deleted or inserted
                    if mlfsent[0] == zaone.split()[1]:
                        print ('----------------')
                        print ('!!!WE NEED TO INSERT WORD \"%s\" AT THE BEGINNING' %zaone.split()[0])    
                        print ("--")
                        print ' '.join(mlfsent)
                        print ('>>')
                        print zaone
                        print ('----------------\n')
                        outsent.insert(0,zaone.split()[0])
                        #print outsent
                    elif mlfsent[1] == zaone.split()[0] and mlfsent[0] != zaone.split()[2]:
                        print ('----------------')
                        print ('!!!WE HAVE TO DELETE \"%s\" AT THE BEGINNING' %mlfsent[0])    
                        print ("--")
                        print ' '.join(mlfsent)
                        print ('>>')
                        print zaone
                        print ('----------------\n')
                        del outsent[0]
                        #print outsent
                    if mlfsent[-1] == zaone.split()[-2] and mlfsent[-1] != zaone.split()[-3]:
                        print ('----------------')
                        print ('!!!WE NEED TO INSERT THE WORD \"%s\" AT THE END' %zaone.split()[-1])    
                        print ("--")
                        print ' '.join(mlfsent)
                        print ('>>')
                        print zaone
                        print ('----------------\n')
                        outsent.append(zaone.split()[-1])
                        #print outsent
                    elif mlfsent[-2] == zaone.split()[-1] and mlfsent[-1] != zaone.split()[-3]:
                        print ('----------------')
                        
                        print ('!!!WE NEED TO DELETE THE WORD \"%s\" AT THE END' %mlfsent[-1])    
                        print ("--")
                        print ' '.join(mlfsent)
                        print ('>>')
                        print zaone
                        print ('----------------\n')
                        del outsent[-1]
                        #print outsent
                    for word in outsent:
                        #print word
                        fout.write('%s\n' %word)
                    fout.write('.\n')


                else:
                    for word in mlfsent:
                        fout.write('%s\n' %word)
                    fout.write('.\n')
            else:
                for word in mlfsent:
                    fout.write('%s\n' %word)
                fout.write('.\n')

            mlfsent = []
            fout.write(line)
            print line
            

        else:
            if line.split()[0] != '.':
                mlfsent.append(line.split()[0])

            bol = 1
            
    for word in mlfsent:
        fout.write('%s\n' %word)
    fout.write('.')  ## last dot
    
    fMLF.close()
    fout.close()



if __name__ == '__main__':
    if len(sys.argv) == 4: 
        main(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print "Usage: python correctMLFusingSentences segmentedNLTK-strip, MLF, outMLF"
