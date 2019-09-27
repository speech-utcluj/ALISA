#!/usr/bin/python


import sys, os
from string import strip
import re, math 
from NAIVE_speech_database_tools import *   ## read_uttsdata

"""
Convert utts.data format transcription into an initial NAIVE format annotation database.

Generate MLF and naive grapheme 'lexicon' for alignment from the d/b

Assume:
  -- whitespace delimits words
  -- all characters are either in letters.txt input file   or  punctuation.txt
  
  outlist is phonelist
"""

## e.g.   ~/proj/whole_system/script/speech_database/initialise_labels.py ~jyamagis/links/cstr2/RJS/utts.data x x data/ENGLISH/letters.txt  data/ENGLISH/punc.txt 

def main_work():

    #################################################
    # ======== Get stuff from command line ==========

    def usage():
        print "Usage: ......  "
        sys.exit(1)

    # e.g. 

    try:
        infile  = sys.argv[1]
        outfile = sys.argv[2]
        outlex  = sys.argv[3]
        outlist = sys.argv[4]
        letter_list = sys.argv[5]
        punc_list  = sys.argv[6]
    except:
        usage()


    #################################################            
    wordtypes = {}
    utts = read_uttsdata(infile)

    letter_map = read_lettermap(letter_list)
    punc_map = read_lettermap(punc_list)     
        
    print "t"
    f = open(outfile, "w")
    f1 = open(outfile+'_2', "w")
    
    lex = {}
    for (name, text) in utts:
        print name
        text = naive_tokenise(text.lower(), letter_map, punc_map)
        (text, lex_fragment) = make_safe_text(text, letter_list, punc_list)  # 
        lex.update(lex_fragment)
        text = ["_UTTEND_"] + text + ["_UTTEND_"]
        f.write("#!MLF!#\n")
        f.write('"*/%s.lab"\n'%(name))
        for word in text:
            f.write(word.upper() + "\n")
        f.write(".\n") 
    f.close()  

                
    ## make a list before removing punc etc:
    seen_in_uttsdata = lex.keys()    

    
    ## make grapheme "lexicon":
    if "_SPACE_" in lex:
        del lex["_SPACE_"]
    for punc_symbol in punc_map.values():
        if punc_symbol in lex:
            del lex[punc_symbol]
        
    wordtypes = lex.keys()    
    wordtypes.sort()
    
    f = open(outlex, "w")

    graphtypes = {}
    for w in wordtypes:
        graphemes = lex[w]    
        for graph in graphemes:
                graphtypes[graph] = "dummy"        
        graphemes = " ".join(graphemes)
        entry = w.upper() + " " + graphemes
        f.write(entry + "\n")

    f.write("_UTTEND_ sil\n")                  ## assume there is always silence at ends of audio            
    for punc_symbol in punc_map.values():    
        if punc_symbol in seen_in_uttsdata:
            f.write(punc_symbol + " sil\n")    ## 1st choice -- initialisation
#           f.write(punc_symbol + " skip\n")   ## 2nd choice -- realign options    
                    
#   f.write("_SPACE_ skip\n")                  ## 1st choice -- initialisation
    f.write("_SPACE_ sil\n")                   ## 2nd choice -- realign options    
    f.close()

    graphtypes["sil"] = "dummy"
    graphtypes["skip"] = "dummy"
        
    graphtypes = sorted(graphtypes.keys())
    writelist(graphtypes, outlist)
    
if __name__=="__main__": 

        main_work()

