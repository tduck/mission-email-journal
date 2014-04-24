import sys, hashlib, uuid, os
from flask import Flask, request, render_template, redirect, session, url_for
from pymongo import MongoClient
from flask.ext.mongokit import MongoKit, Document
import missionJournalDB

app = Flask(__name__)
app.secret_key = os.urandom(256)

client = MongoClient('localhost', 27017)
db = client.myMissionJournal
dbAccess = missionJournalDB.MissionJournalDB()

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
				user = {"email": request.form['username'], 
					"firstName": request.form['given_name'], 
					"lastName": request.form['last_name'], 
					"mission": request.form['mission_name'], 
					"title": request.form['missionary_title'], 
					"salt": salt, 
					"password": hash_pass, 
					"secondaryEmail": request.form['secondary_email']}
				db.users.save(user)
				msg = "Account for " + request.form['username'] + " registered successfully."
				return render_template('landing.html', message = msg)
	return render_template('registration.html', message=msg)

@app.route('/')
@app.route('/index')
def index():
	if 'username' in session:
		return redirect('/messages')
	else:
		return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		required = ['email', 'password']
		for r in required:
			if r not in request.form or request.form[r] == '':
				return render_template('landing.html', message="Your account " + r + " is required.")
		email = request.form['email']
		password = request.form['password']
		if isValidUser(email, password):
			session['username'] = email
			return redirect('/messages')
		else:
			return render_template('landing.html', message="Incorrect email or password.")
	else:
		return redirect('/')

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
	if 'username' in session:
		msg = ''
		current_user = db.users.find_one({"email": session['username']})
		if request.method == 'POST':
			if not request.form['password'] == request.form['password_confirm']:
				msg = "Password confirmation did not match."
			elif not isValidUser(session['username'], request.form['password']): 
				msg = "Incorrect password."
			else:
				db.users.update({"email": session['username']}, 
						{"$set": {"firstName": request.form['given_name'],
								"lastName": request.form['last_name'],
								"mission": request.form['mission_name'],
								"secondaryEmail": request.form['secondary_email']}})
				msg = "Update successful."
				current_user = db.users.find_one({"email": session['username']})
		return render_template('edit_profile.html', given_name=current_user['firstName'],
								last_name=current_user['lastName'],
								mission_name=current_user['mission'],
								secondary_email=current_user['secondaryEmail'],
								message=msg)
	else:
		return redirect('/')

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
	if 'username' in session:
		msg = ''
		if request.method == 'POST':
			required = ['old_password','new_password', 'new_pass_confirm']
	                for r in required:
        	                if r not in request.form or request.form[r] == '':
                	                return render_template('change_password.html', message="All fields are required.")
			if not request.form['new_password'] == request.form['new_pass_confirm']:
				msg = "New password confirmation did not match."
			elif not isValidUser(session['username'], request.form['old_password']):
                                msg = "Incorrect current password."
                        else:
				current_user = db.users.find_one({"email": session['username']})
				hash_pass = hashlib.sha256(request.form['new_password'] + current_user["salt"]).hexdigest()
				db.users.update({"email": session['username']}, {"$set": {"password":hash_pass}})
				msg = "Password changed successfully."
				return render_template('change_password.html', message=msg)
		else:
			return render_template('change_password.html')
	else:
		return redirect('/')

@app.route('/messages')
def messages():
	if 'username' in session:
		messages = getAllMessages(username, password)
		return render_template('messages.html', messages)
	else:
		return redirect('/')

@app.route('/logout')
def logout():
	session.pop('username', None)
	return redirect('/')

def isValidUser(username, password):
	user = db.users.find_one({"email": username})
	if user:
		hash_pass = hashlib.sha256(password + user["salt"]).hexdigest()
		if hash_pass == user["password"]:
			return True
	return False


#this is the REST API

#returns a list of all messages to or from the user as a list of dictionaries in JSON form
@app.route('/getallmessages/<username>/<password>')
def getAllMessages(username, password):
	if isValidUser(username, password):
		messageList = dbAccess.getAllUserMail(username = username)
		return str(messageList)
	else:
		return "the username and password could not be validated"

#returns a list of messages sen by the user as a list of dictionaries in JSON form
@app.route('/getsentmessages/<username>/<password>')
def getSentMessage(username, password):
	if isValidUser(username, password):
		allSentMessages = db.messages.find({"sender":username})
		messageList = []
		if allSentMessages:
			for message in allSentMessages:
				messageList.append(message)
		return str(messageList)
	else:
		return "the username and password could not be validated"

@app.route('/getRecievedmessages/<username>/<password>')
def getRecievedMessage(username, password):
	if isValidUser(username, password):
		allInMessages = db.messages.find({"recipients":username})
		messageList = []
		if allInMessages:
			for message in allInMessages:
				messageList.append(message)
		return str(messageList)
	else:
		return "the username and password could not be validated"


@app.route('/getlance/<username>/<password>')
def getLance(username, password):
	return "hi " + username + " your password is " + password

if __name__ == '__main__':
	app.run()


