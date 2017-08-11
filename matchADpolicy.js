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

	var lowerAlphaReg = /[a-z]/;
	var upperAlphaReg = /[A-Z]/;
	var numReg = /[0-9]/;
	var specialReg = /[!@#$%\^&\*\(\),.<>\?\/;:'"\\\|\+=_\-]/;

	var regArray = [lowerAlphaReg, upperAlphaReg, numReg, specialReg]
	var useVal = "";
	if (value != null){
		useVal = value;
	}

	for (i = 0; i < regArray.length; i++){
		var currentReg = regArray[i];
		var matchesCurrentReg = useVal.test(currentReg);

		if (matchesCurrentReg){
			actualMatches += 1;
		}
	}
	if (actualMatches >= requiredMatches){
		return [];
	} else {
		return [{"policyRequirement" : "MATCH_AD"}];
	}
};