#!/usr/bin/python2.7

#Update roles for list of users. 
#Necessary inputs: 
#    list of users, delineated by newline (\n)
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

	byLines = [parseByLine(inFile)]
	userList = []
	for line in byLines:
		splitByWhitespace = line.split(",")
		user = [splitByWhitespace[position]].strip()
		userList += user

	return userList

def parseByLine(inFile):
	#Output is a list of lines
	with open(str(inFile), 'r') as openFile:
		readFile = openFile.read().strip()

	byLines = readFile.split('\n')[1:]
	return byLines

def debug(debugOn, statement):
	#Use this for debug statements. 
	#debugOn is a boolean
	#statement is statement to print 
	if debugOn:
		print str(statement)

def getRolesById(roleList, getHeaderArgs):
	#Outputs a dictionary of roleName: roleId 
	#for example: {"PRDFND" : "abcde-1234-4fgdssa-354321"}
	rolesById = {}
	for role in roleList:
		getRoleIdUrlArg = 'https://sso.qa.valvoline.com/openidm/managed/role?_queryFilter=name+eq+%22' + str(role).upper()+'%22'
		getRoleIdReq = requests.get(getRoleIdUrlArg, headers = getHeaderArgs)
		roleResultJson = json.loads(getRoleIdReq.text)
		returnedResult = roleResultJson["result"][0]

		if roleResultJson["resultCount"] > 0:
			resultingRole = roleResultJson["result"][0]
			roleId = resultingRole["_id"]
			rolesById.update({str(role) : str(roleId)})

		else:
			print ("ERROR: Could not find role: " + str(role))
			continue

	return rolesById


