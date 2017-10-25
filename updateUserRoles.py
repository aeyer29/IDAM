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

def parseInput(inFile, position):
	#Output is list of users, based on input where each line has a username as the second word, delimited by a comma
	with open(str(inFile), 'r') as openFile:
		readFile = openFile.read().strip()

	byLines = readFile.split('\n')[1:]
	userList = []
	for line in byLines:
		splitByWhitespace = line.split(",")
		user = [splitByWhitespace[position]].strip()
		userList += user

	return userList

def debug(debugOn, statement):
	#Use this for debug statements. 
	#debugOn is a boolean
	#statement is statement to print 
	if debugOn:
		print str(statement)

def getRolesById(roleList):
	rolesById = {}
	for role in roleList:
		getRoleIdUrlArg = 'https://sso.qa.valvoline.com/openidm/managed/role?_queryFilter=name+eq+' + str(role).upper()
		getRoleIdReq = requests.get(getRoleIdUrlArg, headers = getHeaderArgs)
		roleResultJson = json.loads(getRoleIdReq.text)

		if roleResultJson["resultCount"] > 0:
			role = rolesJson["result"][0]
			roleId = role["_id"]
			rolesById.update({str(role) : str(roleId)})

		else:
			print ("ERROR: Could not find role: " + str(role))
			continue

	return rolesById


def main(argv): 
	inputFile = ''
	outputFile = ''
	openidmUsername = ''
	openidmPassword = ''
	toDebug = False
	try: 
		#Define arguments for command
		opts, args = getopt.getopt(argv, "Hi:o:u:p:d",["inputFile=", "outputFile=", "username=", "password="])
	except getopt.GetoptError: 
		print 'updateUsers.py -i <inputFile> -o <outputFile> -u <username> -p <password>'
		sys.exit(2)
	for opt, arg in opts: 
		#Read args from the command
		if opt == '-H': 
			print '\nupdateUsers.py is used to update information for a list of users.' \
			'\nUsage: ./updateUsers.py -i <inputFile> -u <username> -p <password>' \
			'\n-i   --inputFile             file with list of users to process. Delineated by newlines.' \
			'\n-o   --outputFile            Name of file to output. Output is of the format: '\
			'\n                             "first last\tusername\tinitial" (tab separated)'\
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
		elif opt in('-d', '--debug'):
			toDebug = True


	#use list(set()) to ensure each entry is distinct 
	#entries are UUIDs (frID)
	entries = list(set(parseInput(str(inputFile), 13)))

	roleListManager = ["PRDFND", "VLVUAD", "INSGHT", "PROPRO", "VLVPRF", "VLVMON", "SOLUTN", "VIWCAS", "VIWORD", "PRDCTL"]
	roleListStaff = ["PRDFND", "VLVUUR"]

	rolesByIdManager = getRolesById(roleListManager)
	rolesByIdStaff = getRolesById(roleListStaff)


	outString = ""

	#errorUsers is users for which an error was caught and the user was skipped 
	errorUsers = []

	for entry in entries:
		debug(toDebug, "querying for entry: " + str(entry))
		#For each username in the list, send the following command. 
		#use quoteURL to encode the string 
		getUrlArg = 'https://sso.qa.valvoline.com/openidm/managed/user/' + str(entry)

		getHeaderArgs = {'X-OpenIDM-Username':str(openidmUsername), 'X-OpenIDM-Password':str(openidmPassword)}
		getCurlReq = requests.get(getUrlArg, headers = getHeaderArgs)

		#json.loads will return a dict object, so jsonObj is a dictionary of the format: 
		#{"result":[{"_id":"#","_rev":"#","userName":"string","initialPasswordView":"string"}],
		#	"resultCount":#,"pagedResultsCookie":obj,"totalpagedResultsPolicy":"policy","totalPagedResults":#,"remainingPagedResults":#}
		jsonObj = json.loads(getCurlReq.text)

		if !(len(jsonObj["result"])>0):
			#Avoid out of index range errors, and if debugging on, record info from failure. 
			errorUsers += [(entry, "did not find user")]
			debug(toDebug, "    no results for entry: " + str(entry))
			#if toDebug:
			#	with open(str(outputFile) + '_notFound.txt', 'a') as openDebugFile:
			#		openDebugFile.write('User not found: ' + str(entry) + '\n\t' + str(getCurlReq.text) + '\n\tHTTP Status: ' + str(getCurlReq.status_code))
			continue

		#The returnedResult is a dictionary. Note that we only use the first result here from the "result" entry in the dictionary.
		returnedResult = jsonObj["result"][0]
		returnedUsername = str(returnedResult["userName"])

		debug(toDebug, "    found user: " + str(returnedUsername))

		#Get the current roles for the user 
		getRolesUrl = 'https://sso.qa.valvoline.com/openidm/managed/user/' + str(entry) + '/roles?_queryFilter=true'
		getRolesReq = requests.get(getRolesUrl, headers = getHeaderArgs)
		rolesJson = json.loads(getRolesReq.text)


		if (rolesJson["resultCount"]>0):
			#If there are other roles that the user already has, add them to a list of roles to delete
			for role in rolesJson["result"]:
				roleName = str(role["name"])
				roleInstanceID = str(role["_refProperties"]["_id"])
				deleteRoleUrl = 'https://sso.qa.valvoline.com/openidm/managed/user' + returnedID + '/roles/' + roleInstanceID
				roleDeleteReq = requests.delete(deleteRoleUrl, headers = getHeaderArgs)

		# May not need this section - look at status from roleDeleteReq instead to determine if successfully deleted? 
		getRolesReqAfter = requests.get(getRolesUrl, headers = getHeaderArgs)
		rolesJsonAfter = json.loads(getRolesReqAfter.text)
		if rolesJsonAfter["resultCount"] != 0:
			errorUsers += [(entry, "not all roles deleted")]
			rolesNotDeleted = [str(role["name"]) for role in rolesJsonAfter]
			debug(toDebug, "    not all roles for user " + returnedUsername + " were deleted!\n    roles not deleted: " + str(rolesNotDeleted) + '\n    skipping user ' + returnedUsername)
			continue

		#Get the _id for each role to be added to a user ]
		#Note that roles here are stored as 6-character, uppercase "codes" as names, per client requirement


		patchHeaders = getHeaderArgs
		patchHeaders.update({'Content-Type':'application/json'})

		addRoleUrlArg = 'https://sso.qa.valvoline.com/openidm/managed/user/' 
		addRolesList = [{"operation" : "add", "field" : "/roles/-", "value" : {"_ref" : "/managed/role/" + str(rolesById[str(role)]) } } for role in roleList]
		addRoleReq = requests.patch(addRoleUrlArg, json = addRolesList, headers = patchHeaders)


		debug(toDebug, "    added roles for user " + str(entry))



if __name__ == "__main__":
	main(sys.argv[1:])
