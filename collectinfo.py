#!/usr/bin/python2.7

#Update details for list of users. 
#Necessary inputs: 
#    input file
#    output file

import json
import sys
import requests
from urllib import quote as quoteURL

def parseInput(inFile):
	#Output is list of lines (cells delineated by commas, ',')
	with open(str(inFile), 'r') as openFile:
		readFile = openFile.read().strip()

	byLines = readFile.split('\n')[1:]
	return byLines


def collectinfos(inputFile, outputFile): 
	print(parseInput(inputFile))
