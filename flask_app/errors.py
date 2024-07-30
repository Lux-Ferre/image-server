from flask import render_template
from flask_app import app


@app.errorhandler(404)
def not_found(e):
	return render_template("errors/404.html")
