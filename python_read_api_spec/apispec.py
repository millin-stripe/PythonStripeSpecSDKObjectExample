import json

jsonFile = open('apispec.json')

spec = json.load(jsonFile)

specPaths = spec['paths']
#specClass = spec['components']
pathreturns = {}
#Get All Paths
for (k, v) in specPaths.items():
    key = k
    value = v
    #Get All Operations for the Path
    for (operationKey, operationValue) in value.items():
        pathreturns[key] = {}
        pathreturns[key][operationKey] = {}
        #Check for application Types and get Params for Operation
        if 'application/x-www-form-urlencoded' in operationValue['requestBody']['content']:
            if 'properties' in operationValue['requestBody']['content']['application/x-www-form-urlencoded']['schema']:
                operationparams = operationValue['requestBody']['content']['application/x-www-form-urlencoded']['schema']['properties']

        if 'application/json' in operationValue['requestBody']['content']:
            if 'properties' in operationValue['requestBody']['content']['application/json']['schema']:
                    operationparams = operationValue['requestBody']['content']['application/json']['schema']['properties']
        
        #Get Return Object for the Operation and map that Type. It has only ever been application/json
        if 'application/json' in operationValue['responses']['200']['content']:
            if '$ref' in operationValue['responses']['200']['content']['application/json']['schema']:
                operationREF = operationValue['responses']['200']['content']['application/json']['schema']['$ref']
            if 'properties' in operationValue['responses']['200']['content']['application/json']['schema'] :
                operationREF = operationValue['responses']['200']['content']['application/json']['schema']['properties']['data']['items']['$ref']
        #Map Object Ref
        pathreturns[key][operationKey]['objectRef'] = operationREF
        #Split the Object Ref so we can use it to lookup the object
        operationREFSplits = operationREF.split('/')
        classpathone = operationREFSplits[1]
        classpathtwo = operationREFSplits[2]
        classpaththree = operationREFSplits[3]
        #Lookup Operation Class. This pattern is 100% correct
        opsClass = spec[classpathone][classpathtwo][classpaththree]
        #pathreturns[key][operationKey]['class'] = spec[classpathone][classpathtwo][classpaththree]
        #Map ClassName to Operation return ClassName. This pattern has been 100% true as well
        pathreturns[key][operationKey]['className'] = classpaththree
        #Get App Parameters keys and values
        for (opParamsKey, opParamsValue) in operationparams.items():
            #Condition checking to see if the var is an Object, so do we care
            processVar = False
            opParams =[]
            
            # #Verify that type is an attribute in Params
            if 'type' in opParamsValue:
            #See if Type is an object and set processVar
                if (opParamsValue['type'] == 'object'):
                    processVar = True
                if (opParamsValue['type'] == 'array'):
                    processVar = True
            if 'anyOf' in opParamsValue:
                processVar = True
                #Only Process Objects
            if processVar == True:
                opParams.append(opParamsKey)
                foundClass = False
                foundInnerList = False
                #Some of the returns seem to be individual parts of the param name. This allows us to look at each one
                if '_' in opParamsKey:
                    opParams = opParamsKey.split('_')
                    #Add the original Value to the Array
                    opParams.append(opParamsKey)
                #we have a habit of adding a XXXX_data param if we have a param to pass XXXX with an id string. 
                if '_data' in opParamsKey:
                    opParamsKeysNoData = opParamsKey.replace('_data', '')
                    #Check for the simple condition where 2 variables have the same name
                    if opParamsKeysNoData in opParamsKey:
                        opParams.append(opParamsKeysNoData)
                #Set the original Parameter Name
                OriginalParameterName = opParamsKey
                #Loop over all the custom param names we know to look for when no match is found
                while foundClass == False:
                    for opParam in opParams:
                         
                        if 'properties' in opsClass:
                            #See if the Parameter is in the Class Properties
                            if opParam in opsClass['properties']:
                                #See if anyof is in the Parameter this is an array and the ref is in it
                                if 'anyOf' in opsClass['properties'][opParam]:
                                    #see array length, if over one lets set Classes, I dont know if this is needed. None return multiple classes
                                    #if len(opsClass['properties'][opParam]['anyOf']) > 1:
                                    for x in opsClass['properties'][opParam]['anyOf']:
                                        if '$ref' in x:
                                            #Ensure that the input does not allow Multiple Classes
                                            pathreturns[key][operationKey][opParam] = {}
                                            #pathreturns[key][operationKey][opParam]['Classes'] = []
                                            pathreturns[key][operationKey][opParam]['ClassRef'] = x['$ref']
                                            pathreturns[key][operationKey][opParam]['OriginalParamName'] = OriginalParameterName
                                            foundClass = True
                                    # else :
                                    #     for x in opsClass['properties'][opParam]['anyOf']:
                                    #         if '$ref' in x:
                                    #             #Set ClassName when length is <= 1
                                    #             pathreturns[key][operationKey][opParam] = {}
                                    #             pathreturns[key][operationKey][opParam]['ClassRef'] = x['$ref']
                                    #             continue
                                                #foundClass = True
                                #Finding Arrays that map
                                if 'items' in opsClass['properties'][opParam] and foundClass != True:
                                    for y in opsClass['properties'][opParam]['items']:
                                        if '$ref' in y and foundClass != True:
                                            pathreturns[key][operationKey][opParam] = {}
                                            pathreturns[key][operationKey][opParam]['ClassRef'] = opsClass['properties'][opParam]['items']['$ref']
                                            pathreturns[key][operationKey][opParam]['OriginalParamName'] = OriginalParameterName
                                            foundClass = True
                                #Finding Where opParam is in the class properties
                                if '$ref' in opsClass['properties'][opParam] and foundClass != True:
                                    pathreturns[key][operationKey][opParam] = {}
                                    pathreturns[key][operationKey][opParam]['ClassRef'] = opsClass['properties'][opParam]['$ref']
                                    pathreturns[key][operationKey][opParam]['OriginalParamName'] = OriginalParameterName
                                    foundClass = True
                        #The Next check we could do is see if the variable is found in the inner_classes list
                        #Not sure if this woill do anything more than the class check and it is conditional based on the class check
                        #Verify x-stripeResource is an attribute in opsClass


                        #####Commenting out the inner Class stuff

                        # if 'x-stripeResource' in opsClass and foundClass != True:
                        #     #verify inner_classes is an attribute of opsClass['x-stripeResource']
                        #     if 'inner_classes' in opsClass['x-stripeResource']:
                        #         #Verify Paramkey is in opsClass['x-stripeResource']['inner_classes']
                        #         if opParam in opsClass['x-stripeResource']['inner_classes']:
                        #             pathreturns[key][operationKey][opParam] = {}
                        #             pathreturns[key][operationKey][opParam]['ClassName'] = opParam
                        #             pathreturns[key][operationKey][opParam]['OriginalParamName'] = OriginalParameterName
                        #             foundClass = True
                                    
                        #             #foundClass = True
                        #         #Verify ClassName_opParam is in opsClass['x-stripeResource']['inner_classes']    
                        #         if classpaththree + '_' + opParam in opsClass['x-stripeResource']['inner_classes']:
                        #             pathreturns[key][operationKey][opParam] = {}
                        #             pathreturns[key][operationKey][opParam]['ClassName'] = classpaththree + '_' + opParam
                        #             foundClass = True
                                    
                        #             #foundClass = True
                                
                        if opParam == 'metadata':
                            pathreturns[key][operationKey][opParam] = {}
                            pathreturns[key][operationKey][opParam]['ClassName'] = 'MetaData'
                            pathreturns[key][operationKey][opParam]['Metadata'] = True
                            foundClass = True

                    if foundInnerList == False and foundClass == False: 
                        foundClass = True             
                        pathreturns[key][operationKey][opParamsKey] = {}
                        pathreturns[key][operationKey][opParamsKey]['ClassName'] = opsClass['x-resourceId'] + '_' + opParamsKey
                        pathreturns[key][operationKey][opParamsKey]['OriginalParamName'] = opParamsKey
        
                
print(pathreturns)

