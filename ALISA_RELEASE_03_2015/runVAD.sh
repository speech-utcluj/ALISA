#!/bin/sh
#################################################
## Author: Adriana STAN adriana.stan@com.utcluj.ro
## Project Simple4All - www.simple4all.org
## January 2013
#################################################
## This script runs the preliminary audio segmentation step for ALISA
## It uses the GMM-VAD developed by Yoshitaka Mamiya
## To use the advanced configuration methods you can alter the resources/vad/conf.* files

set -e	

echo "---------------------------------------------"
echo "       READING THE CONFIGURATION FILE"
echo "---------------------------------------------"

if [ $# -eq 0 ]
    then
    echo "[ERROR] You did not provide a configuration file!\n\tNow exiting..."
    exit
fi
## Retrieve and check the config variables
eval `grep "^OUTPUT" ./$1`
if [ -n "$OUTPUT" ]; then
    echo "OUTPUT FOLDER: " $OUTPUT
else
    echo "\n[ERROR] You did not specify an OUTPUT folder! \n\tNow exiting..."
    exit
fi
##
eval `grep "^INPUTFOLDER" ./$1`
if [ -n "$INPUTFOLDER" ] && [ -d $INPUTFOLDER/ ] ; then
    echo "INPUT FOLDER FOR RAW SPEECH: "$INPUTFOLDER
else
    echo "\n[ERROR] You did not specify an INPUTFOLDER folder, or the folder does not exist! \n\tNow exiting..."
    exit
fi
##
eval `grep "^INWAV" ./$1`
if [ -n "$INWAV" ] && [ -f $INWAV ]; then
    echo "SILENCE MARKED SPEECH FILE: "$INWAV
else
    echo "\n[ERROR] You did not specify the INWAV file, or the file does not exist! \n\tNow exiting..."
    exit
fi
##
eval `grep "^LABELFILE" ./$1`
if [ -n "$LABELFILE" ] && [ -f $LABELFILE ]; then
    echo "LABEL FOR ABOVE SPEECH FILE: "$LABELFILE
else
    echo "\n[ERROR] You did not specify a LABELFILE, or the file does not exist! \n\tNow exiting..."
    exit
fi
##
eval `grep "^SPTKDIR" ./$1`
if [ -n "$SPTKDIR" ] && [ -d $SPTKDIR ]; then
    echo "SPTK FOLDER: "$SPTKDIR
else
    echo "\n[ERROR] You did not specify the SPTK folder, or the folder does not exist! \n\tNow exiting..."
    exit
fi
##
#eval `grep "^METHOD" ./$1`
#if [ -n "$METHOD" ]; then
#    echo "METHOD FOR SEGMENTATION: "$METHOD
#else
#    echo "\n[ERROR] You did not specify a METHOD! \n\tNow exiting..."
#    exit
#fi
##
eval `grep "^MINLEN" ./$1`
if [ -n "$MINLEN" ]; then
    echo "CONCATENATE FILES SHORTER THAN: $MINLEN sec "
else
    echo "\n[ERROR] You did not specify the MINLEN for concatenating files! \n\tNow exiting..."
    exit
fi
##
echo "---------------------------------------------"
echo "            CONFIG READ OK!                  "
echo "---------------------------------------------"

## CHECKING IF REQUIRED TOOLS EXIST AND CAN BE RUN
## These are mostly SPTK tools!
if  ! type sox > /dev/null ; then
    echo "\n[ERROR] Cannot find 'sox'.\n\tNow exiting..."
    exit
fi
##
if [ ! -x $SPTKDIR/wav2raw ]; then
    echo "\n[ERROR] Cannot find 'wav2raw'. Please make sure that SPTK is installed correctly!\n\tNow exiting..."
    exit
fi
##
if [ ! -x $SPTKDIR/mfcc ]; then
    echo "\n[ERROR] Cannot find 'mfcc'. Please make sure that SPTK is installed correctly!\n\tNow exiting..."
    exit
fi
##
if [ ! -x $SPTKDIR/x2x ]; then
    echo "\n[ERROR] Cannot find 'x2x'. Please make sure that SPTK is installed correctly!\n\tNow exiting..."
    exit
fi
##
if [ ! -x $SPTKDIR/frame ]; then
    echo "\n[ERROR] Cannot find 'frame'. Please make sure that SPTK is installed correctly!\n\tNow exiting..."
    exit
fi
##
if [ ! -x $SPTKDIR/delta ]; then
    echo "\n[ERROR] Cannot find 'delta'. Please make sure that SPTK is installed correctly!\n\tNow exiting..."
    exit
fi
##
if [ ! -x $SPTKDIR/zcross ]; then
    echo "\n[ERROR] Cannot find 'zcross'. Please make sure that SPTK is installed correctly!\n\tNow exiting..."
    exit
fi
##
if [ ! -x $SPTKDIR/gmm ]; then
    echo "\n[ERROR] Cannot find 'gmm'. Please make sure that SPTK is installed correctly!\n\tNow exiting..."
    exit
fi
##
if [ ! -x $SPTKDIR/gmmp ]; then
    echo "\n[ERROR] Cannot find 'gmmp'. Please make sure that SPTK is installed correctly!\n\tNow exiting..."
    exit
fi
##


## CREATE OUTPUT FOLDER AND CHECKING FOR INPUT
if [ ! -d $OUTPUT/ ]; then
    mkdir $OUTPUT/
fi
##
if [ ! -d $INPUTFOLDER/ ]; then
    echo "[ERROR] The INPUTFOLDER does not exist!! Now exiting..."
    exit
fi
##
## CLEANING UP FROM PREVIOUS RUNS
rm -rf $INPUTFOLDER/temp*
rm -rf $OUTPUT/initialWav*
if [ -d $OUTPUT/wav ]; then
    rm -rf $OUTPUT/wav
fi

METHOD=1				                                ## Method to use for segmentation: 0 - Adintool 
                                                        ## 1 - GMM-VAD 2- Zero crossing and energy

## START THE SEGMENTATION
if [ $METHOD -eq 0 ]; then
    # using adintool
	python scripts/vad/VAD.py $METHOD $INPUTFOLDER/ ./resources/vad/conf.adintool $SPTKDIR $OUTPUT
fi

if [ $METHOD -eq 1 ]; then
    # using the GMM-VAD
	FNAME=$(basename $INWAV ".wav")
	cp $INWAV $INPUTFOLDER/
	python scripts/vad/VAD.py $METHOD $INPUTFOLDER/ ./resources/vad/conf.GMM $INWAV $LABELFILE $SPTKDIR $OUTPUT
fi

if [ $METHOD -eq 2 ]; then
    # using the zero-crossing rate
	python scripts/vad/VAD.py $METHOD $INPUTFOLDER/ ./resources/vad/conf.ZCR $SPTKDIR $OUTPUT
fi



## Concatenating files shorter than $MINLEN
if [ $MINLEN > 0 ]; then
    echo "Concatenating files shorter than the specified minimum length..."
    if [ -d $OUTPUT/wavConc ]; then
        rm -rf $OUTPUT/wavConc
    fi
    mkdir $OUTPUT/wavConc

    if [ -d $OUTPUT/logs ]; then
        rm -rf $OUTPUT/logs
    fi
    mkdir $OUTPUT/logs
    python scripts/vad/concatenateSpeechFiles.py $OUTPUT/wav $MINLEN $OUTPUT/wavConc > $OUTPUT/logs/log.concatenateSpeechWav
    rm -rf $OUTPUT/wav
    mv $OUTPUT/wavConc $OUTPUT/wav
fi

## Converting segmented wav files to 16kHz- needed for alignment
echo "Converting segmented audio files to 16 kHz"
if [ -d $OUTPUT/wav16 ]; then
    rm -rf $OUTPUT/wav16
fi
mkdir $OUTPUT/wav16
./scripts/general/fsConvertion.sh $OUTPUT/wav/ $OUTPUT/wav16/
echo "Converting initial audio files to 16 kHz"
if [ -d $OUTPUT/initialWav16 ]; then
    rm -rf $OUTPUT/initialWav16
fi
mkdir $OUTPUT/initialWav16
./scripts/general/fsConvertion.sh $OUTPUT/initialWav/ $OUTPUT/initialWav16/
rm -rf $OUTPUT/initialWav
echo "\nALL DONE OK!\n"
