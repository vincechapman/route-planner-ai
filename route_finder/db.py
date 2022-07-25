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


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


class DatabaseConnection(object):

    def __init__(self, connection, label=None):

        if label is not None:
            self.label = label
        else:
            self.label = connection

        try:
            g.db = connection
            self.db = g.db
            print(f"\n{Fore.LIGHTGREEN_EX}🟢 Database connection opened:{Style.RESET_ALL} {self.label}\n{'-' * 50}\n")
        
        except Exception as e:
            print(f"\n{Fore.LIGHTRED_EX}🔴 Failed to create database connection:{Style.RESET_ALL} {self.label}\n{'-' * 50}\n")
            print(e)

    def __enter__(self):
        return self.db

    def __exit__(self, exc_type, exc_val, traceback):
        if 'db' not in g:
            print(f"\n{Fore.LIGHTMAGENTA_EX}🟣 All database connections closed already.{Style.RESET_ALL}\n")
        else:
            close_db()
            print(f"\n{'-' * 50}\n{Fore.LIGHTMAGENTA_EX}🟣 Database connection closed{Style.RESET_ALL}\n")
            


def get_postgres_db():

    if 'db' not in g:

        try:
            g.db = psycopg2.connect(
                user=os.environ['AWS_RDS_DB_USER'],
                password=os.environ['AWS_RDS_DB_PASSWORD'],
                host=os.environ['AWS_RDS_DB_HOST'],
                port=os.environ['AWS_RDS_DB_PORT']
                )

        except (Exception, Error) as error:
            print(f"{Fore.LIGHTRED_EX}🔴 Error while connecting to PostgreSQL: {error}{Style.RESET_ALL}")

    else:
        print(f'{Fore.YELLOW}🟠 {Style.RESET_ALL}')

    return g.db


def init_db():
    db = get_postgres_db()
    cursor = db.cursor()

    with current_app.open_resource('schema.sql') as f:
        cursor.execute(f.read().decode('utf8'))
        db.commit()
        print("Tables created successfully in PostgreSQL")


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
