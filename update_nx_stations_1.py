from string import ascii_letters, digits
import requests
import json

import os
from dotenv import load_dotenv
load_dotenv()

# from requests_ip_rotator import ApiGateway
# gateway = ApiGateway(site='https://book.nationalexpress.com/coach/', access_key_id=os.environ.get('aws_access_key_id'), access_key_secret=os.environ.get('aws_secret_access_key'))

session = requests.Session()
# session.mount('https://book.nationalexpress.com/coach/', gateway)

from flaskr import create_app
from flaskr.db import get_db, close_db

app = create_app()


def fetch_more_details(code):
        
    response_json = None

    done = False
    tries = 0
    while not done:
        tries += 1
        try:
            response = session.get(f'https://book.nationalexpress.com/nxrest/coachStop/from/{code}', stream=True)
            response_json = json.loads(response.text)
            done = True
        except:
            try:
                response = session.get(f'https://book.nationalexpress.com/nxrest/coachStop/to/{code}', stream=True)
                response_json = json.loads(response.text)
                done = True
            except:
                if tries >= 5:
                    done = True
                    print(f'        No additional information found for {code}')
                else:
                    pass
                    print(f'        Retrying...')
                    # time.sleep(1)
    
    return response_json

def search(query, db):

    url = f"https://www.nationalexpress.com/umbraco/api/stationsapi/search?term={query}&isorigin=false&disableGeoSearch=False" # Note that three is_origin locations disappear when I change is_origin to false in the URL. Perhaps investigate this at some point.
    response = requests.get(url).text
    stations = json.loads(response)[0]['Stations']

    # results = {}

    for i in range(len(stations)):

        print()

        code = stations[i]['LocationCode']
        name = stations[i]['LocationName']

        is_origin = stations[i]['IsOrigin']
        is_destination = stations[i]['IsDestination']

        latitude = stations[i]['Latitude']
        longitude = stations[i]['Longitude']

        with db.cursor() as cursor:
            cursor.execute('SELECT stop_id FROM nx_stations WHERE stop_id = %s', (code,))
            exists = cursor.fetchone()

        # 1 indent
        if exists:
            print(f'    {code} already exists!')
        else:
            print(f'    Adding new station: {code}')

        if not exists:

            if not latitude:
                latitude = None

            if not longitude:
                longitude = None

            address_lines = None

            more_details_found = False

            response_json = fetch_more_details(code)

            if response_json:

                if response_json['latitude']:
                    latitude = response_json['latitude']
                    more_details_found = True
                
                if response_json['longitude']:
                    longitude = response_json['longitude']
                    more_details_found = True
                
                if response_json['addressLines']:
                    address_lines = str(response_json['addressLines'])
                    more_details_found = True

            if more_details_found:
                print(f'        Found more details for {code}:')
                if latitude:
                    print(f'            - Latitude: {latitude}')
                if longitude:
                    print(f'            - Longitude: {longitude}')
                if address_lines:
                    print(f'            - Address: {address_lines}')

            with db.cursor() as cursor:
                cursor.execute('''
                    INSERT INTO public.nx_stations (stop_id, stop_name, is_origin, is_destination, latitude, longitude, address)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)''', (code, name, is_origin, is_destination, latitude, longitude, address_lines,))
                db.commit()

    # return results
    
def get_all_stations():

    # clear_model(NationalExpressStations)

    with app.app_context():

        db = get_db()
        cursor = db.cursor()

        for char in (ascii_letters + digits):
            print('\nMerging all location names that contain:', char)
            try:
                search(char, db) # Merges the latest search query results with current overall stations dictionary.
            except IndexError:
                print('No location names contain', char)

        # db.session.commit()

    close_db()

if __name__ == '__main__':
    # gateway.start()
    get_all_stations()
    # gateway.shutdown()
    pass
