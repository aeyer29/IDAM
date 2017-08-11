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
			'\nUsage: python initialPassword.py -i <inputFile> -u <username> -p <password>' \
			'\n-i   --inputFile             .txt file with list of users to process. Delineated by newlines.' \
			'\n-o   --outputFile            Name of file to output. Output is of the format: '\
			'\n                             "username\tinitial"'\
			'\n                             (tab separated), with each entry on a new line.' \
			'\n-u   --username              The login username for OpenIDM to use for the API call.' \
			'\n-p   --password              The password for the OpenIDM username.'\
			'\n                             Enter "-" in place of password to be prompted. For example:'\
			'\n                             initialPassword.py -i inputFile.txt -o outputFile.txt -u userName -p -'

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

	with open(str(inputFile), 'r') as openFile:
		#read the input list
		readFile = openFile.read()

	entries = readFile.strip().split('\n')

	outString = ""

	for entry in entries:
		#For each username in the list, send the following command. 

		urlArg = 'https://sso.qa.valvoline.com/openidm/managed/user?_queryFilter=userName+eq+%22' + str(entry) + '%22&_fields=userName,mail'
		headerArgs = {'X-OpenIDM-Username':str(openidmUsername), 'X-OpenIDM-Password':str(openidmPassword)}
		curlReq = requests.get(urlArg, headers = headerArgs)

		#json.loads will return a dict object, so jsonObj is a dictionary of the format: 
		#{"result":[{"_id":"#","_rev":"#","userName":"string","mail":"string"}],
		#	"resultCount":#,"pagedResultsCookie":obj,"totalpagedResultsPolicy":"policy","totalPagedResults":#,"remainingPagedResults":#}
		jsonObj = json.loads(curlReq.text)

		#The returnedResult is a dictionary. Note that we only use the first result here from the "result" entry in the dictionary.
		returnedResult = jsonObj["result"][0]
		returnedUsername = returnedResult["userName"]
		returnedMail = returnedResult["mail"]
		addString = returnedUsername + '\t' + returnedMail + '\n'
		outString += addString

	outString = outString.strip()
	print outString
	with open(outputFile,'w') as openOutputFile:
		openOutputFile.write(outString)


if __name__ == "__main__":
	main(sys.argv[1:])
