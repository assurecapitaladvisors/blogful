from flask import render_template

from blog import app
from database import session
from models import Post

import mistune
from flask import request, redirect, url_for

@app.route("/")
@app.route("/page/<int:page>")
def posts(page=1, paginate_by=10):
    # Zero-indexed page
    page_index = page - 1

    count = session.query(Post).count()

    start = page_index * paginate_by
    end = start + paginate_by

    total_pages = (count - 1) / paginate_by + 1
    has_next = page_index < total_pages - 1
    has_prev = page_index > 0

    posts = session.query(Post)
    posts = posts.order_by(Post.datetime.desc())
    posts = posts[start:end]

    return render_template("posts.html",
        posts=posts,
        has_next=has_next,
        has_prev=has_prev,
        page=page,
        total_pages=total_pages
    )

@app.route("/post/<int:postId>")
def get_post(postId=None):
    post = session.query(Post).filter(Post.id==postId).all()[0]
    return render_template("post.html", post=post)

@app.route("/post/<int:postId>/edit", methods=["GET"])
def edit_post_get(postId=None):
    post = session.query(Post).filter(Post.id==postId).all()[0]
    return render_template("edit_post.html", post=post)

@app.route("/post/<int:postId>/edit", methods=["POST"])
def edit_post_post(postId=None):
    post = session.query(Post).filter(Post.id==postId).all()[0]
    post.title = request.form["title"]
    post.content = mistune.markdown(request.form["content"])
    session.add(post)
    session.commit()
    return redirect(url_for("get_post", postId=post.id))

@app.route("/post/<int:postId>/delete/confirm")
def delete_post_confirm(postId=None):
    post = session.query(Post).filter(Post.id==postId).all()[0]
    return render_template("confirm_delete.html", post=post)

@app.route("/post/<int:postId>/delete")
def delete_post(postId=None):
    post = session.query(Post).filter(Post.id==postId).all()[0]
    session.delete(post)
    session.commit()
    return redirect(url_for("posts"))

@app.route("/post/add", methods=["GET"])
def add_post_get():
    return render_template("add_post.html")

@app.route("/post/add", methods=["POST"])
def add_post_post():
    post = Post(
        title=request.form["title"],
        content=mistune.markdown(request.form["content"]),
    )
    session.add(post)
    session.commit()
    return redirect(url_for("posts"))