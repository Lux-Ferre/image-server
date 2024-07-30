from flask import render_template
from flask_app import app


@app.errorhandler(401)
def not_found(e):
	return render_template("errors/401.html")


@app.errorhandler(403)
def unauthenticated(e):
	return render_template("errors/403.html")


@app.errorhandler(404)
def forbidden(e):
	return render_template("errors/404.html")
