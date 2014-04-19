from flask import Flask
from flask.ext.pymongo import PyMongo

app = Flask('mission-email-journal')

from flask import render_template

@app.route('/post/<username>')
def show_user_profile(username):
	return 'User %s' % username

@app.route('/')
@app.route('/index')
def index():
	return render_template('layout.html')

if __name__ == '__main__':
	app.run()
