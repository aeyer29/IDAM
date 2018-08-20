#!/usr/bin/python2.7

#Update details for list of users. 
#Necessary inputs: 
#    list of users, delineated by newline (\n)
#    output file
#    username of OpenIDM user to call API with
#    password of OpenIDM user

import json
import getopt
import getpass
import sys
import requests
from urllib import quote as quoteURL

def parseInput(inFile):
	#Output is list of lines (cells delineated by commas, ',')
	with open(str(inFile), 'r') as openFile:
		readFile = openFile.read().strip()

	byLines = readFile.split('\n')[1:]
	return byLines


def main(argv): 
	inputFile = ''
	outputFile = ''

	try: 
		#Define arguments for command
		opts, args = getopt.getopt(argv, "Hi:o:",["inputFile=", "outputFile="])
	except getopt.GetoptError: 
		print 'ucollectinfo.py -i <inputFile> -o <outputFile>'
		sys.exit(2)
	for opt, arg in opts: 
		#Read args from the command
		if opt == '-H': 
			print '\ncollectinfo.py is used to aggregate responses in csv format' \
			'\nUsage: ./updateUsers.py -i <inputFile> ' \
			'\n-i   --inputFile             response file' \
			'\n-o   --outputFile            Name of file to output. '
	

			#exit if -H is called, as this is just to print a help command
			sys.exit()
		elif opt in ('-i', '--inputFile'): 
			inputFile = arg
		elif opt in ('-o', '--outputFile'):
			outputFile=arg

	#use list(set()) to ensure each entry is distinct 
	print(parseInput(inputFile))


if __name__ == "__main__":
	main(sys.argv[1:])
