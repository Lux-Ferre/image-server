from flask import render_template, abort
from flask_app import app

from repo import SQLiteDB


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
