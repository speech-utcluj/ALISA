#!/usr/bin/python


import sys, os
import re
import shelve
import cPickle
import codecs
#, math



## add path for gensim 0.5 (the relevant versions of numpy/scipy are assumed to be installed):
#gensim_location = os.environ.get("GENSIM_LOC")
## e.g. "/afs/inf.ed.ac.uk/user/s06/s0676515/pr/my_python_packages/gensim-0.5.0/src"
#sys.path.append(gensim_location)

#from gensim import corpora, models, similarities


## TO DO:

## remove:  add_neighbour_field_*

def test_me():

    #################################################
    """
    # ======== Get stuff from command line ==========

    def usage():
        print "Usage: ......  "
        sys.exit(1)

    # e.g. 

    try:
        infile1 = sys.argv[1]
        infile2 = sys.argv[2]
        

        
    except:
        usage()
    """
    db = Speech_Corpus_Labels("/afs/inf.ed.ac.uk/user/s06/s0676515/pr/whole_system/oct_21_test/align/alignment/aligned.4.mlf", filetype="mlf")

    
    db.add_skip_field(6)
    db.add_positional_fields()  ## Start at 0 for 1st subunit in unit; don't let junctures (_SPACE_, _COMMA_ etc
                    ## contribute to counts)



    db.add_neighbour_field_with_ignores( "segment", -2, "LL_seg", ignores=["skip"])
    db.add_neighbour_field_with_ignores( "segment", -1, "L_seg", ignores=["skip"])
    db.add_neighbour_field_with_ignores( "segment", +1, "R_seg", ignores=["skip"])
    db.add_neighbour_field_with_ignores( "segment", +2, "RR_seg", ignores=["skip"])

    ## Contexts ignoring the _SPACE_ word junctures; _COMMA_ and other punc. is used though.
    ## These are for general use in state tying. 
    db.add_neighbour_field_with_ignores( "word", -1, "L_word", ignores=["_DITTO_", '_SPACE_'])
    db.add_neighbour_field_with_ignores( "word", +1, "R_word", ignores=["_DITTO_", '_SPACE_'])

    ## Contexts including the _SPACE_ word juncture; this will be used for VSM tagging and then
    ## prediction of pause at junctures.
    #db.add_neighbour_field_with_ignores( "word", -2, "LL_word_junct", ignores=["_DITTO_"])        
    db.add_neighbour_field_with_ignores( "word", -1, "L_word_junct", ignores=["_DITTO_"])
    db.add_neighbour_field_with_ignores( "word", +1, "R_word_junct", ignores=["_DITTO_"])
    #db.add_neighbour_field_with_ignores( "word", +2, "RR_word_junct", ignores=["_DITTO_"])

    # db.print_segments()
    # 
    
    # sys.exit(1)
    ##db.add_silence_durations()  ## <-- this seems broken, but not necessary -- just use juncture durations
    #



    letter_vsm = "/afs/inf.ed.ac.uk/user/s06/s0676515/pr/whole_system/oct_21_test/vsm/letter/vsm1_250_50"
    db.vsm_tag_field( "LL_seg", letter_vsm, "LL_seg_vsm", 5 ,  to_pad=["_NULL_", "sil", "skip"])
    db.vsm_tag_field( "L_seg",  letter_vsm, "L_seg_vsm", 5 ,  to_pad=["_NULL_", "sil", "skip"])
    db.vsm_tag_field( "segment", letter_vsm, "C_seg_vsm", 5 ,  to_pad=["_NULL_", "sil", "skip"])
    db.vsm_tag_field( "R_seg",  letter_vsm, "R_seg_vsm", 5 ,  to_pad=["_NULL_", "sil", "skip"])   
    db.vsm_tag_field( "RR_seg",  letter_vsm, "RR_seg_vsm", 5 ,  to_pad=["_NULL_", "sil", "skip"]) 


        
    ## TO DO: reading the VSM models takes time -- best not to do this 3 times.
    word_vsm = "/afs/inf.ed.ac.uk/user/s06/s0676515/pr/whole_system/oct_21_test/vsm/word/vsm1_250_50"    
    db.vsm_tag_field( "L_word", word_vsm, "L_word_vsm", 50 ,  to_pad=["_NULL_", "sil", 'XendX'])
    db.vsm_tag_field( "word",   word_vsm, "C_word_vsm", 50 ,  to_pad=["_NULL_", "sil", 'XendX'])        
    db.vsm_tag_field( "R_word", word_vsm, "R_word_vsm", 50 ,  to_pad=["_NULL_", "sil", 'XendX'])      
    
    db.write_table("/afs/inf.ed.ac.uk/user/s06/s0676515/proj/whole_system/test.dat")  ## make fields optional, fields=[""])
    sys.exit(1)
    
    
    #db.print_segments()
    #sys.exit(1)
              

    m = db.fields
    print m
    db.write_table("/afs/inf.ed.ac.uk/user/s06/s0676515/proj/whole_system/test.dat")  ## make fields optional, fields=[""])
    

    
    #################################################
    
 
    
def htk_to_ms(htk_time):
    """
    Convert time in HTK (100 ns) units to ms
    """
    return htk_time / 10000.0

def ms_to_htk(ms_time):
    """
    Convert time in ms to HTK (100 ns) units 
    """
    return ms_time * 10000.0
    
        
def readlist(filename, uni=True):
    if uni:
        f = codecs.open(filename, encoding='utf-8')
    else:    
        f = open(filename, "r")
    data = f.readlines()
    f.close()
    data = [line.strip("\n\r") for line in data]
    return data

    
def writelist(data, filename):
    data=[str(x) for x in data]
    f = open(filename, "w")
    data = "\n".join(data) ## +  "\n"
    f.write(data)
    f.close()

def keep_numeric(seq):
    """Remove items from a sequence that are not float or int
    """
    data = [item for item in seq if (isinstance(item, int)) or (isinstance(item, float))]
    return data

def all_numeric(seq):
    """Test if all items in a sequence are float or int
    """
    test_value = True
    for item in seq:
        if not (isinstance(item, int)) and not (isinstance(item, float)):
            test_value = False
    return test_value
    
def interleave(seq_a, seq_b):
    """Take e.g. [1,2,3] and [5,6,7], return
    [1,5,2,6,3,7]
    """
    assert len(seq_a) == len(seq_b),"To interleave, seqs must be same length"
    interleaved = []
    for (a, b) in zip(seq_a, seq_b):
        interleaved.append(a)
        interleaved.append(b)
    return interleaved

def unpickle_data(fname):    
    print '  *** unpickle_data *** '
    assert os.path.isfile(fname),'File %s doens\'t exist'%(fname)
    
    ##     data = cPickle.load(file(fname)) 
    
    f=open(fname, "r")
    data = cPickle.load(f)
    f.close() 
    return data

def basename(fname):
    """Remove leading path name and extension
    """
    junk,fname = os.path.split(fname)
    fname = re.sub("\.[^\.]+\Z", "", fname)
    return fname

    
###!!! duplicated from train vsm script -- where to put these general utility functs?
####   ^---- Now, modified in this version
def read_text_corpus(fname, uni=True):

    data = readlist(fname, uni=uni)
    
    data=[line.strip("\n ") for line in data]
    data=[re.split("\s+", line) for line in data]
    text=[]
    for line in data:
        text.extend(line)    
    return text

def read_lettermap(fname, uni=True):
    data = readlist(fname, uni=uni)
    data = [line.strip(" \t") for line in data]
    data = [item for item in data if item != ""]    
    data = [re.split("\s+", line) for line in data]
    
    for pair in data:
        assert len(pair)==2,"%s doesn't have 2 elements"%(pair)
    data = dict(data)
    return data


