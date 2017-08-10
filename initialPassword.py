#!/usr/bin/python2.7

#Gather initialPasswordView details for list of users. 
#Necessary inputs: 
#    list of users, delineated by newline (\n)
#    username of OpenIDM user to call API with
#    password of OpenIDM user

import json, subprocess, getopt, sys

def main(argv): 
	inputFile = ''
	openidmUsername = ''
	openidmPassword = ''
	try: 
		opts, args = getopt.getopt(argv, "Hi:u:p:",["inputFile=", "username=", "password="])
	except getopt.GetoptError: 
		print 'initialPassword.py -i <inputFile> -u <username> -p <password>'
		sys.exit(2)
	for opt, arg in opts: 
		if opt == '-H':
			print '\ninitialPassword.py is used to gather intial password information for a list of users.' \
			'\nUsage: python initialPassword.py -i <inputFile> -u <username> -p <password>' \
			'\n-i	--inputFile		.txt file with list of users to process. Delineated by linebreaks.' \
			'\n-u 	--username 		The login username for OpenIDM to use for the API call.' \
			'\n-p 	--password 		The password for the OpenIDM username.\n'
			sys.exit()
		elif opt in ('-i', '--inputFile'): 
			inputFile = arg
		elif opt in ('-u', '--username'):
			openidmUsername = arg
		elif opt in ('-p', '--password'):
			openidmPassword = arg
	#print "inputFile is: " + str(inputFile)
	#print "username is: " + str(openidmUsername)
	#print "password is: " + str(openidmPassword)

	with open(str(inputFile), 'r') as openFile:
		readFile = openFile.read()

	entries = readFile.strip().split('\n')

	for entry in entries:
		#print "entry: " + str(entry)
		userNameArg='-H \"X-OpenIDM-Username:' + str(openidmUsername) + '\"'
		passwordArg='-H \"X-OpenIDM-Password:' + str(openidmPassword) + '\"'
		requestArg='--request GET'
		urlArg='https://sso.qa.valvoline.com/openidm/managed/user?_queryFilter=userName+eq+%22'+str(entry)+'%22&_fields=userName,initialPasswordView'
		#curlCommand='curl -H \"X-OpenIDM-Username:' + str(openidmUsername) + '\" '\
		#'-H \"X-OpenIDM-Password:' + str(openidmPassword) + '\" '\
		#'--request GET ' \
		#'https://sso.qa.valvoline.com/openidm/managed/user?_queryFilter=userName+eq+%22' + str(entry) + '%22&_fields=userName,initialPasswordView'

		#print curlCommand
		#subprocess.check_output(['curl',userNameArg,passwordArg,requestArg,urlArg])
		output = subprocess.check_output(['date','-u'])
		print output


if __name__ == "__main__":
	main(sys.argv[1:])

