from flask import Flask
from flask.ext.pymongo import PyMongo

app = Flask('mission-email-journal')

from flask import render_template

@app.route('/register')
def register():
	return render_template('registration.html')

@app.route('/')
@app.route('/index')
def index():
	return render_template('landing.html')

if __name__ == '__main__':
	app.run()