def make_safe_text(text, letter_list, punc_list, skip_spaces=False, burst_to_letters=False, uni=True):
    """
    Take list of words.
    
    Replace letters / punc as user specifies in letter_list and punc_list.
    For letters, this could include lowercasing and making accented chars safe for HTK.
    For punc, this means making things safe for HTK.
    
    Return 2 lists and a dict:
       1) with plain subsititutions as in letter_list and punc_list
       2) Dict: mapping from words to naive pronunciations
       
    -- use keyword args skip_spaces and burst_to_letters to work over letters, not words
    """

    def all_punc(string, punc_map):
        """
        Are all chars of string in punc_map?
        [unused?]
        """
        value = True
        for char in list(string):
            if char not in punc_map:
                value = False
        return value            

    def make_safe(word, mapping):
        """
        Substitute chars in word according to mapping.
        Return list of mapped chars and that list joined into a word.
        """

        letters = [mapping[char] for char in list(word.lower())]
        word = "".join(letters)
        return (letters, word)
        
    ###letter_map = read_lettermap(letter_list)
    punc_map = read_lettermap(punc_list, uni=uni)   
    
    punc_map[" "] = "_SPACE_"
    
    all_map = read_lettermap(letter_list, uni=uni) ## 1 map for letter AND punc combined
    all_map.update(punc_map)
    
    
    
    lex = {}
    outtext = []
    for word in text:
        if skip_spaces and word == " ":
            pass
        else:   
            (letters, safe_word) = make_safe(word, all_map)
            lex[safe_word] = letters
            if burst_to_letters:
                safe_word = " ".join(letters)
            outtext.append(safe_word)
            
    return outtext, lex

     
     
       
        
    
             
def naive_tokenise(string, letter_map, punc_map):
    """
    Very simple tokenisation -- separate at whitespace; where punc character 
    comes between letter and space, split it off. 
    
    Where space follows punc, don't keep the space.
    [Combine double punctuations.]
    
    Assume a symbol is punc if it's not in letters.txt.
    """
    
#    string = re.sub("\s+", "_SPACE_", string)
    
    
    string =  string + " "   ## so e.g. final stops are tokenised -- take it off at the end


    letter_before  = "(?<=["  +   "".join(letter_map.keys())   + "])"  
    letter_after   = "(?=["   +   "".join(letter_map.keys())   + "])"        
    puncs   = "[^" +   "".join(letter_map.keys())   + "\s]+"   ## punc = not letter or whitespace

    
    
    letter = "["  +   "".join(letter_map.keys())   + "]"  
    nonletter = "[^"  +   "".join(letter_map.keys())   + "]"  
    space = "\s"
    
    def before(s):
        return "(?<=" + s + ")"
    def after(s):
        return "(?=" + s + ")"
        
    tokeniser =   "("  + before(letter) + nonletter + "+" + space + "+" +  "|" +  \
                 space + "+"    + nonletter + "+" + after(letter)   +  "|" +  \
                 space + "+"    + nonletter + "+" + space + "+" +  "|" +  \
                 space + "+)"           
    
    string = re.split(tokeniser, string)
    
    string = [item.strip(" ") for item in string]
    outstring = []
    for item in string[:-1]:   ### -1 takes off appebnded space
        if item == "":
            outstring.append(" ")
        else:
            outstring.append(item)                
    return outstring            
        
    

    
def parse_uttsdata(fname):
    """
    Take contents of Festival utts.data format file
    Return list of pairs: [(name, text), ... ]
    """
 #   f = open(fname, "r")
  #  data = f.readlines()
   #     f.close()
    out_data = []
    for line in data:
        name,text,junk = re.split('"', line)
        name = name.strip(" ()")    
        out_data.append((name, text))
    return out_data

    
def read_uttsdata(fname, uni=True):
    """
    Take contents of Festival utts.data format file
    Return list of pairs: [(name, text), ... ]
    """
    
    data = readlist(fname, uni=uni)

    out_data = []
    for line in data:
        name,text,junk = re.split('"', line)
        name = name.strip(" ()")    
        out_data.append((name, text))
    return out_data

def read_feature_lexicon(lemma_fname, feat_fname, dims_to_keep=0):
    """
    default dims_to_keep = 0 means keep all
    """
    print "reading " + feat_fname + " and " + lemma_fname+ " ..."
    lex={}
    lemmas=readlist(lemma_fname)
    feats=readlist(feat_fname)

    feats = [re.split("\s+", line) for line in feats]
    
    if dims_to_keep > 0:
        feats = [line[:dims_to_keep] for line in feats]
    
    nfeat=len(feats[0]) ## assume all lines are same length

    assert len(feats) == len(lemmas),"n features and n lemma is different"
    
    for (lemm,feat) in zip(lemmas, feats):
        lex[lemm] = [float(item) for item in feat]
    return lex, nfeat          


    

class Speech_Corpus_Labels:
    """
    
    point_number field is added -- this is to provide unique identifier for rows,
    
    min_sil_dur -- if 0, impose no minimum duration
    """
    def __init__(self, in_file, filetype="table", lettermap="", puncmap=False, min_sil_dur=0):
        assert os.path.isfile(in_file),"%s is not a file"%(in_file)
        
        self.special_symbols = ["_DITTO_", "_NA_"]

        self.questions = []

        self.questions_made_for_field = []
        
        self.in_file = in_file

        self.make_field_symbols()

        if puncmap:
            self.punctuation_map_fname = puncmap
            self.punctuation_map = read_lettermap(puncmap)
        if lettermap:
            self.letter_map_fname = lettermap        
            self.letter_map = read_lettermap(lettermap)
            
            
        if filetype == "mlf":
            self.init_from_mlf(min_sil_dur=min_sil_dur)  ## sets (self.segs, self.fields)
        elif filetype == "uttsdata":
            self.init_from_uttsdata()                
        elif filetype == "table":
            self.init_from_table() ## (self.segs, self.fields) 
        elif filetype == "pickle":
            self.init_from_pickle(['discretisers', 'field_map', \
                   'fields', 'segs', 'questions', 'questions_made_for_field']) 
                    #The arg gives things we will try to load from pickled Labels
        else:
            print "Unknown filetype"
            sys.exit(1)

        self.set_field_map()  ## derive from fields -- repeat this when fileds is altered    
        
        if "point_number" not in self.field_map:  
            self.append_column(range(len(self.segs)), "point_number") 
     
    def init_from_uttsdata(self):
        """
        Used for making labels from run-time text
        """
        utts = read_uttsdata(self.in_file)
                  
        speech_data = []  ## collect segment lines here, as in init_from_mlf :-- 
                ## (utt_name, seg_number, int(start), int(end), int(length), segment,word)


        ## Make list of punc
        punctuation = []          
        if self.punctuation_map:
            for item in self.punctuation_map.values():
                if item not in punctuation:
                    punctuation.append(item) 

        lex = {}
        for (name, text) in utts:
            #print name
            #print text
            
         
            
            text = naive_tokenise(text, self.letter_map, self.punctuation_map)
            #print text
            
            (text, sentence_lex) = make_safe_text(text, self.letter_map_fname, self.punctuation_map_fname)  # LEX INCLUDES _SPACE_ SYMBOLS

            sentence_lex["_UTTEND_"] = ["sil"]
            sentence_lex["_SPACE_"] = ["skip"]  ## init as skip, then replace later by prediction from CART
            
            for item in punctuation:
                sentence_lex[item] = ["sil"] ## init as sil, then replace later by prediction from CART
            
            
            
            text = ["_UTTEND_"] + text + ["_UTTEND_"]
            
            i = 0 ## line counter
            start = 0
            length = 10 ## arbitrary dummy segment length
            end = start + length
            for word in text:
                first_letter = True
                for letter in sentence_lex[word]:
                    if first_letter:
                        word_string = word
                    else:
                        word_string = "_DITTO_"    
                    line = [name, i, start, end, length, letter, word_string]
                    i += 1
                    start += length
                    end += length
                    speech_data.append(line)
                    first_letter = False

