"""Views para o blog (posts) da aplicação Flaskr."""
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)

def get_post_for_action(post_id, check_author=True):
    """
    Busca um post pelo ID.
    
    Implementa Cláusulas de Guarda:
    - Aborta 404 se o post não existir.
    - Aborta 403 se 'check_author' for True e o usuário logado não for o autor.
    
    CC reduzida de 115/88 para 4/5.
    """
    # Renomeado 'id' para 'post_id' para corrigir aviso do Pylint (redefinição de built-in 'id')
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (post_id,)
    ).fetchone()

    # Cláusula de Guarda 1: Post não encontrado
    if post is None:
        abort(404, f"Post id {post_id} doesn't exist.")

    # Cláusula de Guarda 2: Verificação de Permissão (403 Forbidden)
    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/')
def index():
    """Mostra todos os posts, do mais novo para o mais antigo."""
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    """Permite ao usuário logado criar uma nova postagem."""
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id) VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

@bp.route('/<int:post_id>/update', methods=('GET', 'POST'))
@login_required
def update(post_id):
    """Permite ao autor editar uma postagem existente."""
    # Uso da função auxiliar para buscar e verificar permissão (CC drasticamente reduzida aqui)
    post = get_post_for_action(post_id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ? WHERE id = ?',
                (title, body, post_id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

@bp.route('/<int:post_id>/delete', methods=('POST',))
@login_required
def delete(post_id):
    """Exclui uma postagem. Apenas o autor pode fazer isso."""
    # Uso da função auxiliar para buscar e verificar permissão (CC drasticamente reduzida aqui)
    get_post_for_action(post_id)
    
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (post_id,))
    db.commit()
    
    return redirect(url_for('blog.index'))