def main(argv): 
	inputFile = ''
	outputFile = 'updateRoles_errors.txt'
	openidmUsername = ''
	openidmPassword = ''
	toDebug = False
	#opts, args = getopt.getopt(argv, "Hi:o:u:p:d",["inputFile=", "outputFile=", "username=", "password=", "debug"])
	try: 
		#Define arguments for command
		opts, args = getopt.getopt(argv, "Hi:o:u:p:d",["inputFile=", "outputFile=", "username=", "password=", "debug"])
	except getopt.GetoptError: 
		print 'updateRoles.py -i <inputFile> -u <username> -p <password>'
		sys.exit(2)
	for opt, arg in opts: 
		#Read args from the command
		if opt == '-H': 
			print '\nupdateRoles.py is used to update roles for a list of users.' \
			'\nThis version assumes the frID of the user is in the 14th column, while the role list type is '\
			'\n    in the 13th column. The role list types are "Owner", "Store Manager", "Area Manager", or '\
			'\n    "Store Staff". Role lists (actual roles added) are hard-coded here. '\
			'\nUsage: ./updateRoles.py -i <inputFile> -u <username> -p <password>' \
			'\n-i   --inputFile             file with list of users to process. Delineated by newlines.' \
			'\n-u   --username              The login username for OpenIDM to use for the API call.' \
			'\n-p   --password              The password for the OpenIDM username.'\
			'\n                             Enter "-" in place of password to be prompted and hide the password. For example:'\
			'\n                             initialPassword -i inputFile.txt -o outputFile.txt -u userName -p -'\
			'\n\nOPTIONAL'\
			'\n-d   --debug                 Debugging option. Prints out more statements and errors. '\
			'\n-o   --outputFile            Name of error file output.'\
			'\n                             Default: updateRoles_errors.txt\n'

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

	entryList = parseByLine(str(inputFile))
	#entries = list(set(parseInput(str(inputFile), 13)))

	getHeaderArgs = {'X-OpenIDM-Username':str(openidmUsername), 'X-OpenIDM-Password':str(openidmPassword)}

	roleListManager = ["PRDFND", "VLVUAD", "INSGHT", "PROPRO", "VLVPRF", "VLVMON", "SOLUTN", "VIWCAS", "VIWORD", "PRDCTL"]
	roleListStaff = ["PRDFND", "VLVUUR"]

	rolesByIdManager = getRolesById(roleListManager, getHeaderArgs)
	rolesByIdStaff = getRolesById(roleListStaff, getHeaderArgs)

	outString = ""

	#errorUsers is users for which an error was caught and the user was skipped. This list is written to the output file at the end of the script.  
	errorUsers = []

	for line in entryList:
		splitByWhitespace = line.split(',')
		entry = splitByWhitespace[13].strip()
		entryLevel = splitByWhitespace[12].strip().lower()
		rolesToAdd = {}
		roleList = []
		
		#we use list(roleListManager) and list(roleListStaff) to dereference the hard-coded lists and ensure that... 
		# ... roleList is, in fact, its own list. 
		if entryLevel in ['owner', 'store manager', 'area manager']:
			rolesToAdd = rolesByIdManager
			roleList = list(roleListManager)
		else:
			rolesToAdd = rolesByIdStaff
			roleList = list(roleListStaff)

		debug(toDebug, "role list for entry: " + str(roleList))
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
		if not (str(getCurlReq.status_code) == '200'):
			#Avoid out of index range errors; continue in the "for" loop if error encountered
			errorUsers += [(entry, "did not find user")]
			debug(toDebug, "    no results for entry: " + str(entry))
			continue

		#The returnedResult is a dictionary. Note that we only use the first result here from the "result" entry in the dictionary.
		returnedUsername = str(jsonObj["userName"])

		debug(toDebug, "    found user: " + str(returnedUsername))

		#Get the current roles for the user 
		getRolesUrl = 'https://sso.qa.valvoline.com/openidm/managed/user/' + str(entry) + '/roles?_queryFilter=true&_fields=_ref,_refProperties,name'
		getRolesReq = requests.get(getRolesUrl, headers = getHeaderArgs)
		rolesJson = json.loads(getRolesReq.text)

		if (rolesJson["resultCount"]>0):
			#If there are other roles that the user does not need, delete them
			#Also skip roles that the user needs, but already has
			for role in rolesJson["result"]:
				roleName = str(role["name"])
				if roleName not in roleList: 
					roleInstanceID = str(role["_refProperties"]["_id"])
					deleteRoleUrl = 'https://sso.qa.valvoline.com/openidm/managed/user/' + str(entry) + '/roles/' + roleInstanceID
					roleDeleteReq = requests.delete(deleteRoleUrl, headers = getHeaderArgs)
					debug(toDebug, "        deleting role: " + roleName + "\n            deleted status: " + str(roleDeleteReq.status_code))
				else: 
					debug(toDebug, "        role already found: " + roleName)
					#Delete the role from the list of roles to add to a user, because we already found it
					roleList.remove(roleName)


		#Note that roles here are stored as 6-character, uppercase "codes" as names, per client requirement
		#Now go an add roles necessary for the user

		patchHeaders = getHeaderArgs
		patchHeaders.update({'Content-Type':'application/json'})

		#Go and ad roles only if we need to - if roleList is nonzero in length
		if len(roleList) > 0:
			addRoleUrlArg = 'https://sso.qa.valvoline.com/openidm/managed/user/' + str(entry) 

			#addRolesList filled as a list comprehension. This will take the place of the data field in the request
			addRolesList = [{"operation" : "add", "field" : "/roles/-", "value" : {"_ref" : "/managed/role/" + str(rolesToAdd[str(role)]) } } for role in roleList]
			addRoleReq = requests.patch(addRoleUrlArg, json = addRolesList, headers = patchHeaders)

			if str(addRoleReq.status_code) != "200":
				errorUsers += [(entry, "error processing add: " + addRoleReq.text)]
				debug(toDebug, "    error processing add for user. Continuing... ")
			else:
				debug(toDebug, "    addRoleReq.status: " + str(addRoleReq.status_code))
				debug(toDebug, "    added roles for user " + returnedUsername + "\n" + "    roles added: " + str(roleList) + "\n")
		else: 
			debug(toDebug, "    all roles already added for user " + returnedUsername + "\n")

	#Write the errors for users out to the outputFile
	with open(str(outputFile), 'w') as openOutFile: 
		openOutFile.write(str(errorUsers))



if __name__ == "__main__":
	main(sys.argv[1:])

