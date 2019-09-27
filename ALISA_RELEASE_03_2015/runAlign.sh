#!/bin/sh
## Author: Adriana STAN adriana.stan@com.utcluj.ro
## Project Simple4All - www.simple4all.org
## Forced alignment: Oliver WATTS
## May 2012
## Edited: August 2014
######################################################################################
## THIS SCRIPT IS USED TO TRAIN ACOUSTIC MODELS AND GET CONFIDENT UTTERANCES
######################################################################################
##
## STEPS:
##
## 1) Create approximate text from a text file and the corresponding audio files
## 2) Using HVite, a background model and different skip networks, find the acoustic scores
##    for all utterances in the testing data
## 3) Using the confidence measure in getConfidentFiles.py, select the "guessed utterances"
## 4) Create speech transcript and copy audio files for the guessed utterances
## 5) Retrain the acoustic models - this is done for initial models, first models and trigrapheme models
## 6) Store new model
## 7) Clean up!! :-)
##
######################################################################################

######################################
##  SET SOME PATHS AND VARIABLES
######################################
if [ $# -eq 0 ]
    then
    echo "[ERROR] You did not provide a configuration file! \n\tNow exiting..."
    exit
fi

echo "---------------------------------------------"
echo "       READING THE CONFIGURATION FILE"
echo "---------------------------------------------"

##
eval `grep "^INPUTFOLDER" ./$1`
if [ -n "$INPUTFOLDER" ] && [ -d $INPUTFOLDER/ ] ; then
    echo "INPUT FOLDER FOR RAW SPEECH: "$INPUTFOLDER
else
    echo "\n[ERROR] You did not specify an INPUTFOLDER folder, or the folder does not exist! \n\tNow exiting..."
    exit
fi ;
##
eval `grep "^OUTPUT" ./$1`
if [ -n "$OUTPUT" ] ; then
    if  [ ! -d $OUTPUT ] ; then
        mkdir $OUTPUT
    fi ;

    echo "OUTPUT FOLDER: " $OUTPUT
else
    echo "\n[ERROR] You did not specify an OUTPUT folder, or the folder does not exist! \n\tNow exiting..."
    exit
fi ;
##
eval `grep "^NAIVE" ./$1`
if [ -n "$NAIVE" ] && [ -d $NAIVE ]; then
    echo "ALISA PATH: " $NAIVE
else
    echo "\n[ERROR] You did not specify the path for ALISA (NAIVE) folder, or the path does not exist! \n\tNow exiting..."
    exit
fi ;
##
eval `grep "^NWIN" ./$1`
if [ -n "$NWIN" ]; then
    echo "Text window dimension: " $NWIN
else
    echo "\n[ERROR] You did not specify the length of the text window (NWIN)! \n\tNow exiting..."
    exit
fi ;
##
eval `grep "^MARKER" ./$1`
if [ -n "$MARKER" ]; then
    echo "FILE MARKER: " $MARKER
else
    echo "\n[ERROR] You did not specify the MARKER for the files! \n\tNow exiting..."
    exit
fi ;
##
eval `grep "^HTK_BIN" ./$1`
if [ -n "$HTK_BIN" ] && [ -d $HTK_BIN ]; then
    echo "HTK folder: " $HTK_BIN
    export HTK_BIN=$HTK_BIN
else
    echo "\n[ERROR] You did not specify the HTK_BIN folder, or the folder does not exist! \n\tNow exiting..."
    exit
fi ;
##
eval `grep "^ESTDIR" ./$1`
if [ -n "$ESTDIR" ] && [ -d $ESTDIR ]; then
    echo "Edinburgh Speech Tools folder: " $ESTDIR
    export ESTDIR=$ESTDIR
else
    echo "\n[ERROR] You did not specify the ESTDIR folder, or the folder does not exist! \n\tNow exiting..."
    exit
fi ;
##
eval `grep "^BOOK" ./$1`
if [ -n "$BOOK" ] && [ -f $BOOK ]; then
    echo "FULL TEXT FILE: "$BOOK
    BOOKFILE=$BOOK
    BOOK=$(basename $BOOKFILE ".txt")
else
    echo "\n[ERROR] You did not specify a BOOK file, or the file does not exist! \n\tNow exiting..."
    exit
fi ;
##
eval `grep "^USEMMI" ./$1`
if [ -n "$USEMMI" ]; then
    echo "USE MMI MODELS?: " $USEMMI
else
    echo "\n[ERROR] You did not specify if USEMMI! \n\tNow exiting..."
    exit
fi ;
##
eval `grep "^SUPERVISED" ./$1`
if [ -n "$SUPERVISED" ]; then
    echo "DO YOU HAVE A SUPERVISED LEXICON?: " $SUPERVISED
else
    echo "\n[ERROR] You did not specify if SUPERVISED! \n\tNow exiting..."
    exit
fi ;
if [ $SUPERVISED -eq 1 ]; then
    eval `grep "^SUPERVISEDDICT" ./$1`
    if [ -n "$SUPERVISEDDICT" ]; then
	    echo "SUPERVISED DICTIONARY: " $SUPERVISEDDICT
	    echo "_COMMA_ sil" > $OUTPUT/temp/addDict
	    echo "_SPACE_ sil" >> $OUTPUT/temp/addDict
        echo "_STOP_ sil" >> $OUTPUT/temp/addDict
        echo "_UTTEND_ sil" >> $OUTPUT/temp/addDict
	    cat $SUPERVISEDDICT $OUTPUT/temp/addDict > $OUTPUT/data/$BOOK-supervised-dict
	    rm $OUTPUT/temp/addDict
    else
	    echo "\n[ERROR] You did not specify the supervised lexicon \n\tNow exiting..."
	    exit
    fi ;

    eval `grep "^LISTOFPHONES" ./$1`
    if [ -n "$LISTOFPHONES" ]; then
	    echo "LIST OF PHONES: " $LISTOFPHONES
	    cp $LISTOFPHONES $OUTPUT/data/$BOOK-supervised-phones
    else
	    echo "\n[ERROR] You did not specify the supervised list of phones \n\tNow exiting..."
	    exit
    fi ;
fi ;
##
eval `grep "^HLMTOOLSDIR" ./$1`
if [ -n "$HLMTOOLSDIR" ] && [ -d $HLMTOOLSDIR ]; then
    echo "HLMTools folder: " $HLMTOOLSDIR
    export HLMTOOLSDIR=$HLMTOOLSDIR
else
    echo "\n[ERROR] You did not specify the HLMTOOLSDIR folder, or the folder does not exist! \n\tNow exiting..."
    exit
fi ;
##
eval `grep "^FROMSTEP" ./$1`
eval `grep "^TOSTEP" ./$1`
echo "RUNNING THE ALIGNMENT FROM STEP: $FROMSTEP TO STEP: $TOSTEP"

## Initialise the run variables
r=0
while [ $r -le 4 ]
   do
   eval "RUN$r=0"
   r=$((r+1))
done
while [ $FROMSTEP -le $TOSTEP ]
    do
    eval "RUN$FROMSTEP=1"
    FROMSTEP=$((FROMSTEP+1))
done
echo "---------------------------------------------"
echo "            CONFIG READ OK!"


###################################################
## CHECKING IF THE TOOLS ARE IN THE SPECIFIED PATHS
##
## HTK: HERest, HVite, HCopy, HBuild, HLRescore,
## HMMIRest, HLEd, HHEd, HDMan, HERest
##
## HLMTOOLS: LNewMap, LGPrep, LBuild
###################################################
if [ ! -x $HTK_BIN/HERest ]; then
    echo "\n[ERROR] Cannot find 'HERest'. Please make sure that HTK is installed correctly!\n\tNow exiting..."
    exit
fi ;

if [ ! -x $HTK_BIN/HVite ]; then
    echo "\n[ERROR] Cannot find 'HVite'. Please make sure that HTK is installed correctly!\n\tNow exiting..."
    exit
fi ;

if [ ! -x $HTK_BIN/HCopy ]; then
    echo "\n[ERROR] Cannot find 'HCopy'. Please make sure that HTK is installed correctly!\n\tNow exiting..."
    exit
fi ;

if [ ! -x $HTK_BIN/HBuild ]; then
    echo "\n[ERROR] Cannot find 'HBuild'. Please make sure that HTK is installed correctly!\n\tNow exiting..."
    exit
fi ;

if [ ! -x $HTK_BIN/HLRescore ]; then
    echo "\n[ERROR] Cannot find 'HLRescore'. Please make sure that HTK is installed correctly!\n\tNow exiting..."
    exit
fi ;

if [ ! -x $HTK_BIN/HMMIRest ]; then
    echo "\n[ERROR] Cannot find 'HMMIRest'. Please make sure that HTK is installed correctly!\n\tNow exiting..."
    exit
fi ;

if [ ! -x $HTK_BIN/HLEd ]; then
    echo "\n[ERROR] Cannot find 'HLEd'. Please make sure that HTK is installed correctly!\n\tNow exiting..."
    exit
fi ;

if [ ! -x $HTK_BIN/HHEd ]; then
    echo "\n[ERROR] Cannot find 'HHEd'. Please make sure that HTK is installed correctly!\n\tNow exiting..."
    exit
fi ;

if [ ! -x $HTK_BIN/HDMan ]; then
    echo "\n[ERROR] Cannot find 'HDMan'. Please make sure that HTK is installed correctly!\n\tNow exiting..."
    exit
fi ;

if [ ! -x $HTK_BIN/HERest ]; then
    echo "\n[ERROR] Cannot find 'HERest'. Please make sure that HTK is installed correctly!\n\tNow exiting..."
    exit
fi ;

if [ ! -x $HLMTOOLSDIR/LNewMap ]; then
    echo "\n[ERROR] Cannot find 'LNewMap'. Please make sure that HLMTOOLS is installed correctly!\n\tNow exiting..."
    exit
fi ;

if [ ! -x $HLMTOOLSDIR/LGPrep ]; then
    echo "\n[ERROR] Cannot find 'LGPrep'. Please make sure that HLMTOOLS is installed correctly!\n\tNow exiting..."
    exit
fi ;

if [ ! -x $HLMTOOLSDIR/LBuild ]; then
    echo "\n[ERROR] Cannot find 'LBuild'. Please make sure that HLMTOOLS is installed correctly!\n\tNow exiting..."
    exit
fi ;

echo "            TOOL CHECK  OK!"
echo "---------------------------------------------"
##
####################################################

set -e

## Paths and variables for forced alignment. DO NOT edit, unless you know
## what you are doing :-)

SCRIPTS=$NAIVE/scripts					     ## Path for forced alignment scripts
WORK=$OUTPUT/work					         ## Output the alignment etc. in here
N_UTTS=15000     					         ## Use only the first $N_UTTS utterances of the speech.
WAV_DIR=$OUTPUT/initialWav16			     ## Initial training audio data
UTTS_DATA=$OUTPUT/data/$BOOK-initialTextData ## Initial training text data
LETTERS=$OUTPUT/data/$BOOK-graphemes		 ## List of graphemes used in the audiobook text
PUNC=$NAIVE/resources/punc.txt				 ## A list of standard punctuation

###################################################
## SET UP THE WORKSPACE
###################################################
if [ $RUN0 -eq 1 ]; then

    start_time=$(date +"%s")
    echo "---------------------------------------------"
    echo "         SETTING UP THE WORKSPACE"
    echo "---------------------------------------------"
    echo "Building the folder structure..."
    if [ -d $OUTPUT/work ]; then
        rm -rf $OUTPUT/work
    fi ;
    if [ -d $OUTPUT/temp ]; then
        rm -rf $OUTPUT/temp
    fi ;
    if [ ! -d $OUTPUT/logs ]; then
        mkdir $OUTPUT/logs
    fi ;
    if [ -d $OUTPUT/results ]; then
        rm -rf $OUTPUT/results
    fi ;
    mkdir $OUTPUT/work $OUTPUT/temp $OUTPUT/results
    
    
    
    echo "Creating approximate text..."
    ls $OUTPUT/wav16/* > $OUTPUT/data/wavList
    python scripts/confidenceScores/getApproxText.py $OUTPUT/data/wavList $OUTPUT/data/$BOOK-segmentedNLTK-strip $NWIN $OUTPUT/data/aproxUtt > $OUTPUT/logs/log.createApproximateText
    echo "Creating word networks..."
    if [ -d $OUTPUT/data/wordNets-1 ]; then
        rm -rf $OUTPUT/data/wordNets-1
    fi ;
    mkdir $OUTPUT/data/wordNets-1
    if [ -d $OUTPUT/data/wordNets-3 ]; then
        rm -rf $OUTPUT/data/wordNets-3
    fi ;
    mkdir $OUTPUT/data/wordNets-3
	python scripts/confidenceScores/createWordNetworkWithLM.py $OUTPUT/data/aproxUtt $OUTPUT/data/$BOOK-bigrams $OUTPUT/data/wordNets-1/ 1 > $OUTPUT/logs/log.skipNets1
	python scripts/confidenceScores/createWordNetworkWithLM.py $OUTPUT/data/aproxUtt $OUTPUT/data/$BOOK-bigrams $OUTPUT/data/wordNets-3/ 3 > $OUTPUT/logs/log.skipNets3
    
   
    end_time=$(date +"%s")
    time_diff=$(($end_time-$start_time))
    echo "***"
    echo "WORKSPACE SETUP DONE IN: $(($time_diff / 60)) minutes and $(($time_diff % 60)) seconds."
    

fi

################################################
##  BUILD INITIAL MODELS FROM 10 MINS OF SPEECH
################################################

if [ $RUN1 -eq 1 ]; then

    start_time=$(date +"%s")

    echo "---------------------------------------------"
    echo "           STARTING THE INITIAL TRAINING     "
    echo "---------------------------------------------"
    echo "Building initial acoustic models..."
    if [ $SUPERVISED -eq 0 ]; then
        PHONELIST=$OUTPUT/data/$BOOK-hmmlist
        DICTIONARY=$OUTPUT/data/$BOOK-dict
    else
        PHONELIST=$OUTPUT/data/$BOOK-supervised-phones
        DICTIONARY=$OUTPUT/data/$BOOK-supervised-dict
    fi ;

    if [ -d $OUTPUT/work ]; then
        rm -rf $OUTPUT/work
    fi ;
    mkdir $OUTPUT/work

    if [ ! -d $OUTPUT/results/initialModels/ ]; then
        mkdir $OUTPUT/results/initialModels/
    fi ;

    $SCRIPTS/forcedAlignment/initial_alignment.sh $WORK/align $SCRIPTS $WAV_DIR  $UTTS_DATA  $LETTERS $PUNC $N_UTTS $SUPERVISED $PHONELIST $DICTIONARY > $OUTPUT/logs/log.initialAlignment_initialModels

    ## Store the model for later use
    if [ ! -d $OUTPUT/data/models ]; then
	    mkdir $OUTPUT/data/models
    fi ;

    cp $OUTPUT/work/align/alignment/hmm25/MMF $OUTPUT/data/models/MMF-0
    cp $OUTPUT/work/align/alignment/hmm25/vFloors $OUTPUT/data/models/vFloors-0
    cp $OUTPUT/data/models/MMF-0 $OUTPUT/results/initialModels/
    cp $OUTPUT/data/models/vFloors-0 $OUTPUT/results/initialModels/
    rm -rf $OUTPUT/work/*

    ## CREATE MFCC'S FOR ALL WAVS
    echo "Create MFCCs for all wav files..."
    ls $OUTPUT/wav16/* > $OUTPUT/data/wavList
    sed "s@wav16@data/mfcc@"  $OUTPUT/data/wavList | sed 's/.wav/.mfcc/' > $OUTPUT/temp/mfccList
    paste $OUTPUT/data/wavList $OUTPUT/temp/mfccList > $OUTPUT/temp/mfccConv
    if [ -d $OUTPUT/data/mfcc ]; then
	    rm -rf  $OUTPUT/data/mfcc
    fi ;
    mkdir $OUTPUT/data/mfcc
    echo "     SOURCEKIND=WAVEFORM
    SOURCEFORMAT=WAV
    ENORMALISE=F
    TARGETKIND=MFCC_E_D_A
    TARGETRATE=100000.0
    SAVECOMPRESSED=T
    SAVEWITHCRC=T
    WINDOWSIZE=100000.0
    USEHAMMING=T
    PREEMCOEF=0.97
    NUMCHANS=26
    CEPLIFTER=22
    NUMCEPS=12" > $OUTPUT/temp/config2

    $HTK_BIN/HCopy -A -D -C $OUTPUT/temp/config2 -S $OUTPUT/temp/mfccConv > $OUTPUT/logs/log.convertToMFCC
    ls $OUTPUT/data/mfcc/* > $OUTPUT/data/testList.scp

    ## GET CONFIDENCE SCORES AND GUESSED UTTS FROM INITIAL MODELS
    SCPFILE=$OUTPUT/data/testList.scp             ## List of all files from audio book to check for confidence
    MODEL=$OUTPUT/data/models/MMF-0        		  ## Initial model just trained

    ## Create the list of utterances for acoustic scores
    sed 's/data\/mfcc\///' $SCPFILE > $OUTPUT/temp/temp0
    
    ## COMPUTE ACOUSTIC SCORES WITH INITIAL MODEL
    echo 'Computing acoustic scores... -- this takes a while :-)'
    ./scripts/confidenceScores/getConfidenceScoresWithLM.sh $MODEL $SCPFILE $OUTPUT/temp/acousticScores $BOOK $OUTPUT $HTK_BIN $DICTIONARY $PHONELIST > $OUTPUT/logs/log.confidenceScores_initialModels

    ## GET CONFIDENT FILES
    echo 'Estimating confident files...'
    python scripts/confidenceScores/getConfidentFiles.py $OUTPUT/temp/acousticScores  $OUTPUT/temp/wordNetConfidence.mlf $OUTPUT/temp/guessedUTTS > $OUTPUT/logs/log.confidentFiles_initialModels

    ## PREPARE DATA FOR NEXT ITERATIONS
    echo "Preparing data for the next steps..."
    if [ -d $OUTPUT/data/retrain ]; then
        rm -rf $OUTPUT/data/retrain
    fi
    mkdir $OUTPUT/data/retrain
    cp $OUTPUT/temp/guessedUTTS $OUTPUT/data/retrain/
    cp $OUTPUT/temp/guessedUTTS $OUTPUT/results/initialModels/guessedUTTS-0
    cp $OUTPUT/temp/wordNetConfidence.mlf $OUTPUT/results/initialModels/wordNetConfidence-0.mlf
    cp $OUTPUT/temp/acousticScores $OUTPUT/results/initialModels/acousticScores-0
    python scripts/confidenceScores/getMLFForGuessedUTTS.py $OUTPUT/results/initialModels/guessedUTTS-0 $OUTPUT/results/initialModels/wordNetConfidence-0.mlf $OUTPUT/results/initialModels/guessedMLF-0.mlf > $OUTPUT/logs/log.guessedMLF-0
    python scripts/general/createSpeechTranscriptFromMLF.py $OUTPUT/temp/guessedUTTS $OUTPUT/temp/wordNetConfidence.mlf $OUTPUT/data/retrain/speech_transcript.txt > $OUTPUT/logs/log.createSpeechTranscript_initialModels
    if [ -d $OUTPUT/data/retrain/wav16 ]; then
        rm -rf $OUTPUT/data/retrain/wav16
    fi
    mkdir $OUTPUT/data/retrain/wav16
    for LABEL in `less $OUTPUT/data/retrain/guessedUTTS` ; do
       cp $OUTPUT/wav16/$LABEL.wav $OUTPUT/data/retrain/wav16/
    done
    echo 'Computing the total duration of the aligned data...'
    python scripts/general/getTotalWavLength.py $OUTPUT/data/retrain/wav16/ $OUTPUT/wav16/
    if [ ! -s $OUTPUT/data/retrain/guessedUTTS ]; then
        echo 'ERROR: Could not align any data with these acoustic models. \n\tNow exiting!!'
        exit
    fi ;
    echo 'Cleaning up...'
    rm -rf $OUTPUT/work/*
    rm -rf $OUTPUT/temp/*
  
    end_time=$(date +"%s")
    time_diff=$(($end_time-$start_time))
    echo "***"
    echo "INITIAL MODEL TRAINING DONE IN: $(($time_diff / 60)) minutes and $(($time_diff % 60)) seconds."

fi

##########################################################
##  FIRST ITERATION MODEL TRAINING
##########################################################
## This could be ran multiple times, but initial tests showed no
## major improvement.

if [ $RUN2 -eq 1 ]; then

    start_time=$(date +"%s")
    echo "---------------------------------------------"
    echo "           STARTING THE FIRST ITERATION      "
    echo "---------------------------------------------"

    WAV_DIR=$OUTPUT/data/retrain/wav16
    UTTS_DATA=$OUTPUT/data/retrain/speech_transcript.txt
	IT=1
    if [ $SUPERVISED -eq 0 ]; then
            PHONELIST=$OUTPUT/data/$BOOK-hmmlist
            DICTIONARY=$OUTPUT/data/$BOOK-dict
    else
            PHONELIST=$LISTOFPHONES
            DICTIONARY=$OUTPUT/data/$BOOK-supervised-dict
    fi
    echo "Building the first iteration acoustic models..."
    $SCRIPTS/forcedAlignment/initial_alignment.sh $WORK/align $SCRIPTS $WAV_DIR  $UTTS_DATA  $LETTERS $PUNC $N_UTTS $SUPERVISED $PHONELIST $DICTIONARY > $OUTPUT/logs/log.initialAlignment_firstIteration
	
	## Store the model for later use
	cp $OUTPUT/work/align/alignment/hmm25/MMF $OUTPUT//data/models/MMF-$IT
	cp $OUTPUT/work/align/alignment/hmm25/vFloors $OUTPUT/data/models/vFloors-$IT
	cp $OUTPUT/work/align/alignment/hmm25/stats $OUTPUT/data/models/stats-$IT
	cp $OUTPUT/data/models/MMF-$IT $OUTPUT/results/MMF-$IT
	rm -rf $OUTPUT/work/*
	

	## GET CONFIDENCE SCORES AND GUESSED UTTS FROM FIRST ITERATION
	ls $OUTPUT/data/mfcc/* > $OUTPUT/data/testList.scp
	SCPFILE=$OUTPUT/data/testList.scp                   ## List of all files from audio book to check for confidence
	MODEL=$OUTPUT/data/models/MMF-$IT        		    ## Initial model just trained

	## COMPUTE ACOUSTIC SCORES WITH INITIAL MODEL
	echo 'Computing acoustic scores... -- this takes a while :-)'
	./scripts/confidenceScores/getConfidenceScoresWithLM.sh $MODEL $SCPFILE $OUTPUT/temp/acousticScores $BOOK $OUTPUT $HTK_BIN $DICTIONARY $PHONELIST > $OUTPUT/logs/log.confidenceScores_firstIteration

	## GET CONFIDENT FILES
	echo 'Estimating confident files...'
	python scripts/confidenceScores/getConfidentFiles.py $OUTPUT/temp/acousticScores $OUTPUT/temp/wordNetConfidence.mlf $OUTPUT/temp/guessedUTTS > $OUTPUT/logs/log.confidentFiles_firstIteration

	## PREPARE DATA FOR NEXT ITERATIONS
	echo "Preparing data for next iterations..."
	if [ -d $OUTPUT/data/retrain ]; then
	      rm -rf $OUTPUT/data/retrain
	fi
	mkdir $OUTPUT/data/retrain
	
	if [ ! -d $OUTPUT/results/firstIteration/ ]; then
        mkdir $OUTPUT/results/firstIteration/
    fi ;

	## COPY RESULTS FOR LATER ANALYSIS
	cp $OUTPUT/temp/guessedUTTS $OUTPUT/data/retrain/guessedUTTS-$IT
	cp $OUTPUT/temp/guessedUTTS $OUTPUT/results/firstIteration/guessedUTTS-$IT
	cp $OUTPUT/temp/wordNetConfidence.mlf $OUTPUT/results/firstIteration/wordNetConfidence-$IT.mlf
	cp $OUTPUT/temp/acousticScores $OUTPUT/results/firstIteration/acousticScores-1
	python scripts/confidenceScores/getMLFForGuessedUTTS.py $OUTPUT/results/firstIteration/guessedUTTS-$IT $OUTPUT/results/firstIteration/wordNetConfidence-$IT.mlf $OUTPUT/results/firstIteration/guessedMLF-$IT.mlf > $OUTPUT/logs/logs.guessedMLF-1
	python scripts/general/createSpeechTranscriptFromMLF.py $OUTPUT/data/retrain/guessedUTTS-$IT $OUTPUT/temp/wordNetConfidence.mlf $OUTPUT/data/retrain/speech_transcript.txt  > $OUTPUT/logs/log.createSpeechTranscript_firstIteration

	if [ -d $OUTPUT/data/retrain/wav16 ]; then
	        rm -rf $OUTPUT/data/retrain/wav16
	fi
	mkdir $OUTPUT/data/retrain/wav16
	## Copy confident wav files for retraining
	for LABEL in `less $OUTPUT/data/retrain/guessedUTTS-$IT` ; do
	     cp $OUTPUT/wav16/$LABEL.wav $OUTPUT/data/retrain/wav16/
	done

    ## COMPUTE THE ALIGNED TIME OUT OF THE TOTAL	
    echo 'Computing the total duration of the aligned data...'
    python scripts/general/getTotalWavLength.py $OUTPUT/data/retrain/wav16/ $OUTPUT/wav16/
    if [ ! -s $OUTPUT/data/retrain/guessedUTTS-$IT ]; then
         echo 'ERROR: Could not align any data with these acoustic models. \n\tNow exiting!!'
         exit
    fi

	## CLEAN UP
	echo 'Cleaning up...'
	rm -rf $OUTPUT/work/*
    cp $OUTPUT/temp/wordNetConfidence.mlf $OUTPUT/temp/wordNetConfidence2.mlf
    
    end_time=$(date +"%s")
    time_diff=$(($end_time-$start_time))
    echo "***"    
    echo "FIRST ITERATION DONE IN: $(($time_diff / 60)) minutes and $(($time_diff % 60)) seconds."

fi

#####################################################
##  BUILD MMI DISCRIMINATIVE MODELS
#####################################################

if [ $RUN3 -eq 1 ] && [ $USEMMI -eq 1 ]; then

        start_time=$(date +"%s")

    	echo "---------------------------------------------"
    	echo "         STARTING DISCRIMINATIVE TRAINING  "
    	echo "---------------------------------------------"

        MLFFile=$OUTPUT/results/firstIteration/wordNetConfidence-1.mlf
        MODEL=$OUTPUT/data/models/MMF-1
        
        if [ $SUPERVISED -eq 0 ]; then
            PHONELIST=$OUTPUT/data/$BOOK-hmmlist
            DICTIONARY=$OUTPUT/data/$BOOK-dict
            GRAPHEMES=$OUTPUT/data/$BOOK-graphemes
        else
            PHONELIST=$LISTOFPHONES
            DICTIONARY=$OUTPUT/data/$BOOK-supervised-dict
            paste $PHONELIST $PHONELIST > $OUTPUT/data/$BOOK-phones-supervised
            GRAPHEMES=$OUTPUT/data/$BOOK-phones-supervised
        fi

        ## CREATE LM
        if [ ! -d $OUTPUT/temp/lmdb ]; then
	        mkdir $OUTPUT/temp/lmdb
        fi
        grep -v 'SENT_START' $MLFFile | grep -v 'SENT_END' > $OUTPUT/temp/wordNetConfidence-1.mlf
        MLFFile=$OUTPUT/temp/wordNetConfidence-1.mlf
        ## PREPARE DATA FOR LM
        ## prepare data for language model - this should be done from the MLF file in order to
        ## avoid problems with SENT_START, SENT_END
        sed "s@$OUTPUT/data/mfcc/@@" $MLFFile > $OUTPUT/temp/tempi.mlf
        echo "Create text from MLF..."
        python scripts/discriminativeTraining/createTxtFromMLF.py  $OUTPUT/temp/tempi.mlf $OUTPUT/temp/tempi2.txt $MARKER
        python scripts/discriminativeTraining/convertWordsToLetters.py $OUTPUT/temp/tempi2.txt $DICTIONARY $OUTPUT/temp/trainLM.txt

        ## Build grapheme dictionary
        echo "!SENT_END sil
!SENT_START  sil
sil []  sil
skip [] sil" > $OUTPUT/data/$BOOK-graphemes-dict
        less $GRAPHEMES >> $OUTPUT/data/$BOOK-graphemes-dict
        
        ## Create a grapheme dictionary (this was added for cases like Ukrainian)
        awk '{print $2}' $GRAPHEMES > $OUTPUT/temp/graph_temp
        paste $OUTPUT/temp/graph_temp $OUTPUT/temp/graph_temp > $OUTPUT/temp/graph_temp2
        less $OUTPUT/temp/graph_temp2 >> $OUTPUT/data/$BOOK-graphemes-dict
        rm $OUTPUT/temp/graph_temp $OUTPUT/temp/graph_temp2
        
        ## CREATE LANGUAGE MODEL
        echo "Creating language model and word network..."
        echo "EX
        DE skip" > $OUTPUT/temp/mkphones0.led
        ## Expand MLF to grapheme sequences
        echo 'Converting MLF data to letters...'
        python scripts/discriminativeTraining/convertMLFWordsToLetters.py $MLFFile $DICTIONARY $OUTPUT/temp/grapheme.mlf
        $HLMTOOLSDIR/LNewMap $BOOK $OUTPUT/temp/$BOOK.wmap
        $HLMTOOLSDIR/LGPrep  -d $OUTPUT/temp/lmdb/ -b 5000 -n 1 $OUTPUT/temp/$BOOK.wmap $OUTPUT/temp/trainLM.txt
        $HLMTOOLSDIR/LBuild  -n 1 $OUTPUT/temp/lmdb/wmap $OUTPUT/temp/trainbg $OUTPUT/temp/lmdb/gram.*
        ## Build a word network from the LM - to do HVite with biased LM and not the skip networks for the numerator lattices
        awk '{print $2}' $OUTPUT/data/$BOOK-graphemes-dict | grep -v '\[\]' | sort | uniq > $OUTPUT/temp/wdlist
        echo '!SENT_START\n!SENT_END' >> $OUTPUT/temp/wdlist
       
        $HTK_BIN/HBuild -n $OUTPUT/temp/trainbg -s '!SENT_START' '!SENT_END' $OUTPUT/temp/wdlist $OUTPUT/temp/full.lat

        ## LATTICE CREATION
        ## DENOMINATOR LATTICES
        ## create train.scp from data/retrain/wav
        echo "Denominator lattice phone marking..."
        ls $OUTPUT/wav16/*.wav | sed "s@$OUTPUT/wav16/@$OUTPUT/data/mfcc/@" | sed 's/\.wav/\.mfcc/' > $OUTPUT/temp/trainDenLat.scp
        if [ -d $OUTPUT/temp/wlat.den ]; then
            rm -rf $OUTPUT/temp/wlat.den/
        fi
        mkdir $OUTPUT/temp/wlat.den
        $HTK_BIN/HVite -T 1 -p -10 -n 4 -t 1500 -z lat -l $OUTPUT/temp/wlat.den/ -w $OUTPUT/temp/full.lat -S $OUTPUT/temp/trainDenLat.scp -i $OUTPUT/temp/temp.mlf -H $MODEL $OUTPUT/data/$BOOK-graphemes-dict $PHONELIST > $OUTPUT/logs/log.denominatorLatticesPhoneMarking

        ## NUMERATOR LATTICES
        ## create config.hlrescore
        echo "STARTWORD      = !SENT_START
        ENDWORD        = !SENT_END
        FIXBADLATS     = T" > $OUTPUT/temp/config.hlrescore
        sed 's/\.rec/\.lab/' $OUTPUT/temp/grapheme.mlf | sed "s@$OUTPUT/data/mfcc@*@" > $OUTPUT/temp/MMI.mlf

        ## Create train.labscp
        sed "s@$OUTPUT/data/mfcc/@*/@"  $OUTPUT/temp/trainDenLat.scp > $OUTPUT/temp/train.labscp
        if [ -d $OUTPUT/temp/wlat.num ]; then
            rm -rf $OUTPUT/temp/wlat.num/
        fi
        mkdir $OUTPUT/temp/wlat.num
        ## Rescoring numerator lattices
        echo "Rescoring numerator lattices..."
        $HTK_BIN/HLRescore -A -C $OUTPUT/temp/config.hlrescore -s 32.0 -p -20.0 -t 300.0 -S $OUTPUT/temp/train.labscp -i $OUTPUT/temp/temp2.mlf -I $OUTPUT/temp/MMI.mlf -n $OUTPUT/temp/trainbg -w  -l $OUTPUT/temp/wlat.num/ $OUTPUT/data/$BOOK-graphemes-dict > $OUTPUT/logs/log.rescoreNumeratorLattices

        ########################################
        ## PHONE MARKING
        ########################################
        ## Make deterministic denominator lattices
        echo "Deterministic denominator lattices..."
        if [ -d $OUTPUT/temp/wlat.den.det ]; then
            rm -rf $OUTPUT/temp/wlat.den.det/
        fi
        mkdir $OUTPUT/temp/wlat.den.det
        ls $OUTPUT/temp/wlat.den/* > $OUTPUT/temp/train.lcp

        $HTK_BIN/HLRescore -T 1 -C $OUTPUT/temp/config.hlrescore -S $OUTPUT/temp/train.lcp -t 220.0 500.0 -s 0.5 -m f -L $OUTPUT/temp/wlat.den/ -w -l $OUTPUT/temp/wlat.den.det $OUTPUT/data/$BOOK-graphemes-dict > $OUTPUT/logs/log.deterministicDenominatorLattices

        ## LATTICES MUST NOT BE BINARY!!!!
        ## USE THIS HACKATON: http://speechtechie.wordpress.com/2009/06/12/using-htk-3-4-1-on-mac-os-10-5/ for Error: AlignDur <= 0
        ## build train.wlat.num.scp with the mfcc of the files that have lattices

        ## NUMERATOR PHONE MARKING:
        echo "Numerator phone marking..."
        ls $OUTPUT/temp/wlat.num/*.lat | sed "s@$OUTPUT/temp/wlat.num@$OUTPUT/data/mfcc@" | sed 's/\.lat/\.mfcc/' > $OUTPUT/temp/train.wlat.num.scp
        if [ -d $OUTPUT/temp/plat.num ]; then
            rm -rf $OUTPUT/temp/plat.num/
        fi
        mkdir $OUTPUT/temp/plat.num
        $HTK_BIN/HVite -A -T 1  -n 4 -m -w -z lat  -l $OUTPUT/temp/plat.num -X lat -L $OUTPUT/temp/wlat.num/ -i $OUTPUT/temp/plat.num/plat.mlf -S $OUTPUT/temp/train.wlat.num.scp -H $MODEL $OUTPUT/data/$BOOK-graphemes-dict $PHONELIST > $OUTPUT/logs/log.numeratorPhoneMarking

        ## DENOMINATOR PHONE MARKING:
        echo "Denominator phone marking..."
        ls $OUTPUT/temp/wlat.den.det/*.lat | sed "s@$OUTPUT/temp/wlat.den.det@$OUTPUT/data/mfcc@" | sed 's/\.lat/\.mfcc/' > $OUTPUT/temp/train.wlat.den.scp
        if [ -d $OUTPUT/temp/plat.den ]; then
            rm -rf $OUTPUT/temp/plat.den
        fi
        mkdir $OUTPUT/temp/plat.den
        $HTK_BIN/HVite -T 1 -n 4 -m -w -z lat -l $OUTPUT/temp/plat.den/ -X lat -L $OUTPUT/temp/wlat.den.det/ -i $OUTPUT/temp/plat.den/plat.mlf -S $OUTPUT/temp/train.wlat.den.scp -H $MODEL $OUTPUT/data/$BOOK-graphemes-dict $PHONELIST > $OUTPUT/logs/log.denominatorPhoneMarking
        rm -rf $OUTPUT/temp/wlat.num
        rm -rf $OUTPUT/temp/wlat.den
        rm -rf $OUTPUT/temp/wlat.den.det

        ## RE-ESTIMATE THE MMI MODELS
        echo "    TARGETKIND=MFCC_E_D_A
            LATPROBSCALE=0.3
            ISMOOTHTAUW = 10
            E=2
            ARC: TRACE=3
            HMMIREST: TRACE=3
            MPE=FALSE" > $OUTPUT/temp/config.mmirest

        ls $OUTPUT/temp/plat.den/*.lat | sed "s@$OUTPUT/temp/plat.den@$OUTPUT/data/mfcc@" | sed 's/\.lat/\.mfcc/' > $OUTPUT/temp/train.plat.den.scp
        rm -rf $OUTPUT/temp/mmihmm-*
        mkdir $OUTPUT/temp/mmihmm-0
        cp $MODEL $OUTPUT/data/models/vFloors-1 $OUTPUT/temp/mmihmm-0/
        MODELNAME=$(basename $MODEL)
        echo "Re-estimating MMI models..."
        for i in 1 2 3 4
        do
            echo "Re-estimation no. $i..."
            mkdir $OUTPUT/temp/mmihmm-$i
            b=$(($i - 1))
            $HTK_BIN/HMMIRest -C $OUTPUT/temp/config.mmirest -w 2.0 -A -H $OUTPUT/temp/mmihmm-$b/$MODELNAME -H $OUTPUT/temp/mmihmm-$b/vFloors-1 -S $OUTPUT/temp/train.plat.den.scp -s $OUTPUT/temp/mmihmm-$i/stats -q $OUTPUT/temp/plat.num -r $OUTPUT/temp/plat.den/ -u tmvw -M $OUTPUT/temp/mmihmm-$i $PHONELIST > $OUTPUT/logs/log.HMMIRest
        done

        cp $OUTPUT/temp/mmihmm-$i/$MODELNAME $OUTPUT/data/models/MMI-graph
        cp $OUTPUT/temp/mmihmm-$i/stats $OUTPUT/data/models/stats-MMI
        rm -rf $OUTPUT/temp/mmihmm-*

        MODEL=$OUTPUT/data/models/MMI-graph
        SCPFILE=$OUTPUT/data/testList.scp


        ## GET CONFIDENT FILES FROM MMI MODELS
        echo 'Computing acoustic scores... -- this takes a while :-)'
	    ./scripts/confidenceScores/getConfidenceScoresWithLM.sh $MODEL $SCPFILE $OUTPUT/temp/acousticScores $BOOK $OUTPUT $HTK_BIN $DICTIONARY $PHONELIST > $OUTPUT/logs/log.confidenceScores_MMI
	    ## GET CONFIDENT FILES
	    echo 'Estimating confident files...'
	    python scripts/confidenceScores/getConfidentFiles.py $OUTPUT/temp/acousticScores $OUTPUT/temp/wordNetConfidence.mlf $OUTPUT/temp/guessedUTTS > $OUTPUT/logs/log.confidentFiles_MMI
	    ## PREPARE DATA FOR NEXT ITERATIONS
	    echo "Preparing data for next iterations"
	    if [ -d $OUTPUT/data/retrain ]; then
	        rm -rf $OUTPUT/data/retrain
	    fi
	    mkdir $OUTPUT/data/retrain
	    ## COPY RESULTS FOR LATER ANALYSIS
	    if [ ! -d $OUTPUT/results/MMI/ ]; then
            mkdir $OUTPUT/results/MMI/
        fi ;
	    cp $OUTPUT/temp/guessedUTTS $OUTPUT/results/MMI/guessedUTTS-MMI
	    cp $OUTPUT/temp/wordNetConfidence.mlf $OUTPUT/results/MMI/wordNetConfidence-MMI.mlf
	    cp $OUTPUT/temp/acousticScores $OUTPUT/results/MMI/acousticScores-MMI
        python scripts/confidenceScores/getMLFForGuessedUTTS.py $OUTPUT/results/MMI/guessedUTTS-MMI $OUTPUT/results/MMI/wordNetConfidence-MMI.mlf $OUTPUT/results/MMI/guessedMLF-MMI.mlf > $OUTPUT/logs/log.guessedMLF-MMI
        cp $OUTPUT/temp/guessedUTTS $OUTPUT/data/retrain/guessedUTTS-MMI
        if [ -d $OUTPUT/data/retrain/wav16 ]; then
	        rm -rf $OUTPUT/data/retrain/wav16
	    fi
	    mkdir $OUTPUT/data/retrain/wav16
	    ## Copy confident wav files for retraining
	    for LABEL in `less $OUTPUT/data/retrain/guessedUTTS-MMI` ; do
	       cp $OUTPUT/wav16/$LABEL.wav $OUTPUT/data/retrain/wav16/
	    done

        ## COMPUTE THE ALIGNED TIME OUT OF THE TOTAL	
        echo 'Computing the total duration of the aligned data...'
        python scripts/general/getTotalWavLength.py $OUTPUT/data/retrain/wav16/ $OUTPUT/wav16/
        if [ ! -s $OUTPUT/results/MMI/guessedUTTS-MMI ]; then
            echo 'ERROR: Could not align any data with these acoustic models. Now exiting!!'
            exit
        fi ;
	    ## CLEAN UP
	    echo 'Cleaning up...'
	    rm -rf $OUTPUT/work/*

        end_time=$(date +"%s")
        time_diff=$(($end_time-$start_time))
        echo "***"        
        echo "MMI TRAINING DONE IN: $(($time_diff / 60)) minutes and $(($time_diff % 60)) seconds."

fi

####################################################################
##  ESTIMATE TRIGRAPHEME MODELS
####################################################################

if [ $RUN4 -eq 1 ]; then

        start_time=$(date +"%s")

	echo "---------------------------------------------"
	echo "    STARTING TRI-GRAPHEME MODEL TRAINING  "
	echo "---------------------------------------------"

	## This following code converts the monographeme models to trigraphemes
	## It uses the MLF file of the SKIP1_LM network generated by any model (except the first)
	## and the guessedMLF file from the same model
	MLFFile=$OUTPUT/results/MMI/guessedMLF-MMI.mlf	#get list of trigraphemes from previous recognition output
	MODEL=$OUTPUT/data/models/MMI-graph
	VFLOORS=$OUTPUT/data/models/vFloors-1
	if [ $USEMMI -eq 0 ]; then
		MODEL=$OUTPUT/data/models/MMF-1
    	MLFFile=$OUTPUT/results/firstIteration/guessedMLF-1.mlf
    	VFLOORS=$OUTPUT/data/models/vFloors-1	
	fi	
    if [ $SUPERVISED -eq 0 ]; then
            PHONELIST=$OUTPUT/data/$BOOK-hmmlist
            DICTIONARY=$OUTPUT/data/$BOOK-dict
            GRAPHEMES=$OUTPUT/data/$BOOK-graphemes
    else
            PHONELIST=$LISTOFPHONES
            DICTIONARY=$OUTPUT/data/$BOOK-supervised-dict
            paste $PHONELIST $PHONELIST > $OUTPUT/data/$BOOK-phones-supervised
            GRAPHEMES=$OUTPUT/data/$BOOK-phones-supervised
    fi

	#Convert Segmented ASCII to a MLF so we can get all tri-graphemes from there
	echo "Creating list of tri-graphemes and dictionary..."
    grep -v '!SENT_END' $MLFFile | grep -v '!SENT_START' > $OUTPUT/temp/tempWordNet.mlf
    MLFFile=$OUTPUT/temp/tempWordNet.mlf
	
	python scripts/trigraphemes/convertSegmentedToLettersMLF.py $OUTPUT/data/$BOOK-segmentedNLTK-strip  $OUTPUT/temp/segAsciiWord
	python scripts/trigraphemes/convertWordsToLettersMLF.py $OUTPUT/temp/segAsciiWord  $DICTIONARY $OUTPUT/temp/segAsciilettersMLF 0
	
	
	awk '{print $1}' $MLFFile > $OUTPUT/temp/wordMLF
	python scripts/trigraphemes/convertWordsToLettersMLF.py $OUTPUT/temp/wordMLF $DICTIONARY $OUTPUT/temp/lettersMLF 1
	echo "WB skip
WB sil
TC

" > $OUTPUT/temp/mktri.led

	$HTK_BIN/HLEd -D -T 1 -n $OUTPUT/temp/triphones1 -l '*' -i $OUTPUT/temp/wintri.mlf $OUTPUT/temp/mktri.led $OUTPUT/temp/lettersMLF >> $OUTPUT/logs/log.trigrapheme
	## Get all triphones from book text
	$HTK_BIN/HLEd -D -T 1 -n $OUTPUT/temp/triphones2 -l '*' -i $OUTPUT/temp/wintri2.mlf $OUTPUT/temp/mktri.led $OUTPUT/temp/segAsciilettersMLF > $OUTPUT/logs/log.trigrapheme
	
	## Create full list of triphones
	python scripts/trigraphemes/getFullListOfTriphones.py $OUTPUT/temp/triphones1 $OUTPUT/temp/triphones2 $OUTPUT/temp/triphones
	#rm $OUTPUT/temp/wintri2.mlf $OUTPUT/temp/triphones1 $OUTPUT/temp/triphones2
	perl scripts/trigraphemes/maketrihed $PHONELIST $OUTPUT/temp/triphones >> $OUTPUT/logs/log.trigrapheme
	mv ./mktri.hed $OUTPUT/temp/mktri.hed
	#Create raw trigrapheme models
	rm -rf $OUTPUT/temp/trihmm-*
	mkdir $OUTPUT/temp/trihmm-0
	$HTK_BIN/HHEd -D -T 1 -H $MODEL -M $OUTPUT/temp/trihmm-0 $OUTPUT/temp/mktri.hed $PHONELIST >> $OUTPUT/logs/log.trigrapheme
	## Re-estimate the models using the correctly guessed utterances
	echo "Re-estimating acoustic models using tri-graphemes..."
	ls $OUTPUT/data/retrain/wav16/* | sed 's/retrain\/wav16/mfcc/' | sed 's/.wav/.mfcc/' > $OUTPUT/temp/train.scp
    MODELNAME=$(basename $MODEL)
    
    echo "TARGETKIND = MFCC_E_D_A" > $OUTPUT/temp/config_HERest
    
    for i in 1 2 3
    do
         echo "Trigrapheme Re-estimation no. $i..."
         mkdir $OUTPUT/temp/trihmm-$i
         b=$(($i - 1))
         $HTK_BIN/HERest -A -D -T 1 -C $OUTPUT/temp/config_HERest -I $OUTPUT/temp/wintri.mlf -S $OUTPUT/temp/train.scp -H $OUTPUT/temp/trihmm-$b/$MODELNAME -H $VFLOORS -s $OUTPUT/temp/trihmm-$i/stats -M $OUTPUT/temp/trihmm-$i $OUTPUT/temp/triphones >> $OUTPUT/logs/log.trigrapheme
    done

    ## Tied-state triphone models
    echo "Creating tied-state tri-grapheme models..."
    echo "AS skip
RS cmu
MP sil sil skip" > $OUTPUT/temp/global.ded
#	$HTK_BIN/HDMan -D -T 1 -b skip -n $OUTPUT/temp/fulllist -g $OUTPUT/temp/global.ded -l $OUTPUT/temp/flog $OUTPUT/data/$BOOK-dict-tri $DICTIONARY >> $OUTPUT/logs/log.trigrapheme

    python scripts/trigraphemes/createTrigraphDict.py $DICTIONARY $OUTPUT/data/$BOOK-dict-tri
    grep -v 'skip' $PHONELIST > $OUTPUT/temp/fulllist
    cat $OUTPUT/temp/fulllist $OUTPUT/temp/triphones > $OUTPUT/temp/fulllist1
	perl scripts/trigraphemes/fixfullist.pl $OUTPUT/temp/fulllist1 $OUTPUT/temp/fulllist
    
    ## Reduce number of mixtures:    
    echo "MD 1 {*.state[2-4].mix}" > $OUTPUT/temp/mixdown.hed
    j=$(($i+1))
    mkdir $OUTPUT/temp/trihmm-$j/
    $HTK_BIN/HHEd -H $OUTPUT/temp/trihmm-$i/$MODELNAME -H $OUTPUT/temp/trihmm-$i/vFloors-1 -M $OUTPUT/temp/trihmm-$j/ $OUTPUT/temp/mixdown.hed $OUTPUT/temp/triphones
#    grep -v bghmm $OUTPUT/temp/fulllist > $OUTPUT/temp/fulllist2
    grep -v skip $OUTPUT/temp/fulllist | grep -v bghmm > $OUTPUT/temp/fulllist2
    echo 'Create the tree.hed file used in triphone state tying...'
    python scripts/trigraphemes/createTreeHED.py $PHONELIST $OUTPUT/ $i $OUTPUT/temp/tree.hed

    echo 'Creating HMM prototypes...'
    jj=$(($j+1))
    mkdir $OUTPUT/temp/trihmm-$jj/
    $HTK_BIN/HHEd -A -D -T 1 -H $OUTPUT/temp/trihmm-$i/vFloors-1 -H $OUTPUT/temp/trihmm-$j/$MODELNAME -M $OUTPUT/temp/trihmm-$jj/ $OUTPUT/temp/tree.hed $OUTPUT/temp/triphones >> $OUTPUT/logs/log.trigrapheme
    jk=$jj   
    for i in 1 2 3
    do
         b=$jk
         jk=$(($jk+1))
         echo "Tied Trigrapheme Re-estimation no. $i..."
         mkdir $OUTPUT/temp/trihmm-$jk
         $HTK_BIN/HERest -A -D -T 1 -C $OUTPUT/temp/config_HERest -I $OUTPUT/temp/wintri.mlf -S $OUTPUT/temp/train.scp -H $OUTPUT/temp/trihmm-$b/$MODELNAME -H $VFLOORS -s $OUTPUT/temp/trihmm-$jk/stats -M $OUTPUT/temp/trihmm-$jk $OUTPUT/temp/tiedlist >> $OUTPUT/logs/log.trigrapheme
    done
    
    ## save the trained models
	cp $OUTPUT/temp/trihmm-$jk/MM* $OUTPUT/data/models/MMF-trig
	cp $OUTPUT/temp/trihmm-$jk/stats $OUTPUT/data/models/stats-trig
    cp $OUTPUT/temp/trihmm-$jk/vFloors* $OUTPUT/data/models/vFloors-trig
    
	## Clean up
	rm -rf $OUTPUT/temp/trihmm*

	## GET CONFIDENCE SCORES AND GUESSED UTTS FROM TRIGRAPHEME MODELS
	ls $OUTPUT/data/mfcc/* > $OUTPUT/data/testList.scp

	SCPFILE=$OUTPUT/data/testList.scp               ## List of all files from audio book to check for confidence
	MODEL=$OUTPUT/data/models/MMF-trig     		    ##
    echo "skip sil" >> $OUTPUT/temp/tiedlist
	## Create the list of utterances for acoustic scores
	sed 's/data\/mfcc\///' $SCPFILE > $OUTPUT/temp/temp0

	## COMPUTE ACOUSTIC SCORES WITH TRIGRAPHEME MODEL
	echo 'Computing acoustic scores... -- this takes a while :-)'
	./scripts/confidenceScores/getConfidenceScoresTriphones.sh $MODEL $SCPFILE $OUTPUT/temp/acousticScores $BOOK 0 $OUTPUT $HTK_BIN > $OUTPUT/logs/log.confidenceScores_trigrapheme
	cp $OUTPUT/temp/triphones $OUTPUT/data/$BOOK-triphones

	## GET CONFIDENT FILES
	echo 'Estimating confident files...'
	python scripts/confidenceScores/getConfidentFiles.py $OUTPUT/temp/acousticScores  $OUTPUT/temp/wordNetConfidence.mlf $OUTPUT/temp/guessedUTTS > $OUTPUT/logs/log.confidentFiles_trigrapheme

	## Copy results for later analysis
	if [ ! -d $OUTPUT/results/trig/ ]; then
        mkdir $OUTPUT/results/trig/
    fi ;
	cp $OUTPUT/temp/guessedUTTS $OUTPUT/results/trig/guessedUTTS-trig
	cp $OUTPUT/temp/wordNetConfidence.mlf $OUTPUT/results/trig/wordNetConfidence-trig.mlf
	cp $OUTPUT/temp/acousticScores $OUTPUT/results/trig/acousticScores-trig
    python scripts/confidenceScores/getMLFForGuessedUTTS.py $OUTPUT/results/trig/guessedUTTS-trig $OUTPUT/results/trig/wordNetConfidence-trig.mlf $OUTPUT/results/trig/guessedMLF-trig.mlf > $OUTPUT/logs/log.guessedMLF-trig
    if [ ! -s $OUTPUT/results/trig/guessedUTTS-trig ]; then
        echo 'ERROR: Could not align any data with these acoustic models. \n\tNow exiting!!'
        exit
    fi;

    ## Create a new speech transcript for the confident files
    python scripts/general/createSpeechTranscriptFromMLF.py $OUTPUT/temp/guessedUTTS $OUTPUT/temp/wordNetConfidence.mlf $OUTPUT/data/retrain/speech_transcript.txt > $OUTPUT/logs/log.createSpeechTranscript_trigrapheme
    if [ -d $OUTPUT/data/retrain/wav16 ]; then
        rm -rf $OUTPUT/data/retrain/wav16
    fi
    mkdir $OUTPUT/data/retrain/wav16

    ## copy guessed wav files for retraining
    for LABEL in `less $OUTPUT/temp/guessedUTTS` ; do
       cp $OUTPUT/wav16/$LABEL.wav $OUTPUT/data/retrain/wav16/
    done
    echo 'Computing the total duration of the aligned data...'
    python scripts/general/getTotalWavLength.py $OUTPUT/data/retrain/wav16/ $OUTPUT/wav16/
    end_time=$(date +"%s")
    time_diff=$(($end_time-$start_time))
    echo "***"    
    echo "TRI-GRAPHEME TRAINING DONE IN: $(($time_diff / 60)) minutes and $(($time_diff % 60)) seconds."

fi
echo "---------------------------------------------"
echo "                ALL DONE OK!!!"
echo "---------------------------------------------"