#        for line in speech_data:
#            print line
        #sys.exit(1)

        fields = ["utt_name", "points_since_utt_start",  "start", "end" ,"length", "segment", "word"]
       
        self.segs = speech_data
        self.fields = fields
        self.set_field_map()
       
       




    def set_init_data(self): 
        """
        Initialise self.init_data from self.inf_file
        """          
        f = open(self.in_file, "r")
        self.init_data = f.readlines()
        f.close()
                   
    def print_segments(self):
           # print "Db: %s"%(mlf_file)
        for line in self.segs:
            print line
        print                 
    def init_from_mlf(self, min_sil_dur=0):
        """
        Read mlf like: 
        #!MLF!#
        "*/rjs_01_0001.rec"
        0 2220000 sil XendX
        2220000 3400000 s surprisingly
        3400000 3860000 u
        3860000 3920000 r
        [...]
        48180000 48420000 r
        48420000 51100000 sil XendX
        .
        "*/rjs_01_0002.rec"
        0 2380000 sil XendX
        2380000 3140000 u using
        3140000 3840000 s
        [...]
        """
        print "        *** read_mlf ***"
        self.set_init_data()

        data = [line.strip(" \n") for line in self.init_data]
        data = data[1:]                 ## cut off #!MLF!#
        name_patt = re.compile('\A"\*/.+"\Z')

        ## first get utts as lists of strings:
        utts = {}
        for line in data:
            if re.match(name_patt, line):
                utt_name = line
                utt_name = utt_name.strip('*"/') ## clean   "*/rjs_01_0100.rec"   -->   rjs_01_0100.rec
                utts[utt_name] = []
            elif line == ".":
                pass
            else:
                utts[utt_name].append(line)
                
        ## then parse the utts:
        speech_data = []
        for utt in sorted(utts.keys()):
            speech_data.extend( self.parse_utt(utts[utt], utt)  )                            
        fields = ["utt_name", "points_since_utt_start",  "start", "end" ,"length", "segment", "word"]
       
        self.segs = speech_data
        self.fields = fields
        self.set_field_map()
       
       
    def add_juncture_field(self):      
        ## Mark junctures as such
        junctures = ["_SPACE_", "_COMMA_"]  
        
        ## ADD OTHER PUNCTS if puncmap has been given at init:
        if self.punctuation_map:
            for item in self.punctuation_map.values():
                if item not in junctures:
                    junctures.append(item)
                    
        values = [(line[self.field_map["word"]] in junctures) for line in  self.segs]
        self.append_column(values, "is_juncture")
        
        
    def add_break_type_field(self):
        
        ## add a field to distinguish {no juncture, junc with break, junc with no break
        
        assert "is_juncture" in self.field_map
        
        values = []
        for line in self.segs:
            if line[self.field_map["is_juncture"]]:
                if line[self.field_map["length"]] > 0.0 and line[self.field_map["segment"]] == "sil":
                    values.append("B")
                else:
                    values.append("NB")
            else:
                values.append("_NA_")               
        self.append_column(values, "break_type")
        
    def add_dummy_break_type_field(self):
        
        ## This is a placeholder, necessary for passing test data through the rpart script
        ## NB for juncturesm _NA_ otherwise
        ## Field is named "break_type"
        
        assert "is_juncture" in self.field_map
        
        values = []
        for line in self.segs:
            if line[self.field_map["is_juncture"]]:
                values.append("NB")  ##
            else:
                values.append("_NA_")               
        self.append_column(values, "break_type")
        
                        
        
    def parse_utt(self, utt_strings, utt_name):
        """
        Take list of strings like: 
        ['0 2000000 sil XendX', '2000000 2340000 h he', '2340000 3080000 e', 
        '3080000 3800000 m moved', '3800000 4980000 o', ...
        
        Return list of 4-tuples:
        [(0, 2000000, 'sil', 'XendX'), (2000000, 2340000, 'h', 'he'), (2340000, 3080000, 'e', '_DITTO_'), 
        (3080000, 3800000, 'm', 'moved'), (3800000, 4980000, 'o', '_DITTO_'), ...
        
        NOW RETURNS LIST OF 7-TUPLES: utt_name, seg_number, int(start), int(end), int(length), segment,word
        
        """    
        utt = [re.split("\s+", line) for line in utt_strings] ## split lines on whitespace
        
        parsed_utt = []
        
        for (seg_number,line) in enumerate(utt):
            if len(line)==3:
                (start,end,segment) = line
                word = "_DITTO_"
            elif len(line)==4:
                (start,end,segment,word) = line
            else:
                print "Bad line length:"
                print line
                sys.exit(1)    
            end = htk_to_ms(int(end))
            start = htk_to_ms(int(start))                
            length = end - start
            parsed_utt.append([utt_name, seg_number, int(start), int(end), int(length), segment,word])
        return parsed_utt


    def recode_as_dummy(self, field_name):
        """
        for a categorical variable with n outcomes, make n new columns 
        named <filed_name>_is_<outcome>, with values 
        """
        values = self.extract_column(field_name)
        outcomes = set(values)
        for outcome in outcomes:
            outcome_values = [str(value==outcome).upper() for value in values]  ## make R boolean from python one
            self.append_column(outcome_values, field_name + "_is_" + outcome)


    def init_from_table(self, sep=","):
        self.set_init_data()
        data=[line.strip("\t \n") for line in self.init_data]
        if sep=="WHITESPACE":
            data=[re.split("\s+",line) for line in data]
        else:    
            data=[line.split(sep) for line in data]
        self.fields = data[0]
        self.segs = data[1:]
        

    def pickle(self, outfile):    
                
        f = open(outfile, "w")
        cPickle.dump(self, f)
        f.close()
        

    def init_from_pickle(self, crucial_fields):    
                
        unpickled = unpickle_data(self.in_file) ## was self =  ...
        for field in crucial_fields:
            if hasattr(unpickled, field):
                setattr(self, field, getattr(unpickled, field))
                
        


    def write_table(self, fname, sep=",", rows=None, keep_fields=None):

        """ This is the funct used also for writing R data
        for other purposes, pickle the database  to preserve any data apart from the table
        itself (discretisation functions etc.)
        """    
    
        def select_fields(line, numbers):
            return [item for (i, item) in enumerate(line) if i in numbers]
            
                
        f=open(fname, "w")
        if keep_fields:
            numbers = [self.field_map[fld] for fld in keep_fields]           
            header = sep.join(select_fields(self.fields, numbers)) + "\n"
                
        else:  ## write all  
            header = sep.join(self.fields) + "\n"            
        f.write(header)
        
        if not rows:
            rows = range(len(self.segs))
        
        rows = dict(zip(rows, rows))    ## dict for quick lookup
      
        for (i, line) in enumerate(self.segs):
            if i in rows:
                if keep_fields:
                    line=sep.join([str(x) for x in select_fields(line, numbers)]) + "\n"
                else:
                    line=sep.join([str(x) for x in line]) + "\n"
                f.write(line)
        f.close()
        
    def set_field_map(self):
        """
        Set field_map which maps from field name to field number.
        Do this on the fly in case fields change.
        """
        self.field_map = dict([(field, i) for (i, field) in enumerate(self.fields)])  
              
    def add_skip_field(self, ms_threshold):

        values = []
        for line in self.segs:
            if line[self.field_map["length"]] == ms_threshold:
                values.append("EPSILON") 
            else:
                values.append("KEEP")
        self.append_column(values, "SKIP_SEGMENT")


    def cancel_short_silences(self, ms_threshold):
            
        values = [] ## replacemnt "segment" field
        for (i, line) in enumerate(self.segs):
            if (line[self.field_map["length"]] < ms_threshold) and (line[self.field_map["word"]] != "_UTTEND_") \
                         and (line[self.field_map["segment"]] == "sil"):
                values.append("skip") 
            else:
                values.append(line[self.field_map["segment"]] )
        self.overwrite_column(values, "segment")
        
        
    def add_positional_fields(self):
        ### points_since_utt_start is made at initiliastion, but htis includes counts for junctures
        ### But we will use 0 in points_since_utt_start to mean a new utt starts.
         
        ## words from utterance:
        ##     - forwards
        
        
        ## 1) segs from utt start:
        values = []
        i = 0
        for line in self.segs:
            values.append(i)
            if line[self.field_map["word"]] not in ["_UTTEND_", "_SPACE_"]:
                i+=1 
            if line[self.field_map["points_since_utt_start"]] == 0:
                i=0             
        self.append_column(values, "segs_since_utt_start")   
        
             
        ## 1) segs from word start:
        values = []
        i = 0
        for line in self.segs:
            if line[self.field_map["word"]] != "_DITTO_":
                i = 0
            values.append(i)
            i+=1 
        self.append_column(values, "segs_since_word_start")
        
        ## words_since_utt_start
        values = []
        i = 0
        for line in self.segs:
            if (line[self.field_map["points_since_utt_start"]] == 0) and (line[self.field_map["word"]]=="_UTTEND_"):
                i=0 ## reset       
                values.append(i)     
            elif line[self.field_map["word"]] not in ["_DITTO_", "_SPACE_"]:
                values.append(i)
                i+=1                    
            else:
                values.append("_DITTO_")     
        self.append_column(values, "words_since_utt_start")

        
        ### backwards:
        # seg in utt
        values = []
        i = 0
        for line in reversed(self.segs):
            values.append(i)
            if line[self.field_map["word"]] not in ["_UTTEND_", "_SPACE_"]:
                i+=1 
            if line[self.field_map["points_since_utt_start"]] == 0:
                i=0
        values.reverse()                
        self.append_column(values, "segs_till_utt_end")

        # word in utt  
        values = []
        i = 0
        zero_next_time=False
        for line in reversed(self.segs):

            if zero_next_time:
                i=0
                zero_next_time=False
            if (line[self.field_map["points_since_utt_start"]] == 0) and (line[self.field_map["word"]=="_UTTEND_"]):
                zero_next_time=True
                values.append(i)                         
            elif line[self.field_map["word"]] not in ["_DITTO_", "_SPACE_"]:
                values.append(i)            
                i+=1
            else:
                values.append("_DITTO_")     
        values.reverse()                  
        self.append_column(values, "words_till_utt_end")
               

        
        # seg in word
        values = []
        i = 0
        for line in reversed(self.segs):
            values.append(i)
            i+=1 
            if line[self.field_map["word"]] != "_DITTO_":
                i=0
        values.reverse()                
        self.append_column(values, "segs_till_word_end")




        #### PUNTUATION DISSTASNCES --- this will be used for predicting breaks
        ## words since punc
        values = []
        i = 0
        for line in self.segs:
            if line[self.field_map["word"]] in self.punctuation_map.values():
                i = 0

            if (line[self.field_map["points_since_utt_start"]] == 0) and (self.field_map["word"]=="_UTTEND_"):
                i=0 ## reset 
                values.append(i)                  
            elif line[self.field_map["word"]] not in ["_DITTO_", "_SPACE_"]:
                values.append(i)            
                i+=1
            else:
                values.append("_DITTO_")                     
        self.append_column(values, "words_since_punctuation")


        ## words till punc
        values = []
        i = 0
        for line in reversed(self.segs):
            if line[self.field_map["word"]] in self.punctuation_map.values():
                i = 0
                
            if (line[self.field_map["points_since_utt_start"]] == 0) and (self.field_map["word"]=="_UTTEND_"):
                i=0 ## reset 
                values.append(i)    
            if line[self.field_map["word"]] not in ["_DITTO_", "_SPACE_"]:
                values.append(i)            
                i+=1  
            else:
                values.append("_DITTO_")                                   
        values.reverse()                
        self.append_column(values, "words_till_punctuation")



    def add_length_fields(self):
        """Fields for length of word, utt
        """
        ## word length
        values = []
        for line in self.segs:
            if line[self.field_map["word"]] == "_UTTEND_" or line[self.field_map["is_juncture"]]:
                values.append("_NA_") 
            elif line[self.field_map["word"]] == "_DITTO_":
                values.append("_DITTO_")                 
            else:
                values.append(len(line[self.field_map["word"]]))    
        self.append_column(values, "word_length")

        ## utt length
        values = []
        for (i, line) in enumerate(self.segs):
            if line[self.field_map["points_since_utt_start"]] == 0:
                values.append(len(self.get_utterance_words(i))) 
            else:
                values.append("_DITTO_")                          
        self.append_column(values, "utterance_length")

        

    def add_distance_to_pause(self, ms_threshold=0):
        """Also add n words between pauses 
        """
        ## 1) segs from pause
        values = []
        i = 0
        for line in self.segs:
            ## reset:
            if line[self.field_map["segment"]] == "sil" and ((float(line[self.field_map["length"]]) > ms_threshold) or \
                             (line[self.field_map["word"]])=="_UTTEND_"):
                i = 0
            ## record:                
            if line[self.field_map["segment"]] != "skip":
                values.append(i)
                i += 1
            else:
                values.append("_NA_")                  
        self.append_column(values, "segs_since_pause>%sms"%(ms_threshold))   
        
             
        ## 2) segs till pause
        values = []
        i = 0
        for line in reversed(self.segs):
            if line[self.field_map["segment"]] == "sil" and ((float(line[self.field_map["length"]]) > ms_threshold) or \
                             (line[self.field_map["word"]])=="_UTTEND_"):
                i = 0
            if line[self.field_map["segment"]] != "skip":
                values.append(i)
                i += 1
            else:
                values.append("_NA_")     
        values.reverse()                     
        self.append_column(values, "segs_till_pause>%sms"%(ms_threshold))    
        
        ## 3) words from pause
        values = []
        i = 0
        for line in self.segs:
            ##resetting:
            if line[self.field_map["segment"]] == "sil" and ((float(line[self.field_map["length"]]) > ms_threshold) or \
                             (line[self.field_map["word"]])=="_UTTEND_"):
                i = 0
            ##recording:
            if line[self.field_map["word"]] != "_DITTO_" and not line[self.field_map["is_juncture"]]: # 

                if line[self.field_map["segment"]] != "skip":
                    values.append(i)
                    i += 1
                else:
                    values.append("_NA_")    
            else:                     
                values.append("_DITTO_")
        self.append_column(values, "words_since_pause>%sms"%(ms_threshold))   
        
             
        ## 4) words till pause
        values = []
        i = 0
        for line in reversed(self.segs):
            ##resetting:
            if line[self.field_map["segment"]] == "sil" and ((float(line[self.field_map["length"]]) > ms_threshold) or \
                             (line[self.field_map["word"]])=="_UTTEND_"):
                i = 0
            ##recording:
            if line[self.field_map["word"]] != "_DITTO_" and not line[self.field_map["is_juncture"]]: # 

                if line[self.field_map["segment"]] != "skip":
                    values.append(i)
                    i += 1
                else:
                    values.append("_NA_")    
            else:                     
                values.append("_DITTO_")
        values.reverse()        
        self.append_column(values, "words_till_pause>%sms"%(ms_threshold))   
        
    def get_spurt_length(self, ms_threshold=0):
        assert "words_since_pause>%sms"%(ms_threshold) in self.field_map
        assert "words_till_pause>%sms"%(ms_threshold) in self.field_map
        values = []
        for line in self.segs:
 
            if line[self.field_map["words_since_pause>%sms"%(ms_threshold)]] == 0:
                values.append(line[self.field_map["words_till_pause>%sms"%(ms_threshold)]])   
            else:                     
                values.append("_DITTO_")
        self.append_column(values, "spurt_length_pauses>%sms"%(ms_threshold))   
        

    def get_neighbour_feature(self, seq,sent,offset, element_length=1): 
        out=[]
        for i in range(len(seq)):  #sym,num in :
            this_sent=sent[i]
            #print "--------"
            #print i
            #print i + offset
            if i + offset  < 0 or i + offset > len(seq)-1:
                neigh_sent=""  
            else:              
                neigh_sent=sent[i+offset]
                neigh=seq[i+offset]
            padding = "_NULL_"    
            ##if element_length > 1:
            ##    padding = ["_NULL_"] *  element_length
            if this_sent != neigh_sent:
                out.append(padding)
            else:
                out.append(neigh)      
        return out  
            
    def add_neighbour_field_OLD(self, c_feature, offset, new_field_name): 
        """
        Derive new field as a time-shifted version of an existing one:
        E.g. if c_feature is centre phone, offset -1 gets L phone.
        Pad with _NULL_ beyond sentence boundaries.
        Treat sil etc as normal phones.            
        """        
        current=self.extract_column(c_feature)
        sentence=self.extract_column("utt_name")
            
        ##### debug:
        if (False):
            print "--------- debugging ---------"
            current=['n', 'a', 'h', 'f', 'r', 'e', 's', 's']
            sentence=['1', '1', '1', '2', '2', '2', '2', '2']
            offset=-2
            n=self.get_neighbour_feature(current,sentence,offset)
            print n
            ## ['a', 'h', '_NULL_', 'r', 'e', 's', 's', '_NULL_'] <-- correct
            
            offset=+1
            n=self.get_neighbour_feature(current,sentence,offset)
            print n
            ## ['a', 'h', '_NULL_', 'r', 'e', 's', 's', '_NULL_'] <--- coreect

            
            sys.exit(1) 

        #print current[:10]
        #print sentence[:10]
        neighbour=self.get_neighbour_feature(current,sentence,offset)
        #print neighbour[:10]
        self.append_column(neighbour, new_field_name)
   
    def add_ditto_neighbour_field( self, c_feature, offset, new_field_name): 
        """
        As add_neighbour_field, except we will ignore "_DITTO_" symbol
        which is added as padding when e.g. a word is only added to the 
        first phone of a word.
        """
        current=self.extract_column(c_feature)
        sentence=self.extract_column("utt_name")
        numbers =  self.extract_column('point_number')  ## corpus-level point numbers for putting things back in.
        
        ## remove ditto entries
        no_ditto = [(feat, sent, number) for (feat, sent, number) in zip(current, sentence, numbers) if feat != "_DITTO_"]  
        sentence = [sent for (feat, sent, number) in no_ditto]
        features  = [feat  for (feat, sent, number) in no_ditto]
        numbers  = [number for (feat, sent, number) in no_ditto]

        ##### debug:
        if (False):
            print "--------- debugging ---------"
            current=['it', '_DITTO_', 'is', '_DITTO_', 'now', '_DITTO_', '_DITTO_']
            sentence=['1', '1', '1', '1', '2', '2', '2']
            numbers = [1,2,3,4,5,6,7]
                
            ## remove ditto entries
            no_ditto = [(feat, sent, number) for (feat, sent, number) in zip(current, sentence, numbers) if feat != "_DITTO_"]  
            sentence = [sent for (feat, sent, number) in no_ditto]
            features_numbers = [(feat, number) for (feat, sent, number) in no_ditto]            
            print no_ditto
            print sentence
            print features_numbers
            
            offset=+1
            n=self.neighbour = self.get_neighbour_feature(features_numbers, sentence, offset, element_length=2)
            print n
            
            
            #    ## ['a', 'h', '_NULL_', 'r', 'e', 's', 's', '_NULL_'] <-- correct
             #   
              #  offset=+1
               # n=self.get_neighbour_feature(current,sentence,offset)
            #print n
            ## ['a', 'h', '_NULL_', 'r', 'e', 's', 's', '_NULL_'] <--- coreect

            
            sys.exit(1) 

       #     print features_numbers[:20]
      #  print sentence[:20]            
        ##### debug:
        print             
        print current[:20]
        print                 
        neighbour_feats = self.get_neighbour_feature(features, sentence, offset)
        
          #  print neighbour[:20]   
        print                   
           # print neighbour_feats[:20]
        print              
        #sys.exit(1)
        
        
        self.append_column(neighbour_feats, new_field_name, point_numbers=numbers)

    def add_neighbour_field( self, c_feature, offset, new_field_name, ignores=[]): 
        """
        Tovreplace both functions above and generalise
        
        We will ignore  symbols in the ignores list (typically things like "_DITTO_"
        which is added as padding when e.g. a word is only added to the 
        first phone of a word.)
        """
        current=self.extract_column(c_feature)
        sentence=self.extract_column("utt_name")
        numbers =  self.extract_column('point_number')  ## corpus-level point numbers for putting things back in.
        
        ## remove ditto entries
        no_ditto = [(feat, sent, number) for (feat, sent, number) in zip(current, sentence, numbers) if feat not in ignores]  
        sentence = [sent for (feat, sent, number) in no_ditto]
        features  = [feat  for (feat, sent, number) in no_ditto]
        numbers  = [number for (feat, sent, number) in no_ditto]

        ##### debug:
        if (False):
            print "--------- debugging ---------"
            current=['it', '_DITTO_', 'is', '_DITTO_', 'now', '_DITTO_', '_DITTO_']
            sentence=['1', '1', '1', '1', '2', '2', '2']
            numbers = [1,2,3,4,5,6,7]
                
            ## remove ditto entries
            no_ditto = [(feat, sent, number) for (feat, sent, number) in zip(current, sentence, numbers) if feat != "_DITTO_"]  
            sentence = [sent for (feat, sent, number) in no_ditto]
            features_numbers = [(feat, number) for (feat, sent, number) in no_ditto]            
            print no_ditto
            print sentence
            print features_numbers
            
            offset=+1
            n=self.neighbour = self.get_neighbour_feature(features_numbers, sentence, offset, element_length=2)
            print n
            
            
            #    ## ['a', 'h', '_NULL_', 'r', 'e', 's', 's', '_NULL_'] <-- correct
             #   
              #  offset=+1
               # n=self.get_neighbour_feature(current,sentence,offset)
            #print n
            ## ['a', 'h', '_NULL_', 'r', 'e', 's', 's', '_NULL_'] <--- coreect

            
            sys.exit(1) 
        
        neighbour_feats = self.get_neighbour_feature(features, sentence, offset)  
        self.append_column(neighbour_feats, new_field_name, point_numbers=numbers)


    def overwrite_column(self, column_values, field_name):
        """
        If there are not values for all rows, values will be added to rows specified in 
        point_numbers, otherwise "other_value" is added.
        """    
        assert field_name in self.field_map,"Database doesn't have a field called %s"%(field_name)

        assert len(column_values) == len(self.segs),"""New column has %s items, exising ones have %s
                                    """%(len(column_values), len(self.segs))
        column_number = self.field_map[field_name]
              
        #print "============"          
        #print self.segs[0]                            
        for i in range(len(self.segs)):
            #print "Overwrite %s with %s"%(self.segs[i][column_number], column_values[i])
            self.segs[i][column_number] = column_values[i] ## overwrite the appropriate value
       
        #print self.segs[0]               
        #print "============"          
                        
        ## We don't need to update field map

 
    def append_column(self, column_values, field_name, point_numbers=[], other_value="_DITTO_"):
        """
        If there are not values for all rows, values will be added to rows specified in 
        point_numbers, otherwise "other_value" is added.
        """    
        assert field_name not in self.field_map,"Database already has a field called %s"%(field_name)
        if len(point_numbers) == 0:
            assert len(column_values) == len(self.segs),"""New column has %s items, exising ones have %s
                                    """%(len(column_values), len(self.segs))
            for i in range(len(self.segs)):
                self.segs[i].append(column_values[i])
        else:
            assert   len(column_values) == len(point_numbers),"""New column has %s items, point numbers have have %s
                                    """%(len(column_values), len(point_numbers))
            point_value = dict(zip(point_numbers, column_values))
            #print point_value
            #sys.exit(1)
            for i in range(len(self.segs)):
                if i in point_value:
                    self.segs[i].append(point_value[i])
                else:
                    self.segs[i].append(other_value)                    
        self.fields.append(field_name)       
        self.set_field_map()  ## update field map

        
    def extract_column(self, field_name):
        """
        Return the values of the named field.
        """
        field_index = self.field_map[field_name]
        values = [line[field_index] for line in self.segs]
        return values
        
        
        
    def vsm_tag_field_OLD(self, field_to_tag, vsm_file, new_name, dims_to_keep, to_pad=[], to_ditto=["_DITTO_"]):
        """
        This is the version prior to the one using "shelved" VSMs
        """

        lex,nfeat=read_feature_lexicon(vsm_file+".lemma", vsm_file+".trans", dims_to_keep=dims_to_keep)


        to_tag = self.extract_column(field_to_tag)
        tagged = []
        for item in to_tag:
            #print item
            if item in lex:
                tagged.append(lex[item])
            elif item in to_ditto:
                tagged.append(["_DITTO_"]*dims_to_keep)                    
            elif item in to_pad:
                tagged.append(lex["_MEAN_"])
            else:
                
                #sys.exit(1)
                tagged.append(lex["_UNSEEN_"])  
        ## add the tags back as new fields:            
     #   header = ['"%s_d%s"'%(new_name, i) 
        for i in range(nfeat):
            
            header = "%s_d%s"%(new_name, i)   
            values = [line[i] for line in tagged] 
            self.append_column(values, header)



    def vsm_tag_field(self, field_to_tag, vsm_file, new_name, dims_to_keep, to_pad=[], to_ditto=["_DITTO_"]):
        """
        Work from "shelved" database
        """

        lex = shelve.open(vsm_file)
