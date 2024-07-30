import secrets
import os

from functools import wraps

from flask import render_template, abort, request, redirect, url_for, flash, session, make_response, jsonify
from flask_app import app

from repo import SQLiteDB


def require_login(f):
	@wraps(f)
	def login_function(*args, **kwargs):
		if 'auth_token' not in session:
			abort(401)
		if session.get('auth_token') not in app.config['TOKENS']:
			abort(403)
		return f(*args, **kwargs)
	return login_function


@app.route("/")
def index():
	return render_template("index.html")


@app.route('/i/<image_uuid>', methods=['GET'])
def get_image(image_uuid):
	with SQLiteDB(app.config["DB_PATH"]) as db:
		image_data = db.get_image_data(image_uuid)

	if image_data is None:
		abort(404)

	filename = image_data["filename"]
	date_time = image_data["date"]

	date = date_time.split(" ")[0]

	return render_template("image.html", filename=f"images/{filename}", date=date)


@app.route('/gallery', methods=['GET'])
@require_login
def gallery():
	return render_template("gallery.html")


@app.route('/get_uuids', methods=['GET'])
@require_login
def get_uuids():
	with SQLiteDB(app.config["DB_PATH"]) as db:
		result = db.get_all_uuids()

	uuids = [uuid[0] for uuid in result]

	return jsonify(uuids), 200


@app.route('/login', methods=['GET'])
def login_page():
	return render_template("login.html")


@app.route('/login', methods=['POST'])
def login():
	stored_username = os.getenv('LOGIN_USERNAME')
	stored_password = os.getenv('LOGIN_PASSWORD')
	username = request.form['username']
	password = request.form['password']

	if username == stored_username and password == stored_password:
		auth_token = secrets.token_hex(16)
		app.config['TOKENS'].append(auth_token)
		session['auth_token'] = auth_token
		response = make_response(redirect(url_for('gallery')))
		response.set_cookie('username', username, httponly=False)

		return response
	else:
		flash('Invalid username or password')
		return redirect(url_for('login_page'))


@app.route('/logout')
def logout():
	if 'auth_token' in session and session.get('auth_token') in app.config['TOKENS']:
		app.config['TOKENS'].remove(session.get('auth_token'))

	response = make_response(redirect(url_for('index')))

	session.pop('auth_token', None)

	response.set_cookie('username', '', expires=0)
	response.set_cookie('session', '', expires=0)

	return response
