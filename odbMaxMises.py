"""
odbMaxMises.py
Code to determine the location and value of the maximum
von-mises stress in an output database.
Usage: abaqus python odbMaxMises.py -odb odbName
       -elset(optional) elsetName
Requirements:
1. -odb   : Name of the output database.
2. -elset : Name of the assembly level element set.
            Search will be done only for element belonging
            to this set. If this parameter is not provided,
            search will be performed over the entire model.
3. -help  : Print usage
"""

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from odbAccess import *
from sys import argv,exit
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def rightTrim(input,suffix):
    if (input.find(suffix) == -1):
        input = input + suffix
    return input
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def getMaxMises(odbName,elsetName):
    """ Print max mises location and value given odbName
        and elset(optional)
    """
    elset = elemset = None
    region = "over the entire model"
    """ Open the output database """
    odb = openOdb(odbName)
    assembly = odb.rootAssembly

    """ Check to see if the element set exists
        in the assembly
    """
    if elsetName:
        try:
            elemset = assembly.elementSets[elsetName]
            region = " in the element set : " + elsetName;
        except KeyError:
            print 'An assembly level elset named %s does' \
                   'not exist in the output database %s' \
                   % (elsetName, odbName)
            odb.close()
            exit(0)
            
    """ Initialize maximum values """
    maxMises = -0.1
    maxElem = 0
    maxStep = "_None_"
    maxFrame = -1
    Stress = 'S'
    isStressPresent = 0
    for step in odb.steps.values():
        print 'Processing Step:', step.name
        for frame in step.frames:
            allFields = frame.fieldOutputs
            if (allFields.has_key(Stress)):
                isStressPresent = 1
                stressSet = allFields[Stress]
                if elemset:
                    stressSet = stressSet.getSubset(
                        region=elemset)      
                for stressValue in stressSet.values:                
                    if (stressValue.mises > maxMises):
                        maxMises = stressValue.mises
                        maxElem = stressValue.elementLabel
                        maxStep = step.name
                        maxFrame = frame.incrementNumber
    if(isStressPresent):
        print 'Maximum von Mises stress %s is %f in element %d'%(
            region, maxMises, maxElem)
        print 'Location: frame # %d  step:  %s '%(maxFrame,maxStep)
    else:
        print 'Stress output is not available in' \
              'the output database : %s\n' %(odb.name)
    
    """ Close the output database before exiting the program """
    odb.close()

#==================================================================
# S T A R T
#    
if __name__ == '__main__':
    
    odbName = None
    elsetName = None
    argList = argv
    argc = len(argList)
    i=0
    while (i < argc):
        if (argList[i][:2] == "-o"):
            i += 1
            name = argList[i]
            odbName = rightTrim(name,".odb")
        elif (argList[i][:2] == "-e"):
            i += 1
            elsetName = argList[i]
        elif (argList[i][:2] == "-h"):            
            print __doc__
            exit(0)
        i += 1
    if not (odbName):
        print ' **ERROR** output database name is not provided'
        print __doc__
        exit(1)
    getMaxMises(odbName,elsetName)
    
