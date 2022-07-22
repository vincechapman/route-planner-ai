import click
from flask import current_app, g
from flask.cli import with_appcontext

import psycopg2
from psycopg2 import Error

import os
from dotenv import load_dotenv
load_dotenv()


def get_db():
    if 'db' not in g:
        try:
            g.db = psycopg2.connect(
                user=os.environ['AWS_RDS_DB_USER'],
                password=os.environ['AWS_RDS_DB_PASSWORD'],
                host=os.environ['AWS_RDS_DB_HOST'],
                port=os.environ['AWS_RDS_DB_PORT']
                )
            g.cursor = g.db.cursor()
        except (Exception, Error) as error:
            print("Error while connecting to PostgreSQL:", error)
    return g.db, g.cursor


def init_db():
    db, cursor = get_db()

    with current_app.open_resource('schema.sql') as f:
        cursor.execute(f.read().decode('utf8'))
        db.commit()
        print("Tables created successfully in PostgreSQL")


def close_db(e=None):
    db = g.pop('db', None)
    cursor = g.pop('cursor', None)

    if db is not None:
        cursor.close()
        db.close()
        print("PostgreSQL connection is closed")


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
