#!/bin/sh
#################################################
## Author: Adriana STAN adriana.stan@com.utcluj.ro
## Project Simple4All - www.simple4all.org
## January 2013
#################################################
## Script used to output the acoustic confidence scores for a model, 
## a list of testing data and an output file

MODEL=$1
SCPFILE=$2
OUT=$3
BOOK=$4

OUTPUT=$5
HTK_BIN=$6
DICTIONARY=$7
PHONELIST=$8

echo $MODEL
echo $OUT
echo $BOOK
echo $OUTPUT
echo $DICTIONARY
echo $PHONELIST


## Create the list of utterances for acoustic scores 
set -e

sed "s@$OUTPUT/data/mfcc/@@" $SCPFILE > $OUTPUT/temp/temp0

###########################################################
#                        				  #
###########################################################

for SKIP in 1 3; do

	echo "=========================="
	echo "SKIP $SKIP"
	echo "=========================="

	####################################
	## ACOUSTIC MODEL WITH WORD NETWORK:
	####################################
	echo "\n##                       Word network:                  ##\n"
	$HTK_BIN/HVite  -T 1  -w -L $OUTPUT/data/wordNets-$SKIP/ -X slf -i $OUTPUT/temp/wordNetConfidence.mlf  -o T -S $SCPFILE -H $MODEL $DICTIONARY $PHONELIST | grep -o '\] .* \[' > $OUTPUT/temp/temp-1
	sed 's/\[//' $OUTPUT/temp/temp-1 | sed 's/\]//' > $OUTPUT/temp/temp1
	rm $OUTPUT/temp/temp-1
	sed 's/\.rec/\.lab/' $OUTPUT/temp/wordNetConfidence.mlf > $OUTPUT/temp/reco2.mlf
	cp $OUTPUT/temp/wordNetConfidence.mlf $OUTPUT/temp/wordNetConfidence-$SKIP
	# in case HVite cannot recognise an utterance, adjust the scpfile for the forced alignment
	grep 'data/mfcc' $OUTPUT/temp/reco2.mlf | sed 's/.lab/.mfcc/' | sed 's/\"//g' > $SCPFILE
	sed "s@$OUTPUT/data/mfcc/@@" $SCPFILE > $OUTPUT/temp/temp0

	########################################
	## ACOUSTIC MODEL WITH FORCED ALIGNMENT:
	########################################
	echo "\n##                     Forced alignment                 ##\n"
	$HTK_BIN/HVite  -T 1  -a -I $OUTPUT/temp/reco2.mlf -i $OUTPUT/temp/reco.mlf -y lab -S $SCPFILE -H $MODEL $DICTIONARY $PHONELIST | grep -o '\] .* \['  > $OUTPUT/temp/temp-1
	sed 's/\[//' $OUTPUT/temp/temp-1 | sed 's/\]//' > $OUTPUT/temp/temp2
	rm $OUTPUT/temp/temp-1


	#####################################
	## BACKGROUND MODEL WITH WORD NETWORK:
	#####################################
	echo "\n##             Background model with word network       ##\n"
	$HTK_BIN/HVite  -T 1  -w resources/bghmm/bghmm.slf -i $OUTPUT/temp/reco.mlf -f -S $SCPFILE -H resources/bghmm/bghmm  $DICTIONARY resources/bghmm/hmmlist_bghmm | grep -o '\] .* \[' > $OUTPUT/temp/temp-1
	sed 's/\[//' $OUTPUT/temp/temp-1 | sed 's/\]//' > $OUTPUT/temp/temp3
	rm $OUTPUT/temp/temp-1

	#########################################
	## BACKGROUND MODEL WITH FORCED ALIGNMENT:
	#########################################
	echo "\n##          Background model with forced alignment      ##\n"
	$HTK_BIN/HVite  -T 1  -a -I resources/bghmm/bghmm.lab -i $OUTPUT/temp/reco.mlf -y lab -S $SCPFILE -H resources/bghmm/bghmm $DICTIONARY resources/bghmm/hmmlist_bghmm | grep -o '\] .* \[' > $OUTPUT/temp/temp-1
	sed 's/\[//' $OUTPUT/temp/temp-1 | sed 's/\]//' > $OUTPUT/temp/temp4
	paste $OUTPUT/temp/temp0 $OUTPUT/temp/temp1 $OUTPUT/temp/temp2 $OUTPUT/temp/temp3 $OUTPUT/temp/temp4 > $OUTPUT/temp/SKIP$SKIP
	rm $OUTPUT/temp/temp1 $OUTPUT/temp/temp2 $OUTPUT/temp/temp3 $OUTPUT/temp/temp4
done

python scripts/confidenceScores/createAcousticScoresFile.py $OUTPUT/temp/SKIP1 $OUTPUT/temp/SKIP3 $OUT

