import os
import shortuuid

from datetime import datetime
from sqlite3 import Error as SQLiteError

from flask import request, jsonify, render_template
from flask_app import app

from repo import SQLiteDB


@app.route("/")
def index():
	return render_template("index.html")


def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]


def require_api_key(f):
	def decorated_function(*args, **kwargs):
		stored_key = os.getenv("API_KEY")
		if request.headers.get('X-API-KEY') != stored_key:
			return jsonify({"error": "Permission denied."}), 401
		return f(*args, **kwargs)
	return decorated_function


@app.route("/upload", methods=['POST'])
@require_api_key
def upload():
	if 'file' not in request.files:
		return jsonify({"error": "No file part"}), 400
	file = request.files["file"]
	if file.filename == '':
		return jsonify({"error": "No selected file"}), 400
	if file and allowed_file(file.filename):
		image_uuid = shortuuid.uuid()
		filename = f"{file.filename}"
		file_path = os.path.join(app.config["UPLOAD_DIR"], filename)
		file.save(file_path)
		date = datetime.utcnow()
		try:
			with SQLiteDB(app.config["DB_PATH"]) as db:
				db.add_image(filename, image_uuid, date)
		except SQLiteError as err:
			err_name = err.sqlite_errorname
			return jsonify({"error": f"Failed to upload image: {err_name}"}), 400
		url = f"{app.config['DOMAIN']}/i/{image_uuid}"
		return jsonify({'uuid': image_uuid, 'url': url}), 201
	else:
		return jsonify({'error': 'File type not allowed'}), 400


@app.route('/i/<image_uuid>', methods=['GET'])
def get_image(image_uuid):
	with SQLiteDB(app.config["DB_PATH"]) as db:
		image_data = db.get_image_data(image_uuid)

	if image_data is not None:
		filename = image_data["filename"]
		date_time = image_data["date"]
	else:
		return jsonify({"error": "Image not found"}), 404

	date = date_time.split(" ")[0]

	return render_template("image.html", filename=f"images/{filename}", date=date)
