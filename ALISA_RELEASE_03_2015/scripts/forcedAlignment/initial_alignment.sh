#!/bin/bash

## Top level script for getting initial alignment with something that resembles the multisyn tools. 
### Calls many scripts adapted over the ages from Multisyn tools

###### locations -----------
WORK=$1
SCRIPT=$2

## resources:
WAVES=$3
UTTSDATA=$4
LETTERS=$5
PUNCS=$6

## settings:
USE_N_UTTS=$7

## supervised dict and phone list settings
SUPERVISED=$8
PHONELIST=$9
DICTIONARY=${10}

###### Store original location so we can move away and then return:
HERE=`pwd`

set -e 

###### setup directory structure, copy in data:

if [ -d $WORK ]; then
	      rm -rf $WORK
	fi
mkdir $WORK
cd $WORK

mkdir lab wav alignment wav_nist mfcc

## cp waves and text transcription:
for wave in `ls $WAVES/*.wav | head -$USE_N_UTTS` ; do
  cp $wave $WORK/wav ;
done

cat $UTTSDATA | head -$USE_N_UTTS > $WORK/utts.data  ## have expanded abbrev.s here?
  
## make initial MLF:
$SCRIPT/forcedAlignment/initialise_labels.py  $WORK/utts.data  $WORK/alignment/words.mlf  $WORK/alignment/main.lex  $WORK/alignment/phone_list $LETTERS $PUNCS unicode

cp $PHONELIST $WORK/alignment/phone_list

######## alignment
$SCRIPT/forcedAlignment/setup_alignment 
$SCRIPT/forcedAlignment/make_mfccs alignment wav utts.data

cd alignment

# make mfcc list:
ls $WORK/mfcc/* > train.scp

## make phonelist ("letters", sil, skip):  -- [this in now done by initialise_labels.py]

$SCRIPT/forcedAlignment/do_align_multisyn_lexicon . $SUPERVISED $PHONELIST $DICTIONARY
cd ..

# Split mlf alignment file (we will actually work from MLF -- but get individual labels for viewing etc.):
grep -v " skip "  $WORK/alignment/aligned.4.mlf > $WORK/alignment/aligned.4.noskip.mlf
$SCRIPT/forcedAlignment/break_mlf $WORK/alignment/aligned.4.noskip.mlf $WORK/lab

## go back to original location:
cd $HERE
