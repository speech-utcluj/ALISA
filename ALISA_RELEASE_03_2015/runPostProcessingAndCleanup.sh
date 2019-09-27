#!/bin/sh
## Author: Adriana STAN adriana.stan@com.utcluj.ro
## Project Simple4All - www.simple4all.org
## October 2013
## Edited: September 2014

####################################################################
## THIS SCRIPT IS USED TO CLEAN UP AFTER ALIGNMENT AND OUTPUT THE
## RESULT IN A NICER FORMAT
####################################################################
if [ $# -eq 0 ]
    then
    echo "[ERROR] You did not provide a configuration file"
    exit
fi

echo "---------------------------------------------"
echo "       READING THE CONFIGURATION FILE"
echo "---------------------------------------------"
##
eval `grep "^INPUTFOLDER" ./$1`
if [ -n "$INPUTFOLDER" ] && [ -d $INPUTFOLDER/ ] ; then
    echo "INPUT FOLDER FOR RAW SPEECH: "$INPUTFOLDER
else
    echo "\n[ERROR] You did not specify an INPUTFOLDER folder, or the folder does not exist! \n\tNow exiting..."
    exit
fi
##
eval `grep "^OUTPUT" ./$1`
if [ -n "$OUTPUT" ] && [ -d $OUTPUT ]; then
    echo "OUTPUT FOLDER: " $OUTPUT
else
    echo "\n[ERROR] You did not specify an OUTPUT folder, or the folder does not exist! \n\tNow exiting..."
    exit
fi
##
eval `grep "^MARKER" ./$1`
if [ -n "$MARKER" ]; then
    echo "FILE MARKER: " $MARKER
else
    echo "\n[ERROR] You did not specify the MARKER for the files! \n\tNow exiting..."
    exit
fi
##
eval `grep "^HTK_BIN" ./$1`
if [ -n "$HTK_BIN" ] && [ -d $HTK_BIN ]; then
    echo "HTK folder: " $HTK_BIN
    export HTK_BIN=$HTK_BIN
else
    echo "\n[ERROR] You did not specify the HTK_BIN folder, or the folder does not exist! \n\tNow exiting..."
    exit
fi
##
eval `grep "^ESTDIR" ./$1`
if [ -n "$ESTDIR" ] && [ -d $ESTDIR ]; then
    echo "Edinburgh Speech Tools folder: " $ESTDIR
    export ESTDIR=$ESTDIR
else
    echo "\n[ERROR] You did not specify the ESTDIR folder, or the folder does not exist! \n\tNow exiting..."
    exit
fi
##
eval `grep "^BOOK" ./$1`
if [ -n "$BOOK" ] && [ -f $BOOK ]; then
    echo "FULL TEXT FILE: "$BOOK
    BOOKFILE=$BOOK
    BOOK=$(basename $BOOKFILE ".txt")
else
    echo "\n[ERROR] You did not specify a BOOK file, or the file does not exist! \n\tNow exiting..."
    exit
fi
##
eval `grep "^SENTB" ./$1`
if [ -n "$SENTB" ]; then
    echo "SENTENCE BOUNDARY CORRECTION?: " $SENTB
else
    echo "\n[ERROR] You did not specify the SENTB option! \n\tNow exiting..."
    exit
fi
##
eval `grep "^ELISION" ./$1`
if [ -n "$ELISION" ]; then
    echo "ELISION SIGN?: " $ELISION
else
    echo "\n[ERROR] You did not specify the ELISION sign! \n\tNow exiting..."
    exit
fi
##
eval `grep "^FINALCONCAT" ./$1`
if [ -n "$FINALCONCAT" ]; then
    echo "CONCATENATE SHORT FILES?: " $FINALCONCAT
else
    echo "\n[ERROR] You did not specify the FINALCONCAT option! \n\tNow exiting..."
    exit
fi
eval `grep "^CLEAN" ./$1`
if [ -n "$CLEAN" ]; then
    echo "REMOVE ALL TEMPORARY FILES?: " $CLEAN
else
    echo "\n[ERROR] You did not specify the CLEAN option! \n\tNow exiting..."
    exit
fi
echo "---------------------------------------------"
echo "            CONFIG READ OK!                  "
echo "---------------------------------------------"


#######################################################
## POST PROCESSING
#######################################################

echo '-------------------------------'
echo "STARTING THE POST PROCESSING"
echo '-------------------------------'

set -e
##  CORRECT SENTENCE BOUNDARIES (OPTIONAL) -- might add some errors

if [ $SENTB -eq 1 ]; then
	echo "CORRECTING SENTENCE BOUNDARIES USING TEXT REFERENCE"
	python scripts/postprocessing/correctMLFusingSentences.py $OUTPUT/data/$BOOK-segmentedNLTK-strip $OUTPUT/temp/wordNetConfidence2.mlf $OUTPUT/temp/correctedMLF.mlf > $OUTPUT/logs/log.sentenceBoundaries
	cp $OUTPUT/temp/correctedMLF.mlf $OUTPUT/temp/wordNetConfidence2.mlf
fi

##  OUTPUT FINAL ALIGNED DATA
echo '\n--------------------------------------------'
echo "YOUR CONFIDENT FILES ARE STORED IN THE OUTPUT/ \nFOLDER ALONG WITH THEIR TRANSCRIPTS!!"
echo "----------------------------------------------"

if [ -d $OUTPUT/ALIGNED ]; then
    rm -rf $OUTPUT/ALIGNED
fi
mkdir $OUTPUT/ALIGNED
mkdir $OUTPUT/ALIGNED/wav
for LABEL in `less $OUTPUT/temp/guessedUTTS` ; do
   cp $OUTPUT/wav/$LABEL.wav $OUTPUT/ALIGNED/wav/
done
cp $OUTPUT/data/retrain/speech_transcript.txt $OUTPUT/ALIGNED/
mkdir $OUTPUT/ALIGNED/txt/
python scripts/postprocessing/createTxtFromSpeechTranscript.py $OUTPUT/ALIGNED/speech_transcript.txt $OUTPUT/ALIGNED/txt/
mkdir $OUTPUT/ALIGNED/txtWithPunctuation/

echo "RESTORING PUNCTUATION..."
python scripts/postprocessing/restorePunctuationListsElision.py $OUTPUT/ALIGNED/txt/ $BOOKFILE $ELISION $OUTPUT/ALIGNED/txtWithPunctuation/ > $OUTPUT/logs/log.restorePunct
echo "CREATE THE FILE WITH TIME ALIGNMENTS AND CORRESPONDING TEXT"
python scripts/postprocessing/getTimesAndTextForFiles.py $INPUTFOLDER $OUTPUT/wav16/ $OUTPUT/ALIGNED/txtWithPunctuation/ $OUTPUT/ALIGNED/$BOOK

## CONCATENATING UTTERANCES THAT MAKE UP A SENTENCE...
if [ $FINALCONCAT -eq 1 ]; then
    mkdir $OUTPUT/ALIGNED/wavConcatenated
    mkdir $OUTPUT/ALIGNED/txtConcatenated
    mkdir $OUTPUT/ALIGNED/txtConcatenatedWithPunctuation
    python scripts/postprocessing/concatenateUtterances.py $OUTPUT/ALIGNED/speech_transcript.txt $OUTPUT/data/$BOOK-segmentedNLTK-strip $OUTPUT/ALIGNED/wav $OUTPUT/ALIGNED/wavConcatenated/ $OUTPUT/ALIGNED/speech_transcript_concatenated.txt > $OUTPUT/logs/log.concatenateUtterances
    python scripts/postprocessing/createTxtFromSpeechTranscript.py $OUTPUT/ALIGNED/speech_transcript_concatenated.txt $OUTPUT/ALIGNED/txtConcatenated/
    echo "RESTORING PUNCTUATION FOR CONCATENATED FILES..."
    python scripts/postprocessing/restorePunctuationListsElision.py $OUTPUT/ALIGNED/txtConcatenated/ $BOOKFILE $ELISION $OUTPUT/ALIGNED/txtConcatenatedWithPunctuation/ > $OUTPUT/logs/log.restorePunctConcat
    echo "CREATE THE FILE WITH TIME ALIGNMENTS AND CORRESPONDING TEXT FOR THE CONCATENATED FILES"
    python scripts/postprocessing/getTimesAndTextForFiles.py $INPUTFOLDER $OUTPUT/wav16/ $OUTPUT/ALIGNED/txtConcatenatedWithPunctuation/ $OUTPUT/ALIGNED/concatenated_$BOOK
fi

## FINAL CLEANUP
if [ $CLEAN -eq 1 ]; then
    echo "Final cleanup..."
    rm -rf $OUTPUT/assessment/ $OUTPUT/temp $OUTPUT/work  $OUTPUT/data/retrain $OUTPUT/data/wordNets-1 $OUTPUT/data/wordNets-3 $OUTPUT/data/aproxUtt $OUTPUT/data/mfcc $OUTPUT/data/models/
fi

echo "-------------------"
echo "     ALL DONE !!   "
echo "-------------------"
