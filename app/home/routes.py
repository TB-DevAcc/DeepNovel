# -*- encoding: utf-8 -*-
"""
MIT License
Copyright (c) 2019 - present AppSeed.us
"""

from flask import redirect, render_template, url_for
from flask_login import current_user, login_required
from jinja2 import TemplateNotFound

from app import login_manager
from app.home import blueprint


@blueprint.route("/index")
@login_required
def index():

    return render_template("index.html")


@blueprint.route("/<template>")
def route_template(template):

    try:

        if not template.endswith(".html"):
            template += ".html"

        return render_template(template)

    except TemplateNotFound:
        return render_template("page-404.html"), 404

    except:
        return render_template("page-500.html"), 500
