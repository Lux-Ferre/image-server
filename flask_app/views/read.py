import secrets
import os

from datetime import datetime, timedelta, UTC
from functools import wraps
from flask_image_resizer.core import resized_img_src

from flask import render_template, abort, request, redirect, url_for, flash, session, make_response, jsonify
from flask_app import app

from repo import SQLiteDB


def require_login(f):
	@wraps(f)
	def login_function(*args, **kwargs):
		if 'auth_token' not in session:
			abort(401)
		with SQLiteDB(app.config["DB_PATH"]) as db:
			valid_token = db.is_valid_token(session['session_id'], session['auth_token'])
		if not valid_token:
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

	date = date_time.strftime("%Y-%m-%d")

	return render_template("image.html", filename=f"images/{filename}", date=date)


@app.route('/gallery', methods=['GET'])
@require_login
def gallery():
	return render_template("gallery.html")


@app.route('/get_images', methods=['GET'])
@require_login
def get_all_images():
	with SQLiteDB(app.config["DB_PATH"]) as db:
		result = db.get_all_images()

	images = []

	for image in result:
		images.append({
			"uuid": image[0],
			"url": resized_img_src(image[1], width=300, height=186, mode="crop", enlarge=True),
			"date": image[2].strftime("%Y-%m-%d"),
		})

	return jsonify(images), 200


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
		expiry = datetime.now(UTC) + timedelta(days=30)
		with SQLiteDB(app.config["DB_PATH"]) as db:
			ident = db.add_token(username, auth_token, expiry)
		session['auth_token'] = auth_token
		session['auth_token_expiry'] = expiry
		session['username'] = username
		session['session_id'] = ident
		response = make_response(redirect(url_for('gallery')))
		response.set_cookie('username', username, httponly=False, expires=expiry)

		return response
	else:
		flash('Invalid username or password')
		return redirect(url_for('login_page'))


@app.route('/logout')
def logout():
	if 'auth_token' in session:
		token = session.get('auth_token')
		ident = session.get('session_id')
		with SQLiteDB(app.config["DB_PATH"]) as db:
			valid_token = db.is_valid_token(ident, token)
			if valid_token:
				db.delete_token(ident)

	response = make_response(redirect(url_for('index')))

	session.pop('auth_token', None)

	response.set_cookie('username', '', expires=0)
	response.set_cookie('session', '', expires=0)

	return response
