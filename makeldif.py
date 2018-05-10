#!/c/Python27/python.exe

#Update details for list of users. 
#Necessary inputs: 
#    list of users, delineated by newline (\n)
#    output file
#    username of OpenIDM user to call API with
#    password of OpenIDM user

import csv
import sys
import getopt

def getLines(inFile):
	lineList = []
	#Output is list of users, based on input where each line has a username as the second word, delimited by a comma
	with open(str(inFile), 'r') as openFile:
		readFile = csv.reader(openFile, delimiter=',')
		for row in readFile:
			lineList += [row]
	firstLine = lineList[0]
	lineList = lineList[1:]
	return (firstLine, lineList)

def makeLdifEntry(inLine):
	email=inLine[4]
	givenName=inLine[0]
	sn=inLine[1]
	cn=givenName + ' ' + sn
	caseId=inLine[2]
	employeeId=inLine[3]

	objectClassList = ["inetuser", "iplanet-am-managed-person", "kbaInfoContainer", \
	"iplanet-am-auth=configuration-service", "devicePrintProfilesContainer", \
	"sunFederationManagerDataStore", "EEOC", "inetorgperson", \
	"forgerock-am-dashboard-service","sunFMSAML2NameIdentifier", \
	"sunIdentityServerLibertyPPService", "top", "iPlanetPreferences", \
	"sunAMAuthAccountLockout", "pushDeviceProfilesContainer", "organizationalPerson", \
	"person", "iplanet-am-user-service", "oathDeviceProfilesContainer"]

	dn="uid=" + str(email) + ",ou=EE_cust,dc=thehartford,dc=com"
	sunInfoKey="ciam-qa-sp|USBank:SAML2.0:UAT|" + str(caseId)
	sunInfo="ciam-qa-sp|USBank:SAML2.0:UAT|" + str(caseId)+ "|null|" + \
	"urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified|null|null|SPRole|false"
	inetUserStatus="Active"
	userPassword="P@ss1234"

	ldifEntry="dn: " + dn + "\n"

	for objectClass in objectClassList: 
		ldifEntry += "objectClass: " + objectClass + "\n"

	ldifEntry += "mail: " + str(email) + "\nEECaseId: " + str(caseId)\
	+ "\nsn: " + sn + "\nEEEmployeeId: " + str(employeeId) + "\n" + \
	"cn: " + str(cn) + "\nsun-fm-saml2-nameid-infokey: " + sunInfoKey \
	+ "\ngivenName: " + str(givenName) + "\ninetUserStatus: " + \
	inetUserStatus + "\nuserPassword: " + userPassword + "\nuid: " + \
	str(email) + "\nsunfm-saml2-nameid-info: " + str(sunInfo)

	return ldifEntry


def main(argv): 
	inputFile = ''
	outputFile = ''
	try: 
		#Define arguments for command
		opts, args = getopt.getopt(argv, "Hi:o:",["inputFile=", "outputFile="])
	except getopt.GetoptError: 
		print './makeldif.py -i <inputFile> -o <outputFile>'
		sys.exit(2)
	for opt, arg in opts: 
		#Read args from the command
		if opt == '-H': 
			print '\nmakeldif.py is used to make an ldif for a list of users.' \
			'\nUsage: ./makeldif.py -i <inputFile> -u <username> -p <password>' \
			'\n-i   --inputFile             CSV file with list of users to process.' \
			'\n-o   --outputFile            Name of ldif file to output.'

			#exit if -H is called, as this is just to print a help command
			sys.exit()
		elif opt in ('-i', '--inputFile'): 
			inputFile = arg
		elif opt in ('-o', '--outputFile'):
			outputFile=arg

	lines = getLines(inputFile)[1]

	ldifStr = ""
	endLine = len(lines)-1
	lineNum = 0
	for line in lines: 
		ldifStr+= makeLdifEntry(line)
		if lineNum != endLine: 
			ldifStr+= "\n\n"
		lineNum += 1

	with open(outputFile, 'w') as openOutFile: 
		openOutFile.write(ldifStr)
	print ldifStr


if __name__ == "__main__":
	main(sys.argv[1:])
