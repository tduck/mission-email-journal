
import smtpd
import asyncore
import datetime
from pymongo import MongoClient


class MailServer(smtpd.SMTPServer):
	def initDB(self):
		client = MongoClient("107.170.214.197", 27017)
		self.db = client.myMissionJournal


	#peer = the client's address, a tuple containig IP and incoming port
	#mailfrom = the "from" information out of the message envelope, given to the server by the client when the mesage is delivered. this does not necessarily match the From header in all cases
	#rcpttos = the list of recipients from the message envelope. Again, this does not always mathc the To header, especially if someone is blind carbon copied
	#data = the full RFC 2822
	def process_message(self, peer, mailfrom, rcpttos, data):
		print 'Receiving message from:', peer
		print 'Message addressed from:', mailfrom
		print 'Message addressed to  :', rcpttos
		print 'Message length        :', len(data)
		print data

		if "adamsonlance@gmail.com" in rcpttos:

			if self.findUser(rcpttos, mailfrom):
				messageObject = {"sender": mailfrom, "recipients": rcpttos, "date": datetime.datetime.utcnow(), "message": data} 
				messageID = self.db.mesaages.insert(messageObject)

		print self.db.collection_names()
		return


	def findUser(self, sentTo, sentFrom):
		toUsers = []
		fromUser = None
		users = self.db.users

		#self.db.users.insert({"email": "adamsonlance@gmail.com", "firstName": "Lance", "lastName":  "Adamson", "mission": "Mexico, Tuxtla-Gutierrez"})

		for address in sentTo:
			user = users.find_one({"email": address})
			if user:
				toUsers.append(user)

		fromUser = users.find_one({"email": sentFrom})
		
		if len(toUsers) > 0 or fromUser:
			return True
		else:
			return False

if __name__ == "__main__":
	server = MailServer(("localhost", 1025), None)
	server.initDB()
	asyncore.loop()
