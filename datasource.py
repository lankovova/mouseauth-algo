from pandas import read_json
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
DB = client.mouseauth

def grammarsToJson(grammars):
	return { k: g.to_json() for k, g in grammars.items() }

def grammarsFromJson(jsonGrammars):
	return { k: read_json(g) for k, g in jsonGrammars.items() }

def getUserData(userID):
	userData = DB.users.find_one({ "id": userID })

	if userData is None:
		return None

	return {
		"id": userData["id"],
		"grammars": grammarsFromJson(userData["grammars"]),
		"trainings": userData["trainings"]
	}

def addNewUser(userID, grammars):
	return DB.users.insert_one({
		"id": userID,
		"grammars": grammarsToJson(grammars),
		"trainings": 1,
	})

def trainUser(userID, grammars):
	return DB.users.update_one({
		"id": userID
	}, {
		"$set": { "grammars": grammarsToJson(grammars) },
		"$inc": { "trainings": 1 }
	})
