from api.app.config import init_settings
from libs.db import init_db

engine = init_db(init_settings().db_url)
