import re

cnvDict = {
    "baseName":"",
    "categoryName":"",
    "userInitials":"",
    "date":""
}

baseName = "testScene"
categoryName = "Model"
userInitials = "ard"

cnvDict["baseName"] = baseName
cnvDict["categoryName"] = categoryName
cnvDict["userInitials"] = userInitials

conventionTemplate = "<userInitials>_<categoryName>,<baseName>_asdf<categoryName>_<userInitials>"


items = re.findall(r'<(.*?)\>', conventionTemplate)

newCnv=conventionTemplate
for i in items:
    if i in cnvDict.keys():
        newCnv=newCnv.replace("<%s>" %i, cnvDict[i])

print newCnv
