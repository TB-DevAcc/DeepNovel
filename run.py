# -*- encoding: utf-8 -*-
"""
MIT License
Copyright (c) 2020 - Tobias Becher
"""

from os import environ
from sys import exit

from decouple import config
from flask_migrate import Migrate

from app import create_app, db
from config import config_dict

# CHANGE FOR PRODUCTION
DEBUG = config("DEBUG", default=True)

get_config_mode = "Debug" if DEBUG else "Production"

try:
    app_config = config_dict[get_config_mode.capitalize()]

except KeyError:
    exit("Error: Invalid <config_mode>. Expected values [Debug, Production] ")

app = create_app(app_config)
Migrate(app, db)

if __name__ == "__main__":
    app.run()  # 0.0.0.0:5005
