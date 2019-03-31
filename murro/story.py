from flask import (Blueprint, flash, g, redirect, render_template, request,
        url_for,)
from werkzeug.exceptions import abort

from murro.auth import login_required
from murro.db import get_db

bp = Blueprint('news',__name__)

@bp.route('/')
def index():
    db = get_db()
    stories = db.execute(
            'SELECT s.id, title, facts, analysis, created, news_date, '
            ' author_id, username'
            ' FROM story s JOIN user u ON s.author_id = u.id'
            ' ORDER BY created DESC'
            ).fetchall()
    return render_template('news/index.html', stories=stories)

@bp.route('/create', methods=('GET','POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        facts = request.form['facts']
        analysis = request.form['analysis']
        news_date = request.form['news_date']
        error = None

        if not title:
            error = 'Title is required.'
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                    'INSERT INTO story (title, facts, analysis, '
                    ' news_date, author_id)'
                    ' VALUES (?, ?, ?, ?, ?)',
                    (title, facts, analysis, news_date, g.user['id'])
                    )
            db.commit()
            return redirect(url_for('news.index'))

    return render_template('news/create.html')

def get_story(id, check_author=True):
    story = get_db().execute(
            'SELECT s.id, title, facts, analysis, news_date,'
            ' created, author_id, username'
            ' FROM story s JOIN user u ON s.author_id = u.id'
            ' WHERE s.id = ?',
            (id,)
        ).fetchone()

    if story is None:
        abort(404, "Post if {0} doesn't exist.".format(id))

    if check_author and story['author_id'] != g.user['id']:
        abort(403)

    return story

@bp.route('/<int:id>/update', methods=('GET','POST'))
@login_required
def update(id):
    story = get_story(id)

    if request.method == 'POST':
        title = request.form['title']
        facts = request.form['facts']
        analysis = request.form['analysis']
        news_date = request.form['news_date']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                    'UPDATE story SET title = ?, facts = ?, analysis = ?,'
                    ' news_date = ?'
                    ' WHERE id = ?',
                    (title, facts, analysis, news_date, id)
                )
            db.commit()
            return redirect(url_for('news.index'))
    return render_template('news/update.html', story=story)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_story(id)
    db = get_db()
    db.execute('DELETE FROM story WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('news.index'))
