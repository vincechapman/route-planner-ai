def add_to_postgresql():

    from route_finder import create_app
    app = create_app()

    from route_finder.db import get_postgres_db, close_db
    from psycopg2.extras import execute_batch

    from transport_sdk.national_express.get_stations.update_nx_stations import get_sqlite_db

    with app.app_context():

        sqlite_db = get_sqlite_db()
        sqlite_cursor = sqlite_db.cursor()

        sqlite_cursor.execute("""
            SELECT * FROM nx_stations
        """)

        data = sqlite_cursor.fetchall()
        print('Grabbed data from SQLite database (i.e. nx_stations_cache.db)')

        sqlite_db.close()
        print("\n🔴 SQLite connection is closed.\n")

        postgres_db = get_postgres_db()
        postgres_cursor = postgres_db.cursor()

        # This clears all rows from the table without removing the table itself.
        postgres_cursor.execute("""
        DELETE FROM public.nx_stations;
        """)
        print(f'public.nx_stations has been cleared.')

        query = """
        INSERT INTO public.nx_stations (stop_id, stop_name, is_origin, is_destination, latitude, longitude, address, airport_stop, country, type, european, euroline)
            VALUES (%s, %s, %s::boolean, %s::boolean, %s, %s, %s, %s::boolean, %s, %s, %s::boolean, %s::boolean)
            """

        execute_batch(postgres_cursor, query, data)

        print(f'public.nx_stations has been updated.')

        postgres_db.commit()

        close_db()


        # This ensures the SQLite database has been cleared, ready for next time. 

        import os
        from pathlib import Path
        current_directory = Path(__file__).parent.resolve()

        from transport_sdk.national_express.get_stations.update_nx_stations import db_name

        file_path = db_name
        if os.path.isfile(f'{current_directory}/{file_path}'):
            os.remove(f'{current_directory}/{file_path}')
            print("\nCache has been deleted\n")
        else:
            print("\nCache does not exist\n")