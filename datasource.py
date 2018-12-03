from pymongo import MongoClient
import pandas as pd

client = MongoClient('localhost', 27017)
DB = client.mouseauth

def grammarsToDict(grammars):
	return { k: g.to_dict('index') for k, g in grammars.items() }

def grammarsFromDict(grammars):
	return { k: pd.DataFrame.from_dict(g, orient='index') for k, g in grammars.items() }

def getUserData(userID):
	userData = DB.users.find_one({ "id": userID })

	if userData is None:
		return None

	return {
		"id": userData["id"],
		"grammars": grammarsFromDict(userData["grammars"]),
		"trainings": userData["trainings"],
		"rules": userData["rules"]
	}

def addNewUser(userID, grammars, rules):
	return DB.users.insert_one({
		"id": userID,
		"grammars": grammarsToDict(grammars),
		"trainings": 1,
		"rules": rules,
	})

def trainUser(userID, grammars, rules):
	return DB.users.update_one({
		"id": userID
	}, {
		"$set": {
			"grammars": grammarsToDict(grammars),
			"rules": rules
		},
		"$inc": { "trainings": 1 }
	})
