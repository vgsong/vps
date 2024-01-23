from app import app, db
from app.forms import LoginForm, PostForm, BookForm
from app.models import User, Post

from flask import render_template, request, redirect, flash, url_for
from urllib.parse import urlsplit
from flask_login import current_user, login_user, logout_user, login_required

import sqlalchemy as sa
from sqlalchemy import desc

@app.route('/')
@app.route('/index')
def index():
    u=db.session.get(User,1)
    query = u.posts.select()
    posts = db.session.scalars(query).all()
    return render_template('index.html', posts=posts)

@app.route('/aboutme')
def aboutme():
    return render_template('aboutme.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=True)
        next_page=request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page=url_for('index')
        return redirect(next_page)
        
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/post', methods=['GET','POST'])
@login_required
def post():
    form = PostForm()
    if request.method == 'GET':
        return render_template('post.html', form=form)
    
    if form.validate_on_submit():
        u=db.session.get(User,1)
        post = Post(title= form.title.data, body=form.body.data, author=u)
        db.session.add(post)
        db.session.commit()
        flash('Post posted')
        return redirect(url_for('index'))
    

@app.route('/post/<id>')
def post_detail(id):
    post = db.session.get(Post,id)
    return render_template('postdetail.html', post=post)



@app.route('/postbook')
@login_required
def postbook():
    form = BookForm()
    return render_template('postbook.html', form=form)


@app.route('/projsearch')
def projsearch():
    return render_template('projsearch.html')