#        print lex
#        print lex["_MEAN_"]
#        print len(lex["_MEAN_"]        )
#        print "%%%"
        nfeat = len(lex["_MEAN_"])  ## chosen entry arbitrarily -- but we assume all entries are same length
        assert dims_to_keep <= nfeat

        to_tag = self.extract_column(field_to_tag)
        tagged = []
        for item in to_tag:
            item = str( item )  ## added for syntehsis -- otherwise unicode gives errror
            #print item
            if item in lex:
                features = [float(entry) for entry in lex[item][:dims_to_keep]]  ## Cos vsm script outputs strings (change this?)
                tagged.append(features)
            elif item in to_ditto:
                tagged.append(["_DITTO_"]*dims_to_keep)                    
            elif item in to_pad:
                tagged.append([float(entry) for entry in lex["_MEAN_"][:dims_to_keep]])
            else:  
                if "_UNSEEN_" in lex:
                    tagged.append([float(entry) for entry in lex["_UNSEEN_"][:dims_to_keep]])
                else:
                    print """    *** warning: function vsm_tag_field -- item %s unseen, but no _UNSEEN_ in %s, using _MEAN_ instead! ***
                            """%(item, vsm_file)
                    tagged.append([float(entry) for entry in lex["_MEAN_"][:dims_to_keep]])
        for i in range(dims_to_keep):
            
            header = "%s_d%s"%(new_name, i)   
            values = [line[i] for line in tagged] 
            self.append_column(values, header)
        
        lex.close()




    def get_utterance_words(self, i, exclude=["_DITTO_", "_SPACE_", "_UTTEND_"]):
        """
        Get list of words in utt, starting at point i in segments till end of utterance
        """
        words = []

        for (i, line) in enumerate(self.segs[i:]):
            #print line[self.field_map["words_till_utt_end"]]
            if line[self.field_map["word"]] not in exclude:
                words.append(line[self.field_map["word"]])        
            if line[self.field_map["words_till_utt_end"]] == 0:
                #print "------------------------"
                #print
                break
        return words
        

    def add_vsm_utterance_features(self,  vsm_file, new_name, dims_to_keep):
        """
        Add utt-level VSM features -- this is not a simple tagging -- utterances must be projected into the new space
        """
        lsi = models.LsiModel.load(vsm_file + ".lsi")
        dictionary = corpora.Dictionary.load(vsm_file + ".dict")
        tfidf = models.TfidfModel.load(vsm_file + ".tfidf")        
        vocab = readlist(vsm_file + ".vocab")     
        vocab = dict(zip(vocab, vocab))


        def get_most_freq_word_in_dictionary(dictionary):
            freq = 0
            word_id = False
            for (key,val) in dictionary.docFreq.items():
                if val > freq:
                    freq = val
                    word_id = key
            word = dictionary.id2token[word_id]
            return word

        ## The following will ony be used in the case of empty bag of words:
        most_freq_word = get_most_freq_word_in_dictionary(dictionary)
        empty_count = 0  ## only break if empty)_count gets larger than a thresh.
         
        padding = ["_DITTO_"] * dims_to_keep
        features = []
        for (i, line) in enumerate(self.segs):
            if line[self.field_map["points_since_utt_start"]] == 0:
                utterance = self.get_utterance_words(i)
                #print utterance
                utterance = [word for word in utterance if word in vocab]
