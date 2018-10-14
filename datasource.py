from pymongo import MongoClient

client = MongoClient('localhost', 27017)
DB = client.mouseauth

def getUserData(userID):
	return DB.users.find_one({ "id": userID })

def addNewUser(userID, grammars):
	return DB.users.insert_one({
		"id": userID,
		"grammars": grammars,
		"trainings": 1,
	})

def trainUser(userID, grammars):
	return DB.users.update_one({
		"id": userID
	}, {
		"$set": { "grammars": grammars },
		"$inc": { "trainings": 1 }
	})
