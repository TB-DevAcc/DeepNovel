# -*- encoding: utf-8 -*-
"""
MIT License
Copyright (c) 2019 - present AppSeed.us
"""

import re

from flask import abort, flash, json, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from jinja2 import TemplateNotFound
from transformers import AutoTokenizer, GPT2TokenizerFast, TFAutoModelWithLMHead, pipeline

from app import db, login_manager
from app.base.forms import PostForm
from app.base.models import Post, User
from app.base.pipes import AI
from app.home import blueprint

ai = AI()


@blueprint.route("/index")
@login_required
def index():
    user_posts = Post.query.filter(Post.user_id == current_user.id).all()
    # Make Date readable
    for i in range(len(user_posts)):
        user_posts[i].date_posted = user_posts[i].date_posted.strftime("%d.%m.%Y at %H:%M")
    return render_template("index.html", user=current_user, posts=user_posts)


@blueprint.route("/<template>")
def route_template(template):

    try:

        if not template.endswith(".html"):
            template += ".html"

        return render_template(template, user=current_user)

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
        flash("Your document has been created!", "success")
        return redirect(url_for("home_blueprint.index"))

    return render_template("create_post.html", title="New Post", form=form, legend="New Post")


@blueprint.route("/editor/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    form = PostForm()
    toolbar_formats = formats = [
        ["bold", "italic", "underline", "strike"],
        # ["color", "background"],
        [("script", "sub"), ("script", "super")],
        [*[("header", f"{i}") for i in range(1, 3)], "blockquote", "code-block"],
        [("list", "ordered"), ("list", "bullet"), ("indent", "-1"), ("indent", "+1")],
        [("direction", "rtl"), "align"],
        ["link", "image", "video", "formula"],
        ["clean"],
    ]
    return render_template(
        "editor.html",
        title=post.title,
        post=post,
        form=form,
        formats=toolbar_formats,
        isinstance=isinstance,
        tuple=tuple,
    )


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
        return redirect(url_for("editor", post_id=post.id))
    elif request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
    return render_template(
        "create_post.html", title="Update Post", form=form, legend="Update Post"
    )


@blueprint.route("/editor/<int:post_id>/update_content", methods=["GET", "POST"])
@login_required
def update_content(post_id):
    """
    update_content receives ajax requests for the editor content. 
    For GET requests it sends the stored content, 
    for POST requests it stores the received value in posts.

    Args:
        post_id (string): id of the entry in the post table, that it's referring to

    Returns:
        Success or Failure
    """
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    # print("METHOD", request.method)
    if request.method == "GET":
        # print("CONTENT", post.content)
        return post.content
    elif request.method == "POST":
        # print("CONTENT", request.form)
        try:
            post.content = request.form["doc"]
            db.session.commit()
            return json.dumps({"success": True}), 200, {"ContentType": "text"}
        except Exception as e:
            return json.dumps({"success": False}), 500, {"ContentType": "text"}


@blueprint.route("/editor/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Your document has been deleted!", "success")
    return redirect(url_for("home_blueprint.index"))


## AI requests

# Text Generation
@blueprint.route("/generate/<int:post_id>", methods=["POST"])
@login_required
def generate(post_id):
    l = int(request.form["length"])
    doc = request.form["doc"]
    try:
        doc = doc.split(".")[-3]
    except IndexError:
        doc = doc.split(".")[-1]
    doc_length = len(doc)
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    if l == 1:
        doc = ai.generate(doc, max_length=50)[0]["generated_text"][doc_length:]
        # doc = "GENERATED LINE"
        print("GENERATED", doc)
        return jsonify(doc), 200
    elif l < 500:
        doc = ai.generate(doc, min_length=30, max_length=100)[0]["generated_text"][doc_length:]
        # doc = "GENERATED PARAGRAPH"
        print("GENERATED", doc)
        return jsonify(doc), 200
    else:
        doc = ai.generate(doc, min_length=100)[0]["generated_text"][doc_length:]
        # doc = "GENERATED CHAPTER"
        print("GENERATED", doc)
        return jsonify(doc), 200
    abort(500)


# question-answering
@blueprint.route("/answer/<int:post_id>", methods=["POST"])
@login_required
def answer(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    doc = request.form["doc"]
    question = request.form["question"]
    print("DOC", doc)
    print("Q", question)
    doc = ai.answer(question=question, context=doc)
    # doc = "Answer"
    return jsonify(doc), 200


# analyzing
@blueprint.route("/analyze/<int:post_id>", methods=["POST"])
@login_required
def analyze(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    doc = request.form["doc"]
    doc = ai.mark_entities(doc)
    print("ANALYSIS:", doc)
    # Postprocess output into set of persons, organizations and locations
    P = set()
    O = set()
    L = set()
    for e in doc:
        if e["entity_group"] == "I-PER" or e["entity_group"] == "B-PER":
            P.add(e["word"])
        elif e["entity_group"] == "I-ORG" or e["entity_group"] == "B-ORG":
            O.add(e["word"])
        elif e["entity_group"] == "I-LOC" or e["entity_group"] == "B-LOC":
            L.add(e["word"])
    print("ANALYSIS P:", P)
    print("ANALYSIS O:", O)
    print("ANALYSIS L:", L)
    return jsonify({"P": list(P), "O": list(O), "L": list(L)}), 200