#                print utterance
#                print dictionary
#                print dir(dictionary)
                bag_of_words = dictionary.doc2bow(utterance)
                
                if len(bag_of_words) == 0:
                    ## This happens with short utts with only weird words,
                    ## so that the bag of kept words is empty, e.g.:
                    ## (rjs_01_0340 "sportscar deconstruction")
                    ## Need to devise a good way to deal with these ones (some
                    ## special token). For now, we will just add the most
                    ## freq token in the dictionary.
                    ## Only break if the count of empty utts gets larger than a thresh. (10)
                    print "  'Empty' utterance:"
                    print "     " + str(self.get_utterance_words(i)) 
                    utterance = [most_freq_word]
                    bag_of_words = dictionary.doc2bow(utterance)
                    empty_count += 1
                #assert empty_count <= 40,"More than 60 'empty' utterances..."  
                if empty_count <= 20:
                    print "WARNING: More than 20 'empty' utterances..." 
                 
                               
#                print bag_of_words
                bow_tfidf = tfidf[bag_of_words]
#                print bow_tfidf
                bow_lsi = lsi[bow_tfidf]
#                print bow_lsi
                vsm_values = [value for (index, value) in bow_lsi]
#                print vsm_values
#                print dims_to_keep 
#                print len(vsm_values)
#                print "----------------"
                assert dims_to_keep <= len(vsm_values)

                features.append(vsm_values[:dims_to_keep])
            else:
                features.append(padding)
                
        for i in range(dims_to_keep):
            
            header = "%s_d%s"%(new_name, i)   
            values = [line[i] for line in features] 
            self.append_column(values, header)



    def add_silence_durations(self):
        assert "segs_till_word_end" in self.field_map,"Need field segs_till_word_end to add_silence_durations"
        values = []
        for line in self.segs:
            ## NB: sil segments are treated as words
            if line[self.field_map["segs_till_word_end"]] == 0:
                if line[self.field_map["segment"]] == "sil":
                    values.append(line[self.field_map["length"]])
                else:
                    values.append(0.0) ## 0.0 duration silence
        self.append_column(values, "pause_after_word")                            




    def expand_out_dittos(self):
        """
        In each field,  replace _DITTO_ with the nearest (upwards) non-_DITTO_ value.
        This is for use just prior to writing out R data and HTS labels.
        """
        print "Expand out _DITTO_ symbols..."
        for column_name in self.field_map.keys():
            column = self.extract_column(column_name)
            if "_DITTO_" in column:
                new_column = []
                ##print column[:10]
                assert column[0] != "_DITTO_","First item of field %s is _DITTO_ -- this shouldn't have happened"%(column_name)
                for item in column:
                    ##print item
                    if item != "_DITTO_":
                        last_good_item = item
                    if item == "_DITTO_":
                        new_column.append(last_good_item)
                    else:
                        new_column.append(item)                        
                self.overwrite_column(new_column, column_name)
        
    
    
    def match_fields(self, regex_field_patt):
        """find subset of fields that match the specifed pattern    """
        matched_fields = []            
        field_patt = re.compile(regex_field_patt)         
        for field in sorted(self.field_map.keys()):            
            if re.match(field_patt, field):
                matched_fields.append(field)
        return matched_fields
        
        
    def make_discretisers(self, regex_field_patt, number_bins=50, method="uniform"):
        """
        Methods of discretisation: uniform
                       standard_set -- (Breiman's name) put boundaries between 
                               each consecutive pair of values
                               -- ignore number_bins in this case
        """
        ## see ~/proj/distrib_pos/scripts/discretise_vsm.py  
        assert method in ["uniform","standard_set"],"Unknown method of discretisation"  ## add , "quantiles"
        
        if not hasattr(self, "discretisers"):
            self.discretisers = {}
            
        ##print regex_field_pattOSW
        fields_to_do = self.match_fields(regex_field_patt)
                
        for field in fields_to_do:   
            values = self.extract_column(field)
            self.discretisers[field] = Discretiser(values, field, number_bins=number_bins, method=method)
            

    def discretise_fields(self, regex_field_patt):
        """
        New field name will be field + "_DISC"            
        """
        assert hasattr(self, "discretisers")
        
        fields_to_do = self.match_fields(regex_field_patt)
                        
        for field in fields_to_do:
            discretiser = self.discretisers[field]
            values = self.extract_column(field)
                            
            disc_values = []
            for value in values:
                if value=="_DITTO_":
                    disc_values.append(value)
                else:
                    disc_values.append(discretiser.bin(value))

            self.append_column(disc_values, field + "_DISC")



