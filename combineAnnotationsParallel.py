#!/usr/bin/python -W all
"""
    combineAnnotationsParallel.py: combine the tags generated by machine learning experiments
    usage: paste file1 [file2 ..] | combineAnnotations.py [-m minConfidence] [-h] file1 [file2 ...]
    notes:
    - expected input line format: hashsign number colon gold-tag guessed-tag confidence-score [repeated]
    - option -m specifies acceptance confidence score for classes (default: 0.0)
    20170622 erikt(at)xs4all.nl
"""

import getopt
import re
import sys

COMMAND = sys.argv.pop(0) # this command
USAGE = "paste file1 [file2 ..] | "+COMMAND+"[-m minConfidence]"
OTHER = "O" # other tag
NONE = "-1" # unknown tag
HASH = "#" # hash sign
BLOCKSIZE = 5 # number of data items per block: hash id gold guess confidence
minConfidence = -1000.0 # minimum confidence score for class assignment
hasHeading = False

# check for command line options
def checkOptions():
    global hasHeading,minConfidence

    try: (opts,args) = getopt.getopt(sys.argv,"hm:",[])
    except: sys.exit(USAGE)
    for option in opts:
        if option[0] == "-m": minConfidence = float(option[1])
        elif option[0] == "-h": hasHeading = True
    return(args) # remaining command line arguments

# check options
args = checkOptions()
# initialize gold tags, guess tags and confidence values
goldTags = {}
guessedTags = {} # best classes per item
confidenceValues = {} # best confidence scores per item
confidenceValues2 = {} # second best confidence scores per item
history = {}
nbrOfFields = -1
if hasHeading: print "gold bestClass bestConfidence secondBestClass secondBestConfidence"
# process input
for line in sys.stdin:
    line = line.rstrip()
    fields = line.split()
    if nbrOfFields < 0: nbrOfFields = len(fields)
    if len(fields) != nbrOfFields:
        sys.exit(COMMAND+": unexpected number of fields on line: "+line+"\n")
    confidences = []
    gold = ""
    for i in range(0,len(fields),BLOCKSIZE):
        if fields[i] != HASH: sys.exit(COMMAND+": missing hash sign on position "+str(i+1)+" of line: "+line+"\n")
        if len(fields) < i+BLOCKSIZE: sys.exit(COMMAND+": number of tokens is not a multiple of "+BLOCKSIZE+" on line "+line+"\n")
        # assume that class values are numeric and data line is sorted
        confidence = fields[i+BLOCKSIZE-1]
        confidences.append(float(confidence))
        if fields[i+2] != OTHER: gold = fields[i+2]
    bestConfidence = -1
    bestIndex = -1
    secondBestConfidence = -1
    secondBestIndex = -1
    for i in range(0,len(confidences)):
        if confidences[i] > bestConfidence and confidence >= minConfidence:
            secondBestConfidence = bestConfidence
            secondBestIndex = bestIndex
            bestConfidence = confidences[i]
            bestIndex = i
        elif confidences[i] > secondBestConfidence and confidence >= minConfidence:
            secondBestConfidence = confidences[i]
            secondBestIndex = i
 
    if len(args) == 0:
        bestClass = str(bestIndex+1)
        secondBestClass = str(secondBestIndex+1)
    else:
        if len(args) < bestIndex+1: sys.exit(COMMAND+": too few class arguments, looking for "+str(bestIndex+1)+"\n")
        if len(args) < secondBestIndex+1: sys.exit(COMMAND+": too few class arguments, looking for "+str(secondBestIndex+1)+"\n")
        bestClass = args(bestIndex)
        secondBestClass = args(secondBestIndex)
    print "%s %s %0.3f %s %0.3f" % (gold,bestClass,bestConfidence,secondBestClass,secondBestConfidence)
