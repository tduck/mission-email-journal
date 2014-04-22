import sys, hashlib, uuid
from flask import Flask, request, render_template
from pymongo import MongoClient
from flask.ext.mongokit import MongoKit, Document
#from flask.ext.login import LoginManager

app = Flask(__name__)
client = MongoClient('localhost', 27017)
db = client.myMissionJournal
#login_manager = LoginManager()

@app.route('/register', methods=['GET', 'POST'])
def register():
	msg=''
	if request.method == 'POST':
		if not '@' in request.form['username']:
			msg = "Please enter a valid email address." 
		elif not request.form['password'] == request.form['password_confirm']:
			msg = "The passwords you entered do not match. Please try again."
		elif len(request.form['password']) < 8 or len(request.form['password']) > 20:
			msg = "Please choose a password that is between 8 and 20 characters long."
		elif len(request.form['given_name']) == 0 or len(request.form['last_name']) == 0:
			msg = "Please fill out all required fields."
		else:
			findUser = db.users.find_one({"email": request.form['username']})
                        if findUser:
				msg = "An account for the user " + request.form['username'] + " already exists."
		        else:
				salt = uuid.uuid4().hex
				hash_pass = hashlib.sha256(request.form['password'] + salt).hexdigest()
				user = {"email": request.form['username'], "firstName": request.form['given_name'], "lastName": request.form['last_name'], "mission": request.form['mission_name'], "title": request.form['missionary_title'], "salt": salt, "password": hash_pass}				
				db.users.save(user)
				msg = "Account for " + request.form['username'] + " registered successfully."
				return render_template('landing.html', message = msg)
	return render_template('registration.html', message=msg)

@app.route('/')
@app.route('/index')
def index():
	return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	return render_template('landing.html')

@app.route('/edit_profile')
def edit_profile():
	return render_template('edit_profile.html')

@app.route('/messages')
def messages():
	return render_template('messages.html')

def isValidUser(username, password):
	user = db.users.find_one({"email": username})
	if user:
		hash_pass = hashlib.sha256(password + user["salt"]).hexdigest()
		if hash_pass == user["password"]:
			return True
	return False


#this is the REST API

#returns a list of all messages to or from the user as a list of dictionaries in JSON form
@app.route('/getAllMessages/<username>/<password>')
def getAllMessages(username, password):
	if isValidUser(username, password):
		#allUserMessages = db.messages.find({$or[{"sender":username},{"recipients":username}]})
		if allUserMessages:
			messageList = []
			for message in allUserMessages:
				messageList.append(message)
			return str(messageList)
			#return "got to the right place"
		else:
			return "no messages could be found for the user"
	else:
		return "the username and password could not be validated"

#returns a list of messages sen by the user as a list of dictionaries in JSON form
@app.route('/getSentMessages/<username>/<password>')
def getSentMessage(username, password):
	if isValidUser(username, password):
		allSentMessages = db.messages.find({"sender":username})
		if allSentMessages:
			messageList = []
			for message in allSentMessages:
				messageList.append(message)
			return str(messageList)
		else:
			return "no messages could be found for the user"
	else:
		return "the username and password could not be validated"

@app.route('/getlance/<username>/<password>')
def getLance(username, password):
	return "hi " + username + " your password is " + password

if __name__ == '__main__':
	app.run()


