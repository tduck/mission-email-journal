import sys, hashlib, uuid, os
from pymongo import MongoClient, ASCENDING, DESCENDING

class MissionJournalDB:

	def getDB(self):
		return MongoClient("localhostls", 27017).myMissionJournal

	def getUsersColection(self):
		return self.getDB().users

	def getMessagesCollection(self):
		return self.getDB().messages

	def getUserByEmail(self, email):
		return self.getUsersColection().find_one({"email": email})

	def isValidUser(self, userName, password):
		user = self.getUserByEmail(email = userName)
		if user:
			hash_pass = hashlib.sha256(password + user["salt"]).hexdigest()
			if hash_pass == user["password"]:
				return True
		return False

	def getAllUserMail(self, userName):
		allUserMessages = self.getMessagesCollection().find({"$or":[{"sender":username},{"recipients":username}]})
		messageList = []

		if allUserMessages:
			for message in allUserMessages:
				messageList.append(message)

		return messageList

	def getUserSentMail(self, userName):
		allSentMessages = self.getMessagesCollection().find({"sender":username})
		messageList = []
		if allSentMessages:
			for message in allSentMessages:
				messageList.append(message)

		return messageList

	def getUserRecievedMail(self, userName):
		allInMessages = self.getMessagesCollection().find({"recipients":username})
		messageList = []
		if allInMessages:
			for message in allInMessages:
				messageList.append(message)