#    def write_discretisers(self, outfile):
#        """
#        Write discretisers by pickling -- Redundant if we use pickle functions for whole DB
#        """
#        assert hasattr(self, "discretisers")
#        f = open(outfile, "w")
#        cPickle.dump(self.discretisers, f)
#        f.close()
#        
#    def load_discretisers(self, infile):
#        """
#        Redundant if we use pickle functions ...
#        """
#        assert not hasattr(self, "discretisers"),"Database already has discretisers loaded!"
#        self.discretisers = unpickle_data(infile)


    def get_field_questions(self, field):
        """
        For a field that does not have a discretiser, make a question name
        and values directly from its data.

        If the field has a discretiser, then get the (intelligibly named)
        questions from that object.

        Return questsions as strings in form of HTK itemlists.

        """
        assert hasattr(self, "discretisers")
        assert hasattr(self, "field_symbol_map")        
        original_field = field.replace("_DISC", "")
        if original_field in self.discretisers:
            questions = self.discretisers[original_field].get_questions()
        else:
            questions = []
            values = self.extract_column(field)
            values = [item for item in values if item not in ["_DITTO_", "_NA_"]] ## don't discard _NULL_ (end of sentence marker)
            values = list(set(values))  ## unique
            values.sort()
            if all_numeric(values):
                ##print "NUMERIC"
                for i in range(len(values)-1):
                    ## single point question -- specific first
                    question_name = field + "_=_" + str(values[i])
                    question_values = [values[i]]
                    questions.append((question_name, question_values))
                    ## range question -- more general last
                    question_name = field + "_<=_" + str(values[i])
                    question_values = range(values[i+1])
                    questions.append((question_name, question_values))
            else:
                ##print "NOT NUMERIC"
                for i in range(len(values)):
                    ## single point questions only
                    question_name = field + "_=_" + str(values[i])
                    question_values = [values[i]]
                    questions.append((question_name, question_values))                
        ## format questions into HTK string.
        question_strings = []
        for (question_name, question_values) in questions:
            question_values = ["*|%s:%s|*"%(self.field_symbol_map[field], value) for value in question_values]
            question_values = ",".join(question_values)
            question = "QS %s {%s}"%(question_name, question_values)
            question_strings.append(question)
        return question_strings




    def make_field_symbols(self):
        """Make a list of symbols to use -- these are to be popped off
        the front of the list as questions are made for the necessary fields.
        """
        self.field_symbols = []
        alphabet = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        
        for a in alphabet:
            self.field_symbols.append("%s"%(a)) 
        for a in alphabet:
            for b in alphabet:
                self.field_symbols.append("%s%s"%(a,b))  
        # Assume we will never have > 26^3 (17,576) fields  
        for a in alphabet:
            for b in alphabet:
                for c in alphabet:
                    self.field_symbols.append("%s%s%s"%(a,b,c))                  
