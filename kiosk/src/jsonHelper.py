import json

def createJSON(path):
    with open(path, 'w') as f:
        print("The json file is created")
    return path

def getJson(filePath: str):
    with open(filePath) as f:
        data = json.load(f)
    return data

def setJson(filePath: str, jsonData):
    with open(filePath, 'w') as f:
        f.seek(0)
        json.dump(jsonData, f, indent=2)