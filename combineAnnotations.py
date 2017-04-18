#!/usr/bin/python -W all
"""
    combineTags.py: combine the tags generated by machine learning experiments
    usage: combineTags.py file1 [file2 ...]
    note expected line format: hashsign number colon gold-tag guessed-tag confidence-score
    20170418 erikt(at)xs4all.nl
"""

import re
import sys

# this command
COMMAND = sys.argv[0]
# other tag
OTHER = "O"

# get files
files = sys.argv
# remove command from file list
files.pop(0)
# initialize gold tags, guess tags and confidence values
goldTags = {}
guessedTags = {}
confidenceValues = {}
# process files
for file in files:
    try:
        f = open(file,"r") # try to open the current input file
    except:
        sys.stderr.write(COMMAND+": cannot read file "+file+"!\n")
    patternHash = re.compile("^#")
    # read each line of the fil
    for line in f:
        # only process line that start with a hash sign
        if patternHash.match(line):
           # split the line in fields based on white space separators
           fields = line.split()
           # line should contain at least five fields
           if len(fields) >= 5:
              # give the field elements names: id, gold-tag, guessed-tag, confidence
              thisId = fields[1]
              gold = fields[2]
              guess = fields[3]
              confidence = float(fields[4])
              # if the gold tag is not blank: store it
              if gold != OTHER: goldTags[thisId] = gold
              # if the guessed tag is not blank, store the most confident prediction
              if guess != OTHER and (not thisId in guessedTags or confidence > confidenceValues[thisId]):
                  guessedTags[thisId] = guess
                  confidenceValues[thisId] = confidence

# show results
for thisId in sorted(guessedTags.iterkeys()):
    # sanity checks: guessed-id should be in goldTags and confidenceValues
    if not thisId in goldTags: sys.exit(COMMAND+": no gold tag for id "+thisId+"!\n")
    if not thisId in confidenceValues: sys.exit(COMMAND+": no confidence value for id "+thisId+"!\n")
    # show results
    print "# %s %s %s %0.3f" % (thisId,goldTags[thisId],guessedTags[thisId],confidenceValues[thisId])