#        for (i, field) in enumerate(self.fields):
#            self.field_symbols[field] = triples[i]
            

    def make_questions(self, regex_field_patt):
    
        """
        Make a set of questions relating to fields matching supplied 
        regex_field_patt. Empty lines are suffixed: this allows
        structuring of qfiles with empty lines by calling make questions
        several times.
        """
        print "Make questions -- %s"%(regex_field_patt)

        if not hasattr(self, "field_symbol_map"):
            self.field_symbol_map = {}
    
        fields_to_do = self.match_fields(regex_field_patt)
               
        for field in fields_to_do:
            self.field_symbol_map[field] = self.field_symbols.pop(0)
            self.questions_made_for_field.append(field)
            qq = self.get_field_questions(field)
            self.questions.extend(qq)
 
        self.questions.extend(["",""])


    def write_question_file(self, outfile, silences_question=False):
        """Write the database's currently stored questions to file
        """
        f = open(outfile, "w")
        
        if silences_question:
            f.write("QS C-silences {*-sil+*}\n\n\n")
        
        for line in self.questions:
            f.write(line + "\n")
        f.close()


    def write_HTS_labels(self, outdir, skip_epsilon=False, extra_fields=True, field_key_fname=False):

        """
        """
        assert os.path.isdir(outdir),"The directory %s does not exist"%(outdir)

        if extra_fields:
                assert "segment" in self.field_map
                assert "utterance_length" in  self.field_map
                
        current_utterance = basename(self.segs[0][self.field_map["utt_name"]])
        utterance_start_indexes = [(0, current_utterance)]

#        print self.segs[0]
#        print self.segs[0][self.field_map["utt_name"]]
#        print basename(self.segs[0][self.field_map["utt_name"]])

        for (i, line) in enumerate(self.segs):
            new_utterance = basename(line[self.field_map["utt_name"]])
            if new_utterance != current_utterance:
                current_utterance = new_utterance                
                utterance_start_indexes.append((i, new_utterance))
        
#        print utterance_start_indexes

        for (i, utt_name) in utterance_start_indexes:
#            print outdir
#            print utt_name
            utt_file = os.path.join(outdir, utt_name + ".lab")
            print "Writing label: " + utt_name
            self.write_HTS_label(i, utt_file, skip_epsilon=skip_epsilon, extra_fields=extra_fields)

        if field_key_fname:
            fields_to_keep =  self.questions_made_for_field
            separators = [self.field_symbol_map[field] for field in self.questions_made_for_field]
            key = ["%s\t%s\n"%(sep, fld) for (sep, fld) in  zip(separators, fields_to_keep)]
            f = open(field_key_fname, "w")
            for line in key:
                f.write(line)
            f.close()    

    def write_HTS_label(self, start_row, outfile, skip_epsilon=False, extra_fields=True):
        """Start at index start_row of segs and keep writing till utterance name changes.

        The labels will include all fields for which questions have been made.

        Rows that have segment=="skip",  will not be written, and optionally
        rows that are predicted epsilon.

        Start times will be recomputed by using previous segment's end time (to handle
        cases where segments with non-zero duration are skipped); we assume that all
        utterances start at 0.
        
        extra_fields means add -A+ and /J/B-B-B  where A is semgnet and B is utt length in words
        In this way, labels are compatible with junichi's scripts
        """

        fields_to_keep = [self.field_map[field] for field in self.questions_made_for_field]

        separators = ["|" + self.field_symbol_map[field] + ":" for field in self.questions_made_for_field]

        f = open(outfile, "w")

        old_utterance = self.segs[start_row][self.field_map["utt_name"]]

        start = 0
        for line in self.segs[start_row:]:
            current_utterance = line[self.field_map["utt_name"]]
            if old_utterance != current_utterance:
                break
            if line[self.field_map["segment"]] != "skip":
                line_out = [str(line[i]) for i in fields_to_keep] ## select fields
                line_out = interleave(separators, line_out) 
                line_out = "".join(line_out)  + "|"
                
                if extra_fields:
                        line_extra = [self.field_map[field] for field in ["segment", "utterance_length"]]
                        line_extra = [str(line[i]) for i in line_extra] 
                        (seg,utt) = line_extra
                        line_extra = "-%s+/J/%s-%s-%s"%(seg,utt,utt,utt)
                        line_out = line_out + line_extra
                
                end = int(ms_to_htk(line[self.field_map["end"]]))

                line_out = " %s %s %s\n"%(start, end, line_out)

                start = end ## re-init for next segment

                f.write(line_out)
        f.close()            
        
    def apply_pause_decision_tree(self, tree, new_field_name):
        """
        This should be made more general than just for pauses.
        Pauses placed at B -- arbitrary 100 ms
        """
        values = []
        for line in self.segs:
            if line[self.field_map["is_juncture"]]:
                values.append(tree.classify(line))
            else:
                values.append("_NA_")
        #print values
        self.append_column(values, "pause_predicted")     
        
        ## set up lengths appropriately:
        values = []
        for line in self.segs:
            if line[self.field_map["word"]] == "_UTTEND_" or  line[self.field_map["pause_predicted"]] == "B":
                values.append(100)
            else:
                values.append(line[self.field_map["length"]])
        #print values                        
        self.overwrite_column(values, "length")

        ## set up segments appropriately:
        values = []
        for line in self.segs:
            if line[self.field_map["word"]] == "_UTTEND_" or  line[self.field_map["pause_predicted"]] == "B":
                values.append("sil")
            elif line[self.field_map["pause_predicted"]] == "NB":
                values.append("skip")
            else:
                values.append(line[self.field_map["segment"]])
        #print values        
        self.overwrite_column(values, "segment")
                

                    
