from config import Config
from app.api import create_app

config = Config()
app, _ = create_app(config)
