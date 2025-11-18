"""Módulo de conexão e inicialização do banco de dados SQLite."""
import sqlite3

import click
from flask import current_app, g

def get_db():
    """Retorna a conexão com o banco de dados."""
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None): # Removido o argumento 'e' não utilizado se não for necessário
    """Fecha a conexão com o banco de dados se estiver aberta."""
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    """Carrega o esquema do banco de dados e inicializa."""
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
def init_db_command():
    """Limpa os dados existentes e cria as tabelas."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    """Registra as funções de banco de dados na aplicação Flask."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
