import click
from flask import current_app, g
from flask.cli import with_appcontext

import psycopg2
from psycopg2 import Error

import os
from dotenv import load_dotenv
load_dotenv()

import colorama
from colorama import Fore, Style
colorama.init()

def get_db():
    if 'db' not in g:
        try:
            g.db = psycopg2.connect(
                user=os.environ['AWS_RDS_DB_USER'],
                password=os.environ['AWS_RDS_DB_PASSWORD'],
                host=os.environ['AWS_RDS_DB_HOST'],
                port=os.environ['AWS_RDS_DB_PORT']
                )
            print(Fore.LIGHTGREEN_EX)
            print("\n🟢 PostgreSQL connection is open.\n")
            print(Style.RESET_ALL)
        except (Exception, Error) as error:
            print("Error while connecting to PostgreSQL:", error)
    else:
        print(Fore.YELLOW)
        print("\n🟠 PostgreSQL connection is already open.\n")
        print(Style.RESET_ALL)
    return g.db


def init_db():
    db = get_db()
    cursor = db.cursor()

    with current_app.open_resource('schema.sql') as f:
        cursor.execute(f.read().decode('utf8'))
        db.commit()
        print("Tables created successfully in PostgreSQL")


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()
        print(Fore.LIGHTRED_EX)
        print("\n🔴 PostgreSQL connection is closed.\n")
        print(Style.RESET_ALL)


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
