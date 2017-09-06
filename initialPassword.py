#!/usr/bin/python2.7

#Gather initialPasswordView details for list of users. 
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

def parseInput(inFile):
	#Output is list of users, based on input where each line has a username as the first word
	with open(str(inFile), 'r') as openFile:
		readFile = openFile.read().strip()

	byLines = readFile.split('\n')
	userList = []
	for line in byLines:
		splitByWhitespace = line.split()
		user = [splitByWhitespace[0]]
		userList += user

	return userList


def main(argv): 
	inputFile = ''
	outputFile = ''
	openidmUsername = ''
	openidmPassword = ''
	try: 
		#Define arguments for command
		opts, args = getopt.getopt(argv, "Hi:o:u:p:",["inputFile=", "outputFile=", "username=", "password="])
	except getopt.GetoptError: 
		print 'initialPassword.py -i <inputFile> -o <outputFile> -u <username> -p <password>'
		sys.exit(2)
	for opt, arg in opts: 
		#Read args from the command
		if opt == '-H': 
			print '\ninitialPassword.py is used to gather intial password information for a list of users.' \
			'\nUsage: ./initialPassword.py -i <inputFile> -u <username> -p <password>' \
			'\n-i   --inputFile             .txt file with list of users to process. Delineated by newlines.' \
			'\n-o   --outputFile            Name of file to output. Output is of the format: '\
			'\n                             "username\tinitial\tfirst last" (tab separated)'\
			'\n                             (tab separated), with each entry on a new line.' \
			'\n-u   --username              The login username for OpenIDM to use for the API call.' \
			'\n-p   --password              The password for the OpenIDM username.'\
			'\n                             Enter "-" in place of password to be prompted and hide the password. For example:'\
			'\n                             initialPassword -i inputFile.txt -o outputFile.txt -u userName -p -'

			#exit if -H is called, as this is just to print a help command
			sys.exit()
		elif opt in ('-i', '--inputFile'): 
			inputFile = arg
		elif opt in ('-o', '--outputFile'):
			outputFile=arg
		elif opt in ('-u', '--username'):
			openidmUsername = arg
		elif opt in ('-p', '--password'):
			if arg == '-':
				openidmPassword = getpass.getpass("Enter your password:")
			else:
				openidmPassword = arg


	entries = parseInput(str(inputFile))

	outString = ""

	for entry in entries:
		#For each username in the list, send the following command. 

		urlArg = 'https://sso.qa.valvoline.com/openidm/managed/user?_queryFilter=userName+eq+%22' + str(entry) + '%22&_fields=userName,initialPasswordView,givenName,sn'

		headerArgs = {'X-OpenIDM-Username':str(openidmUsername), 'X-OpenIDM-Password':str(openidmPassword)}
		curlReq = requests.get(urlArg, headers = headerArgs)

		#json.loads will return a dict object, so jsonObj is a dictionary of the format: 
		#{"result":[{"_id":"#","_rev":"#","userName":"string","initialPasswordView":"string"}],
		#	"resultCount":#,"pagedResultsCookie":obj,"totalpagedResultsPolicy":"policy","totalPagedResults":#,"remainingPagedResults":#}
		jsonObj = json.loads(curlReq.text)

		#The returnedResult is a dictionary. Note that we only use the first result here from the "result" entry in the dictionary.
		returnedResult = jsonObj["result"][0]
		returnedUsername = returnedResult["userName"]
		returnedInitial = returnedResult["initialPasswordView"]
		returnedFirst = returnedResult["givenName"]
		returnedLast = returnedResult["sn"]
		addString = returnedUsername + '\t' + returnedInitial + '\t' + returnedFirst + ' ' + returnedLast + '\n'

		outString += addString

	outString = outString.strip()

	with open(str(outputFile),'w') as openOutputFile:
		openOutputFile.write(outString)



if __name__ == "__main__":
	main(sys.argv[1:])
