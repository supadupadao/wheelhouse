from api.app.config import init_settings
from libs.db import Database

conn = Database(init_settings().DB_URL)
