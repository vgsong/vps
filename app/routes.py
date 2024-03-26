from app import app, db
from app.forms import LoginForm, PostForm
from app.models import User, Post

from flask import render_template, request, redirect, flash, url_for
from urllib.parse import urlsplit
from flask_login import current_user, login_user, logout_user, login_required

from sqlalchemy import desc

import sqlalchemy as sa
import pandas as pd

from pivottablejs import pivot_ui

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
        return redirect(url_for('excelb'))
    
@app.route('/post/<id>')
def post_detail(id):
    post = db.session.get(Post,id)
    return render_template('postdetail.html', post=post)

# @app.route('/postbook')
# @login_required
# def postbook():
#     form = BookForm()
#     return render_template('postbook.html', form=form)

@app.route('/projsearch')
def projsearch():

    return render_template('projsearch.html')


@app.route('/post/edit/<int:id>', methods=['GET','POST'])
@login_required
def postedit(id):
    user = db. session.get(User,1)
    postedit = db.session.get(Post,id)
    
    if request.method == "POST":
        postedit.title = request.form.get('title')
        postedit.body = request.form.get('body')

        db.session.add(postedit)
        db.session.commit()
        flash('Post Succesfully Edited!')
        return redirect(url_for('excelb'))

    if request.method == "GET":
        form = PostForm()
        form.title.data = postedit.title
        form.body.data = postedit.body
        return render_template('postedit.html', form=form)
    
    else:
        flash('Post does not exist')
        return render_template('index.html')
    

@app.route('/excelb')
def excelb():
    # u=db.session.get(User,1)

    #  uncomment this for backup
    # query = u.posts.select()
    # posts = db.session.scalars(query).all()
    
    # used for pagination 
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page=page, per_page=4)
    return render_template('excelb.html', posts=posts)

@app.route('/dashmenu')
def dashmenu():

    dashmenu_mapp = {
        'EMP HOURS': 'dasha',
        'NEW DASH': 'dashb',
    }
    
    return render_template('dash_menu.html', dashmenu_mapp=dashmenu_mapp)


@app.route('/dasha', methods=['GET','POST'])
def dasha():
    df = pd.read_csv('./app/static/csv/vdata.csv')
    emp_unique = df['EMPNAME'].unique()

    if request.method == 'POST':
        summ_dict = {}
        emp_name = request.form.get('emp_names')  # obtains selected value from emp_names form
        emp_selected = df[df['EMPNAME'].str.contains(emp_name)]  # filter df col empname based on selection
        
        summ_dict['TOTAL_HOURS'] = emp_selected['HOURS'].sum()
        summ_dict['TOTAL_REG'] = emp_selected[emp_selected['TYPE'].str.contains('REGULAR')]['HOURS'].sum()
        summ_dict['TOTAL_OH'] = emp_selected[emp_selected['TYPE'].str.contains('OH')]['HOURS'].sum()
        summ_dict['BILLA_%'] = '{:0.1f}'.format((summ_dict['TOTAL_REG'] / summ_dict['TOTAL_HOURS'])*100)

        

        pivot_mper = emp_selected.groupby(['TYPE','MPER'])['HOURS'].sum().unstack()  # created pivot table
        pivot_proj = emp_selected.groupby(['PROJ','TYPE','MPER'])['HOURS'].sum().unstack()  # created pivot table

        pivot_ui(emp_selected , outfile_path='./app/templates/pivot.html')

        return render_template('dash_a.html', 
                               emp_unique=emp_unique, 
                               emp_name=emp_name, 
                               summ_dict = summ_dict, 
                               table_one=pivot_mper.to_html(classes="emp_df_table"), 
                               table_two = pivot_proj.to_html(classes="emp_df_table")
                               )

    return render_template('dash_a.html', emp_unique=emp_unique)

@app.route('/dashb', methods=['GET','POST'])
def dashb():
    return render_template('dash_b.html')


@app.route('/pivot')
def pivot():
    return render_template('pivot.html')