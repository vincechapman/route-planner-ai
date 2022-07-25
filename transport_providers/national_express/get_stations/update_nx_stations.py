import json

import colorama
from colorama import Fore, Style
colorama.init() # Aparently this init() is needed for windows

from route_finder import create_app
app = create_app()

import requests
session = requests.Session()

url_to = 'https://book.nationalexpress.com/nxrest/coachStop/to'
url_from = 'https://book.nationalexpress.com/nxrest/coachStop/from'

db_name = 'nx_stations_cache.db'

from pathlib import Path
current_directory = Path(__file__).parent.resolve()


def get_sqlite_db():
    
    import sqlite3
    db = sqlite3.connect(f'{current_directory}/{db_name}')

    print("\n🟢 SQLite connection is open.\n")

    return db


def init_sqlite_db():

    db = get_sqlite_db()
    cursor = db.cursor()

    with open(f'{current_directory}/schema.sql', 'rb') as f:
        cursor.executescript(f.read().decode('utf8'))
        db.commit()
        print(f"Tables created successfully in {db_name}")

    return db
    

def adding_stations_to_cache(nx_stations):
    
    db = init_sqlite_db()
    cursor = db.cursor()

    data = [(stop_id, nx_stations[stop_id]['stop_name'], nx_stations[stop_id]['is_origin'], nx_stations[stop_id]['is_destination'], nx_stations[stop_id]['latitude'], nx_stations[stop_id]['longitude']) for stop_id in dict.keys(nx_stations)]
    # print(data)

    try:
        cursor.executemany("""
            INSERT INTO nx_stations (stop_id, stop_name, is_origin, is_destination, latitude, longitude)
            VALUES (?, ?, ?, ?, ?, ?)""", data)

        db.commit()

        print(f'Data committed to {db_name} successfully!')
        
    except Exception as e:
        print(f'Error adding data to {db_name}')
        try:
            print(e.message, e.args)
        except:
            print(e)
    
    finally:
        db.close()
        print("\n🔴 SQLite connection is closed.\n")


def get_nx_stations():

    nx_stations = {}


    # Getting TO stations

    response = session.get(url_to, stream=True)
    response = json.loads(response.text)

    for row in response:

        stop_id = row['id']

        # This sets empty rows to None
        if not row['longitude'].strip():
            row['longitude'] = None
        if not row['latitude'].strip():
            row['latitude'] = None

        nx_stations[stop_id] = {
            'stop_name': row['text'],
            'longitude': row['longitude'],
            'latitude': row['latitude'],
            'is_destination': True,
            'is_origin': False
            }


    # Getting FROM stations

    response = session.get(url_from, stream=True)
    response = json.loads(response.text)

    for row in response:

        stop_id = row['id']

        # This sets empty rows to None
        if not row['longitude'].strip():
            row['longitude'] = None
        if not row['latitude'].strip():
            row['latitude'] = None

        # This ONLY applies to rows in the response that DO NOT exist in nx_stations already.
        if not nx_stations[stop_id]:

            nx_stations[stop_id] = {
                'stop_name': row['text'],
                'longitude': row['longitude'],
                'latitude': row['latitude'],
                'is_destination': False
                }
            print(f'{Fore.GREEN}FROM ONLY station added!{Style.RESET_ALL}')

        # This applies to ALL rows in the response
        nx_stations[stop_id]['is_origin'] = True

        # This checks for disparities between TO and FROM.
        try:
            if nx_stations[stop_id]['stop_name'] != row['text']:
                print(f'For stop {row["id"]}, \'stop_name\' in FROM did not match TO')
                raise ValueError
            if nx_stations[stop_id]['longitude'] != row['longitude']:
                print(f'For stop {row["id"]}, \'longitude\' in FROM did not match TO')
                raise ValueError
            if nx_stations[stop_id]['latitude'] != row['latitude']:
                print(f'For stop {row["id"]}, \'latitude\' in FROM did not match TO')
                raise ValueError
        except ValueError:
            pass

    adding_stations_to_cache(nx_stations)

    return nx_stations
        

def print_nx_stations(nx_stations):

    for idx, stop_id in enumerate(dict.keys(nx_stations)):

        stop_name = nx_stations[stop_id]['stop_name']
        longitude = nx_stations[stop_id]['longitude']
        latitude = nx_stations[stop_id]['latitude']
        is_origin = nx_stations[stop_id]['is_origin']
        is_destination = nx_stations[stop_id]['is_destination']
        
        print()
        print(f'{Fore.LIGHTBLACK_EX}# {idx}')
        print(f'{"-" * 50}{Style.RESET_ALL}')
        print(f'STOP ID: {Fore.LIGHTRED_EX}{stop_id}{Style.RESET_ALL}')
        print(f'STOP NAME: {Fore.LIGHTCYAN_EX}{stop_name}{Style.RESET_ALL}')
        if longitude:
            print(f'LONGITUDE: {Fore.LIGHTYELLOW_EX}{longitude}{Style.RESET_ALL}')
        if latitude:
            print(f'LATITUDE: {Fore.LIGHTYELLOW_EX}{latitude}{Style.RESET_ALL}')
        print(f'IS ORIGIN: {Fore.MAGENTA}{is_origin}{Style.RESET_ALL}')
        print(f'IS DESTINATION: {Fore.MAGENTA}{is_destination}{Style.RESET_ALL}')
        print()


def queue_requests_for_more_info(nx_stations):

    from rq import Retry

    from transport_providers.national_express.get_stations import q
    q.empty() # Removes any items in the Queue from before.

    from transport_providers.national_express.get_stations.fetch_more_info import fetch_more_details

    '''Would the program be faster if I used enqueue_many instead? Would there be any price implications of making multiple calls.'''
    # jobs = q.enqueue_many(
    #     [
    #         Queue.prepare_data(fetch_more_details, str(stop_id), job_id=f'Fetching more details for {stop_id}...') for stop_id in dict.keys(nx_stations)
    #     ]
    # )

    count = 0
    for stop_id in dict.keys(nx_stations):
        q.enqueue(fetch_more_details, stop_id, retry=Retry(max=3, interval=[10, 30, 60]))
        count +=1

    print(Fore.LIGHTBLUE_EX)
    print(f'\n{count} jobs queued.\n')
    print(Style.RESET_ALL)


if __name__ == '__main__':
    nx_stations = get_nx_stations()
    print_nx_stations(nx_stations)
    queue_requests_for_more_info(nx_stations)
    pass

'''
Ideally I'd make this so that it tries this method of grabbing data first, and then if it fails at any point (which it might do if national express change anything with their API e.g. if stopId becomes stationId) it switches to the selenium based approach, which is slower but based on html.

It should also notify me in this case so that I can get the direct API method up and running again. The selenium method would be much slower.

I think wherever web scraping functions are used, we should always implement:

- backup option/s (doesn't have to be the best solution, just something that carries out the same task using a different method.)

- a notification system (something that notifies me when changes have been made on nx's API/website that affect our program)

- a testing system (maybe something that keeps a record of the latest API response that worked, so that if our program stops crashing we can compare the response against the last response that worked to try and identify disparities that may be causing the program to fail. This might then use the notification system to notify me of these changes.)

- a down-for-maintenance system or a warning message. If the program detects a change in NX's API that is causing the program to crash, it should set itself to down-for-maintance or warn users and allow them to proceed at their own discretion.

'''