#!/user/bin/python
# -*- coding: utf-8 -*-

## Author: Yoshitaka Mamiya
## Edited: Adriana STAN adriana.stan@com.utcluj.ro
## Project Simple4All - www.simple4all.org
## January 2013

import math
import os
import re
import shutil
import subprocess
import sys


def adintool_vad(wDir, cFile, worDir):

    print "Now running adintools for each wav files.",
    # make directory for VADed wav files
    os.mkdir(worDir+"/wav_VAD")

    # read cFile and set variables
    confFile = open(cFile, "r")
    adintoolArg = "" # adintool command argument
    for line in confFile:
        if len(line.split()) == 1:
            matter = line.strip(" \n#")
        elif matter == "adintool":
            if line.split()[1] != "def":
                if line.split()[0] == "l":
                    adintoolArg += "-lv %s " % line.split()[1]
                elif line.split()[0] == "z":
                    adintoolArg += "-zc %s " % line.split()[1]
                elif line.split()[0] == "h":
                    adintoolArg += "-headmargin %s " % line.split()[1]
                elif line.split()[0] == "t":
                    adintoolArg += "-tailmargin %s " % line.split()[1]

    # run adintool for each wav files
    borderSec = 15 # temporary
    borderSec2 = 20 # temporary
    totalLength = 0 # total wav length beyond borderSec
    totalLength2 = 0 # total wav length beyond borderSec2
    beyondCount = 0 # the number of trimmed wav beyond borderSec
    beyondCount2 = 0 # the number of trimmed wav beyond borderSec2
    lessCount = 0 # the number of trimmed wav less than borderSec
    files = os.listdir(wDir)
    files.sort()
    for inFile in files:
        if os.path.splitext(inFile)[1] == ".wav":
            print ".",
            # extract sampling rate
            p = subprocess.Popen("soxi -r %s" % (wDir+"/"+inFile),
                                 shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
            p.wait()
            sampRate = float(p.stdout.readline().strip())
            # run adintool
            p = subprocess.Popen("scripts/vad/adintool -in file -freq %s %s -out file -filename %s"
                                 % (sampRate, adintoolArg, worDir+"/wav_VAD/"+os.path.splitext(inFile)[0]),
                                 shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
            adinresult = p.communicate(wDir+"/"+inFile)[0]
            print adinresult
    # rename wav files
    # extract length of wav files
    # remove 0 length wav files
    files = os.listdir(worDir+"/wav_VAD")
    files.sort()
    for inFile in files:
        if os.path.splitext(inFile)[1] == ".wav":
            # extract length and count
            p = subprocess.Popen("soxi -d %s/wav_VAD/%s" % (worDir, inFile),
                                 shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
            p.wait()
            wavlength = re.split(":", p.stdout.readline().strip())
            wav_length = int(wavlength[0])*360+int(wavlength[1])*60+float(wavlength[2])
            if wav_length >= borderSec:
                totalLength += wav_length
                beyondCount += 1
                if wav_length >= borderSec2:
                    totalLength2 += wav_length
                    beyondCount2 += 1
            # remove 0 length files
            elif wav_length == 0:
                os.remove(worDir+"/wav_VAD/"+inFile)
                continue
            else:
                lessCount += 1
            # rename
            tempA = inFile.split(".")
            temp = len(tempA)
            if temp == 3:
                filename = "%s_%05d.wav" % (tempA[0], int(tempA[1])+1)
            else:
                filename = ""
                for i in range(0, temp-3):
                    filename += tempA[i] + "."
                filename += "%s_%05d.wav" % (tempA[temp-3], int(tempA[temp-2])+1)
            os.rename(worDir+"/wav_VAD/"+inFile, worDir+"/wav_VAD/"+filename)

    print "\nWav files have been made in wav_VAD directory."
    print "The number of wav files which length is over %d sec      : %4d" % (borderSec, beyondCount)
    print "The total length of wav files which length is over %d sec: %4.2f" % (borderSec, totalLength)
    print "The number of wav files which length is less than %d sec : %4d" % (borderSec, lessCount)
    print "The number of wav files which length is over %d sec      : %4d" % (borderSec2, beyondCount2)
    print "the total length of wav files which length is over %d sec: %4.2f" % (borderSec2, totalLength2)

    return 0


def integrate_features(inFile1, dim1, inFile2, dim2, outFile, sptkDir):

    # transform inFile1 and inFile2 into ascii
    # %sa in Popen below means that e.g. inFile is "temp.mfcc", %sa is "temp.mfcca" 
    p1 = subprocess.Popen("%s/x2x +fa < %s > %sa" % (sptkDir, inFile1, inFile1),
                          shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    p2 = subprocess.Popen("%s/x2x +fa < %s > %sa" % (sptkDir, inFile2, inFile2),
                          shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    p1.communicate()
    p2.communicate()

    # open inFile1, inFile2 and outFile
    infile1 = open(inFile1+"a", "r")
    infile2 = open(inFile2+"a", "r")
    outfile = open(outFile+"a", "w")

    # read inFiles dim times and write into outFile
    while True:
        for num in range(1, dim1+1): # range(1, dim1+1) means that number of iteration is dim1
            outfile.write(infile1.readline())
        for num in range(1, dim2+1):
            outfile.write(infile2.readline())
        # judge whether file finished
        cur_pointer = infile1.tell() # current position of file pointer
        if infile1.readline() != "":
            infile1.seek(cur_pointer, 0) # return file pointer
        else:
            break

    infile1.close()
    infile2.close()
    outfile.close()

    # transform outFile into float
    p = subprocess.Popen("%s/x2x +af < %sa > %s" % (sptkDir, outFile, outFile),
                         shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    p.communicate()

    return 0


def median_filter(inFile, outFile, medianWindowLength):

    infile = open(inFile, "r")

    count = 0
    array1 = [] # array to sort value 
    array2 = [] # array to save window length values
    array3 = [] # array to save output
    halfLength = (medianWindowLength - 1) / 2

    # calculate median
    for line in infile:
        num = float(line.strip())
        array1.append(num)
        array2.append(num)
        count += 1
        if count > medianWindowLength:
            array1.remove(array2[0])
            array2.remove(array2[0])
            array1.sort()
            array3.append(array1[halfLength+1])
        # halfLength number from start is calculated below
        elif count > halfLength:
            array1.sort()
            array3.append(array1[len(array1)/2]) # if len(array1) is even number, bigger position is chosen as median
    # halfLength number from end is calculated below
    for line in range(0, halfLength):
        array1.remove(array2[0])
        array2.remove(array2[0])
        array1.sort()
        array3.append(array1[len(array1)/2])
    
    infile.close()

    # output
    outfile = open(outFile, "w")
    for num in range(0, len(array3)):
        outfile.write(str(array3[num]))
        outfile.write("\n")
    outfile.close()

    return 0


def normal_dist(ave, sigma2, x):

    # calculate f(x) of normal distribution from arguments
    temp1 = 1.0 / math.pow(2.0*math.pi*sigma2, 0.5)
    temp2 = math.exp(-1.0*math.pow(x-ave, 2)/(2.0*sigma2))
    return temp1*temp2


def bisection_cross_normal(ave1, sigma21, ave2, sigma22, prec, upper):

    # calculate the cross point of two normal distributions
    x1 = ave1 # left value
    x2 = ave2 # right value
    count = 0 # number of iteration
    while True:
        x3 = (x2 - x1) / 2.0 + x1 # middle of x1 and x2
        y1 = normal_dist(ave1, sigma21, x3) # dist value of sp
        y2 = normal_dist(ave2, sigma22, x3) # dist value of sil
        # check condition to finish
        y3 = y1 - y2
        if math.fabs(y3) < prec:
            return x3
        # renovate x1 or x2
        elif y3 > 0:
            x1 = x3
        else:
            x2 = x3
        # check number of iteration
        count += 1
        if count > upper:
            return 0.0


def gmm_vad(wDir, initWav, cFile, lFile, worDir, sptkDir):

    print "Now calculating the initial GMMs.",
    sys.stdout.flush()

    # cutting position
    cut_speech = []
    cut_silence = []

    # preparing two directories for speech and silence wav files etc
    os.mkdir(worDir+"/speech")
    os.mkdir(worDir+"/silence")
    speechDir = worDir + "/speech"
    silenceDir = worDir + "/silence"

    # read cFile and set variables
    confFile = open(cFile, "r")
     # SPTK command argument
    mfccArg = ""
    zerocrossArg = ""
    gmmArg = ""
    gmmpArg = ""
    mfccLength = 12 # default
    frameLength = 256 # default
    deltaFlag = True
    zerocrossFlag = True

    # read the configuration parameters
    for line in confFile:
        if len(line.split()) == 1:
            matter = line.strip(" \n#")
        elif matter == "MFCC":
            if line.split()[1] != "def":
                if line.split()[0] != "d" and line.split()[0] != "E" and line.split()[0] != "0":
                    mfccArg += "-" + line.split()[0] + " " + line.split()[1] + " "
                    if line.split()[0] == "m":
                        mfccLength = line.split()[1]
                    elif line.split()[0] == "l":
                        frameLength = line.split()[1]
                else:
                    mfccArg += "-" + line.split()[0] + " "
                    if line.split()[0] == "E":
                        mfccLength += 1
                    elif line.split()[0] == "0":
                        mfccLength += 1
        elif matter == "DELTA":
            if line.split()[1] == "0":
                deltaFlag = False
            else:
                deltaArg = "-m %d -r 1 %s" % (mfccLength-1, line.split()[1])
        elif matter == "ZEROCROSS":
            if line.split()[1] != "def":
                zerocrossFlag = False
            else:
                zerocrossArg = "-l %s " % frameLength
        elif matter == "GMM":
            if line.split()[1] != "def":
                gmmArg += "-" + line.split()[0] + " " + line.split()[1] + " "
                if line.split()[0] == "m":
                    gmmpArg += "-m " + line.split()[1] + " "
        elif matter == "THRESHOLD":
            if line.split()[0] == "f":
                thShiftFlag = int(line.split()[1])
            elif line.split()[0] == "m":
                moveTh = int(line.split()[1])
            elif line.split()[0] == "c":
                totalLengthCondition = int(line.split()[1])
        elif matter == "LENGTH":
            if line.split()[0] == "f":
                lenFlag = int(line.split()[1])
            elif line.split()[0] == "s":
                minimumLen = int(line.split()[1])
            elif line.split()[0] == "c":
                wayToCon = int(line.split()[1]) 
        elif matter == "LABEL":
            if line.split()[0] == "f":
                labelFlag = int(line.split()[1])               
    
    # calculate vector length
    if deltaFlag:
        if zerocrossFlag:
            vectorLength = mfccLength * 2 + 1
        else:
            vectorLength = mfccLength * 2
    else:
        if zerocrossFlag:
            vectorLength = mfccLength + 1
        else:
            vectorLength = mfccLength
    frameArg = "-l %s -p %d" % (frameLength, int(frameLength)/2)
    gmmArg += "-l " + str(vectorLength) + " "
    gmmpArg += "-l " + str(vectorLength) + " "
    confFile.close()
    print ".",
    sys.stdout.flush()
     # extract sampling rate of initial wav file
    p = subprocess.Popen("soxi -r %s" % (wDir+"/"+initWav),
                         shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    p.wait()
    initSampRate = float(p.stdout.readline().strip())
    mfccArg += "-f %.3f " % (initSampRate/1000.0)

    # extract length of initial wav file
    p = subprocess.Popen("soxi -d %s" % (wDir+"/"+initWav),
                         shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    p.wait()
    wavlength = re.split(":", p.stdout.readline().strip())
    wavlength_sec = int(wavlength[0])*360+int(wavlength[1])*60+float(wavlength[2])
    print ".",
    sys.stdout.flush()

    # read label File and extract cutting positions and calculate statistics of sil
    flab = open(lFile, "r")
    sil_his=[]
    pre_line = ""
    for line in flab:
        # extract cutting positions for silence
        if re.search("sil", line):
            # from start to current label
            if re.search("#", pre_line):
                cut_silence.append("0 %s" % line.split()[0])
                sil_his.append(float(line.split()[0]))
            # from the end of previous label to current label
            else:
                length = float(line.split()[0]) - float(pre_line.split()[0])
                if length > 0:
                    cut_silence.append("%s %s" % (pre_line.split()[0], length))
                    sil_his.append(length)
                else:
                    print float(line.split()[0])
                    print "Warnng: Time stamp of Label File is not in order."
                    return -1
            # check length
        
            if float(int(float(line.split()[0])*10))/10 > wavlength_sec:
                print "Warning: Time stamp of Label File is over length of initial wav file."
                return -1
        # extract cutting positions for speech
        elif not re.search("#", line):
            if re.search("#", pre_line):
                cut_speech.append("0 %s" % line.split()[0])
            else:
                length = float(line.split()[0]) - float(pre_line.split()[0])
                if length > 0:
                    cut_speech.append("%s %s" % (pre_line.split()[0], length))
                else:
                    print float(line.split()[0])
                    print "Warning: Time stamp of Label File is not in order."
                    return -1
            if float(int(float(line.split()[0])*10))/10 > wavlength_sec:
                print "Warning: Time stamp of Label File is over length of initial wav file."
                return -1
        pre_line = line
    flab.close()
    print ".",
    sys.stdout.flush()
    # calculate average of sil
    ave_sil = 0.0
    for time in sil_his:
        ave_sil += time
    ave_sil /= len(sil_his)

    # cut initial wav file and put into prepared directories
    temp = 1
    for arg in cut_speech:
        p = subprocess.Popen("sox %s %s/speech_%05d.wav trim %s" % (wDir+"/"+initWav, speechDir, temp, arg),
                             shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
        p.wait()
        if re.search("Premature EOF", p.stdout.readline().strip()):
            print "Error: failed to extract speech part from initial wav file."
            return 1
        temp += 1
    temp = 1
    for arg in cut_silence:
        p = subprocess.Popen("sox %s %s/silence_%05d.wav trim %s" % (wDir+"/"+initWav, silenceDir, temp, arg),
                             shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
        p.wait()
        if re.search("Premature EOF", p.stdout.readline().strip()):
            print "Error: failed to extract speech part from initial wav file."
            return 1
        temp += 1
    print ".",
    sys.stdout.flush()

    # connect wav files in speech directory
    files = os.listdir(speechDir)
    files.sort()
     # exception for 1 file
    if len(files) == 1:
        os.rename(speechDir+"/"+files[0], speechDir+"/speech_for_gmm.wav")
     # in the case directory contains plural wav files
    else:
        temp = 1
        arg = ""
        for inFile in files:
            if temp <= 2:
                arg = arg + speechDir + "/" + inFile + " "
                if temp == 2:
                    p = subprocess.Popen("sox %s %s/temp%d.wav" % (arg, speechDir, temp),
                                         shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
                    p.communicate()
                    arg = speechDir + "/temp%d.wav " % temp
            else:
                arg = arg + speechDir + "/" + inFile + " " + speechDir + "/temp%d.wav" % temp
                p = subprocess.Popen("sox %s" % arg,
                                     shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
                p.communicate()
                os.remove(speechDir+"/temp%d.wav"%(temp-1))
                arg = speechDir + "/temp%d.wav " % temp
            temp += 1
        os.rename(arg.strip(), speechDir+"/speech_for_gmm.wav")
    print ".",
    sys.stdout.flush()

    # connect wav files in silence directory
    files = os.listdir(silenceDir)
    files.sort()
     # exception for 1 file
    if len(files) == 1:
        os.rename(silenceDir+"/"+files[0], silenceDir+"/silence_for_gmm.wav")
     # in the case directory contains plural wav files
    else:
        temp = 1
        arg = ""
        for inFile in files:
            if temp <= 2:
                arg = arg + silenceDir + "/" + inFile + " "
                if temp == 2:
                    p = subprocess.Popen("sox %s %s/temp%d.wav" % (arg, silenceDir, temp),
                                         shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
                    p.communicate()
                    arg = silenceDir + "/temp%d.wav " % temp
            else:
                arg = arg + silenceDir + "/" + inFile + " " + silenceDir + "/temp%d.wav" % temp
                p = subprocess.Popen("sox %s" % arg,
                                     shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
                p.communicate()
                os.remove(silenceDir+"/temp%d.wav"%(temp-1))
                arg = silenceDir + "/temp%d.wav " % temp
            temp += 1
        os.rename(arg.strip(), silenceDir+"/silence_for_gmm.wav")
    print ".",
    sys.stdout.flush()

    # convert connected wav file to raw(float) file
    p1 = subprocess.Popen("%s/wav2raw +f %s/speech_for_gmm.wav" % (sptkDir,speechDir),
                          shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    p2 = subprocess.Popen("%s/wav2raw +f %s/silence_for_gmm.wav" % (sptkDir, silenceDir),
                         shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    p1.communicate()
    p2.communicate()

    # make frame shifted raw file
    p1 = subprocess.Popen("%s/frame %s %s/speech_for_gmm.raw > %s/speech_for_gmm.rawf" % (sptkDir, frameArg, speechDir, speechDir),
                          shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    p2 = subprocess.Popen("%s/frame %s %s/silence_for_gmm.raw > %s/silence_for_gmm.rawf" % (sptkDir, frameArg, silenceDir, silenceDir),
                          shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    p1.communicate()
    p2.communicate()

    # calculate mfcc
    p1 = subprocess.Popen("%s/mfcc %s %s/speech_for_gmm.rawf > %s/speech_for_gmm.mfcc" % (sptkDir, mfccArg, speechDir, speechDir),
                          shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    p2 = subprocess.Popen("%s/mfcc %s %s/silence_for_gmm.rawf > %s/silence_for_gmm.mfcc" % (sptkDir,mfccArg, silenceDir, silenceDir),
                          shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    p1.communicate()
    p2.communicate()

    # calculate delta mfcc
    if deltaFlag:
        p1 = subprocess.Popen("%s/delta %s %s/speech_for_gmm.mfcc > %s/speech_for_gmm.delta" % (sptkDir, deltaArg, speechDir, speechDir),
                              shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
        p2 = subprocess.Popen("%s/delta %s %s/silence_for_gmm.mfcc > %s/silence_for_gmm.delta" % (sptkDir, deltaArg, silenceDir, silenceDir),
                              shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
        p1.communicate()
        p2.communicate()

    # calculate zero cross
    if zerocrossFlag:
        p1 = subprocess.Popen("%s/zcross %s < %s/speech_for_gmm.rawf > %s/speech_for_gmm.zcross" % (sptkDir, zerocrossArg, speechDir, speechDir),
                              shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
        p2 = subprocess.Popen("%s/zcross %s < %s/silence_for_gmm.rawf > %s/silence_for_gmm.zcross" % (sptkDir, zerocrossArg, silenceDir, silenceDir),
                              shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
        p1.communicate()
        p2.communicate()

    # integrate features
    if deltaFlag:
        if zerocrossFlag:
            integrate_features(speechDir+"/speech_for_gmm.delta", 2*mfccLength, speechDir+"/speech_for_gmm.zcross", 1,
                               speechDir+"/speech_for_gmm.feat", sptkDir)
            integrate_features(silenceDir+"/silence_for_gmm.delta", 2*mfccLength, silenceDir+"/silence_for_gmm.zcross", 1,
                               silenceDir+"/silence_for_gmm.feat", sptkDir)
        else:
            os.rename(speechDir+"/speech_for_gmm.delta", speechDir+"/speech_for_gmm.feat")
            os.rename(silenceDir+"/silence_for_gmm.delta", silenceDir+"/silence_for_gmm.feat")
    elif zerocrossFlag:
        integrate_features(speechDir+"/speech_for_gmm.mfcc", mfccLength, speechDir+"/speech_for_gmm.zcross", 1,
                           speechDir+"/speech_for_gmm.feat", sptkDir)
        integrate_features(silenceDir+"/silence_for_gmm.mfcc", mfccLength, silenceDir+"/silence_for_gmm.zcross", 1,
                           silenceDir+"/silence_for_gmm.feat", sptkDir)
    else:
        os.rename(speechDir+"/speech_for_gmm.mfcc", speechDir+"/speech_for_gmm.feat")
        os.rename(silenceDir+"/silence_for_gmm.mfcc", silenceDir+"/silence_for_gmm.feat")

    # calculate gmm
    p = subprocess.Popen("%s/gmm %s %s/speech_for_gmm.feat > %s/speech.gmm" % (sptkDir, gmmArg, speechDir, speechDir),
                         shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    p = subprocess.Popen("%s/gmm %s %s/silence_for_gmm.feat > %s/silence.gmm" % (sptkDir, gmmArg, silenceDir, silenceDir),
                         shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)

    print "\nGMMs for speech and silence have been made."
    print "Now calculating the probabilities of each wav files.",
    sys.stdout.flush()

    # calculate probability using gmm
    files = os.listdir(wDir)
    files.sort()
    for inFile in files:
        print ".",
        sys.stdout.flush()
        if os.path.splitext(inFile)[1] == ".wav":
            filename = os.path.splitext(inFile)[0]
            p = subprocess.Popen("%s/wav2raw +f %s/%s" % (sptkDir, wDir, inFile),
                                 shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
            p.communicate()
            print wDir+"/"+filename+".raw", worDir+"/"+filename+".raw"
            os.rename(wDir+"/"+filename+".raw", worDir+"/"+filename+".raw")
            p = subprocess.Popen("%s/frame %s %s/%s.raw > %s/%s.rawf" % (sptkDir, frameArg, worDir, filename, worDir, filename),
                                 shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
            p.communicate()
            p = subprocess.Popen("%s/mfcc %s %s/%s.rawf > %s/%s.mfcc" % (sptkDir, mfccArg, worDir, filename, worDir, filename),
                                 shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
            p.communicate()
            if deltaFlag:
                p = subprocess.Popen("%s/delta %s %s/%s.mfcc > %s/%s.delta" % (sptkDir, deltaArg, worDir, filename, worDir, filename),
                                     shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
                p.communicate()
                if zerocrossFlag:
                    p = subprocess.Popen("%s/zcross %s < %s/%s.rawf > %s/%s.zcross" % (sptkDir, zerocrossArg, worDir, filename, worDir, filename),
                                         shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
                    p.communicate()
                    integrate_features(worDir+"/"+filename+".delta", 2*mfccLength, worDir+"/"+filename+".zcross", 1,
                                       worDir+"/"+filename+".feat", sptkDir)
                else:
                    os.rename(worDir+"/"+filename+".delta", worDir+"/"+filename+".feat")
            elif zerocrossFlag:
                p = subprocess.Popen("%s/zcross %s < %s/%s.rawf > %s/%s.zcross" % (sptkDir, zerocrossArg, worDir, filename, worDir, filename),
                                     shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
                p.communicate()
                integrate_features(worDir+"/"+filename+".mfcc", mfccLength, worDir+"/"+filename+".zcross", 1,
                                   worDir+"/"+filename+".feat", sptkDir)
            else:
                os.rename(worDir+"/"+filename+".mfcc", worDir+"/"+filename+".feat")
            
            p1 = subprocess.Popen("%s/gmmp %s %s/speech/speech.gmm %s/%s.feat > %s/%s.speech" % (sptkDir, gmmpArg, worDir, worDir, filename, worDir, filename),
                                  shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
            p2 = subprocess.Popen("%s/gmmp %s %s/silence/silence.gmm %s/%s.feat > %s/%s.silence" % (sptkDir, gmmpArg, worDir, worDir, filename, worDir, filename),
                                  shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
            p1.communicate()
            p2.communicate()
            p1 = subprocess.Popen("%s/x2x +fa < %s/%s.speech > %s/%s.speecha" % (sptkDir, worDir, filename, worDir, filename),
                                  shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
            p2 = subprocess.Popen("%s/x2x +fa < %s/%s.silence > %s/%s.silencea" % (sptkDir, worDir, filename, worDir, filename),
                                  shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
            p1.communicate()
            p2.communicate()

    print "\nProbabilities of wav files for GMMs have been calculated."
    print "Now calculating cutting positions of each wav files.",
    sys.stdout.flush()

    # compare probabilities and write result into outfile
    files = os.listdir(worDir)
    files.sort()
    for inFile in files:
        if os.path.splitext(inFile)[1] == ".speecha":
            filename = os.path.splitext(inFile)[0]
            spfile = open(worDir+"/"+inFile, "r")
            sifile = open(worDir+"/"+filename+".silencea", "r")
            outfile = open(worDir+"/"+filename+".result", "w")
            spscore = spfile.readline()
            while spscore:
                siscore = sifile.readline()
                scoredif = float(spscore) - float(siscore)
                outfile.write(str(scoredif)+"\n")
                spscore = spfile.readline()
            spfile.close()
            sifile.close()
            outfile.close()
    print ".",
    sys.stdout.flush()

    # median filtering
    medianWindowLength = 11 # temporary (odd number required)
    files = os.listdir(worDir)
    files.sort()
    for inFile in files:
        if os.path.splitext(inFile)[1] == ".result":
            filename = os.path.splitext(inFile)[0]
            
            median_filter(worDir+"/"+inFile, worDir+"/"+filename+".fdresult", medianWindowLength)
    print ".",
    sys.stdout.flush()

    # calculate histogram of sp and sil for initial data
    files = os.listdir(worDir)
    files.sort()
#    for inFile in files: # discover result file for initial wav file
#        if os.path.splitext(inFile)[1] == ".fdresult":
#            break
    inFile = os.path.splitext(initWav)[0]+ '.fdresult'
    frameSecHalfLength = float(frameLength) / initSampRate / 2.0
    frameCount = 0.0
    ccount = 0 # count for lasting minus value
    iniresfile = open(worDir+"/"+inFile, "r")
    labfile = open(lFile, "r")
    currentFlag = ""
    currentSeg = [0.0, 0.0]
    silhistfile = open(worDir+"/silhist", "w")
    sphistfile = open(worDir+"/sphist", "w")
    for line in iniresfile:
        frameCount += 1
        if float(line.strip()) < 0.0:
            ccount += 1
        elif ccount != 0:
            segPlcSec = (frameCount - 1 - ccount / 2.0) * frameSecHalfLength # middle sec of continuous minus value

            if segPlcSec > currentSeg[1]:
                while True:
                    inLine = labfile.readline().strip()
                    if inLine == "":
                        print "Error occurs in initial decoding process."
                        print segPlcSec, currentSeg[1]
                        return 1
                    if re.search("#", inLine):
                        continue
                    elif re.search("sil", inLine):
                        currentFlag = "sil"
                        currentSeg[0] = currentSeg[1]
                        currentSeg[1] = float(inLine.split()[0])
                    else:
                        currentFlag = "speech"
                        currentSeg[0] = currentSeg[1]
                        currentSeg[1] = float(inLine)
                    if segPlcSec <= currentSeg[1]:
                        break
            if currentFlag == "sil":
                silhistfile.write(str(ccount)+"\n")
                ccount = 0
            else:
                sphistfile.write(str(ccount)+"\n")
                ccount = 0
    iniresfile.close()
    labfile.close()
    silhistfile.close()
    sphistfile.close()
    print ".",
    sys.stdout.flush()
     # count number of each degree
    sildeg = {}
    silhistfile = open(worDir+"/silhist", "r")
    for line in silhistfile:
        cur_degree = int(round(int(line.strip()), -1))
        if cur_degree in sildeg:
            sildeg[cur_degree] += 1
        else:
            sildeg[cur_degree] = 1
    silhistfile.close()
    spdeg = {}
    sphistfile = open(worDir+"/sphist", "r")
    for line in sphistfile:
        cur_degree = int(round(int(line.strip()), -1))
        if cur_degree in spdeg:
            spdeg[cur_degree] += 1
        else:
            spdeg[cur_degree] = 1
    sphistfile.close()

    # discover positions to divide
    # make two normal distribution for sil and sp histograms
    siltotal = 0L
    silcount = 0
    siltotal2 = 0L
    for key in sildeg.keys():
        siltotal += key * sildeg[key]
        silcount += sildeg[key]
        siltotal2 += key * key * sildeg[key]
    if silcount == 0:
        silcount = 1    
    silave = float(siltotal) / float(silcount)
    sildev = pow(float(silcount * siltotal2 - siltotal * siltotal) / float(silcount * silcount), 0.5)
    sptotal = 0L
    spcount = 0
    sptotal2 = 0L
    for key in spdeg.keys():
        sptotal += key * spdeg[key]
        spcount += spdeg[key]
        sptotal2 += key * key * spdeg[key]
    if spcount == 0:
        spcount = 1
    spave = float(sptotal) / float(spcount)
    spdev = pow(float(spcount * sptotal2 - sptotal * sptotal) / float(spcount * spcount), 0.5)
    prec = 0.001 # temporary
    upper = 500 # temporary
     # calculate cross point of sil distribution and sp distribution
    dPos = bisection_cross_normal(spave, spdev*spdev, silave, sildev*sildev, prec, upper)
     # check dPos calculated
    if dPos == 0.0:
        print "\nI cannot calculate where I should divide sp and sil."
        print "sp_distribution:  ave[%4f], dev[%4f]" % (spave, spdev)
        print "sil_distribution: ave[%4f], dev[%4f]" % (silave, sildev)
        return 1
    elif dPos*frameSecHalfLength < 0.05: # shorter than 50msec # temporary
        print "\nWarning: Border between sp and sil is shorter than 50msec."
        print "Border: %4f[msec]" % (dPos*frameSecHalfLength)
    else:
        print "."
     # decide length condition
    if thShiftFlag:
        files = os.listdir(worDir)
        files.sort()
        conditionFlg = 0
        initialdPos = dPos
        while True:
            # error judgement
            if conditionFlg * moveTh > initialdPos:
                print "I cannot control sil and sp threshold."
                print "Please set suitable THRESHOLD condition."
                return 1
            totalOverSec = 0.0 # total length of over threshold wav
            for inFile in files:
                if os.path.splitext(inFile)[1] == ".fdresult":
                    resfile = open(worDir+"/"+inFile, "r")
                    lines = resfile.readlines()
                    resfile.close()
                    count = 0 # a number of current frame from previous cut point
                    contCount = 0 # the number of continuing minus values
                    for line in lines:
                        count += 1
                        if float(line.strip()) < 0:
                            contCount += 1
                        elif contCount != 0:
                            if contCount > dPos:
                                cutSecLength = (count - contCount / 2) * frameSecHalfLength
                                if cutSecLength > 15: # cut length if over 15 sec # temporary
                                    totalOverSec += cutSecLength
                                count = contCount / 2
                            contCount = 0
            if conditionFlg == 0:
                conditionFlg += 1
                conditionValue = totalLengthCondition - totalOverSec
                if conditionValue > 0: # in the case wav over 15 sec is less, make threshold bigger
                    dPos += moveTh
                elif conditionValue < 0:
                    dPos -= moveTh
                else:
                    break
            else:
                conditionFlg += 1
                if conditionValue * (totalLengthCondition - totalOverSec) > 0: # in the case pre result and current result have the same sign
                    conditionValue = totalLengthCondition - totalOverSec
                    if conditionValue > 0:
                        dPos += moveTh
                    else:
                        dPos -= moveTh
                elif conditionValue * (totalLengthCondition * totalOverSec) < 0:
                    if math.fabs(conditionValue) > math.fabs(totalLengthCondition * totalOverSec): # compare the difference of pre result and current result
                        break
                    else:
                        if conditionValue > 0:
                            dPos -= moveTh
                            break
                        else:
                            dPos += moveTh
                            break
                else: # in the case current result matches the condition
                    break
        print "initial threshold   : %d" % initialdPos
        print "controlled threshold: %d" % dPos
     # discover positions to divide
    if labelFlag:
        os.mkdir(worDir+"/assessment")
    files = os.listdir(worDir)
    files.sort()
    for inFile in files:
        if os.path.splitext(inFile)[1] == ".fdresult":
            print ".",
            resfile = open(worDir+"/"+inFile, "r")
            lines = resfile.readlines()
            resfile.close()
            cutfile = open(worDir+"/"+os.path.splitext(inFile)[0]+".cut", "w")
            if labelFlag:
                assessfile = open(worDir+"/assessment/"+os.path.splitext(inFile)[0]+".lab", "w")
            count = 0 # a number of current frame
            contCount = 0 # the number of continuing minus values
            for line in lines:
                count += 1
                if float(line.strip()) < 0:
                    contCount += 1
                else:
                    if contCount != 0:
                        if float(contCount) > dPos:
                            # write a frame number
                            cutfile.write("%d\n" % int(count-1-contCount/2))
                            if labelFlag:
                                if count - contCount == 1:
                                    assessfile.write("%f sil\n" % ((count-1)*frameSecHalfLength))
                                else:
                                    assessfile.write("%f speech\n" % ((count-contCount)*frameSecHalfLength))
                                    assessfile.write("%f sil\n" % ((count-1)*frameSecHalfLength))
                        else:
                            if labelFlag:
                                if count -contCount == 1:
                                    assessfile.write("%f sp\n" % ((count-1)*frameSecHalfLength))
                                else:
                                    assessfile.write("%f speech\n" % ((count-contCount)*frameSecHalfLength))
                                    assessfile.write("%f sp\n" % ((count-1)*frameSecHalfLength))
                        contCount = 0
            if labelFlag:
                if float(contCount) > dPos:
                    assessfile.write("%f speech\n" % ((count-contCount)*frameSecHalfLength))
                    assessfile.write("end sil\n")
                else:
                    assessfile.write("end speech\n")
            cutfile.close()
            if labelFlag:
                assessfile.close()
    print "\nCutting positions are determined."

    # cut wav files
    os.mkdir(worDir+"/wav_VAD")
    files = os.listdir(worDir)
    files.sort()
    if labelFlag:
        for inFile in files:
            if os.path.splitext(inFile)[1] == ".lab":
                oldName = os.path.join(worDir, inFile)
                newName = os.path.join(worDir, "wav_VAD", inFile)
                shutil.move(oldName, newName)
    borderSec = 15 # temporary
    borderSec2 = 20 # temporary
    totalLength = 0.0 # total length of trimmed wav beyond borderSec
    totalLength2 = 0.0 # total length of trimmed wav beyond borderSec2
    beyondCount = 0 # the number of trimmed wav beyond borderSec
    beyondCount2 = 0 # the number of trimmed wav beyond borderSec
    lessCount = 0 # the number of trimmed wav less thatn borderSec

    for inFile in files:
        if os.path.splitext(inFile)[1] == ".cut":
            filename = os.path.splitext(inFile)[0]
            cutfile = open(worDir+"/"+inFile, "r")
            lines = cutfile.readlines()
            cutfile.close()
            pre_cut_position = 0.0
            ccount = 1
            for line in lines:
                current_cut_position = pre_cut_position * frameSecHalfLength
                wav_length = (float(line.strip()) - pre_cut_position) * frameSecHalfLength
                p = subprocess.Popen("sox %s/%s.wav %s/wav_VAD/%s_%05d.wav trim %f %f"
                                     % (wDir, filename, worDir, filename, ccount, current_cut_position, wav_length),
                                     shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
                p.communicate()
                pre_cut_position = float(line.strip())
                ccount += 1
                if wav_length >= borderSec:
                    totalLength += wav_length
                    beyondCount += 1
                    if wav_length >= borderSec2:
                        totalLength2 += wav_length
                        beyondCount2 += 1
                else:
                    lessCount += 1
            current_cut_position = pre_cut_position * frameSecHalfLength
            p = subprocess.Popen("sox %s/%s.wav %s/wav_VAD/%s_%05d.wav trim %f"
                                 % (wDir, filename, worDir, filename, ccount, current_cut_position),
                                 shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
            p.communicate()
            p = subprocess.Popen("soxi -d %s/wav_VAD/%s_%05d.wav" % (worDir, filename, ccount),
                                 shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
            p.wait()
            wavlength = re.split(":", p.stdout.readline().strip())
            wav_length = int(wavlength[0])*360+int(wavlength[1])*60+float(wavlength[2])
            if wav_length >= borderSec:
                totalLength += wav_length
                beyondCount += 1
                if wav_length >= borderSec2:
                    totalLength2 += wav_length
                    beyondCount2 += 1
            else:
                lessCount += 1
      
   
    print "Wav files are made in wav_VAD directory."
    print "The number of wav files which length is over %d sec      : %4d" % (borderSec, beyondCount)
    print "The total length of wav files which length is over %d sec: %4.2f" % (borderSec, totalLength)
    print "The number of wav files which length is less than %d sec : %4d" % (borderSec, lessCount)
    print "The number of wav files which length is over %d sec      : %4d" % (borderSec2, beyondCount2)
    print "The total length of wav files which length is over %d sec: %4.2f" % (borderSec2, totalLength2)
 


   # concatenate wav files if there are shorter wav files than minimumLen

    sys.stdout.flush()
    if lenFlag:
        print ""
        print "Now concatenating wav files are shorter than %d sec." % minimumLen    
        resDir = os.path.join(worDir, "wav_VAD")
        tempDir = os.path.join(resDir, "temp")
        os.mkdir(tempDir)
        files = os.listdir(resDir)
        files.sort()
        if wayToCon:
            files.reverse()
        baseName = ""
        curFile = ""
        curLen = 0.0
        for inFile in files:
            if os.path.splitext(inFile)[1] == ".wav":
                curBaseName = inFile[0:-10]
                p = subprocess.Popen("sox %s -n stat" % os.path.join(resDir, inFile),
                                     shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
                result = p.communicate()[0].split("\n")
                for line in result:
                    if re.search("Length", line):
                        wavLen = float(line.split()[2])
                if baseName != curBaseName:
                    baseName = curBaseName
                    oldName = os.path.join(resDir, inFile)
                    newName = os.path.join(tempDir, inFile)
                    shutil.move(oldName, newName)
                    curFile = newName
                    curLen = wavLen
                else:
                    if wavLen >= minimumLen:
                        if curLen >= minimumLen:
                            oldName = os.path.join(resDir, inFile)
                            newName = os.path.join(tempDir, inFile)
                            shutil.move(oldName, newName)
                            curFile = newName
                            curLen = wavLen
                        else:
                            Name1 = curFile
                            Name2 = os.path.join(resDir, inFile)
                            Name3 = os.path.join(tempDir, inFile)
                            p = subprocess.Popen("sox %s %s %s" % (Name2, Name1, Name3),
                                                 shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
                            p.communicate()
                            os.remove(Name1)
                            shutil.move(Name3, Name1)
                            curLen += wavLen
                    else:
                        Name1 = curFile
                        Name2 = os.path.join(resDir, inFile)
                        Name3 = os.path.join(tempDir, inFile)
                        p = subprocess.Popen("sox %s %s %s" % (Name1, Name2, Name3),
                                             shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
                        p.communicate()
                        os.remove(Name1)
                        shutil.move(Name3, Name1)
                        curLen += wavLen
        # remove original VADed wav files
        files = os.listdir(resDir)
        for inFile in files:
            if os.path.splitext(inFile)[1] == ".wav":
                oldName = os.path.join(resDir, inFile)
                os.remove(oldName)
        # move concatenated wav files to the directory which had original VADed wav files
        files = os.listdir(tempDir)
        files.sort()
        baseName = ""
        for inFile in files:
            if os.path.splitext(inFile)[1] == ".wav":
                curBaseName = inFile[0:-10]
                if curBaseName != baseName:
                    count = 1
                    baseName = curBaseName
                else:
                    count += 1
                oldName = os.path.join(tempDir, inFile)
                newFileName = "%s_%05d.wav" % (baseName, count)
                newName = os.path.join(resDir, newFileName)
                shutil.move(oldName, newName)
        os.rmdir(tempDir)
        print "Concatenating has finished."


    return 0


def zc_vad(wDir, cFile, worDir, sptkDir):

    print "Now calculating features for each wav files.",
    sys.stdout.flush()
    # make directory for VADed wav files
    os.mkdir(worDir+"/wav_VAD")

    # extract sampling rate of wav file
    files = os.listdir(wDir)
    files.sort()
    for inFile in files:
        if os.path.splitext(inFile)[1] == ".wav":
            p = subprocess.Popen("soxi -r %s" % (wDir+"/"+inFile),
                                 shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
            p.wait()
            SampRate = int(p.stdout.readline().strip())
            break

    # read cFile and set variables
    confFile = open(cFile, "r")
    for line in confFile:
        if len(line.split()) == 1:
            matter = line.strip(" \n#")
        elif matter == "ZEROCROSS":
            if line.split()[0] == "f":
                frameLength = int(line.split()[1])
                lArg = SampRate * frameLength / 1000
                zcrossArg = "-l %d" % lArg # command argument for zcross in SPTK
                mfccArg = "-l %d -m 0 -f %d -w 1 -E" % (lArg, SampRate) # command argument for mfcc in SPTK
            elif line.split()[0] == "t":
                tTh = int(line.split()[1])
            elif line.split()[0] == "l":
                lvTh = int(line.split()[1])
            elif line.split()[0] == "z":
                zcTh = int(line.split()[1])

    # transform wav to raw
    # calculate zero cross from raw
    # calculate energy from raw
    # transform zero cross and energy to ascii
    # filter zero cross and energy
    # make one file from zero cross and energy
    for inFile in files:
        if os.path.splitext(inFile)[1] == ".wav":
            filterLength = 11 # temporary
            filename = worDir + "/" + os.path.splitext(inFile)[0]

            p = subprocess.Popen("%s/wav2raw +f %s/%s" % (sptkDir, wDir, inFile),
                                 shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
            p.communicate()

            os.rename(wDir+"/"+os.path.splitext(inFile)[0]+".raw", filename+".raw") # move raw file to worDir
            p = subprocess.Popen("%s/zcross %s <%s.raw> %s.zc" % (sptkDir,zcrossArg, filename, filename),
                                 shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
            p.communicate()
            p = subprocess.Popen("%s/mfcc %s %s.raw > %s.en" % (sptkDir,mfccArg, filename, filename),
                                 shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
            p.communicate()
            p = subprocess.Popen("%s/x2x +fa %s.zc > %s.zca" % (sptkDir,filename, filename),
                                 shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
            p.communicate()
            median_filter(filename+".zca", filename+".fdzca", filterLength)
            p = subprocess.Popen("%s/x2x +fa %s.en > %s.ena" % (sptkDir,filename, filename),
                                 shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
            p.communicate()
            median_filter(filename+".ena", filename+".fdena", filterLength)

            zcaFile = open(filename+".fdzca", "r")
            enaFile = open(filename+".fdena", "r")
            featFile = open(filename+".feata", "w")
            for line in zcaFile:
                featFile.write(line)
                featFile.write(enaFile.readline())
            zcaFile.close()
            enaFile.close()
            featFile.close()

            print ".",
            sys.stdout.flush()

    print "\nNow deciding cut points.",
    sys.stdout.flush()
    # decide cut points
    # output files for assessment
    os.mkdir(worDir+"/assessment")
    files = os.listdir(worDir)
    files.sort()
    for inFile in files:
        if os.path.splitext(inFile)[1] == ".feata":
            count = 0
            contCount = 0
            contFlg = 0
            filename = worDir + "/" + os.path.splitext(inFile)[0]
            featFile = open(filename+".feata", "r")
            cutFile = open(filename+".cut", "w")
            labFile = open(worDir+"/assessment/"+os.path.splitext(inFile)[0]+".lab", "w")
            while True:
                count += 1
                line1 = featFile.readline().strip()
                line2 = featFile.readline().strip()
                if line1 == "":
                    break
                zcValue = float(line1)
                lvValue = float(line2)
                if zcValue > zcTh and lvValue < lvTh:
                    contCount += 1
                elif contCount != 0:
                    if zcValue > zcTh or lvValue < lvTh:
                        contCount += 1
                        continue
                    if contCount < tTh:
                        contCount = 0
                        continue
                    if count-1 == contCount:
                        cutFile.write("0\n")
                    else:
                        cutFile.write(str(count-1-(contCount/2.0)))
                        cutFile.write("\n")
                        labFile.write(str((count-contCount-1)*frameLength/1000.0)+" speech\n")
                        labFile.write(str((count-1)*frameLength/1000.0)+" sil\n")
                    contCount = 0
            featFile.close()
            cutFile.close()
            labFile.write("end speech")
            labFile.close()
            print ".",
            sys.stdout.flush()

    print "\nNow cutting wav files.",
    sys.stdout.flush()
    # cut wav files
    files = os.listdir(worDir)
    files.sort()
    for inFile in files:
        if os.path.splitext(inFile)[1] == ".cut":
            count = 1
            cutFile = open(worDir+"/"+inFile, "r")
        
            pre_line = float(cutFile.readline().strip())
            for line in cutFile:
                startSec = pre_line * frameLength / 1000.0
                durSec = (float(line.strip()) - pre_line) * frameLength / 1000.0
                trimArg = "%s/%s.wav %s/wav_VAD/%s_%05d.wav trim %f %f" % (wDir, os.path.splitext(inFile)[0], worDir, os.path.splitext(inFile)[0], count, startSec, durSec)
                p = subprocess.Popen("sox %s" % trimArg,
                                     shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
                p.wait()
                if re.search("Premature EOF", p.stdout.readline().strip()):
                    print "Error: failed to extract speech part from initial wav file."
                    return 1
                count += 1
                pre_line = float(line.strip())
            startSec = pre_line * frameLength / 1000.0
            trimArg = "%s/%s.wav %s/wav_VAD/%s_%05d.wav trim %f" % (wDir, os.path.splitext(inFile)[0], worDir, os.path.splitext(inFile)[0], count, startSec)
            p = subprocess.Popen("sox %s" % trimArg,
                                 shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
            p.wait()
            if re.search("Premature EOF", p.stdout.readline().strip()):
                print "Error: failed to extract speech part from initial wav file."
                return 1
            cutFile.close()
            print ".",
            sys.stdout.flush()
    print ""

    # calculate wav length and display
    borderSec = 15 # temporary
    borderSec2 = 20 # temporary
    beyondCount = 0
    beyondCount2 = 0
    totalLength = 0.0
    totalLength2 = 0.0
    lessCount = 0
    files = os.listdir(worDir+"/wav_VAD")
    files.sort()
    for inFile in files:
        if os.path.splitext(inFile)[1] == ".wav":
            p = subprocess.Popen("sox %s -n stat" % (worDir+"/wav_VAD/"+inFile),
                                 shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
            result = p.communicate()[0].split("\n")
            for line in result:
                if re.search("Length", line):
                    wavLen = float(line.split()[2])
                    if wavLen >= borderSec:
                        totalLength += wavLen
                        beyondCount += 1
                        if wavLen >= borderSec2:
                            totalLength2 += wavLen
                            beyondCount2 += 1
                    else:
                        lessCount += 1
    print "Wav files are made in wav_VAD directory."
    print "The number of wav files which length is over %d sec      : %4d" % (borderSec, beyondCount)
    print "The total length of wav files which length is over %d sec: %4.2f" % (borderSec, totalLength)
    print "The number of wav files which length is less than %d sec : %4d" % (borderSec, lessCount)
    print "The number of wav files which length is over %d sec      : %4d" % (borderSec2, beyondCount2)
    print "the total length of wav files which length is over %d sec: %4.2f" % (borderSec2, totalLength2)


    return 0


####################
#       MAIN       #
####################

def main(*argvs):
    
    # read argvs into variables depending on the number of arguments
    if len(argvs) == 5:
        flag = argvs[0]
        wDir = argvs[1]
        cFile = argvs[2]
        sptkDir = argvs[3]
        outDir = argvs[4]
    else:
        flag = argvs[0]
        wDir = argvs[1]
        cFile = argvs[2]
        initWav = os.path.split(argvs[3])[1]
        lFile = argvs[4]
        sptkDir = argvs[5]
        outDir = argvs[6]

    # simple error checking
    if not os.path.isdir(wDir):
        print "Warning: Wav File Directory does not exist."
        return 1
    elif not os.path.isfile(cFile):
        print "Warning: Config File does not exist."
        return 1
    elif ( flag == "0" ) and ( len(argvs) == 6 ):
            print "Warning: Too many arguments for this flag."
            return 1
    elif ( flag == "1" ) and ( len(argvs) != 7 ):
            print "Warning: Too few arguments for this flag."
            return 1
    #elif not os.path.isfile(lFile):
    #        print "Warning: Label File does not exist."
    #        return 1
    elif flag == "2":
        if len(argvs) == 6:
            print "Warning: Too much arguments for this flag."
            return 1
        elif not os.path.isdir(sptkDir):
            print "Warning: SPTK Directory does not exist."
            return 1      
        else:
            print "Warning: Unsupported flag is set."
            return 1

    # check wDir and confirm name of initial wav file
    # name of initial wav file is used only in the case flag == 1
    files = os.listdir(wDir)
    files.sort()
    wavFiles = []
    for inFile in files:
        if os.path.splitext(inFile)[1] == ".wav":
            wavFiles.append(inFile)
            #if initWav == "":
            #    initWav = inFile
    if wavFiles == []:
        print "Warning: Wav File Directory does not contain wav files."
        return 1
    else:
        for inFile in wavFiles:
            # checking wav file format using sox
            p = subprocess.Popen("sox %s -n stat" % (wDir+"/"+inFile),
                                 shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
            (stdouterr, stdin) = (p.stdout, p.stdin)
            while True:
                line = stdouterr.readline()
                if not line:
                    break
                if re.search("can't open input file", line):
                    print "Warning: Wav File %s does not match wav format." % inFile
                    return 1

    # checking cFile here

    # checking lFile here

    # prepare working directory
    temp = 0
    while True:
        if not os.path.isdir(wDir+"/temp"+str(temp)):
            worDir = wDir + "/temp" + str(temp)
            os.mkdir(worDir)
            break
        else:
            temp += 1

    # if flag == 0, this module runs adintool
    if flag == "0":
        print "----------------------------------------"
        print "VAD using adintool Start"
        print "----------------------------------------"
        val = adintool_vad(wDir, cFile, worDir)
        if val == 0:
            print "----------------------------------------"
            print "VAD successflly finished."
            print "----------------------------------------"
        else:
            print "----------------------------------------"
            print "VAD failed."
            print "----------------------------------------"

    # if flag == 1, this module runs GMM VAD
    elif flag == "1":
        print "----------------------------------------"
        print "VAD with GMM Start"
        print "Initial Wav File - %s" % initWav
        print "----------------------------------------"
        val = gmm_vad(wDir, initWav, cFile, lFile, worDir, sptkDir)
        if val == 0:
            print "----------------------------------------"
            print "VAD successflly finished."
            print "----------------------------------------"
        else:
            print "----------------------------------------"
            print "VAD failed."
            print "----------------------------------------"

    # if flag == 2, this module runs zero-cross and energy VAD
    elif flag == "2":
        print "--------------------------------------------"
        print "VAD using zero-cross and energy Start"
        print "--------------------------------------------"
        val = zc_vad(wDir, cFile, worDir, sptkDir)
        if val == 0:
            print "----------------------------------------"
            print "VAD successflly finished."
            print "----------------------------------------"

        else:
            print "----------------------------------------"
            print "VAD failed."
            print "----------------------------------------"

    if val == 0:
            # CLEAN UP:

            print ("The VAD segmented files are in %s/wav" %outDir)
            print "----------------------------------------"
            print "CLEANING UP..."

            p = subprocess.Popen("mv %s/wav_VAD %s/wav" %(worDir, outDir),
                                     shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
            p.communicate()
            
            p = subprocess.Popen("mv %s/assessment %s/assessment" %(worDir, outDir),
                                     shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
            p.communicate()


            p = subprocess.Popen("rm -rf %s" %(worDir),
                                     shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
            p.communicate()

            os.mkdir(outDir+"/initialWav/")
            
            # copy the initial wavs, for GMM the ones used at silence estimation, for the rest just the first 50
            if flag == "1":
                p = subprocess.Popen("mv %s/wav/%s*.wav %s/initialWav/" %(outDir,os.path.splitext(initWav)[0], outDir),
                                     shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
                p.communicate()

            elif flag == "2" or flag == "0":
                    files = os.listdir(outDir+'/initialWav/')
                    files.sort()
                    for i in range(50):
                         p = subprocess.Popen("cp %s/initialWav/%s %s/initialWav/" %(outDir, files[i], outDir),
                                     shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
                         p.communicate()
                    
            print "----------------------------------------"
            print "ALL DONE OK!!\n"

    return 0


if __name__ == '__main__':
    if len(sys.argv) == 6:
        main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    elif len(sys.argv) == 8:
        main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7])
    else:
        print "Usage: python VAD.py <Flag> <Wav File Directory> <Config File> <SPTK dir> <outDir>"
        print "Usage: python VAD.py <Flag> <Wav File Directory> <Config File> <Inital Wav> <Label File> <SPTK dir> <outDir>"
