# -*- encoding: utf-8 -*-
"""
MIT License
Copyright (c) 2019 - present AppSeed.us
"""

from flask import abort, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from jinja2 import TemplateNotFound

from app import db, login_manager
from app.base.forms import PostForm
from app.base.models import Post, User
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
        return render_template("errors/page-404.html"), 404

    except:
        return render_template("errors/page-500.html"), 500


## Editor Posts


@blueprint.route("/editor/new", methods=["GET", "POST"])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Your document has been saved!", "success")
        return redirect(url_for("index"))
    return render_template("create_post.html", title="New Post", form=form, legend="New Post")


@blueprint.route("/editor/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("post.html", title=post.title, post=post)


@blueprint.route("/editor/<int:post_id>/update", methods=["GET", "POST"])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("Your document has been updated!", "success")
        return redirect(url_for("post", post_id=post.id))
    elif request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
    return render_template(
        "create_post.html", title="Update Post", form=form, legend="Update Post"
    )


@blueprint.route("/editor/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Your document has been deleted!", "success")
    return redirect(url_for("home"))
