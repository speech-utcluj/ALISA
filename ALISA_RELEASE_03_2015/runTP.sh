#!/bin/sh
#################################################
## Author: Adriana STAN adriana.stan@com.utcluj.ro
## Project Simple4All - www.simple4all.org
## May 2012
## Edited: September 2014
#################################################
## This script runs all the steps for text processing
## Some of the steps require manual intervention, so please pay attention
set -e	

if [ $# -eq 0 ]
    then
    echo "[ERROR] You did not provide a configuration file"
    exit
fi
eval `grep "^OUTPUT" ./$1`
if [ -n "$OUTPUT" ] && [ -d $OUTPUT ]; then
    echo "OUTPUT FOLDER: " $OUTPUT
else
    echo "\n[ERROR] You did not specify an OUTPUT folder! \n\tNow exiting..."
    exit
fi
##
eval `grep "^FROMTPSTEP" ./$1`
echo "FROM STEP: " $FROMTPSTEP
eval `grep "^TOTPSTEP" ./$1`
echo "TO STEP: " $TOTPSTEP
##
eval `grep "^BOOK" ./$1`
if [ -n "$BOOK" ] && [ -f $BOOK ]; then
    FNAME=$(basename $BOOK )
    echo "FULL TEXT FILE: "$FNAME
else
    echo "\n[ERROR] You did not specify the BOOK file, or the file does not exist! \n\tNow exiting..."
    exit
fi
##
eval `grep "^INITIALTEXT" ./$1`
if [ -n "$INITIALTEXT" ] && [ -f $INITIALTEXT ]; then
    echo "INITIAL TEXT FILE: "$INITIALTEXT
else
    echo "\n[ERROR] You did not specify the INITIALTEXT file, or the file does not exist! \n\tNow exiting..."
    exit
fi

if [ ! -d $OUTPUT/temp ]; then
    mkdir $OUTPUT/temp/
fi

eval `grep "^SUPERVISED" ./$1`
if [ -n "$SUPERVISED" ]; then
    echo "DO YOU HAVE A SUPERVISED LEXICON?: " $SUPERVISED
else
    echo "\n[ERROR] You did not specify if SUPERVISED! \n\tNow exiting..."
    exit
fi ;



if [ ! -d $OUTPUT/data ]; then
    mkdir $OUTPUT/data/
fi

##---------------------------------------------------
## STEP 1) TEXT PROCESSING
##---------------------------------------------------
    echo "-------------------------"
    echo "TEXT PROCESSING"
    echo "-------------------------"

    ## The following varibles were used in a previous version of ALISA, just ignore them
    NUTTS=50        # Number of utterances to be selected for the initial
			        # training data

    N=30		    # number of grapheme occurences to count

    INIRND=1	    # boolean value to specify if the initial text data should be
        		    # selected so that a minimum number of occurences for each grapheme
        		    # appears in the text, or just select the first NUTTS utterances
        		    # and determine the occurences for each grapheme. 0 - random, 1 - initial

    ## RUN THE TEXT PROCESSING
    python scripts/tp/textProcessingModule.py $BOOK $NUTTS $N $INIRND $INITIALTEXT $OUTPUT $SUPERVISED $FROMTPSTEP $TOTPSTEP

