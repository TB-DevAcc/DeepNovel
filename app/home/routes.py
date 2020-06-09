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
        ["color", "background"],
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


# model = TFAutoModelWithLMHead.from_pretrained("distilgpt2")
# tokenizer = GPT2TokenizerFast.from_pretrained(
#     "gpt2", unk_token="<|unknown|>", eos_token="<|endoftext|>",  # bos_token="<|beginoftext|>",
# )


# def gen(prompt, min_length=0, max_length=250):

#     print("INPUT:", prompt)
#     # try:
#     #     prompt = prompt[-200:]
#     # except:
#     #     pass
#     # prompt = "<|beginoftext|>" + prompt + "<|endoftext|>"
#     last_dot = prompt.rfind(".")
#     if last_dot == -1:
#         pass
#     else:
#         pass
#         # prompt = prompt[: last_dot + 1] + "<|endoftext|>" + prompt[last_dot + 1 :]
#     print("PROMPT:", prompt)

#     inputs = tokenizer.encode(prompt, add_special_tokens=False, return_tensors="tf")

#     print("INPUT IDS:", inputs)

#     prompt_length = len(
#         tokenizer.decode(inputs[0], skip_special_tokens=False, clean_up_tokenization_spaces=True)
#     )
#     outputs = model.generate(
#         inputs, max_length=max_length, min_length=min_length, do_sample=True, top_p=0.95, top_k=60,
#     )
#     print("OUTPUTS:", outputs)
#     generated = tokenizer.decode(outputs[0])[prompt_length:]
#     print("GENERATED:", generated)

#     generated = re.sub("<|beginoftext|>", "", generated)
#     generated = re.sub("<|endoftext|>", "", generated)

#     print("GENERATED CLEAN:", generated)

#     return generated


# Text Generation
@blueprint.route("/generate/<int:post_id>", methods=["POST"])
@login_required
def generate(post_id):
    l = int(request.form["length"])
    doc = request.form["doc"]
    doc = doc.split(".")[-1]
    doc_length = len(doc)
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    if l == 1:
        doc = ai.generate(doc)[0]["generated_text"][doc_length:]
        print("GENERATED", doc)
        # doc = gen(doc, max_length=50)
        # doc = "GENERATED LINE"
        return jsonify(doc), 200
    elif l < 500:
        doc = ai.generate(doc, min_length=50)[0]["generated_text"][doc_length:]
        # doc = "GENERATED PARAGRAPH"
        return jsonify(doc), 200
    else:
        doc = ai.generate(doc, min_length=100)[0]["generated_text"][doc_length:]
        # doc = "GENERATED CHAPTER"
        return jsonify(doc), 200
    abort(500)


# question-answering
@blueprint.route("/qa/<int:post_id>/<string:question>", methods=["GET"])
@login_required
def answer(post_id, question):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    doc = post.content
    print("DOC", doc)
    print("Q", question)
    # doc = ai.answer(question, doc)
    doc = "Answer"
    return jsonify(doc), 200
