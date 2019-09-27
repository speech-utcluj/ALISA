#!/bin/sh

#################################################
## Author: Adriana STAN adriana.stan@com.utcluj.ro
## Project Simple4All - www.simple4all.org
## May 2012
#################################################

## This script converts all wav files from a folder to 16kHz
## Inputs: input directory

## Will create a folder with the ending 16. E.g. wav will become wav16

#HOME=`pwd`
INDIR=$1
OUTDIR=$2

set -e
cd $INDIR
echo $INDIR
for wave in `ls *.wav` ; do
	#echo $wave ;
	sox -G $wave  -r 16000 -c 1 $OUTDIR/$wave 
done

cd $HOME

