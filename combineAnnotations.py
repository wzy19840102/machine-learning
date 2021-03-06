#!/usr/bin/python -W all
"""
    combineAnnotations.py: combine the tags generated by machine learning experiments
    usage: combineAnnotations.py [-m minConfidence] file1 [file2 ...]
    notes:
    - expected line format: hashsign number colon gold-tag guessed-tag confidence-score
    - option -m specifies acceptance confidence score for classes (default: 0.0)
    20170418 erikt(at)xs4all.nl
"""

import getopt
import re
import sys

# this command
COMMAND = sys.argv.pop(0)
USAGE = COMMAND+"[-m minConfidence] file1 [file2 ...]"
# other tag
OTHER = "O"
# unknown tag
NONE = "-1"
# minimum confidence score for class assignment
minConfidence = -1000.0

# check for command line options
def checkOptions():
    global minConfidence

    try: (opts,args) = getopt.getopt(sys.argv,"m:",[])
    except: sys.exit(USAGE)
    for option in opts:
        if option[0] == "-m": minConfidence = float(option[1])
    return(args) # remaining command line arguments

# check options
args = checkOptions()
# set files
files = args
# initialize gold tags, guess tags and confidence values
goldTags = {}
guessedTags = {} # best classes per item
confidenceValues = {} # best confidence scores per item
confidenceValues2 = {} # second best confidence scores per item
history = {}
# process files
for fileName in files:
    try:
        inFile = open(fileName,"r") # open the current input file
    except:
        sys.exit(COMMAND+": cannot read file "+fileName+"!\n")
    # determine gold tag based on fila name
    fields = fileName.split(".")
    fileNameGoldTag = fields[-1]
    patternHash = re.compile("^#")
    # confidence score data, necessary for normalization
    confidences = {}
    confidenceMax = -1000
    confidenceMin = 1000
    # read each line of the file
    for line in inFile:
        # only process line that start with a hash sign
        if patternHash.match(line):
           # split the line in fields based on white space separators
           fields = line.split()
           # line should contain at least five fields
           if len(fields) >= 4:
              # give the field elements names: id, gold-tag, guessed-tag, confidence
              thisId = fields[1]
              gold = fields[2]
              confidence = float(fields[-1])
              # if the gold tag is not blank: store it
              if gold != OTHER: 
                  goldTags[thisId] = gold
                  # sanity check
                  if gold != fileNameGoldTag and gold != NONE: 
                      sys.exit(COMMAND+": gold tag does not match file name! ("+gold+","+file+")\n")
              confidences[thisId] = confidence
              if confidence > confidenceMax: confidenceMax = confidence
              if confidence < confidenceMin: confidenceMin = confidence
    inFile.close()
    # normalize confidences
    for thisId in confidences:
        # skip normalization
        # confidences[thisId] = (confidences[thisId]-confidenceMin)/(confidenceMax-confidenceMin)
        # store the most confident prediction (earlier only if > 0)
        # ignore the guess: it is only set when confidence > 0.5
        if thisId in history: history[thisId] += " "+fileNameGoldTag+":"+str(confidences[thisId])
        else: history[thisId] = fileNameGoldTag+":"+str(confidences[thisId])
        # keep the tag with the highest confidence
        if not thisId in guessedTags or confidences[thisId] > confidenceValues[thisId]:
            guessedTags[thisId] = fileNameGoldTag
            if thisId in confidenceValues:
                confidenceValues2[thisId] = confidenceValues[thisId]
            confidenceValues[thisId] = confidences[thisId]
        elif not thisId in confidenceValues2 or confidences[thisId] > confidenceValues2[thisId]:
            confidenceValues2[thisId] = confidences[thisId]

# determine default guess: most frequently guessed tag
counts = {}
for thisId in guessedTags:
    guess = guessedTags[thisId]
    if guess in counts: counts[guess] += 1
    else: counts[guess] = 1
bestGuess = ""
bestCount = -1
for guess in counts:
    if counts[guess] > bestCount:
        bestGuess = guess
        bestCount = counts[guess]

# show results
unclassified = 0
for thisId in sorted(guessedTags.iterkeys()):
    # sanity checks: guessed-id should be in goldTags and confidenceValues
    if not thisId in history: history[thisId] = ""
    if not thisId in goldTags: goldTags[thisId] = OTHER
    if not thisId in guessedTags: guessedTags[thisId] = bestGuess
    if not thisId in confidenceValues: confidenceValues[thisId] = 0.0
    if confidenceValues[thisId] < minConfidence:
        guessedTags[thisId] = OTHER
        unclassified += 1
    # show results
    print "# %s %s %s %0.3f %0.3f %s" % (thisId,goldTags[thisId],guessedTags[thisId],confidenceValues[thisId],confidenceValues2[thisId],history[thisId])
if unclassified > 0:
    sys.stderr.write("unclassified: "+str(unclassified)+"\n")