class Discretiser:
    def __init__(self, values, field_name, number_bins=50, method="uniform"):
        """
        Object to assign any real number to a numbered bin.
        
        Methods of discretisation: uniform
                       standard_set -- (Breiman's name) put boundaries between 
                               each consecutive pair of values
                               -- ignore number_bins in this case
                               
        """
        
        assert method in ["uniform","standard_set"],"Unknown method of discretisation"  ## add , "quantiles"

        ## only keep floats and ints:
#        print values[:50]
        values = keep_numeric(values)
#        print values[:50]

        self.bins = []
        self.field_name = field_name

        if method=="uniform":
                                 
            maxi = max(values)
            mini = min(values) 
            step = (maxi-mini) / float(number_bins)
                
            lower_edge = float("-inf") ## platform-specific behaviour pre-python 3?
            upper_edge = mini + step   
#            name = "%s_IS_LESS_THAN_%.3f"%(field, upper_edge) 
            for k in range(1, number_bins):
                self.bins.append((lower_edge, upper_edge, k))
                lower_edge = upper_edge
                upper_edge = upper_edge + step 
#                name = "%s_IS_BETWEEN_%.3f_AND_%.3f"%(field, lower_edge, upper_edge)  
            ## final bin        
            k = number_bins
            upper_edge = float("inf")
#            name = "%s_IS_MORE_THAN_%.3f"%(field, lower_edge)
            self.bins.append((lower_edge, upper_edge, k))

        if method=="standard_set":
            
            # Get sorted types
            values = list(set(values))
            if len(values) > 100:
                sys.exit("Using standard set for discretisation of %s gives %s bins!"%(field, len(values)))
            values.sort()

            lower_edge = float("-inf") ## platform-specific behaviour pre-python 3?
            for i in range(1,len(values)):

                ## diff in val between last and this one
                diff = values[i] - values[i-1]
                upper_edge = values[i] - (0.5 * (diff))
                self.bins.append((lower_edge, upper_edge, i))
                lower_edge=upper_edge
            ## final bin        
            i = len(values)
            upper_edge = float("inf")                
            self.bins.append((lower_edge, upper_edge, i))

        """   ### NOT IMPLEMENTED ------------
        if method=="quantiles":
            for j in range(n):   

                ## find bins over indexes:  
                bin_edges=[]       
                step=m / float(number_bins)
                binedge= step
                for k in range(number_bins-1):
                    binedge+= step
                    bin_edges.append(binedge)  
                
                ## discretise:               
                vals=feats[:,j]
                vals = vals.tolist()
                vals_order = zip(vals, range(len(vals)))
                vals_order.sort()
                order = [order for (val, order) in vals_order]
                order_rank = zip(order, range(len(order)))
                order_rank.sort()
                rank=[r for (o,r) in order_rank]
                
                for i in range(m):
                    disc_feats[i,j] = bin(rank[i], bin_edges)        
        """  
        
        
    def bin(self, value):
        
        for (lower_edge, upper_edge, bin_number) in self.bins:   
            if (value > lower_edge) and (value <= upper_edge):
                return bin_number
        sys.exit("No bin found -- something is wrong with the bin-set")


    def get_questions(self):
        """
        Return question names and values (values as Python lists, not formatted as HTK itemlists)
        """
        
        questions = []
        qnames = []  ## only used for finding duplicate names

        ## First get "single bin" questions:            
        for (lower_edge, upper_edge, bin_number) in self.bins[1:-1]:
            question_name = '%s_between_%.3f_and_%.3f'%(self.field_name, lower_edge, upper_edge) 
            question_values = [bin_number]
            
            ## Take care that there are no duplicate names by adjusting precision:
            if (question_name) in qnames:
                i = 4 ## starting value was 3
                while question_name in qnames:
                    format_string = '%%s_between_%%.%sf_and_%%.%sf'%(i, i)
                    question_name = format_string%(self.field_name, lower_edge, upper_edge) 
                    i += 1
                    
            questions.append((question_name, question_values))
            qnames.append(question_name)
            
        ## ... then get range questions:
        for (lower_edge, upper_edge, bin_number) in self.bins[:-1]:
            question_name = '%s_<=%.3f'%(self.field_name, upper_edge) 
            question_values = range(1, bin_number + 1)
            
            ## Take care that there are no duplicate names by adjusting precision:            
            if question_name in qnames:
                i = 4 ## starting value was 3
                while question_name in qnames:
                    format_string = '%%s_<=%%.%sf'%(i)
                    question_name = format_string%(self.field_name, upper_edge) 
                    i += 1            
                    
            questions.append((question_name, question_values))
            qnames.append(question_name)
            
        return questions
        
          
    
class Decision_tree:
    def __init__(self, fname, field_map):
        f = open(fname, "r")
        data = f.readlines()
        f.close()
        data = [line.strip(" \n") for line in data]
        data = [line.split(" ") for line in data if line[0] != "#"]
        self.field_map = field_map  ## maps from test variable names to indexes in input feature vectors        
        self.nodes = {}
        for (node, isleaf, question, yes_child, no_child, decision) in data:
            self.nodes[node] = Node(isleaf, question, decision, yes_child, no_child, self.field_map)

    def classify(self, data_line):
        current_node = "1"  ## RPART calls root node 1
        while self.nodes[current_node].isleaf == "False":
            current_node = self.nodes[current_node].node_decision(data_line)
        #print self.nodes[current_node].decision                
        return  self.nodes[current_node].decision


class Node:
    def __init__(self, isleaf, question, decision, yes_child, no_child, field_map):
        self.isleaf = isleaf ## string, not boolean!
        self.decision = decision
        self.yes_child = yes_child
        self.no_child = no_child
        
        ## 3 operations used in RPART trees (2 float, 1 category):
        def get_operation(string, value):
                if string == "<":
                        def operation(x):
                                return (x < float(value))
                elif string == ">=":
                        def operation(x):
                                return (x >= float(value))
                elif string == "=":
                        def operation(x):
                                return (x in ",".split(value))                                
                return operation     
                
        if self.isleaf == "False": ## string, not boolean!
            test_variable, comparison_string, value = re.split("(<|>=|=)", question)
            self.test_variable = test_variable
            self.comparison = get_operation(comparison_string, value)
            self.test_variable_ix = field_map[test_variable]
            
    def node_decision(self, features):    
        #print self.test_variable
        if self.comparison(features[self.test_variable_ix]):
            return self.yes_child
        else:
            return self.no_child    
                

  
        
                
if __name__=="__main__": 

    test_me()




