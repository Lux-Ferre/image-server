class Config:
	DB_PATH = "image_storage.db"
	ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
	UPLOAD_DIR = "flask_app/static/images"
	DOMAIN = "https://img.luxferre.dev"
	IMAGES_PATH = ["static/images"]
	FLUSH_TOKENS_ON_STARTUP = False
