

var matchAD_policy = {
	"policyId" : "match-ad",
	"policyExec" : "matchAD",
	"clientValidation" : "true",
	"validateOnlyIfPresent" : "true",
	"policyRequirements" : ["MATCH_AD"]
}

addPolicy(matchAD_policy);

function matchAD(fullObject, value, params, property){
	var requiredMatches = 3;
	var actualMatches = 0;

	// The values below describe the regexes used to validate a password. 
	var lowerAlphaReg = /[a-z]/;
	var upperAlphaReg = /[A-Z]/;
	var numReg = /[0-9]/;
	var specialReg = /[!@#$%\^&\*\(\),.<>\?\/;:'"\\\|\+=_\-]/;

	var regArray = [lowerAlphaReg, upperAlphaReg, numReg, specialReg]
	var useVal = ""; 
	// Just so we don't mess with the input value, and ensure the value we use is a string
	if (value != null){
		useVal = value;
	}

	// Loop through the array of regexes and record whether it matches by adding to actualMatches.
	// actualMatches keeps track of the number of regexes the input value matches. 
	for (i = 0; i < regArray.length; i++){
		var currentReg = regArray[i];
		var matchesCurrentReg = useVal.test(currentReg);

		if (matchesCurrentReg){
			actualMatches += 1;
		}
	}

	// Return empty list if policy requirement has been met - the input value matched at least 
	// the required number of matches. 
	if (actualMatches >= requiredMatches){
		return [];
	} else {
		return [{"policyRequirement" : "MATCH_AD"}];
	}
};