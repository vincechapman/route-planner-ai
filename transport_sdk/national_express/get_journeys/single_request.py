import json

from datetime import datetime

from transport_sdk.national_express.get_journeys.helpers import generate_headers, dict_hash
from proxy_rotator import build_rotator, bd_proxy_rotator

def single_request(payload, headers=generate_headers(), opener=build_rotator(deactivate_proxies=False)):

    '''This function makes 1 request to the national express API for a specific date and time.'''

    payload_hash = dict_hash(payload)

    try:

        response = bd_proxy_rotator(
            url='https://book.nationalexpress.com/nxrest/journey/search/OUT',
            headers=headers,
            payload=payload,
            opener=opener
        )

        request_time = datetime.utcnow()

        status_code = response.code
        response = json.load(response)

        # This checks if the request has been blocked by incapsula
        if status_code == 200 and not response['journeyCommand']:

            raise Exception("Request failed. Most likely blocked by incapsula. Or response JSON structure/naming has been updated.")

    except Exception as e:
        
        print('\nINCAPSULA ERROR!!!\n')
        print(e)
    
    else:

        from route_finder import create_app
        app = create_app()

        from route_finder.db import get_postgres_db, DatabaseConnection

        with app.app_context():
            with DatabaseConnection(get_postgres_db()) as db:

                cursor = db.cursor()

                for journey in response['journeyCommand']:

                    journey_id = journey['journeyId']

                    departure_stop_id = journey['legs'][0]['departureStopId']
                    destination_stop_id = journey['legs'][-1]['destinationStopId']
                    
                    departure_date = datetime.date(datetime.strptime(journey['departureDateTime'].split('T')[0], '%Y-%m-%d'))
                    arrival_date = datetime.date(datetime.strptime(journey['arrivalDateTime'].split('T')[0], '%Y-%m-%d'))

                    departure_time = datetime.time(datetime.strptime(journey['departureDateTime'].split('T')[1], '%H:%M:%S'))
                    arrival_time = datetime.time(datetime.strptime(journey['arrivalDateTime'].split('T')[1], '%H:%M:%S'))

                    price = float(str(journey['fare']['amountInPennies'])[:-2] + '.' + str(journey['fare']['amountInPennies'])[-2:])

                    extra_fees = None # Add booking fees and other here

                    cursor.execute('''
                        INSERT INTO public.nx_journeys (journey_id, departure_stop_id, destination_stop_id, departure_date, departure_time, arrival_date, arrival_time, price, extra_fees, payload_hash, request_time)
                            VALUES (%(journey_id)s, %(departure_stop_id)s, %(destination_stop_id)s, %(departure_date)s, %(departure_time)s, %(arrival_date)s, %(arrival_time)s, %(price)s, %(extra_fees)s, %(payload_hash)s, %(request_time)s)
                            ON CONFLICT (journey_id) DO UPDATE SET
                                price = %(price)s,
                                departure_stop_id = %(departure_stop_id)s,
                                destination_stop_id = %(destination_stop_id)s,
                                departure_date = %(departure_date)s,
                                departure_time = %(departure_time)s,
                                arrival_date = %(arrival_date)s,
                                arrival_time = %(arrival_time)s,
                                extra_fees = %(extra_fees)s,
                                request_time = %(request_time)s;
                        ''', {
                            'journey_id': journey_id,
                            'departure_stop_id': departure_stop_id,
                            'destination_stop_id': destination_stop_id,
                            'departure_date': departure_date,
                            'departure_time': departure_time,
                            'arrival_date': arrival_date,
                            'arrival_time': arrival_time,
                            'price': price,
                            'extra_fees': extra_fees,
                            'payload_hash': payload_hash,
                            'request_time': request_time,
                            }
                    )

                db.commit()

                print(f'Added/updated {payload_hash} in database.')

    return response


if __name__ == '__main__':

    from transport_sdk.national_express.get_journeys.helpers import generate_payload

    single_request(
        payload=generate_payload(
            journey_type='SINGLE',
            outbound_date='07/08/2022',
            outbound_time='17:00',
            from_station_id='57000',
            to_station_id='87025'),
        headers=generate_headers(),
        opener=build_rotator(deactivate_proxies=True)
    )