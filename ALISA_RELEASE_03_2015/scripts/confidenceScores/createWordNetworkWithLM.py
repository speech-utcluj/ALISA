# -*- coding: utf-8 -*-

#################################################
## Author: Adriana STAN adriana.stan@com.utcluj.ro
## Project Simple4All - www.simple4all.org
## May 2012
#################################################

import sys, os

def main(wlistFile, LMfile, netsDir, skip):
    """Creates a 'skip network' in HTK format using an additional LM.
    """


    fin = open(wlistFile, 'r')
    bigram = {}

    sent = 1
    print ("==================================")
    print ("START")

    fLM = open (LMfile)
    #read bigram list
    for line in fLM.readlines():
        line = line.decode("utf-8")
        line = line.strip()
        if bigram.has_key(line.split()[0]):
            bigram[line.split()[0]].append(line.split()[1].strip())    
        else:
            bigram[line.split()[0]]= []
            bigram[line.split()[0]].append(line.split()[1])    
        
    #print bigram
    for sentence in fin.readlines():
        nodes = []
        arcs = []
        wlist = []
        sentence = sentence.replace("-", ' ')
        sentence = sentence.replace("(", '')
        sentence = sentence.replace(",", '')
        netname = netsDir+sentence[0:sentence.find('\"')-1]+'.slf'
        sentence = sentence[sentence.find("\"")+1:sentence.rfind("\"")]
        
        print ("========================")    
        print ("PROCESSING SENTENCE: %s" %int(sent))
        print ("--")
        #print sentence
        print ("--")
        for word in sentence.split():

            wlist.append(word.strip().decode("utf-8"))
        
        nodes.append('!NULL')        # Node 0
        nodes.append('!NULL')        # Node 1
        nodes.append('!SENT_END')    # Mode 2
        nodes.append('!SENT_START')  # Node 3

        arcs.append((0,3)) # !NULL->!SENT_START
        arcs.append((2,1)) # !SENT_END->!NULL

#        netname = nets + '.slf' # AS: change to input
        net = open(netname, 'w')

        i=4
        print ("GENERATING NODES AND ARCS!")
        
        for w in wlist:
            nodes.append(w)
            if i+1 <= len(wlist)+3:
                arcs.append((i, i+1))  # arc from previous word to this word
            
#            AS: add arcs depending on the skip number
            for j in range (2, int(skip)+1):

                if i+j <= len(wlist)+3:
#                    print wlist[i+j-4], bigram['şo']
                    if wlist[i+j-4] in bigram[wlist[i-4]]:
                        #print 'Exists'
                        arcs.append((i, i+j))  # AS: j word skip
                    #else:
                    #    print 'Not exists'
                        #print cmd    

#

            if i != 3:
                arcs.append((3, i))  # skip arc to this word from initial silence

            arcs.append((i, 2))  # skip arc out to the final silence

            i=i+1
        print ("FOUND: %d nodes" %i)
        print ("WRITING TO FILE: %s" %netname)



        print >> net, 'N=%d L=%d' % (len(nodes), len(arcs))

        for (i, n) in enumerate(nodes):

            print >> net, 'I=%d W=%s' % (i, n.upper().encode("utf-8"))

        for (j, arc) in enumerate(arcs):

            print >> net, 'J=%d S=%d E=%d' % (j, arc[0], arc[1])
        sent += 1
    print ("=========================")
    print ("\tDONE!")
    print ("=========================")
    fin.close()

if __name__ == '__main__':
    if len(sys.argv) == 5: 
        main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print "Usage: python createWordNetwork.py  <approx text> <LM file> <outputNetworkFolder> <N-skip>"



#print i,i+j
                    #print wlist[i-4], wlist[i+j-4], i+j-4
                    #cmd = "awk '{if ($2 == \"" + wlist[i-4] +"\" && $3 == \"" +wlist[i+j-4]+"\") print $1 } ' " + LMfile + " > tmp "
                    #os.system(cmd)
                    #fT= open('tmp')
                    #bol = fT.readline()
                    
                    #fT.close()
