import requests
import json

from transport_providers.national_express.get_stations import q
from transport_providers.national_express.get_stations.update_nx_stations import get_sqlite_db

from route_finder import create_app

app = create_app()
session = requests.Session()

db = get_sqlite_db()
cursor = db.cursor()

def add_to_cache(response):

    print(json.dumps(response, indent=4))

    stop_id = response['stopId']
    airport_stop = response['airportStop']
    country = response['country']
    type = response['type']
    address_lines = str(response['addressLines'])
    european = response['european']
    euroline = response['euroline']

    cursor.execute("""
        UPDATE nx_stations
        SET
            airport_stop = ?,
            country = ?,
            type = ?,
            address = ?,
            european = ?,
            euroline = ?
        WHERE stop_id = ?;""", (airport_stop, country, type, address_lines, european, euroline, stop_id,))
    db.commit()

    db.close()

def fetch_more_details(stop_id):
        
    response_json = None

    done = False
    tries = 0
    while not done:
        tries += 1
        try:
            response = session.get(f'https://book.nationalexpress.com/nxrest/coachStop/from/{stop_id}', stream=True)
            response_json = json.loads(response.text)
            done = True
        except:
            try:
                response = session.get(f'https://book.nationalexpress.com/nxrest/coachStop/to/{stop_id}', stream=True)
                response_json = json.loads(response.text)
                done = True
            except:
                if tries >= 5:
                    done = True
                    print(f'No additional information found for {stop_id}')
                else:
                    pass
                    print(f'Retrying...')
                    # time.sleep(1)

    add_to_cache(response_json)
    
    if not len(q):
        print('\nQueue is empty!\n')
        from transport_providers.national_express.get_stations.upload_to_postgres import add_to_postgresql
        db.close()
        add_to_postgresql()
    else:
        print('\nJobs remaining', len(q), '\n')
